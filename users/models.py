from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models

from courses.models import Course, Lesson


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Пользователь должен иметь email")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Суперпользователь должен иметь is_staff=True")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Суперпользователь должен иметь is_superuser=True")

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(
        verbose_name="Почта", unique=True, help_text="Введите почту"
    )
    phone_number = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name="Номер телефона",
        help_text="Введите номер телефона",
    )
    city = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Город",
        help_text="Введите название города",
    )
    avatar = models.ImageField(
        upload_to="users/avatars",
        verbose_name="Аватар",
        help_text="Загрузите аватар",
        null=True,
        blank=True,
    )

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class Payment(models.Model):
    CASH = "cash"
    TRANSACTION = "transaction"
    STRIPE = "stripe"

    PAYMENT_CHOICES = [
        (CASH, "Наличные"),
        (TRANSACTION, "Банковский перевод"),
        (STRIPE, "Stripe"),
    ]

    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (PENDING, "Ожидает оплаты"),
        (PAID, "Оплачен"),
        (FAILED, "Ошибка оплаты"),
        (CANCELLED, "Отменён"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payments")
    payment_date = models.DateField()
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Сумма платежа",
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="payments", blank=True, null=True
    )
    lesson = models.ForeignKey(
        Lesson, on_delete=models.CASCADE, related_name="payments", blank=True, null=True
    )
    payment_type = models.CharField(
        choices=PAYMENT_CHOICES, max_length=15, verbose_name="Способ оплаты"
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=PENDING,
        verbose_name="Статус платежа",
    )

    session_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Id сессии",
        help_text="Укажите Id сессии",
    )
    link = models.URLField(
        max_length=399,
        null=True,
        blank=True,
        verbose_name="Ссылка на оплату",
        help_text="Укажите ссылку на оплату",
    )

    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"
        ordering = ["-payment_date"]
