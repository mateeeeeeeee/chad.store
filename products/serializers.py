from rest_framework import serializers
from .models import Product, ProductTag, Review, Cart, FavoriteProduct
from users.models import User


class ProductSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Product
        fields = ["id",'name', 'description', 'quantity', 'price', 'currency',"reviews"]

class CartSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    products = ProductSerializer(many=True, read_only=True)
    product_ids = serializers.PrimaryKeyRelatedField(
        source='products',
        queryset=Product.objects.all(),
        write_only=True,
        many=True
    )
    
    class Meta:
        model = Cart
        fields = ['product_ids', 'user', 'products']

    def create(self, validate_data):
        user = validate_data.pop('user')
        products = validate_data.pop('products')

        cart, _ = Cart.objects.get_or_create(user=user)

        cart.products.add(*products)

        return cart



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
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    product_id = serializers.IntegerField(write_only=True)
    class Meta:
        model = FavoriteProduct
        fields = ['id','product','product_id', 'user']
        read_only_fields = ['id', 'product']

    def validate_product_id(self,value):
        if not Product.objects.filter(id=value).exists():
            raise serializers.ValidationError('given product_id doesnot exists')
        return value
    
    def create(self, validated_data):
        user = validated_data.pop('user')
        product_id = validated_data.pop('product_id')
        product = Product.objects.get(id=product_id)
        favorite_product, created = FavoriteProduct.objects.get_or_create(user=user, product=product)

        if not created:
            raise serializers.ValidationError('Product with given id is already in favorites')
        return favorite_product


    
class ReviewSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(write_only=True) 
    class Meta:
        model = Review
        fields = '__all__'

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
    