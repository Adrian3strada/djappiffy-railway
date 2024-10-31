from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import NotAuthenticated
from .serializers import MarketStandardProductSizeSerializer, MarketSerializer
from .models import MarketStandardProductSize, Market
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

        user_organizations = user.organizations_organization.all()
        return MarketStandardProductSize.objects.filter(market__organization__in=user_organizations)


class MarketViewSet(viewsets.ModelViewSet):
    serializer_class = MarketSerializer
    filterset_fields = ['country', 'is_enabled']
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            raise NotAuthenticated()

        if user.is_superuser:
            return Market.objects.all()

        user_organizations = user.organizations_organization.all()
        return Market.objects.filter(organization__in=user_organizations)
