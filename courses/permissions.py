from rest_framework import permissions


class IsModerator(permissions.BasePermission):

    message = "Вы должны быть модератором для доступа к запрашиваемому ресурсу"

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        return request.user.groups.filter(name="moderator").exists()


class IsNotModerator(permissions.BasePermission):
    message = "Модераторы не могут создавать объекты."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        # Разрешаем, если пользователь НЕ в группе moderator
        return not user.groups.filter(name="moderator").exists()


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user
