from django.contrib import admin
from .models import Product , ProductTag , Review, ProductImage, Cart, FavoriteProduct

class ImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ImageInline]


admin.site.register(ProductTag)
admin.site.register(Review)
admin.site.register(ProductImage)
admin.site.register(Cart)
admin.site.register(FavoriteProduct)