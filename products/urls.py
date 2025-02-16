from django.urls import path
from products.views import CartViewSet,ProductTagListView, FavoriteProductViewSet, ReviewViewSet, ProductViewSet, ProductImageViewSet

urlpatterns = [
    path('products/', ProductViewSet.as_view(), name="products"),
    path('products/<int:pk>/', ProductViewSet.as_view(), name='product'),
    path('cart/', CartViewSet.as_view(), name='carts'),
    path('products/<int:product_id>/images/', ProductImageViewSet.as_view(), name='images'),
    path('products/<int:product_id>/images/<int:pk>/', ProductImageViewSet.as_view(), name='image'),
    path('tags/', ProductTagListView.as_view(), name='product_tag_view'),
    path('favorite_product/', FavoriteProductViewSet.as_view(), name='favorite_product_view'),
    path('favorite_product/<int:pk>/', FavoriteProductViewSet.as_view(), name='favorite_product'),
    path('reviews/', ReviewViewSet.as_view(), name="reviews"),
]

