from django.contrib import admin
from .models import CategoryImage, Category

class ImageInline(admin.TabularInline):
    model = CategoryImage
    extra = 0

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    inlines = [ImageInline]

admin.site.register(CategoryImage)


