from rest_framework import viewsets
from django.utils import translation
from .serializers import ProductSerializer
from .models import Product

#


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

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
