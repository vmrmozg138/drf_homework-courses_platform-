from rest_framework import serializers

from .models import Payment, User


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"


"""поменял местами сериализаторы - использую вложенный сериализатор платежа 
в сериализаторе пользователя для вывода истории платежей. а для того, чтобы 
порядок был по возрастанию даты, прописан ordering в модели платежа """


class UserSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = "__all__"
