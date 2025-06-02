from rest_framework import serializers
from packhouses.receiving.models import Batch
from packhouses.catalogs.serializers import MarketSerializer, ProductSerializer


class BatchSerializer(serializers.ModelSerializer):
    market = serializers.SerializerMethodField(read_only=True)
    # product = serializers.SerializerMethodField(read_only=True)
    product = serializers.SerializerMethodField(source='incomingproduct.scheduleharvest.product', read_only=True)
    product_phenology = serializers.SerializerMethodField(source='incomingproduct.scheduleharvest.product_phenology', read_only=True)

    def get_market(self, obj):
        if obj.incomingproduct and obj.incomingproduct.scheduleharvest:
            return MarketSerializer(obj.incomingproduct.scheduleharvest.market, read_only=True).data
        return None

    def get_product_aaa(self, obj):
        if obj.incomingproduct and obj.incomingproduct.scheduleharvest:
            return ProductSerializer(obj.incomingproduct.scheduleharvest.product, read_only=True).data
        return None

    class Meta:
        model = Batch
        fields = '__all__'
        read_only_fields = ['ooid', 'created_at']
