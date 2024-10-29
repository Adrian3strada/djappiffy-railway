from rest_framework import serializers
from packhouses.catalogs.models import MarketStandardProductSize


class MarketStandardProductSizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketStandardProductSize
        fields = '__all__'
