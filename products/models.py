from django.db import models
from config.util_models.models import TimeStampdModel
from products.choices import Currency
from django.core.validators import MaxValueValidator
from users.models import User
from config.utils.image_validators import validate_image_resolution, validate_image_size, validate_image_count

class Product(TimeStampdModel):
    user = models.ForeignKey("users.User",null=True, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.FloatField()
    currency = models.CharField(max_length=255,choices=Currency.choices, default=Currency.GEL)
    quantity = models.PositiveSmallIntegerField()

    def __str__(self):
        return f'product name {self.name}'


class ProductTag(TimeStampdModel):
    name = models.CharField(max_length=255)
    products = models.ManyToManyField('products.Product', related_name='tags')
        
    def __str__(self):
        return f'tag name {self.name}'


class Review(TimeStampdModel):
    user = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='reviews')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(validators=[MaxValueValidator(5)])
    content = models.TextField()
    
    class Meta:
        unique_together = ['product','user']
    def __str__(self):
        return f'user name {self.user}'
    

class Cart(TimeStampdModel):
    products = models.ManyToManyField('products.Product', related_name='carts')
    user = models.OneToOneField('users.User', related_name='cart', on_delete=models.CASCADE)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='cart_items', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price_at_time_of_addition = models.FloatField()

    def __str__(self):
        return f'{self.product.name} - {self.quantity} items'
    
    def total_price(self):
        return self.quantity * self.price_at_time_of_addition


class FavoriteProduct(TimeStampdModel):
    product = models.ForeignKey('products.Product', related_name='favorite_products', on_delete=models.CASCADE)
    user = models.ForeignKey('users.User', related_name='favorite_products', on_delete=models.SET_NULL, null=True, blank=True)


class ProductImage(TimeStampdModel, models.Model):
    product = models.ForeignKey('products.Product', related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/',validators=[validate_image_resolution, validate_image_size])

    def clean(self):
        if self.product_id:
            validate_image_count(self.product_id)
        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

