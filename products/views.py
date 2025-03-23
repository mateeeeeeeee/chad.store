from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Product, Cart, ProductTag, FavoriteProduct, Review, ProductImage, CartItem
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.views import status, APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin
from products.serializers import ProductSerializer, CartSerializer, ProductTagSerializer, FavoriteProductSerializer, ReviewSerializer, ProductImageSerializer, CartItemSerializer
from rest_framework.generics import ListAPIView, ListCreateAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.viewsets import GenericViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from .pagination import ProductPagination
from .filters import ProductFilter, ReviewFilter
from rest_framework.exceptions import PermissionDenied
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle, ScopedRateThrottle
from rest_framework.decorators import action
from .permissions import IsObjectOwnerOrReadOnly
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.validators import ValidationError
from rest_framework.response import Response
from rest_framework import status


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = ProductFilter
    search_fields = ['name','description']
    pagination_class = ProductPagination

    @action(detail=False, methods=['GET'], url_path="my_products")
    def get_my_products(self, request, pk=None):
        queryset = self.queryset.filter(user=self.request.user)
        serrializer = self.get_serializer(queryset,many=True)
        return Response(serrializer.data)
    

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
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'tag'


class FavoriteProductViewSet(ModelViewSet):
    queryset = FavoriteProduct.objects.all()
    serializer_class = FavoriteProductSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'likes'
    http_method_names = ['get','post','delete']

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user)
        return queryset

    

class ReviewViewSet(ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated, IsObjectOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ReviewFilter

    def get_queryset(self, *args,**kwargs):
        queryset = self.queryset.filter(product_id=self.kwargs['product_pk'])
        return queryset


class ProductImageViewSet(ListModelMixin,CreateModelMixin,RetrieveModelMixin,DestroyModelMixin,GenericViewSet):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    http_method_names = ['get','post','delete']


    def get_queryset(self):
        return self.queryset.filter(product__id=self.kwargs['product_pk'])
    
    def create(self,requset, *args, **kwargs):
        try:
            super().create(requset, *args, **kwargs)
        except ValidationError as e:
            return Response ({"error":f"{e}"}, status=status.HTTP_400_BAD_REQUEST)
    
class CartItemViewSet(ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return self.queryset.filter(cart__user=self.request.user)
    
    def perform_destroy(self, instance):
        if instance.cart.user != self.request.user:
            raise PermissionDenied('You do not have permission to delete this review')
        instance.delete()

    def perform_update(self, serializer):
        instance = self.get_object()
        if instance.cart.user != self.request.user:
            raise PermissionDenied('You do not have permission to update this item')
        serializer.save()