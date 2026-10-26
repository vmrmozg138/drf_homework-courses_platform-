from rest_framework import generics, permissions, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from .models import Course, Lesson
from .permissions import IsModerator, IsNotModerator, IsOwner
from .serializers import CourseSerializer, LessonSerializer

"""Контроллер для модели Course реализован через ViewSet"""


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

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
    permission_classes = IsAuthenticated

    def perform_create(self, serializer):
        if not Course.objects.exists():
            raise ValidationError({"course": "Сначала необходимо создать курс."})

        serializer.save(owner=self.request.user)


class LessonListAPIView(generics.ListAPIView):
    serializer_class = LessonSerializer

    def get_queryset(self):
        qs = Lesson.objects.all()
        user = self.request.user

        if not user.is_authenticated:
            return qs.none()

        if user.groups.filter(name="moderator").exists():
            return qs

        return qs.filter(owner=user)

    permission_classes = IsAuthenticated


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


class LessonDestroyAPIView(generics.DestroyAPIView):
    queryset = Lesson.objects.all()

    def get_permissions(self):
        return [IsOwner()]
