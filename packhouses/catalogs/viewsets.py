from rest_framework import viewsets
from rest_framework.exceptions import NotAuthenticated
from .serializers import (MarketSerializer, ProductMarketClassSerializer, VehicleSerializer,
                          ProductVarietySerializer, ProductHarvestSizeKindSerializer, ProviderSerializer,
                          ProductPhenologyKindSerializer, ClientSerializer, ProductSizeSerializer,
                          MaquiladoraSerializer, ProductPackagingSerializer, ProductPresentationSerializer,
                          SupplySerializer, OrchardSerializer, OrchardGeoLocationSerializer,
                          HarvestingCrewSerializer,
                          SizePackagingSerializer, PalletSerializer,
                          HarvestingCrewProviderSerializer, CrewChiefSerializer, ProductSerializer,
                          OrchardCertificationSerializer, ProductRipenessSerializer, ServiceSerializer,
                          PestProductKindSerializer, DiseaseProductKindSerializer
                          )
from .models import (Market, ProductMarketClass, Vehicle, HarvestingCrewProvider, CrewChief, ProductVariety,
                     ProductHarvestSizeKind, ProductPhenologyKind, Client, Maquiladora, Provider,
                     Product, ProductPackaging, ProductPresentation, SizePackaging, Pallet, ProductPackagingPallet,
                     Supply, Orchard, HarvestingCrew, ProductSize, OrchardCertification, OrchardGeoLocation,
                     ProductRipeness, Service
                     )
from common.base.models import (PestProductKind, DiseaseProductKind)
from django_filters.rest_framework import DjangoFilterBackend


class ProductHarvestSizeKindViewSet(viewsets.ModelViewSet):
    serializer_class = ProductHarvestSizeKindSerializer
    filterset_fields = ['product', 'is_enabled']
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            raise NotAuthenticated()

        return ProductHarvestSizeKind.objects.filter(product__organization=self.request.organization)


class ProductPhenologyKindViewSet(viewsets.ModelViewSet):
    serializer_class = ProductPhenologyKindSerializer
    filterset_fields = ['product', 'is_enabled']
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            raise NotAuthenticated()

        return ProductPhenologyKind.objects.filter(product__organization=self.request.organization)


class MarketViewSet(viewsets.ModelViewSet):
    serializer_class = MarketSerializer
    filterset_fields = ['countries', 'is_enabled']
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            raise NotAuthenticated()

        queryset = Market.objects.filter(organization=self.request.organization)

        product = self.request.GET.get('product')

        if product:
            queryset = queryset.filter(product__id=product)

        return queryset


class ProviderViewSet(viewsets.ModelViewSet):
    serializer_class = ProviderSerializer
    filterset_fields = ['category', 'is_enabled', 'id']
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            raise NotAuthenticated()

        queryset = Provider.objects.filter(organization=self.request.organization)

        categories = self.request.GET.get('categories')

        if categories:
            category_list = categories.split(',')
            queryset = queryset.filter(category__in=category_list)

        return queryset





class ProductMarketClassViewSet(viewsets.ModelViewSet):
    serializer_class = ProductMarketClassSerializer
    filterset_fields = ['market', 'product', 'is_enabled']
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            raise NotAuthenticated()

        return ProductMarketClass.objects.all()


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    filterset_fields = ['kind', 'measure_unit_category', 'is_enabled']
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            raise NotAuthenticated()

        queryset = Product.objects.filter(organization=self.request.organization)

        markets = self.request.GET.get('markets')

        if markets:
            items_list = markets.split(',')
            queryset = queryset.filter(markets__in=items_list)

        return queryset


class PalletViewSet(viewsets.ModelViewSet):
    serializer_class = PalletSerializer
    filterset_fields = ['market', 'product', 'is_enabled']
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            raise NotAuthenticated()

        queryset = Pallet.objects.filter(organization=self.request.organization)

        size_packagings__product_size = self.request.GET.get('size_packagings__product_size')

        if size_packagings__product_size:
            queryset = queryset.filter(size_packagings__product_size=size_packagings__product_size)

        return queryset


class MaquiladoraViewSet(viewsets.ModelViewSet):
    serializer_class = MaquiladoraSerializer
    filterset_fields = ['organization', 'is_enabled']
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            raise NotAuthenticated()

        queryset = Maquiladora.objects.filter(organization=self.request.organization)

        return queryset


class ProductVarietyViewSet(viewsets.ModelViewSet):
    serializer_class = ProductVarietySerializer
    filterset_fields = ['product', 'is_enabled']
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            raise NotAuthenticated()

        return ProductVariety.objects.filter(product__organization=self.request.organization)


class PackagingViewSet(viewsets.ModelViewSet):
    serializer_class = ProductPackagingSerializer
    filterset_fields = ['product', 'market', 'is_enabled']
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            raise NotAuthenticated()

        queryset = ProductPackaging.objects.filter(organization=self.request.organization)

        return queryset


class SizePackagingViewSet(viewsets.ModelViewSet):
    serializer_class = SizePackagingSerializer
    filterset_fields = ['category', 'product_size', 'product_presentation', 'pallet', 'is_enabled']
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            raise NotAuthenticated()

        queryset = SizePackaging.objects.filter(organization=self.request.organization)

        market = self.request.GET.get('market')
        product = self.request.GET.get('product')
        pallet = self.request.GET.get('pallet')

        if market:
            queryset = queryset.filter(product_size__market=market)

        if product:
            queryset = queryset.filter(product_size__product=product)

        if pallet:
            queryset = queryset.filter(pallet=pallet)

        return queryset


class ProductSizeViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSizeSerializer
    filterset_fields = ['product', 'market', 'category', 'standard_size', 'is_enabled']
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            raise NotAuthenticated()

        queryset = ProductSize.objects.filter(product__organization=self.request.organization)

        categories = self.request.GET.get('categories')
        varieties = self.request.GET.get('varieties')

        if categories:
            category_list = categories.split(',')
            queryset = queryset.filter(category__in=category_list)

        if varieties:
            variety_list = varieties.split(',')
            queryset = queryset.filter(varieties__in=variety_list)

        return queryset


class ProductPresentationViewSet(viewsets.ModelViewSet):
    serializer_class = ProductPresentationSerializer
    filterset_fields = ['product', 'markets', 'presentation_supply_kind', 'presentation_supply', 'is_enabled']
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            raise NotAuthenticated()

        return ProductPresentation.objects.filter(organization=self.request.organization)


class SupplyViewSet(viewsets.ModelViewSet):
    serializer_class = SupplySerializer
    filterset_fields = ['kind', 'usage_discount_quantity', 'capacity', 'is_enabled']
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            raise NotAuthenticated()

        queryset = Supply.objects.filter(organization=self.request.organization)

        capacity__gte = self.request.GET.get('capacity__gte')
        capacity__lte = self.request.GET.get('capacity__lte')

        if capacity__gte:
            queryset = queryset.filter(capacity__gte=capacity__gte)
        if capacity__lte:
            queryset = queryset.filter(capacity__lte=capacity__lte)

        return queryset


class VehicleViewSet(viewsets.ModelViewSet):
    serializer_class = VehicleSerializer
    filterset_fields = ['category', 'is_enabled', 'id']
    pagination_class = None
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            raise NotAuthenticated()

        queryset = Vehicle.objects.filter(organization=self.request.organization)

        # Filtrar por múltiples IDs si se proporciona 'ids' en la querystring
        ids = self.request.query_params.get('ids')
        if ids:
            ids_list = [int(i) for i in ids.split(',')]  # Convierte a una lista de enteros
            queryset = queryset.filter(id__in=ids_list)

        return queryset


class HarvestingCrewProviderViewSet(viewsets.ModelViewSet):
    serializer_class = HarvestingCrewProviderSerializer
    filterset_fields = ['organization', 'is_enabled']
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            raise NotAuthenticated()

        return HarvestingCrewProvider.objects.filter(organization=self.request.organization)


class CrewChiefViewSet(viewsets.ModelViewSet):
    serializer_class = CrewChiefSerializer
    filterset_fields = ['provider', 'is_enabled']
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            raise NotAuthenticated()

        return CrewChief.objects.filter(provider__organization=self.request.organization)


class ClientViewSet(viewsets.ModelViewSet):
    serializer_class = ClientSerializer
    filterset_fields = ['organization', 'is_enabled', 'country']
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            raise NotAuthenticated()

        queryset = Client.objects.filter(organization=self.request.organization)

        category = self.request.GET.get('category')
        maquiladora = self.request.GET.get('maquiladora')

        if category:
            queryset = queryset.filter(category=category)
        if maquiladora:
            queryset = queryset.filter(maquiladora__id=maquiladora)

        return queryset

class OrchardViewSet(viewsets.ModelViewSet):
    serializer_class = OrchardSerializer
    filterset_fields = ['organization', 'is_enabled', 'product']
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            raise NotAuthenticated()

        return Orchard.objects.filter(organization=self.request.organization)

class HarvestingCrewViewSet(viewsets.ModelViewSet):
    serializer_class = HarvestingCrewSerializer
    filterset_fields = ['organization', 'is_enabled', 'provider']
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            raise NotAuthenticated()

        return HarvestingCrew.objects.filter(organization=self.request.organization)


class OrchardCertificationViewSet(viewsets.ModelViewSet):
    serializer_class = OrchardCertificationSerializer
    filterset_fields = ['is_enabled', 'orchard']
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            raise NotAuthenticated()

        return OrchardCertification.objects.filter(orchard__organization=self.request.organization)


class OrchardGeoLocationViewSet(viewsets.ModelViewSet):
    serializer_class = OrchardGeoLocationSerializer
    filterset_fields = ['is_enabled', 'orchard']
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            raise NotAuthenticated()

        return OrchardGeoLocation.objects.filter(orchard__organization=self.request.organization)


class ProductRipenessViewSet(viewsets.ModelViewSet):
    serializer_class = ProductRipenessSerializer
    filterset_fields = ['product', 'is_enabled']
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            raise NotAuthenticated()

        return ProductRipeness.objects.filter(product__organization=self.request.organization)


class ServiceViewSet(viewsets.ModelViewSet):
    serializer_class = ServiceSerializer
    filterset_fields = ['service_provider', 'is_enabled']
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            raise NotAuthenticated()

        return Service.objects.filter(organization=self.request.organization)

class ProductKindViewSetMixin:
    model = None  # This should be set by subclasses

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            raise NotAuthenticated()

        queryset = self.model.objects.all()
        product_kind_id = self.request.query_params.get('product_kind_id')

        if product_kind_id:
            queryset = queryset.filter(product_kind_id=product_kind_id)

        return queryset

class PestProductKindViewSet(viewsets.ModelViewSet):
    """
    A viewset for managing PestProductKind objects.

    Query Parameters:
        - product_kind_id (int): Filters the PestProductKind objects by the associated product kind ID.
    """
    serializer_class = PestProductKindSerializer

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            raise NotAuthenticated()

        queryset = PestProductKind.objects.all()
        product_kind_id = self.request.query_params.get('product_kind_id')

        if product_kind_id:
            queryset = queryset.filter(product_kind_id=product_kind_id)

        return queryset

class DiseaseProductKindViewSet(viewsets.ModelViewSet):
    serializer_class = DiseaseProductKindSerializer

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            raise NotAuthenticated()

        queryset = DiseaseProductKind.objects.all()
        product_kind_id = self.request.query_params.get('product_kind_id')

        if product_kind_id:
            queryset = queryset.filter(product_kind_id=product_kind_id)

        return queryset
