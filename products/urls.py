from django.urls import path, include
from products.views import CartViewSet,ProductTagListView, FavoriteProductViewSet, ReviewViewSet, ProductViewSet, ProductImageViewSet, CartItemViewSet
from rest_framework_nested import routers

router = routers.DefaultRouter()
router.register('products', ProductViewSet)
router.register('favorite_products', FavoriteProductViewSet)
router.register('cart', CartViewSet)
router.register('tags', ProductTagListView)
router.register('cart_items', CartItemViewSet, basename='cart-items')
products_router = routers.NestedDefaultRouter(
    router,
    'products',
    lookup='product'
)

products_router.register('images',ProductImageViewSet)
products_router.register('reviews',ReviewViewSet)
# products_router.register(r'my_products',ProductViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('', include(products_router.urls)),
]


