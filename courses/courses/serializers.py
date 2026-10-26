from rest_framework import serializers

from .models import Course, Lesson

"""LessonShortSerializer это для отображения вложенного сериализатора в курсе"""


class LessonShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = (
            "id",
            "title",
            "description",
        )


class CourseSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()
    lessons_info = LessonShortSerializer(
        source="lessons",
        many=True,
        read_only=True,
    )

    def get_lessons_count(self, obj):
        return obj.lessons.count()

    class Meta:
        model = Course
        fields = (
            "id",
            "title",
            "description",
            "lessons_count",
            "lessons_info",
        )


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = (
            "id",
            "title",
            "description",
            "course",
        )
