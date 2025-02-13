from django.urls import path
from products.views import CartViewSet,product_tag_view, FavoriteProductViewSet, ReviewViewSet, ProductViewSet

urlpatterns = [
    path('products/', ProductViewSet.as_view(), name="products"),
    path('products/<int:pk>/', ProductViewSet.as_view(), name='product'),
    path('cart/', CartViewSet.as_view(), name='carts'),
    path('product_tag/<int:pk>/', product_tag_view, name='product_tag_view'),
    path('favorite_product/', FavoriteProductViewSet.as_view(), name='favorite_product_view'),
    path('favorite_product/<int:pk>/', FavoriteProductViewSet.as_view(), name='favorite_product'),
    path('reviews/', ReviewViewSet.as_view(), name="reviews"),
]

