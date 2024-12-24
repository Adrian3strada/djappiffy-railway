from rest_framework import viewsets
from rest_framework.exceptions import NotAuthenticated
from .serializers import (MarketStandardProductSizeSerializer, MarketSerializer, VehicleSerializer,
                          HarvestingCrewProviderSerializer, CrewChiefSerializer)
from .models import MarketStandardProductSize, Market, Vehicle, HarvestingCrewProvider, CrewChief
filterset_fields = ['market', 'is_enabled']


class MarketStandardProductSizeViewSet(viewsets.ModelViewSet):
    serializer_class = MarketStandardProductSizeSerializer
    filterset_fields = ['market', 'is_enabled']
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            raise NotAuthenticated()

        if user.is_superuser:
            return MarketStandardProductSize.objects.all()

        user_organizations = user.organizations_organization.all()  # TODO: cambiar query a contexto por dominio
        return MarketStandardProductSize.objects.filter(market__organization__in=user_organizations)


class MarketViewSet(viewsets.ModelViewSet):
    serializer_class = MarketSerializer
    filterset_fields = ['countries', 'is_enabled']
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            raise NotAuthenticated()

        if user.is_superuser:
            return Market.objects.all()

        user_organizations = user.organizations_organization.all()
        return Market.objects.filter(organization__in=user_organizations)

class VehicleViewSet(viewsets.ModelViewSet):
    serializer_class = VehicleSerializer
    filterset_fields = ['scope', 'is_enabled']
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            raise NotAuthenticated()

        if user.is_superuser:
            return Vehicle.objects.all()

        user_organizations = user.organizations_organization.all()
        return Vehicle.objects.filter(organization__in=user_organizations)

class HarvestingCrewProviderViewSet(viewsets.ModelViewSet):
    serializer_class = HarvestingCrewProviderSerializer
    filterset_fields = ['organization', 'is_enabled']
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            raise NotAuthenticated()

        if user.is_superuser:
            return HarvestingCrewProvider.objects.all()

        user_organizations = user.organizations_organization.all()
        return HarvestingCrewProvider.objects.filter(organization__in=user_organizations)

class CrewChiefViewSet(viewsets.ModelViewSet):
    serializer_class = CrewChiefSerializer
    filterset_fields = ['harvesting_crew_provider',]
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            raise NotAuthenticated()

        if user.is_superuser:
            return CrewChief.objects.all()

        user_organizations = user.organizations_organization.all()
        return CrewChief.objects.filter(organization__in=user_organizations)
