from rest_framework import serializers
from packhouses.catalogs.models import (
    Market, ProductMarketClass, Vehicle, HarvestingCrewProvider,
    ProductVariety, ProductPhenologyKind, ProductMassVolumeKind, Maquiladora,
    CrewChief, ProductHarvestSizeKind, Client, Provider, Product, Supply, ProductSize, Orchard, ProductPackaging,
    HarvestingCrew, OrchardCertification, ProductRipeness
)
from django.utils.translation import gettext_lazy as _
from packhouses.purchase.models import PurchaseOrderSupply



class ProductSerializer(serializers.ModelSerializer):
    price_measure_unit_category_display = serializers.SerializerMethodField(read_only=True)
    product_market_classes = serializers.SerializerMethodField(read_only=True)
    packaging = serializers.SerializerMethodField(read_only=True)

    def get_price_measure_unit_category_display(self, obj):
        return obj.get_price_measure_unit_category_display()

    def get_product_market_classes(self, obj):
        product_market_classes = ProductMarketClass.objects.filter(product=obj)
        return ProductMarketClassSerializer(product_market_classes, many=True).data

    def get_packaging(self, obj):
        packaging = ProductPackaging.objects.filter(product=obj)
        return PackagingSerializer(packaging, many=True).data

    class Meta:
        model = Product
        fields = '__all__'


class PackagingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductPackaging
        fields = '__all__'


class ProductHarvestSizeKindSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductHarvestSizeKind
        fields = '__all__'


class ProductPhenologyKindSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductPhenologyKind
        fields = '__all__'


class ProductMassVolumeKindSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductMassVolumeKind
        fields = '__all__'


class ProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provider
        fields = '__all__'


class SupplySerializer(serializers.ModelSerializer):
    class Meta:
        model = Supply
        fields = '__all__'


class MarketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Market
        fields = '__all__'


class ProductMarketClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductMarketClass
        fields = '__all__'


class ProductVarietySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariety
        fields = '__all__'


class ProductSizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSize
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


class OrchardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Orchard
        fields = '__all__'

class HarvestingCrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = HarvestingCrew
        fields = '__all__'


class MaquiladoraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Maquiladora
        fields = '__all__'

from rest_framework import serializers

class OrchardCertificationSerializer(serializers.ModelSerializer):
    verifier_name = serializers.SerializerMethodField()
    expired_text = serializers.SerializerMethodField()

    class Meta:
        model = OrchardCertification
        fields = '__all__'

    def get_verifier_name(self, obj):
        return obj.verifier.name

    def get_expired_text(self, obj):
        return _('Expired')

class ProductRipenessSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductRipeness
        fields = '__all__'

class PurchaseOrderSupplySerializer(serializers.ModelSerializer):
    purchase_order_supply_options = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseOrderSupply
        fields = '__all__'

    def get_purchase_order_supply_options(self, obj):
        # Obtener las opciones válidas para purchase_order_supply
        return [
            {
                'id': pos.id,
                'name': str(pos.requisition_supply.supply)  # Nombre del Supply
            }
            for pos in PurchaseOrderSupply.objects.filter(purchase_order=obj.purchase_order)
        ]
