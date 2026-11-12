from datetime import timedelta

from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils import timezone


@shared_task
def deactivate_inactive_users():
    User = get_user_model()
    cutoff_date = timezone.now() - timedelta(days=30)

    users_to_deactivate = User.objects.filter(
        is_active=True, last_login__lt=cutoff_date, is_superuser=False, is_staff=False
    )

    count = users_to_deactivate.update(is_active=False)
    print(f"[CELERY] Заблокировано пользователей (>30 дней без входа): {count}")
    return count
