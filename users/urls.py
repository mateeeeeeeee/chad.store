from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, RegisterViewSet, ProfileViewSet

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('register',RegisterViewSet, basename='register')
router.register(r'user', ProfileViewSet, basename='user')
urlpatterns = [
    path('', include(router.urls))
]
