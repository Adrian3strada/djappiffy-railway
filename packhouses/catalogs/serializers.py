from rest_framework import serializers
from packhouses.catalogs.models import (
                                        MarketStandardProductSize, Market, Vehicle, HarvestingCrewProvider,
                                        CrewChief
                                        )


class MarketStandardProductSizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketStandardProductSize
        fields = '__all__'


class MarketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Market
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
