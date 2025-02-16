from django.urls import path
from categories.views import CategoryDetailListView, CategoryImageListView, CategoryListView



urlpatterns = [
    path('categories/', CategoryListView.as_view(), name='categories'),
    path('categories/<int:pk>/', CategoryDetailListView.as_view(), name='category'),
    path('categories/<int:category_id>/images/', CategoryImageListView.as_view()),
]