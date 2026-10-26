from django.urls import path
from rest_framework.routers import DefaultRouter

from .apps import UsersConfig
from .views import UserListAPIView, UserUpdateAPIView

app_name = UsersConfig.name


urlpatterns = [
    path("update/<int:pk>", UserUpdateAPIView.as_view(), name="users-update"),
    path("list/", UserListAPIView.as_view(), name="users-list"),
]
