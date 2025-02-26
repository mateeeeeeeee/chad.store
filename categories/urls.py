from django.urls import path, include
from rest_framework_nested import routers
from categories.views import CategoryListView, CategoryDetailListView, CategoryImageListView

router = routers.DefaultRouter()
router.register('categories', CategoryListView)

category_router = routers.NestedDefaultRouter(
    router,
    'categories',
    lookup='category'
)
category_router.register('details', CategoryDetailListView)
category_router.register('images', CategoryImageListView)
urlpatterns = [
    path('', include(router.urls)),
    path('', include(category_router.urls)),
]
