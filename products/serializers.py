from rest_framework import serializers


class ProductSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    description = serializers.CharField()
    quantity = serializers.IntegerField()
    price = serializers.FloatField()
    currency = serializers.ChoiceField(choices=['GEL','USD','EURO'])