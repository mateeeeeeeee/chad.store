from django.urls import path
from products.views import cart_view,product_tag_view, favorite_product_view, ReviewViewSet, ProductViewSet

urlpatterns = [
    path('products/', ProductViewSet.as_view(), name="products"),
    path('products/<int:pk>/', ProductViewSet.as_view(), name='product'),
    path('cart/', cart_view, name='carts'),
    path('product_tag/<int:pk>/', product_tag_view, name='product_tag_view'),
    path('favorite_product/', favorite_product_view, name='favorite_product_view'),
    path('reviews/', ReviewViewSet.as_view(), name="reviews"),
]

