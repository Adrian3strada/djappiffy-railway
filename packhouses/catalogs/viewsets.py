from itertools import product

from rest_framework import viewsets
from rest_framework.exceptions import NotAuthenticated

from .serializers import (MarketSerializer, ProductMarketClassSerializer, VehicleSerializer,
                          ProductVarietySerializer, ProductHarvestSizeKindSerializer, ProviderSerializer,
                          ProductPhenologyKindSerializer, ProductMassVolumeKindSerializer, ClientSerializer, ProductSizeSerializer,
                          MaquiladoraSerializer, PackagingSerializer,
                          SupplySerializer, OrchardSerializer, HarvestingCrewSerializer,
                          HarvestingCrewProviderSerializer, CrewChiefSerializer, ProductSerializer,
                          OrchardCertificationSerializer
                          )
from .models import (Market, ProductMarketClass, Vehicle, HarvestingCrewProvider, CrewChief, ProductVariety,
                     ProductHarvestSizeKind, ProductPhenologyKind, ProductMassVolumeKind, Client, Maquiladora, Provider,
                     Product, Packaging,
                     Supply, Orchard, HarvestingCrew, ProductSize, OrchardCertification
                     )
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


class ProductMassVolumeKindViewSet(viewsets.ModelViewSet):
    serializer_class = ProductMassVolumeKindSerializer
    filterset_fields = ['product', 'is_enabled']
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            raise NotAuthenticated()

        return ProductMassVolumeKind.objects.filter(product__organization=self.request.organization)


class MarketViewSet(viewsets.ModelViewSet):
    serializer_class = MarketSerializer
    filterset_fields = ['countries', 'is_enabled']
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            raise NotAuthenticated()

        return Market.objects.filter(organization=self.request.organization)


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
    filterset_fields = ['organization', 'is_enabled']
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            raise NotAuthenticated()

        return Product.objects.filter(organization=self.request.organization)

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
    serializer_class = PackagingSerializer
    filterset_fields = ['product', 'markets', 'is_enabled']
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            raise NotAuthenticated()

        return Packaging.objects.filter(organization=self.request.organization)


class ProductSizeViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSizeSerializer
    filterset_fields = ['product', 'market', 'is_enabled']
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            raise NotAuthenticated()

        return ProductSize.objects.all()


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


class SupplyViewSet(viewsets.ModelViewSet):
    serializer_class = SupplySerializer
    filterset_fields = ['kind', 'is_enabled']
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            raise NotAuthenticated()

        return Supply.objects.all()


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



