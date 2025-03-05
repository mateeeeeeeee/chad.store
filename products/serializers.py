from rest_framework import serializers
from .models import Product, ProductTag, Review, Cart, FavoriteProduct, ProductImage, CartItem
from users.models import User



class ReviewSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(write_only=True) 
    class Meta:
        model = Review
        exclude = ['updated_at',"product"]

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

        existing_reviews = Review.objects.filter(user=user, product=product)
        if existing_reviews.exists():
            raise serializers.ValidationError("You already reviewed this product")
        

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
    


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset = Product.objects.all(),
        write_only = True,
        source='product'
    )
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id','product','product_id','quantity','price_at_time_of_addition','total_price']
        read_only_fields = ['price_at_time_of_addition']
        
    def get_total_price(self, obj):
        return obj.total_price()
    
    def create(self, validated_data):
        product = validated_data.get('product')
        user = self.context['request'].user
        cart, created = Cart.objects.get_or_create(user=user)
        validated_data['cart'] = cart
        validated_data['price_at_time_of_addition'] = product.price

        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        quantity = validated_data.pop('quantity')
        instance.quantity = quantity
        instance.save()
        return instance
    

class CartSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'total']

    def get_total(self, obj):
        return sum(item.total_price() for item in obj.items.all())