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

class ProductViewSet(ListModelMixin, CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, GenericViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

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

    

class ReviewViewSet(ListModelMixin, CreateModelMixin, GenericViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self, *args,**kwargs):
        queryset = self.queryset.filter(product_id=self.kwargs['product_pk'])
        return queryset


class ProductImageViewSet(ListModelMixin,CreateModelMixin,RetrieveModelMixin,DestroyModelMixin,GenericViewSet):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get','post','delete']

    def get_queryset(self):
        return self.queryset.filter(product__id=self.kwargs['product_pk'])
    