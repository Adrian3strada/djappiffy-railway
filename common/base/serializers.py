from rest_framework import serializers
from django.utils import translation
from .models import (ProductKind, ProductKindCountryStandardSize, CapitalFramework,
                     ProductKindCountryStandardPackaging, SupplyKind, SupplyMeasureUnitCategory, FruitPurchasePriceCategory)
from cities_light.contrib.restframework3 import CountrySerializer as BaseCountrySerializer
from cities_light.contrib.restframework3 import RegionSerializer as BaseRegionSerializer
from cities_light.contrib.restframework3 import SubRegionSerializer as BaseSubRegionSerializer
from cities_light.contrib.restframework3 import CitySerializer as BaseCitySerializer

#


class CountrySerializer(BaseCountrySerializer):
    id = serializers.IntegerField()


class RegionSerializer(BaseRegionSerializer):
    id = serializers.IntegerField()


class SubRegionSerializer(BaseSubRegionSerializer):
    id = serializers.IntegerField()


class CitySerializer(BaseCitySerializer):
    id = serializers.IntegerField()


class ProductKindSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductKind
        fields = "__all__"


class SupplyKindSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplyKind
        fields = "__all__"


class CountryProductStandardSizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductKindCountryStandardSize
        fields = "__all__"


class ProductStandardPackagingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductKindCountryStandardPackaging
        fields = "__all__"


class CapitalFrameworkSerializer(serializers.ModelSerializer):
    class Meta:
        model = CapitalFramework
        fields = "__all__"

class SupplyMeasureUnitCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplyMeasureUnitCategory
        fields = "__all__"

class FruitPurchasePriceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FruitPurchasePriceCategory
        fields = "__all__"
