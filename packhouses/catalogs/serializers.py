from rest_framework import serializers
from packhouses.catalogs.models import (
    Market, Vehicle, HarvestingCrewProvider,
    ProductVariety, ProductSeasonKind, ProductMassVolumeKind, Maquiladora,
    CrewChief, ProductHarvestSizeKind, Client, Provider, Product
)


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class ProductHarvestSizeKindSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductHarvestSizeKind
        fields = '__all__'


class ProductSeasonKindSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSeasonKind
        fields = '__all__'


class ProductMassVolumeKindSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductMassVolumeKind
        fields = '__all__'


class ProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provider
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


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'


class MaquiladoraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Maquiladora
        fields = '__all__'
