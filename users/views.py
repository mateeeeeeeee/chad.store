from django.shortcuts import render
from rest_framework import mixins, viewsets, permissions, response, status
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer, RegisterSerializer, ProfileSerializer, PasswordResetSerializer, PasswordResetConfirmSerializer, EmailCodeResendserializer, EmailcoedConfirmSerializer
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
from datetime import timedelta
from config.celery import app

User = get_user_model()

class UserViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer


class RegisterViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

    @action(detail=False, methods=['post'], url_path='resend_code', serializer_class=EmailCodeResendserializer)
    def resend_code(self, request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user = serializer.validated_data['user']
        existing_code = EmailVerificationCode.objects.filter(user=user).first()
        if existing_code:
            time_diff = timezone.now() - existing_code.created_at
            if time_diff < timedelta(minutes=1):
                wait_seconds = 60 - int(time_diff.total_seconds())
                return response.Response({'detail': f'დაელოდე {wait_seconds} წამი კოდის ხელახლა გასაგზავნად'}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        self.send_verification_code(user)
        return response.Response({"message": 'ვერიფიკაციის კოდი ხელახლა არის გამოგზავნილი'})

    
    @action(detail=False, methods=["post"], url_path="confirm_code", serializer_class=EmailcoedConfirmSerializer)
    def confirm_code(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            user.is_active = True
            user.save()
            return response.Response({"message": "მომხმარებელი არის წარმატებით გააქტიურებული"}, status=status.HTTP_200_OK)
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            self.send_verification_code(user)
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
        app.send_task('users.tasks.send_mail_async', args=[subject, message, user.email])
        # send_mail(subject, message, 'no-reply@example.com', [user.email])


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

            subject = "პაროლის აღდგენა"
            message=f"დააჭირეთ ლინკს რათა აღადგინოთ პაროლი {reset_url}"

            app.send_task('users.tasks.send_mail_async', args=[subject, message, user.email])

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