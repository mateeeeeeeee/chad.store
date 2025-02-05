from rest_framework import serializers
from .models import Product, ProductTag, Review, Cart, FavoriteProduct
from users.models import User


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = ['name', 'description', 'quantity', 'price', 'currency']

class CartSerializer(serializers.ModelSerializer):

    class Meta:
        model = Cart
        fields = ['product_id', 'quantity']

    def validate_product_id(self, value):# ვნახულობთ არსებობს თუ არა პროდუქტი ამ id-ით
        if not Product.objects.filter(id=value).exists():
            raise serializers.ValidationError("Product does not exist.")
        return value

    def validate_quantity(self, value):# ვნახულობთ პროდუქტის რაოდენობა თუ არის 0-ზე მეტი
        if value < 1:
            raise serializers.ValidationError("Quantity must be greater than 0.")
        return value
    
class ProductTagSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductTag
        fields = ['product_id', 'tag_name']

    def validate_product_id(self, value):# ვნახულობთ არსებობს თუ არა ეს პროდუქტი
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Product not found")
        return value
    
    def validate_tag_name(self, value):# ვნახულობთ ამ პროდუქტს თუ აქვს ასეთი tag-ი
        product_id = self.initial_data.get('product_id')
        if ProductTag.objects.filter(name=value, product__id=product_id).exists():
            raise serializers.ValidationError("Tag name already exists for this product.")
        return value
        

class FavoriteProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = FavoriteProduct
        fields = ['product_id', 'user_id']

    def validate_product_id(self, value):# ვნახულობთ თუ არსებობს ეს პროდუქტი
        if not Product.objects.filter(id=value).exists():
            raise serializers.ValidationError("Product does not exist.")
        return value

    def validate_user_id(self, value):# ვნახულობთ არსებობს თუ არა ეს მომხმარებელი
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("User does not exist.")
        return value

    
class ReviewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Review
        fields = ['user', 'product', 'rating']

    def validate_product_id(self, value):# ვნახულობთ თუ ეს პროდუქტი არსებობს
        try:
            Product.objects.get(id=value)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Invalid product_id. Product does not exist.")
        return value

    def validate_rating(self, value):# რეიტინგი უნდა იყოს 1 ზე მეტი ან 5 ზე ნაკლები, რადგან სხვა რიცხვი არ შეესაბამება რეალურ მაჩვენებს :)
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value

    def create(self, validated_data):# ვქმნით review-ს
        product = Product.objects.get(id=validated_data['product_id'])
        user = self.context['request'].user

        review = Review.objects.create(
            product=product,
            user=user,
            content=validated_data['content'],
            rating=validated_data['rating'],
        )
        return review
    