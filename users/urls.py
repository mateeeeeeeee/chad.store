from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, RegisterViewSet, ProfileViewSet, ResetPasswordViewSet

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('register',RegisterViewSet, basename='register')
router.register(r'user', ProfileViewSet, basename='user')
router.register('reset_password', ResetPasswordViewSet, basename='reset_password')
urlpatterns = [
    path('', include(router.urls))
]
