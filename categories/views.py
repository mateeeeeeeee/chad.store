from django.shortcuts import render
from .models import Category, CategoryImage
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from categories.serializers import CategorySerializer, CategoryDetailSerializers, CategoryImageSerializer
from rest_framework.generics import ListAPIView, ListCreateAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin
from rest_framework.viewsets import GenericViewSet


class CategoryListView(ListModelMixin, GenericViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]


class CategoryDetailListView(RetrieveModelMixin, GenericViewSet):
    queryset = Category.objects.all()
    serializer_class = CategoryDetailSerializers
    permission_classes = [IsAuthenticated]
    
class CategoryImageListView(ListModelMixin,CreateModelMixin,GenericViewSet):
    queryset = CategoryImage.objects.all()
    serializer_class = CategoryImageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(category__id=self.kwargs['category_pk'])
