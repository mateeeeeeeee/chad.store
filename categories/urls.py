from django.urls import path, include
from rest_framework_nested import routers
from categories.views import CategoryDetailViewSet, CategoryImageViewSet, CategoryViewSet

router = routers.DefaultRouter()
router.register('categories', CategoryViewSet)

category_router = routers.NestedDefaultRouter(
    router,
    'categories',
    lookup='category'
)
category_router.register('details', CategoryDetailViewSet)
category_router.register('images', CategoryImageViewSet)
urlpatterns = [
    path('', include(router.urls)),
    path('', include(category_router.urls)),
]
