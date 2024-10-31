from rest_framework import viewsets
from django.utils import translation
from .serializers import ProductSerializer, CitySerializer, RegionSerializer
from .models import Product
from cities_light.models import City
from cities_light.contrib.restframework3 import CityModelViewSet as BaseCityModelViewSet
from cities_light.contrib.restframework3 import RegionModelViewSet as BaseRegionModelViewSet

#


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()


    """
    def list(self, request, *args, **kwargs):
        # Detectar el idioma desde el parámetro de consulta o URL
        lang = request.query_params.get('lang', None)  # Alternativamente, puedes extraerlo de kwargs si está en la URL
        if lang:
            translation.activate(lang)

        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        # Para la vista detallada de un producto
        lang = request.query_params.get('lang', None)
        if lang:
            translation.activate(lang)

        return super().retrieve(request, *args, **kwargs)
    """


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


