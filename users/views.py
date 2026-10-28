from datetime import date

import requests
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status, viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from courses.models import Course, Lesson
from users.services.stripe import create_checkout_session, retrieve_checkout_session

from .filters import PaymentFilter
from .models import Payment, User
from .serializers import (
    PaymentSerializer,
    PaymentStatusSerializer,
    RegisterSerializer,
    UserSerializer,
)


class UserListAPIView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]


class UserUpdateAPIView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return User.objects.filter(pk=user.pk)


class UserRetrieveAPIView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return User.objects.all()
        return User.objects.filter(pk=user.pk)


class UserDestroyAPIView(generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    queryset = User.objects.none()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PaymentsListAPIView(generics.ListAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter,
    ]
    """для фильтрации используем PaymentFilter"""
    filterset_class = PaymentFilter

    ordering_fields = ["payment_date"]
    ordering = ["-payment_date"]


class CreatePaymentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        if "course_id" in data:
            item = get_object_or_404(Course, pk=data["course_id"])
            payment_data = {"course": item, "lesson": None}
        else:
            item = get_object_or_404(Lesson, pk=data["lesson_id"])
            payment_data = {"course": None, "lesson": item}

        payment = Payment.objects.create(
            user=request.user,
            payment_date=date.today(),
            amount=item.price,
            payment_type=Payment.STRIPE,
            status=Payment.PENDING,
            **payment_data,
        )

        try:
            session = create_checkout_session(
                payment=payment,
                item=item,
                success_url=(
                    "http://localhost:8000/" "?session_id={CHECKOUT_SESSION_ID}"
                ),
                cancel_url="http://localhost:8000/",
            )
        except (requests.RequestException, ValueError):
            payment.status = Payment.FAILED
            payment.save(update_fields=["status"])
            return Response(
                {"detail": "Не удалось создать платёжную сессию."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response(
            {
                "payment_id": payment.pk,
                "session_id": session["id"],
                "payment_url": session["url"],
            },
            status=status.HTTP_201_CREATED,
        )


class CheckPaymentStatusAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Payment.objects.all()

    def get(self, request, payment_id):
        payment = get_object_or_404(
            self.get_queryset(),
            pk=payment_id,
            user=request.user,
        )

        if not payment.session_id:
            return Response(
                {"detail": "У платежа нет Stripe Session ID."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            session = retrieve_checkout_session(payment.session_id)
        except (requests.RequestException, ValueError):
            return Response(
                {"detail": "Не удалось проверить платёж в Stripe."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        stripe_payment_status = session.get("payment_status")
        stripe_session_status = session.get("status")

        if stripe_payment_status == "paid":
            payment.status = Payment.PAID
            payment.save(update_fields=["status"])
        elif stripe_session_status == "expired":
            payment.status = Payment.CANCELLED
            payment.save(update_fields=["status"])

        response_data = {
            "payment_id": payment.pk,
            "status": payment.status,
            "stripe_payment_status": stripe_payment_status,
            "stripe_session_status": stripe_session_status,
        }

        serializer = PaymentStatusSerializer(data=response_data)
        serializer.is_valid(raise_exception=True)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
