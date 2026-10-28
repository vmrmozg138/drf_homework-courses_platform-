import re
from rest_framework import serializers

YOUTUBE_ONLY_PATTERN = re.compile(
    r'(?:https?://)(?:www\.)?youtube\.com/watch\?v=[A-Za-z0-9_-]{11}\b'
)

def validate_only_youtube_links(value: str) -> str:
    if not value:
        return value

    if not YOUTUBE_ONLY_PATTERN.match(value):
        raise serializers.ValidationError(
            "Разрешена только ссылка на YouTube вида youtube.com/watch?v=..."
        )
    return value


