from django.contrib.auth.models import Group
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient, force_authenticate

from users.models import User

from .models import Course, CourseSubscription, Lesson


class LessonsAndSubscriptionTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user_owner = User.objects.create_user(
            email="owner@example.com", password="pass"
        )

        self.user_other = User.objects.create_user(
            email="other@example.com", password="pass"
        )

        self.user_moderator = User.objects.create_user(
            email="mod@example.com", password="pass"
        )

        moderator_group, _ = Group.objects.get_or_create(name="moderator")
        self.user_moderator.groups.add(moderator_group)

        self.course = Course.objects.create(title="Test Course", owner=self.user_owner)
        self.lesson = Lesson.objects.create(
            title="Test Lesson", course=self.course, owner=self.user_owner
        )

    def test_create_lesson_by_owner(self):
        """Обычный пользователь может создать урок, если есть курс."""
        self.client.force_authenticate(user=self.user_owner)
        payload = {
            "title": "New Lesson",
            "description": "Desc",
            "course": self.course.id,
        }
        response = self.client.post("/lessons/create/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Lesson.objects.filter(title="New Lesson").exists())

    def test_create_lesson_without_course_raises_error(self):
        """Если курсов нет вообще — создание урока должно падать с ValidationError."""
        Course.objects.all().delete()
        self.client.force_authenticate(user=self.user_owner)
        payload = {"title": "No Course Lesson", "description": "Desc"}
        response = self.client.post("/lessons/create/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("course", response.data)

    def test_list_lessons_owner_sees_own(self):
        """Владелец видит свои уроки (пагинация: results)."""
        self.client.force_authenticate(user=self.user_owner)
        response = self.client.get("/lessons/list/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Пагинация DRF: данные лежат в results
        self.assertEqual(len(response.data["results"]), 1)

    def test_list_lessons_other_user_sees_none(self):
        """Другой пользователь не видит чужие уроки (get_queryset)."""
        self.client.force_authenticate(user=self.user_other)
        response = self.client.get("/lessons/list/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 0)

    def test_list_lessons_moderator_sees_all(self):
        """Модератор видит все уроки."""
        self.client.force_authenticate(user=self.user_moderator)
        response = self.client.get("/lessons/list/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data["results"]), 1)

    def test_retrieve_lesson_owner_can_access(self):
        """Владелец может получить свой урок."""
        self.client.force_authenticate(user=self.user_owner)
        response = self.client.get(f"/lessons/{self.lesson.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_lesson_other_cannot_access(self):
        """Другой пользователь получает 403 на чужой урок (IsOwner)."""
        self.client.force_authenticate(user=self.user_other)
        response = self.client.get(f"/lessons/{self.lesson.id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_lesson_owner_can(self):
        """Владелец может обновить свой урок (PATCH)."""
        self.client.force_authenticate(user=self.user_owner)
        payload = {"title": "Updated Title"}
        response = self.client.patch(
            f"/lessons/update/{self.lesson.id}/", payload, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.title, "Updated Title")

    def test_update_lesson_other_cannot(self):
        """Другой пользователь не может обновить чужой урок."""
        self.client.force_authenticate(user=self.user_other)
        payload = {"title": "Hacked Title"}
        response = self.client.patch(
            f"/lessons/update/{self.lesson.id}/", payload, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_destroy_lesson_owner_can(self):
        """Владелец может удалить свой урок."""
        self.client.force_authenticate(user=self.user_owner)
        response = self.client.delete(f"/lessons/delete/{self.lesson.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Lesson.objects.filter(id=self.lesson.id).exists())

    def test_destroy_lesson_other_cannot(self):
        """Другой пользователь не может удалить чужой урок."""
        self.client.force_authenticate(user=self.user_other)
        response = self.client.delete(f"/lessons/delete/{self.lesson.id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Lesson.objects.filter(id=self.lesson.id).exists())

    def test_subscribe_toggle_creates_subscription(self):
        """POST создаёт подписку если её нет."""
        self.client.force_authenticate(user=self.user_owner)
        url = f"/courses/{self.course.id}/subscribe/"
        response = self.client.post(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            CourseSubscription.objects.filter(
                user=self.user_owner, course=self.course
            ).exists()
        )
        self.assertEqual(response.data["message"], "Подписка добавлена")

    def test_subscribe_toggle_removes_subscription(self):
        """Повторный POST удаляет подписку."""
        CourseSubscription.objects.create(user=self.user_owner, course=self.course)

        self.client.force_authenticate(user=self.user_owner)
        url = f"/courses/{self.course.id}/subscribe/"
        response = self.client.post(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(
            CourseSubscription.objects.filter(
                user=self.user_owner, course=self.course
            ).exists()
        )
        self.assertEqual(response.data["message"], "Подписка удалена")

    def test_subscribe_unauthenticated_returns_401(self):
        """Неавторизованный пользователь получает 401."""
        self.client.force_authenticate(user=None)
        url = f"/courses/{self.course.id}/subscribe/"
        response = self.client.post(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_subscribe_other_user_can_subscribe_to_any_course(self):
        """Любой авторизованный пользователь может подписаться на любой курс."""
        self.client.force_authenticate(user=self.user_other)
        url = f"/courses/{self.course.id}/subscribe/"
        response = self.client.post(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            CourseSubscription.objects.filter(
                user=self.user_other, course=self.course
            ).exists()
        )
