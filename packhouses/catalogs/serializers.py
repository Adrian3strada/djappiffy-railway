from rest_framework import serializers
from packhouses.catalogs.models import (
    Market, ProductMarketClass, Vehicle, HarvestingCrewProvider, Pallet, ProductPackagingPallet,
    ProductVariety, ProductPhenologyKind, Maquiladora, ProductPresentation, OrchardGeoLocation,
    CrewChief, ProductHarvestSizeKind, Client, Provider, Product, Supply, ProductSize, Orchard, ProductPackaging,
    HarvestingCrew, OrchardCertification, ProductRipeness, SizePackaging, Service
)
from common.base.models import (PestProductKind, DiseaseProductKind)
from django.utils.translation import gettext_lazy as _
from rest_framework_gis.serializers import GeoFeatureModelSerializer


class ProductSerializer(serializers.ModelSerializer):
    measure_unit_category_display = serializers.SerializerMethodField(read_only=True)
    product_market_classes = serializers.SerializerMethodField(read_only=True)
    packaging = serializers.SerializerMethodField(read_only=True)

    def get_measure_unit_category_display(self, obj):
        return obj.get_measure_unit_category_display()

    def get_product_market_classes(self, obj):
        product_market_classes = ProductMarketClass.objects.filter(product=obj)
        return ProductMarketClassSerializer(product_market_classes, many=True).data

    def get_packaging(self, obj):
        packaging = ProductPackaging.objects.filter(product=obj)
        return ProductPackagingSerializer(packaging, many=True).data

    class Meta:
        model = Product
        fields = '__all__'


class ProductPackagingSerializer(serializers.ModelSerializer):
    packaging_supply_detail = serializers.SerializerMethodField(read_only=True)

    def get_packaging_supply_detail(self, obj):
        return SupplySerializer(obj.packaging_supply, read_only=True).data

    class Meta:
        model = ProductPackaging
        fields = '__all__'


class SizePackagingSerializer(serializers.ModelSerializer):

    class Meta:
        model = SizePackaging
        fields = '__all__'


class ProductHarvestSizeKindSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductHarvestSizeKind
        fields = '__all__'


class ProductPhenologyKindSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductPhenologyKind
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


class PalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pallet
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


class ProductPresentationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductPresentation
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

    def validate(self, data):
        producer = data.get('producer')
        producer_name = data.get('producer_name')
        if not producer and not producer_name:
            raise serializers.ValidationError(
                _("Debe enviar al menos 'producer' o 'producer_name'.")
            )
        if producer and producer_name:
            raise serializers.ValidationError(
                _("No puede enviar ambos: 'producer' y 'producer_name'.")
            )
        return data

    def create(self, validated_data):
        if validated_data.get('producer'):
            validated_data['producer_name'] = None
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if instance.producer or validated_data.get('producer'):
            validated_data['producer_name'] = None
        return super().update(instance, validated_data)


class HarvestingCrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = HarvestingCrew
        fields = '__all__'


class MaquiladoraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Maquiladora
        fields = '__all__'


class OrchardCertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrchardCertification
        fields = '__all__'

    def create(self, validated_data):
        # Preserve 'certification_kind_name' only if 'certification_kind' is not provided
        if not validated_data.get('certification_kind') and validated_data.get('certification_kind_name'):
            # 'certification_kind_name' remains unchanged
            pass
        else:
            # Clear 'certification_kind_name' if 'certification_kind' is provided
            validated_data['certification_kind_name'] = None

        # Preserve 'verifier_name' only if 'verifier' is not provided
        if not validated_data.get('verifier') and validated_data.get('verifier_name'):
            # 'verifier_name' remains unchanged
            pass
        else:
            # Clear 'verifier_name' if 'verifier' is provided
            validated_data['verifier_name'] = None

        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Si ya existe FK, limpia el campo *_name
        if validated_data.get('certification_kind'):
            validated_data['certification_kind_name'] = None
        if validated_data.get('verifier'):
            validated_data['verifier_name'] = None
        return super().update(instance, validated_data)


class OrchardGeoLocationSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = OrchardGeoLocation
        fields = '__all__'
        geo_field = 'geom'

    def validate(self, data):
        geom = data.get('geom')
        coordinates = data.get('coordinates')
        file = data.get('file')

        if not geom and not coordinates and not file:
            raise serializers.ValidationError(
                _("You must provide at least one of: 'geom', 'coordinates', or 'file'.")
            )
        return data


class ProductRipenessSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductRipeness
        fields = '__all__'

class ServiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Service
        fields = '__all__'

class PestProductKindSerializer(serializers.ModelSerializer):
    pest = serializers.CharField(source='pest.name', read_only=True)

    class Meta:
        model = PestProductKind
        fields = ['id', 'pest']

class DiseaseProductKindSerializer(serializers.ModelSerializer):
    disease = serializers.CharField(source='disease.name', read_only=True)

    class Meta:
        model = DiseaseProductKind
        fields = ['id', 'disease']
