from django.conf import settings
from django.db import models


class Course(models.Model):
    title = models.CharField(max_length=100)
    preview = models.ImageField(upload_to="images/", null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="courses",
        verbose_name="Владелец",
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )
    stripe_product_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )
    stripe_price_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"


class Lesson(models.Model):
    title = models.CharField(max_length=100, verbose_name="")
    description = models.TextField(null=True, blank=True)
    preview = models.ImageField(upload_to="images/", null=True, blank=True)
    video_url = models.URLField(null=True, blank=True, max_length=500)

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons")

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="lessons",
        verbose_name="Владелец",
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )
    stripe_product_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )
    stripe_price_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"


class CourseSubscription(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subscriptions",
        verbose_name="Пользователь",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="subscribers",
        verbose_name="Курс",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата подписки")

    class Meta:
        verbose_name = "Подписка на курс"
        verbose_name_plural = "Подписки на курсы"
        # чтобы нельзя было подписаться дважды на один курс
        unique_together = ("user", "course")

    def __str__(self):
        return f"{self.user.email} — {self.course.title}"
