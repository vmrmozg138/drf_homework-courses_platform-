from rest_framework import generics, viewsets
from rest_framework.exceptions import ValidationError

from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer

"""Контроллер для модели Course реализован через ViewSet"""


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer


"""Контроллеры для модели Lesson - через generics"""


class LessonCreateAPIView(generics.CreateAPIView):
    serializer_class = LessonSerializer

    def perform_create(self, serializer):
        if not Course.objects.exists():
            raise ValidationError({"course": "Сначала необходимо создать курс."})

        serializer.save()


class LessonListAPIView(generics.ListAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


class LessonRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


class LessonUpdateAPIView(generics.UpdateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


class LessonDestroyAPIView(generics.DestroyAPIView):
    queryset = Lesson.objects.all()
