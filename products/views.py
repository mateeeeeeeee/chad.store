from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Product, Cart, ProductTag, FavoriteProduct, Review
from rest_framework import status
from rest_framework.views import status, APIView
from products.serializers import ProductSerializer, CartSerializer, ProductTagSerializer, FavoriteProductSerializer, ReviewSerializer


class ProductListCreateView(APIView):
    def get(self, request):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            product = serializer.save()
            return Response({'id': product.id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProductDetailUpdateDeleteView(APIView):
    def get(self, request, pk):
        obj = get_object_or_404(Product, pk=pk)
        serializer = ProductSerializer(obj)
        return Response(serializer.data)
    
    def put(self,request, pk):
        obj = get_object_or_404(Product, pk=pk)
        serializer = ProductSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self,request,pk):
        obj = get_object_or_404(Product, pk=pk)
        serializer = ProductSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self,request,pk):
        obj = get_object_or_404(Product, pk=pk)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET', 'POST'])
def cart_view(request):
    if request.method == "GET":
        cart = Cart.objects.filter(user=request.user).first()
        cart_list = []

        if cart:
            for i in cart.products.all():
                cart_list.append({
                    'id': i.id,
                    'product': i.name
                })
        return Response({'cart': cart_list})

    elif request.method == "POST":
        data = request.data

        serializer = CartSerializer(data=data)
        if serializer.is_valid():
            product = Product.objects.get(id=data.get('product'))
            cart, created = Cart.objects.get_or_create(user=request.user)
            cart.products.add(product)

            return Response({'message': 'Product added to cart'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

@api_view(["GET", "POST"])
def product_tag_view(request, pk):
    if request.method == "GET":
        product = Product.objects.filter(pk=pk).first()

        tags_list = []
        for tag in product.product_tags.all():
            tags_list.append({
                "id": tag.id,
                "name": tag.name
            })
        return Response({"tags": tags_list})

    elif request.method == "POST":
        serializer = ProductTagSerializer(data=request.data)
        if serializer.is_valid():
            product_id = serializer.validated_data['product_id']
            tag_name = serializer.validated_data['tag_name']

            product = Product.objects.get(pk=product_id)
            tag = ProductTag.objects.create(name=tag_name)
            product.product_tags.add(tag)

            return Response({"message": "Tag added successfully"}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
def favorite_product_view(request):
    if request.method == "GET":
        user = request.user
        favorite_products = FavoriteProduct.objects.filter(user=user)
        favorite_products_list = []

        for fp in favorite_products:
            favorite_products_list.append({
                "id": fp.product.id,
                "name": fp.product.name
            })
        return Response({"favorite_products": favorite_products_list})

    elif request.method == "POST":
        serializer = FavoriteProductSerializer(data=request.data)
        if serializer.is_valid():
            product_id = serializer.validated_data['product_id']
            user_id = serializer.validated_data['user_id']
            favorite_product, created = FavoriteProduct.objects.get_or_create(user_id=user_id, product_id=product_id)

            return Response({"message": "Product added to favorites"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['GET', 'POST'])
def review_view(request):
    if request.method == 'GET':
        reviews = Review.objects.all()
        review_list = []
        
        for review in reviews:
            review_data = {
                'id': review.id,
                'product_id': review.product.id,
                'content': review.content,
                'rating': review.rating
            }
            review_list.append(review_data)
        
        return Response({'reviews': review_list})

    elif request.method == 'POST':
        serializer = ReviewSerializer(data=request.data, context={"request":request})
        if serializer.is_valid():
            review = serializer.save()
            return Response(
                {'id': review.id, 'message': 'Review created successfully!'},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    