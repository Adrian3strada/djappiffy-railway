from rest_framework import serializers
from packhouses.catalogs.models import (
    MarketStandardProductSize, Market, Vehicle, HarvestingCrewProvider,
    ProductVariety, ProductQualityKind, ProductMassVolumeKind,
    CrewChief, ProductHarvestSizeKind
)


class MarketStandardProductSizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketStandardProductSize
        fields = '__all__'


class ProductHarvestSizeKindSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductHarvestSizeKind
        fields = '__all__'


class ProductQualityKindSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductQualityKind
        fields = '__all__'


class ProductMassVolumeKindSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductMassVolumeKind
        fields = '__all__'

class MarketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Market
        fields = '__all__'


class ProductVarietySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariety
        fields = '__all__'


class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = '__all__'


class HarvestingCrewProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = HarvestingCrewProvider
        fields = '__all__'


class CrewChiefSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrewChief
        fields = '__all__'
