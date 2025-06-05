from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from .models import Batch

class BatchSerializer(serializers.ModelSerializer):
    yield_orchard_producer = serializers.SerializerMethodField(read_only=True)
    harvest_product_provider = serializers.SerializerMethodField(read_only=True)
    ingress_weight = serializers.SerializerMethodField(read_only=True)
    yield_orchard_registry_code = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Batch
        fields = '__all__'

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

    def get_ingress_weight(self, obj):
        ingress_weight = obj.ingress_weight
        return ingress_weight if ingress_weight else 0

    def get_yield_orchard_registry_code(self, obj):
        return obj.yield_orchard_registry_code if obj.yield_orchard_registry_code else None
