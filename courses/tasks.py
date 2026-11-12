from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

from .models import Course, CourseSubscription


@shared_task(bind=True, max_retries=3)
def send_course_update_notification(self, course_id: int):
    """
    Рассылка об обновлении курса всем подписчикам.
    """
    try:
        course = Course.objects.get(pk=course_id)
    except Course.DoesNotExist:
        return  # Курс удалён, ничего не делаем

    subscribers = CourseSubscription.objects.filter(course=course).select_related(
        "user"
    )

    emails = [sub.user.email for sub in subscribers if sub.user.email]

    if not emails:
        print(f"Нет подписчиков с email для курса {course.id} — рассылка пропущена.")
        return

    subject = f"Курс «{course.title}» был обновлён!"
    message = (
        f"Привет! Курс «{course.title}», на который ты подписан, был обновлён.\n\n"
        f"Заходи и проверяй новые материалы!"
    )

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=emails,
            fail_silently=False,
        )
        print(
            f"Рассылка для курса '{course.title}' завершена. Письма отправлены на {len(emails)} адресов."
        )
    except Exception as exc:
        """Если отправка не удалась — пробуем ещё 3 раза"""
        raise self.retry(exc=exc, countdown=60)
