from rest_framework import generics, permissions, status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Course, CourseSubscription, Lesson
from .paginators import CoursePagination, LessonPagination
from .permissions import IsModerator, IsNotModerator, IsOwner
from .serializers import CourseSerializer, LessonSerializer
from .tasks import send_course_update_notification

"""Контроллер для модели Course реализован через ViewSet"""


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    pagination_class = CoursePagination

    def get_permissions(self):

        user = self.request.user
        is_moderator = (
            user.is_authenticated and user.groups.filter(name="moderator").exists()
        )

        if self.action == "create":
            return [IsNotModerator()]

        if self.action == "destroy":
            return [IsOwner()]

        if self.action == "list":
            return []

        if self.action in ["retrieve", "update", "partial_update"]:
            if is_moderator:
                return [IsModerator()]
            else:
                return [IsOwner()]

        return []

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        if not user.is_authenticated:
            return qs.none()

        if user.groups.filter(name="moderator").exists():
            return qs

        return qs.filter(owner=user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


"""Контроллеры для модели Lesson - через generics"""


class LessonCreateAPIView(generics.CreateAPIView):
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        if not Course.objects.exists():
            raise ValidationError({"course": "Сначала необходимо создать курс."})

        lesson = serializer.save(owner=self.request.user)
        course = lesson.course
        course.save()
        send_course_update_notification.delay(course.id)


class LessonListAPIView(generics.ListAPIView):
    serializer_class = LessonSerializer
    pagination_class = LessonPagination

    def get_queryset(self):
        qs = Lesson.objects.all()
        user = self.request.user

        if not user.is_authenticated:
            return qs.none()

        if user.groups.filter(name="moderator").exists():
            return qs

        return qs.filter(owner=user)

    permission_classes = [IsAuthenticated]


class LessonRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        user = self.request.user
        if user.is_authenticated and user.groups.filter(name="moderator").exists():
            return [IsModerator()]
        return [IsOwner()]


class LessonUpdateAPIView(generics.UpdateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        user = self.request.user
        if user.is_authenticated and user.groups.filter(name="moderator").exists():
            return [IsModerator()]
        return [IsOwner()]

    def perform_update(self, serializer):
        lesson = serializer.save()
        course = lesson.course
        course.save()
        send_course_update_notification.delay(course.id)


class LessonDestroyAPIView(generics.DestroyAPIView):
    queryset = Lesson.objects.all()

    def get_permissions(self):
        return [IsOwner()]


"""контроллер для подписки"""


class CourseSubscribeToggleView(APIView):
    def post(self, request, course_id):
        user = request.user
        if not user.is_authenticated:
            return Response(
                {"detail": "Требуется авторизация."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        course = get_object_or_404(Course, id=course_id)

        # Ищем существующую подписку пользователя на этот курс
        subs_item = CourseSubscription.objects.filter(user=user, course=course)

        if subs_item.exists():
            # Подписка есть → удаляем
            subs_item.delete()
            message = "Подписка удалена"
            status_code = status.HTTP_200_OK
        else:
            # Подписки нет → создаём
            CourseSubscription.objects.create(user=user, course=course)
            message = "Подписка добавлена"
            status_code = status.HTTP_201_CREATED

        return Response({"message": message}, status=status_code)
