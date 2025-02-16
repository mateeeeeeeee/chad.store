from rest_framework import serializers
from .models import Product, ProductTag, Review, Cart, FavoriteProduct, ProductImage
from users.models import User



class ReviewSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(write_only=True) 
    class Meta:
        model = Review
        exclude = ['updated_at', 'created_at']

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

class ProductTagSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductTag
        fields = ['id', 'name']

class ProductSerializer(serializers.ModelSerializer):
    reviews = ReviewSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        source='tags',
        queryset=ProductTag.objects.all(),
        many=True,
        write_only=True,
    )
    tags = ProductTagSerializer(many=True, read_only=True)
    class Meta:
        model = Product
        exclude = ['created_at', 'updated_at']
        

    def create(self, validated_data):
        tags = validated_data.pop('tags',[])
        product = Product.objects.create(**validated_data)
        product.tags.set(tags)
        return product
    
    def update(self, instance, validate_data):
        tags = validate_data.pop('tags', None)
        if tags is not None:
            instance.tags.set(tags)
        return super().update(instance, validate_data)
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

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image','product']
    
    