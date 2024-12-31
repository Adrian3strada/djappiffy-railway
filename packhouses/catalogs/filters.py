from django.contrib import admin
from cities_light.models import Country, Region, City
from common.profiles.models import UserProfile, OrganizationProfile, PackhouseExporterSetting, PackhouseExporterProfile
from .models import Product, ProductProvider
from common.base.models import ProductKind
from django.utils.translation import gettext_lazy as _


class ProductKindForPackagingFilter(admin.SimpleListFilter):
    title = _('Product Kind')
    parameter_name = 'kind'

    def lookups(self, request, model_admin):
        product_kinds = ProductKind.objects.filter(for_packaging=True, is_enabled=True)
        if hasattr(request, 'organization'):
            packhouse_exporter_profile = PackhouseExporterProfile.objects.get(organization=request.organization)
            product_kinds = packhouse_exporter_profile.packhouseexportersetting.product_kinds.filter(is_enabled=True)
        return [(kind.id, kind.name) for kind in product_kinds]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(kind__id=self.value())
        return queryset


class ProductByOrganizationFilter(admin.SimpleListFilter):
    title = _('Product')
    parameter_name = 'product'

    def lookups(self, request, model_admin):
        products = Product.objects.filter(organization=request.organization, is_enabled=True)
        return [(product.id, product.name) for product in products]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(product__id=self.value())
        return queryset


class ProductVarietySizeProductFilter(admin.SimpleListFilter):
    title = 'Product'  # Nombre que se muestra en el admin
    parameter_name = 'product'

    def lookups(self, request, model_admin):
        # Opciones para el filtro, basadas en los productos disponibles
        products = Product.objects.all()
        return [(product.id, product.kind.name) for product in products]

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

class StateFilterUserCountry(admin.SimpleListFilter):
    title = 'State'
    parameter_name = 'state'

    def lookups(self, request, model_admin):
        user_profile = UserProfile.objects.get(user=request.user)
        country = user_profile.country

        states = Region.objects.filter(country_id=country.id)
        return [(state.id, state.display_name) for state in states]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(state__id=self.value())
        return queryset


