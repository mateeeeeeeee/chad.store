from django.shortcuts import render
from rest_framework import mixins, viewsets, permissions, response, status
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer, RegisterSerializer, ProfileSerializer, PasswordResetSerializer
from products.permissions import IsObjectOwnerOrReadOnly
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi



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

class ResetPasswordViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = PasswordResetSerializer

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.get(email=email)
            
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            # reset_url = request.build_absolute_url(
            #     reverse('password_reset_confirm', kwargs={"uidb64": uid, "token":token})
            # )
            reset_url = f"http://127.0.0.1:8000/reset_password_confirm/{uid}/{token}/"

            send_mail(
                'პაროლის აღდგენა',
                f"დააჭირეთ ლინკს რათა აღადგინოთ პაროლი {reset_url}",
                "noreply@example.com",
                [user.email],
                fail_silently=False
            )

            return response.Response({"message": 'წერილი წარმატებით არის გაგზავნილი'}, status=status.HTTP_200_OK)
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
