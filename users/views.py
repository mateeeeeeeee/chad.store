from django.shortcuts import render
from rest_framework import mixins, viewsets, permissions, response, status
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer, RegisterSerializer, ProfileSerializer, PasswordResetSerializer, PasswordResetConfirmSerializer
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
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
import random
from users.models import EmailVerificationCode
from django.utils import timezone

User = get_user_model()

class UserViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer


class RegisterViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                self.send_verification_code(user)
                user = serializer.save()
            except Exception:
                return response.Response({"Detail": "something unexpected happened try again later"})
            return Response(
                {"detail": "user registered succesfully. verification code sent to email"},
                status=status.HTTP_201_CREATED)
                                                
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def send_verification_code(self, user):
        code = str(random.randint(100000, 999999))

        EmailVerificationCode.objects.update_or_create(
            user=user,
            defaults={"code":code, "created_at": timezone.now()}
        )
        subject = "your verification"
        message = f"Hello {user.username}, your verification code is {code}"
        send_mail(subject, message, 'no-reply@example.com', [user.email])


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

            reset_url = request.build_absolute_uri(
                reverse('password_reset_confirm', kwargs={"uidb64": uid, "token":token})
            )

            send_mail(
                'პაროლის აღდგენა',
                f"დააჭირეთ ლინკს რათა აღადგინოთ პაროლი {reset_url}",
                "noreply@example.com",
                [user.email],
                fail_silently=False
            )

            return response.Response({"message": 'წერილი წარმატებით არის გაგზავნილი'}, status=status.HTTP_200_OK)
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class PasswordResetConfirmViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = PasswordResetConfirmSerializer

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('uid64', openapi.IN_PATH, description='User id Encoded with BASE64', type=openapi.TYPE_STRING),
        openapi.Parameter('token', openapi.IN_PATH, description='Password reset token', type=openapi.TYPE_STRING)
    ])
    def create(self, request, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return response.Response({'message': 'პაროლი წარმატებით შეიცვალა'})
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)