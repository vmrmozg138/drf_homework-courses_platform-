from django.urls import path

from .apps import UsersConfig
from .views import UserUpdateAPIView

app_name = UsersConfig.name

urlpatterns = [
    path("users/update/<int:pk>", UserUpdateAPIView.as_view(), name="users-update"),
]
