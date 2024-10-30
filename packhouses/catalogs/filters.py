from django.contrib import admin
from cities_light.models import Region

from .models import Product, ProductProvider


class ProductVarietySizeProductFilter(admin.SimpleListFilter):
    title = 'Product'  # Nombre que se muestra en el admin
    parameter_name = 'product'

    def lookups(self, request, model_admin):
        # Opciones para el filtro, basadas en los productos disponibles
        products = Product.objects.all()
        return [(product.id, product.name) for product in products]

    def queryset(self, request, queryset):
        # Filtra el queryset de `ProductVarietySize` basado en el producto seleccionado
        if self.value():
            return queryset.filter(variety__product__id=self.value())
        return queryset


class ProductProviderStateFilter(admin.SimpleListFilter):
    title = 'Provider state'  # Nombre que se muestra en el admin
    parameter_name = 'provider_state'

    def lookups(self, request, model_admin):
        # Opciones para el filtro, basadas en los estados de proveedor disponibles
        states = Region.objects.all()
        # return [(state.id, state.name) for state in states]
        return [(state.id, state.display_name) for state in states]

    def queryset(self, request, queryset):
        # Filtra el queryset de `ProductProvider` basado en el estado de proveedor seleccionado
        if self.value():
            return queryset.filter(state__id=self.value())
        return queryset
