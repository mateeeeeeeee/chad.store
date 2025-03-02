from django_filters import FilterSet, NumberFilter, DateFilter, DateTimeFilter
from products.models import Product, Review

class ProductFilter(FilterSet):
    price_min = NumberFilter(field_name='price', lookup_expr='gte')
    price_max = NumberFilter(field_name='price', lookup_expr='lte')

    class Meta:
        model = Product
        fields = ['categories', 'price_min', 'price_max']

class ReviewFilter(FilterSet):
    rating_min = NumberFilter(field_name='rating', lookup_expr='gte')
    rating_max = NumberFilter(field_name='rating', lookup_expr='lte')
    date_min = DateTimeFilter(field_name='created_at', lookup_expr='gte')
    date_max = DateTimeFilter(field_name='created_at', lookup_expr='lte')
    class Meta:
        model = Review
        fields = ['rating_min', 'rating_max', 'date_min', 'date_max']