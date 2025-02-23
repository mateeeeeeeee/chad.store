from django.urls import path
from products.views import CartViewSet,ProductTagListView, FavoriteProductViewSet, ReviewViewSet, ProductViewSet, ProductImageViewSet

urlpatterns = [
    path('products/', ProductViewSet.as_view({'get': 'list', 'post': 'create'}), name="products"),
    path('products/<int:pk>/', ProductViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='product'),
    path('cart/', CartViewSet.as_view(), name='carts'),
    path('products/<int:product_id>/images/', ProductImageViewSet.as_view({'get':'list','post':'create'}), name='images'),
    path('products/<int:product_id>/images/<int:pk>/', ProductImageViewSet.as_view({'get':'retrieve','delete':'destroy'}), name='image'),
    path('tags/', ProductTagListView.as_view(), name='product_tag_view'),
    path('favorite_product/', FavoriteProductViewSet.as_view({'get':'list','post':'create'}), name='favorite_product_view'),
    path('favorite_product/<int:pk>/', FavoriteProductViewSet.as_view({'get':'retrieve','delete':'destroy'}), name='favorite_product'),
    path('products/<int:product_id>/reviews/', ReviewViewSet.as_view(), name="reviews"),
]

