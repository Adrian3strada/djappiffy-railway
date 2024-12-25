from rest_framework import serializers
from packhouses.catalogs.models import MarketStandardProductSize, Market


class MarketStandardProductSizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketStandardProductSize
        fields = '__all__'


class MarketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Market
        fields = '__all__'
