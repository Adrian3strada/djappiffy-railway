from rest_framework import serializers
from packhouses.catalogs.models import (
    Market, ProductMarketClass, Vehicle, HarvestingCrewProvider, Pallet,
    ProductVariety, ProductPhenologyKind, Maquiladora, ProductPresentation, OrchardGeoLocation,
    CrewChief, ProductHarvestSizeKind, Client, Provider, Product, Supply, ProductSize, Orchard, ProductPackaging,
    HarvestingCrew, OrchardCertification, ProductRipeness, SizePackaging, Service
)
from common.base.models import (PestProductKind, DiseaseProductKind)
from django.utils.translation import gettext_lazy as _
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from packhouses.packhouse_settings.models import OrchardCertificationVerifier, OrchardCertificationKind


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
    products = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Orchard._meta.get_field('products').related_model.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Orchard
        fields = '__all__'

    def validate(self, data):
        if self.instance is None:
            producer = data.get('producer')
            producer_name = data.get('producer_name')
            if not producer and not producer_name:
                raise serializers.ValidationError(
                    _("You must send 'producer' or 'producer_name'.")
                )
            if producer and producer_name:
                raise serializers.ValidationError(
                    _("You can not send: 'producer' and 'producer_name' at the same time.")
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

    def validate(self, attrs):
        certification_kind = attrs.get('certification_kind')
        if not certification_kind:
            raise serializers.ValidationError({
                'certification_kind': _('Este campo es requerido.')
            })
        return attrs

    def create(self, validated_data):
        return super().create(validated_data)

    def update(self, instance, validated_data):
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
        orchard = data.get('orchard')

        # Solo exigir en POST
        if not self.instance and not geom and not coordinates and not file:
            raise serializers.ValidationError(
                _("You must provide at least one of: 'geom', 'coordinates', or 'file'.")
            )

        if orchard:
            qs = OrchardGeoLocation.objects.filter(orchard=orchard)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    {"orchard": _("This orchard already has a geolocation assigned.")}
                )

        return data

    def update(self, instance, validated_data):
        if 'file' in validated_data and isinstance(validated_data['file'], str):
            validated_data.pop('file')

        return super().update(instance, validated_data)


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
