from django.contrib import admin
from cities_light.models import Country, Region, City
from common.profiles.models import UserProfile, OrganizationProfile, PackhouseExporterSetting, PackhouseExporterProfile
from .models import Product, ProductVariety, Market, ProductHarvestSizeKind, ProductQualityKind, ProductMassVolumeKind
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


class ByProductForOrganizationFilter(admin.SimpleListFilter):
    title = _('Product')
    parameter_name = 'product'

    def lookups(self, request, model_admin):
        products = Product.objects.filter(organization=request.organization, is_enabled=True)
        return [(product.id, product.name) for product in products]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(product__id=self.value())
        return queryset


class ByProductVarietyForOrganizationFilter(admin.SimpleListFilter):
    title = _('Product Variety')
    parameter_name = 'product_variety'

    def lookups(self, request, model_admin):
        product_varieties = ProductVariety.objects.filter(product__organization=request.organization, is_enabled=True)
        return [(product_variety.id, f"{product_variety.product.name}: {product_variety.name}") for product_variety in product_varieties]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(product_variety__id=self.value())
        return queryset


class ByMarketForOrganizationFilter(admin.SimpleListFilter):
    title = _('Market')
    parameter_name = 'market'

    def lookups(self, request, model_admin):
        markets = Market.objects.filter(organization=request.organization, is_enabled=True)
        return [(market.id, market.name) for market in markets]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(market__id=self.value())
        return queryset


class ByProductHarvestSizeKindForOrganizationFilter(admin.SimpleListFilter):
    title = _('Product harvest size kind')
    parameter_name = 'product_harvest_size_kind'

    def lookups(self, request, model_admin):
        product_harvest_size_kinds = ProductHarvestSizeKind.objects.filter(product__organization=request.organization, is_enabled=True)
        return [(product_harvest_size_kind.id, f"{product_harvest_size_kind.product.name}: {product_harvest_size_kind.name}") for product_harvest_size_kind in product_harvest_size_kinds]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(product_harvest_size_kind=self.value())
        return queryset


class ByProductQualityKindForOrganizationFilter(admin.SimpleListFilter):
    title = _('Size Kind')
    parameter_name = 'product_size_kind'

    def lookups(self, request, model_admin):
        print("request.organization", request.organization)
        product_size_kinds = ProductQualityKind.objects.filter(product__organization=request.organization, is_enabled=True)
        print("product_size_kinds", product_size_kinds)
        return [(product_size_kind.id, product_size_kind.name) for product_size_kind in product_size_kinds]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(size_kind=self.value())
        return queryset


class ByProductMassVolumeKindForOrganizationFilter(admin.SimpleListFilter):
    title = _('Mass volume Kind')
    parameter_name = 'product_mass_volume_kind'

    def lookups(self, request, model_admin):
        product_mass_volume_kinds = ProductMassVolumeKind.objects.filter(product__organization=request.organization, is_enabled=True)
        return [(product_mass_volume_kind.id, product_mass_volume_kind.name) for product_mass_volume_kind in product_mass_volume_kinds]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(product_mass_volume_kind=self.value())
        return queryset


class StateFilterUserCountry(admin.SimpleListFilter):
    title = 'State'
    parameter_name = 'state'

    def lookups(self, request, model_admin):
        user_profile = UserProfile.objects.get(user=request.user)
        if hasattr(request, 'organization'):
            organization_profile = OrganizationProfile.objects.get(organization=request.organization)
            country = organization_profile.country

            states = Region.objects.filter(country_id=country.id)
            return [(state.id, state.display_name) for state in states]
        return Region.objects.none()

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(state__id=self.value())
        return queryset


