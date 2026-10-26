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

    def __str__(self):
        return self.name

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

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"
