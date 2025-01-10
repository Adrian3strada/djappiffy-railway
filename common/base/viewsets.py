from rest_framework import viewsets
from .serializers import ProductKindSerializer, CitySerializer, SubRegionSerializer, RegionSerializer, CountrySerializer
from .models import ProductKind
from cities_light.contrib.restframework3 import CityModelViewSet as BaseCityModelViewSet
from cities_light.contrib.restframework3 import SubRegionModelViewSet as BaseSubRegionModelViewSet
from cities_light.contrib.restframework3 import RegionModelViewSet as BaseRegionModelViewSet
from cities_light.contrib.restframework3 import CountryModelViewSet as BaseCountryModelViewSet

#


class ProductKindViewSet(viewsets.ModelViewSet):
    serializer_class = ProductKindSerializer
    queryset = ProductKind.objects.all()
    filterset_fields = ['for_packaging', 'for_orchard', 'for_eudr']


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
        region = self.request.GET.get('region')
        if state:
            queryset = queryset.filter(region_id=state)
        if region:
            queryset = queryset.filter(region_id=region)
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


