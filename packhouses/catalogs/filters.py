from django.contrib import admin
from .models import ProductVarietySize, Product


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
