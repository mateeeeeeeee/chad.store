from django.db import models
from config.util_models.models import TimeStampdModel


class Category(TimeStampdModel):
    name = models.CharField(max_length=255, unique=True)
    products = models.ManyToManyField('products.Product', related_name='categories')

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"



class CategoryImage(TimeStampdModel):
    category = models.ForeignKey('categories.Category', related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='categories/')
    is_active = models.BooleanField(default=False)



