from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Product
from rest_framework import status


@api_view(['GET','POST'])
def products_view(request):
    if request.method == "GET":
        products = Product.objects.all()
        products_list = []

        for product in products:
            products_list.append({
                'id': product.id,
                'name': product.name,
                'description': product.description,
                'price': product.price,
                'currency': product.currency,
                'quantity': product.quantity,
            })
        return Response({'products': products_list})

    elif request.method == "POST":
        data = request.data
        from products.serializers import ProductSerializer

        data = request.data
        serializer = ProductSerializer(data=data)
        if serializer.is_valid():
            created_product = Product.objects.create(
                name=data.get('name'),
                description=data.get('description'),
                price=data.get('price'),
                quantity=data.get('quantity'),
                currency=data.get('currency'),
            )
            return Response({'id':created_product.id}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  
