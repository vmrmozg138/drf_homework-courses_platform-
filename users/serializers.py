from rest_framework import serializers

from .models import Payment, User


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"


"""Добавлен сериализатор для создания платежа"""


class PaymentCreateSerializer(serializers.Serializer):
    course_id = serializers.IntegerField(required=False)
    lesson_id = serializers.IntegerField(required=False)

    def validate(self, attrs):
        course_id = attrs.get("course_id")
        lesson_id = attrs.get("lesson_id")

        if bool(course_id) == bool(lesson_id):
            raise serializers.ValidationError(
                "Укажите course_id или lesson_id, но не оба сразу."
            )

        return attrs


"""А также сериализатор для проверки статуса платежа"""


class PaymentStatusSerializer(serializers.Serializer):
    payment_id = serializers.IntegerField()
    status = serializers.CharField()
    stripe_payment_status = serializers.CharField(
        allow_null=True,
    )
    stripe_session_status = serializers.CharField(
        allow_null=True,
    )


"""поменял местами сериализаторы - использую вложенный сериализатор платежа 
в сериализаторе пользователя для вывода истории платежей. а для того, чтобы 
порядок был по возрастанию даты, прописан ordering в модели платежа """


class UserSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = "__all__"


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "password", "password_confirm"]

    def validate(self, data):
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError("Пароли не совпадают")
        return data

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")
        user = self.Meta.model(**validated_data)
        user.set_password(password)
        user.save()
        return user
