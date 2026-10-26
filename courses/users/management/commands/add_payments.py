from datetime import date

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from courses.models import Course, Lesson
from users.models import Payment

User = get_user_model()


class Command(BaseCommand):
    help = "Add test payments to the database"

    def handle(self, *args, **kwargs):
        user1 = User.objects.get(email="user1@gmail.com")
        user2 = User.objects.get(email="user2@gmail.com")

        course = Course.objects.get(title="Курс_1")
        lesson = Lesson.objects.get(title="База 1. Введение")

        payments = [
            {
                "user": user1,
                "payment_date": date(2026, 10, 20),
                "amount": 1500.00,
                "course": course,
                "payment_type": Payment.CASH,
                "lesson": None,
            },
            {
                "user": user2,
                "payment_date": date(2026, 10, 20),
                "amount": 500.00,
                "lesson": lesson,
                "payment_type": Payment.TRANSACTION,
                "course": None,
            },
        ]

        for payment_data in payments:
            payment, created = Payment.objects.get_or_create(**payment_data)

            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"Successfully added payment: {payment.id}")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"Payment already exists: {payment.id}")
                )
