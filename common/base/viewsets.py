from rest_framework import viewsets
from .serializers import (ProductKindSerializer, CitySerializer, SubRegionSerializer, RegionSerializer,
                          CapitalFrameworkSerializer, ProductStandardPackagingSerializer, SupplyKindSerializer,
                          CountrySerializer, CountryProductStandardSizeSerializer)
from .models import ProductKind, ProductKindCountryStandardSize, CapitalFramework, ProductKindCountryStandardPackaging, SupplyKind
from cities_light.contrib.restframework3 import CityModelViewSet as BaseCityModelViewSet
from cities_light.contrib.restframework3 import SubRegionModelViewSet as BaseSubRegionModelViewSet
from cities_light.contrib.restframework3 import RegionModelViewSet as BaseRegionModelViewSet
from cities_light.contrib.restframework3 import CountryModelViewSet as BaseCountryModelViewSet

#


class ProductKindViewSet(viewsets.ModelViewSet):
    serializer_class = ProductKindSerializer
    pagination_class = None
    queryset = ProductKind.objects.all()
    filterset_fields = ['for_packaging', 'for_orchard', 'for_eudr', 'is_enabled']


class SupplyKindViewSet(viewsets.ModelViewSet):
    serializer_class = SupplyKindSerializer
    pagination_class = None
    queryset = SupplyKind.objects.all()
    filterset_fields = ['category', 'is_enabled']


class CapitalFrameworkViewSet(viewsets.ModelViewSet):
    serializer_class = CapitalFrameworkSerializer
    pagination_class = None
    queryset = CapitalFramework.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset()
        country_id = self.request.GET.get('country')
        if country_id:
            queryset = queryset.filter(country_id=country_id)
        return queryset


class CountryProductStandardSizeViewSet(viewsets.ModelViewSet):
    serializer_class = CountryProductStandardSizeSerializer
    pagination_class = None
    multiple_standards = False

    def get_queryset(self):
        queryset = ProductKindCountryStandardSize.objects.all()
        product_kind = self.request.GET.get('product_kind')
        country = self.request.GET.get('country')
        countries = self.request.GET.get('countries')
        if countries:
            country_ids = countries.split(',')
            queryset = queryset.filter(standard__country_id__in=country_ids)
        if product_kind:
            queryset = queryset.filter(standard__product_kind_id=product_kind)
        if country:
            queryset = queryset.filter(standard__country_id=country)

        standards = queryset.values_list('standard', flat=True).distinct()
        self.multiple_standards = standards.count() > 1
        return queryset


class ProductStandardPackagingViewSet(viewsets.ModelViewSet):
    serializer_class = ProductStandardPackagingSerializer
    filterset_fields = ['supply_kind', 'standard', 'max_product_amount']
    pagination_class = None

    def get_queryset(self):
        queryset = ProductKindCountryStandardPackaging.objects.all()
        supply_kind__category = self.request.GET.get('supply_kind__category')
        standard__country__in = self.request.GET.get('standard__country__in')
        max_product_amount__lte = self.request.GET.get('max_product_amount__lte')
        max_product_amount__gte = self.request.GET.get('max_product_amount__gte')

        if supply_kind__category:
            queryset = queryset.filter(supply_kind__category=supply_kind__category)
        if max_product_amount__lte:
            queryset = queryset.filter(max_product_amount__lte=max_product_amount__lte)
        if max_product_amount__gte:
            queryset = queryset.filter(max_product_amount__gte=max_product_amount__gte)
        if standard__country__in:
            country_ids = standard__country__in.split(',')
            queryset = queryset.filter(standard__country__in=country_ids)

        return queryset


class CountryViewSet(BaseCountryModelViewSet):
    serializer_class = CountrySerializer
    pagination_class = None

    def get_queryset(self):
        queryset = super().get_queryset()
        country_ids = self.request.GET.get('id')
        if country_ids:
            ids_list = country_ids.split(',')
            queryset = queryset.filter(id__in=ids_list)
        return queryset


class RegionViewSet(BaseRegionModelViewSet):
    serializer_class = RegionSerializer
    pagination_class = None

    def get_queryset(self):
        queryset = super().get_queryset()
        country = self.request.GET.get('country')
        if country:
            queryset = queryset.filter(country_id=country)
        return queryset


class SubRegionViewSet(BaseSubRegionModelViewSet):
    serializer_class = SubRegionSerializer
    pagination_class = None

    def get_queryset(self):
        queryset = super().get_queryset()
        state = self.request.GET.get('region')
        if state:
            queryset = queryset.filter(region_id=state)
        return queryset


class CityViewSet(BaseCityModelViewSet):
    serializer_class = CitySerializer
    pagination_class = None

    def get_queryset(self):
        queryset = super().get_queryset()
        region = self.request.GET.get('region')
        subregion = self.request.GET.get('subregion')
        country = self.request.GET.get('country')
        if country:
            queryset = queryset.filter(country_id=country)
        if region:
            queryset = queryset.filter(region_id=region)
        if subregion:
            queryset = queryset.filter(subregion_id=subregion)
        return queryset


