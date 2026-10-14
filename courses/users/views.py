from rest_framework import generics

from courses.users.models import User
from courses.users.serializers import UserSerializer


class UserUpdateAPIView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
