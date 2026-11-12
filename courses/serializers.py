from rest_framework import serializers

from .models import Course, CourseSubscription, Lesson
from .validators import validate_only_youtube_links

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
    is_subscribed = serializers.SerializerMethodField()

    lessons_info = LessonShortSerializer(
        source="lessons",
        many=True,
        read_only=True,
    )

    def get_lessons_count(self, obj):
        return obj.lessons.count()

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        if not request or not request.user or not request.user.is_authenticated:
            return False

        return CourseSubscription.objects.filter(user=request.user, course=obj).exists()

    class Meta:
        model = Course
        fields = (
            "id",
            "title",
            "description",
            "lessons_count",
            "lessons_info",
            "is_subscribed",
        )


class LessonSerializer(serializers.ModelSerializer):
    video_url = serializers.URLField(
        allow_blank=True, required=False, validators=[validate_only_youtube_links]
    )

    class Meta:
        model = Lesson
        fields = ("id", "title", "description", "course", "video_url")


"""сериализатор для подписки"""


class CourseSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseSubscription
        fields = ["id", "user", "course", "created_at"]
        read_only_fields = ["user", "created_at"]
