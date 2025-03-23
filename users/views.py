from django.shortcuts import render
from rest_framework import mixins
from rest_framework import viewsets
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer, RegisterSerializer, ProfileSerializer
from products.permissions import IsObjectOwnerOrReadOnly
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import action
from rest_framework.response import Response



User = get_user_model()

class UserViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer


class RegisterViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer


class ProfileViewSet(mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated, IsObjectOwnerOrReadOnly]

    def get_object(self):
        return self.request.user

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
