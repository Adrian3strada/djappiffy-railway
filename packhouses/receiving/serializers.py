from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from .models import Batch

from packhouses.catalogs.models import ProductPhenologyKind
from packhouses.receiving.models import Batch
from packhouses.catalogs.serializers import MarketSerializer, ProductSerializer, ProductPhenologyKindSerializer


class BatchSerializer(serializers.ModelSerializer):
    yield_orchard_producer = serializers.SerializerMethodField(read_only=True)
    harvest_product_provider = serializers.SerializerMethodField(read_only=True)
    ingress_weight = serializers.SerializerMethodField(read_only=True)
    weight_received = serializers.SerializerMethodField(read_only=True)
    yield_orchard_registry_code = serializers.SerializerMethodField(read_only=True)
    market = serializers.SerializerMethodField(read_only=True)
    product = serializers.SerializerMethodField(read_only=True)
    product_phenology = serializers.SerializerMethodField(read_only=True)

    def get_market(self, obj):
        if obj.incomingproduct and obj.incomingproduct.scheduleharvest:
            return MarketSerializer(obj.incomingproduct.scheduleharvest.market, read_only=True).data
        return None

    def get_product(self, obj):
        if obj.incomingproduct and obj.incomingproduct.scheduleharvest:
            return ProductSerializer(obj.incomingproduct.scheduleharvest.product, read_only=True).data
        return None

    def get_product_phenology(self, obj):
        if obj.incomingproduct and obj.incomingproduct.scheduleharvest:
            return ProductPhenologyKindSerializer(obj.incomingproduct.scheduleharvest.product_phenology, read_only=True).data
        return None

    class Meta:
        model = Batch
        fields = '__all__'
        read_only_fields = ['ooid', 'created_at']

    def get_yield_orchard_producer(self, obj):
        producer = obj.yield_orchard_producer
        return {
            "id": producer.id,
            "name": producer.name
        } if producer else None

    def get_harvest_product_provider(self, obj):
        provider = obj.harvest_product_provider
        return {
            "id": provider.id,
            "name": provider.name
        } if provider else None

    def get_weight_received(self, obj):
        weight_received = obj.weight_received
        return weight_received if weight_received else 0
    def get_ingress_weight(self, obj):
        ingress_weight = obj.ingress_weight
        return ingress_weight if ingress_weight else 0

    def get_yield_orchard_registry_code(self, obj):
        return obj.yield_orchard_registry_code if obj.yield_orchard_registry_code else None
