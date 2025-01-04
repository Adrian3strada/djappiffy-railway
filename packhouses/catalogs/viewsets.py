from rest_framework import viewsets
from rest_framework.exceptions import NotAuthenticated
from .serializers import (MarketStandardProductSizeSerializer, MarketSerializer, VehicleSerializer,
                          ProductVarietySerializer, ProductHarvestSizeKindSerializer,
                          ProductQualityKindSerializer, ProductMassVolumeKindSerializer, ClientSerializer,
                          HarvestingCrewProviderSerializer, CrewChiefSerializer)
from .models import (MarketStandardProductSize, Market, Vehicle, HarvestingCrewProvider, CrewChief, ProductVariety,
                     ProductHarvestSizeKind, ProductQualityKind, ProductMassVolumeKind, Client)


class MarketStandardProductSizeViewSet(viewsets.ModelViewSet):
    serializer_class = MarketStandardProductSizeSerializer
    filterset_fields = ['market', 'is_enabled']
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            raise NotAuthenticated()

        queryset = MarketStandardProductSize.objects.filter(market__organization=self.request.organization)
        markets = self.request.GET.get('markets')
        if markets:
            market_list = markets.split(',')
            queryset = queryset.filter(market__id__in=market_list)

        return queryset


class ProductHarvestSizeKindViewSet(viewsets.ModelViewSet):
    serializer_class = ProductHarvestSizeKindSerializer
    filterset_fields = ['product', 'is_enabled']
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            raise NotAuthenticated()

        return ProductHarvestSizeKind.objects.filter(product__organization=self.request.organization)


class ProductQualityKindKindViewSet(viewsets.ModelViewSet):
    serializer_class = ProductQualityKindSerializer
    filterset_fields = ['product', 'is_enabled']
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            raise NotAuthenticated()

        return ProductQualityKind.objects.filter(product__organization=self.request.organization)


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


class ProductVarietyViewSet(viewsets.ModelViewSet):
    serializer_class = ProductVarietySerializer
    filterset_fields = ['product', 'is_enabled']
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            raise NotAuthenticated()

        return ProductVariety.objects.filter(product__organization=self.request.organization)


class VehicleViewSet(viewsets.ModelViewSet):
    serializer_class = VehicleSerializer
    filterset_fields = ['scope', 'is_enabled']
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
    filterset_fields = ['harvesting_crew_provider', ]
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            raise NotAuthenticated()

        return CrewChief.objects.filter(organization=self.request.organization)

class ClientViewSet(viewsets.ModelViewSet):
    serializer_class = ClientSerializer
    filterset_fields = ['organization', 'is_enabled', 'country']
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            raise NotAuthenticated()

        return Client.objects.filter(organization=self.request.organization)
