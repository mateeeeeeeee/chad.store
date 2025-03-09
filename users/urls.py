from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, RegisterViewSet

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('register',RegisterViewSet, basename='register')

urlpatterns = [
    path('', include(router.urls))
]
