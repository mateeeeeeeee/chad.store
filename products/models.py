from django.db import models
from config.util_models.models import TimeStampdModel
from products.choices import Currency
from django.core.validators import MaxValueValidator


class Product(TimeStampdModel):
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
    
    def __str__(self):
        return f'user name {self.user}'
    

class Cart(TimeStampdModel):
    products = models.ManyToManyField('products.Product', related_name='carts')
    user = models.OneToOneField('users.User', related_name='cart', on_delete=models.CASCADE)


class FavoriteProduct(TimeStampdModel):
    product = models.ForeignKey('products.Product', related_name='favorite_products', on_delete=models.CASCADE)
    user = models.ForeignKey('users.User', related_name='favorite_products', on_delete=models.SET_NULL, null=True, blank=True)


class ProductImage(TimeStampdModel):
    product = models.ForeignKey('products.Product', related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/')

