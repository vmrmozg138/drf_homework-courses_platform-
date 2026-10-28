from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .apps import UsersConfig
from .views import (
    CreatePaymentAPIView,
    RegisterView,
    UserDestroyAPIView,
    UserListAPIView,
    UserRetrieveAPIView,
    UserUpdateAPIView,
)

app_name = UsersConfig.name


urlpatterns = [
    path("login", TokenObtainPairView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("users/", UserListAPIView.as_view(), name="user-list"),
    path("users/<int:pk>/", UserRetrieveAPIView.as_view(), name="user-detail"),
    path("users/<int:pk>/update/", UserUpdateAPIView.as_view(), name="user-update"),
    path("users/<int:pk>/delete/", UserDestroyAPIView.as_view(), name="user-delete"),
    path("register/", RegisterView.as_view(), name="register"),
    path(
        "payments/create/",
        CreatePaymentAPIView.as_view(),
        name="payment-create",
    ),
]
