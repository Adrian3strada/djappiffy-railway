from rest_framework import viewsets
from django.utils import translation
from .serializers import ProductSerializer, CitySerializer, RegionSerializer, CountrySerializer
from .models import Product
from cities_light.models import City
from cities_light.contrib.restframework3 import CityModelViewSet as BaseCityModelViewSet
from cities_light.contrib.restframework3 import RegionModelViewSet as BaseRegionModelViewSet
from cities_light.contrib.restframework3 import CountryModelViewSet as BaseCountryModelViewSet

#


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()


class CountryViewSet(BaseCountryModelViewSet):
    serializer_class = CountrySerializer
    pagination_class = None

    def get_queryset(self):
        queryset = super().get_queryset()
        country_ids = self.request.GET.get('id')
        print('country_ids', country_ids)
        if country_ids:
            ids_list = country_ids.split(',')
            print('ids_list', ids_list)
            queryset = queryset.filter(id__in=ids_list)
            print('queryset', queryset)
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


class CityViewSet(BaseCityModelViewSet):
    serializer_class = CitySerializer
    pagination_class = None

    def get_queryset(self):
        queryset = super().get_queryset()
        region = self.request.GET.get('region')
        country = self.request.GET.get('country')
        if country:
            queryset = queryset.filter(country_id=country)
        if region:
            queryset = queryset.filter(region_id=region)
        return queryset


