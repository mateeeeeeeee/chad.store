from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Product, Cart, ProductTag, FavoriteProduct, Review, ProductImage
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.views import status, APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin
from products.serializers import ProductSerializer, CartSerializer, ProductTagSerializer, FavoriteProductSerializer, ReviewSerializer, ProductImageSerializer
from rest_framework.generics import ListAPIView, ListCreateAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.viewsets import GenericViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from .pagination import ProductPagination
from .filters import ProductFilter, ReviewFilter
from rest_framework.exceptions import PermissionDenied




class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = ProductFilter
    search_fields = ['name','description']
    pagination_class = ProductPagination

class CartViewSet(ListModelMixin,GenericViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user)
        return queryset
        

class ProductTagListView(ListModelMixin,GenericViewSet):
    queryset = ProductTag.objects.all()
    serializer_class = ProductTagSerializer
    permission_classes = [IsAuthenticated]


class FavoriteProductViewSet(ListModelMixin,CreateModelMixin,DestroyModelMixin,GenericViewSet):
    queryset = FavoriteProduct.objects.all()
    serializer_class = FavoriteProductSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get','post','delete']

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user)
        return queryset

    

class ReviewViewSet(ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ReviewFilter

    def get_queryset(self, *args,**kwargs):
        queryset = self.queryset.filter(product_id=self.kwargs['product_pk'])
        return queryset

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise PermissionDenied('you cant delete this review')
        instance.delete()

    def perform_update(self, serializer):
        instance = self.get_object()
        if instance.user != self.request.user:
            raise PermissionDenied("You cant change this review")
        serializer.save()


class ProductImageViewSet(ListModelMixin,CreateModelMixin,RetrieveModelMixin,DestroyModelMixin,GenericViewSet):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get','post','delete']

    def get_queryset(self):
        return self.queryset.filter(product__id=self.kwargs['product_pk'])
    