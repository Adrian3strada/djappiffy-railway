from itertools import product

from rest_framework import viewsets
from rest_framework.exceptions import NotAuthenticated
from .serializers import (MarketSerializer, VehicleSerializer,
                          ProductVarietySerializer, ProductHarvestSizeKindSerializer, ProviderSerializer,
                          ProductSeasonKindSerializer, ProductMassVolumeKindSerializer, ClientSerializer,
                          MaquiladoraSerializer,
                          HarvestingCrewProviderSerializer, CrewChiefSerializer, ProductSerializer)
from .models import (Market, Vehicle, HarvestingCrewProvider, CrewChief, ProductVariety,
                     ProductHarvestSizeKind, ProductSeasonKind, ProductMassVolumeKind, Client, Maquiladora,
                     Provider, Product)


class ProductHarvestSizeKindViewSet(viewsets.ModelViewSet):
    serializer_class = ProductHarvestSizeKindSerializer
    filterset_fields = ['product', 'is_enabled']
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            raise NotAuthenticated()

        return ProductHarvestSizeKind.objects.filter(product__organization=self.request.organization)


class ProductSeasonKindKindViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSeasonKindSerializer
    filterset_fields = ['product', 'is_enabled']
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            raise NotAuthenticated()

        return ProductSeasonKind.objects.filter(product__organization=self.request.organization)


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


class ProviderViewSet(viewsets.ModelViewSet):
    serializer_class = ProviderSerializer
    filterset_fields = ['category', 'is_enabled']
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


class VehicleViewSet(viewsets.ModelViewSet):
    serializer_class = VehicleSerializer
    filterset_fields = ['category', 'is_enabled']
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            raise NotAuthenticated()

        return Vehicle.objects.filter(organization=self.request.organization)


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

