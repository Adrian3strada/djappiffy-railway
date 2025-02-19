from django.contrib import admin
from cities_light.models import Country, Region, SubRegion, City
from common.profiles.models import UserProfile, OrganizationProfile, PackhouseExporterSetting, PackhouseExporterProfile
from .models import ProductKindCountryStandard, CountryProductStandardSize, CapitalFramework
from common.base.models import ProductKind
from django.utils.translation import gettext_lazy as _


class ByCountryForCapitalFrameworkFilter(admin.SimpleListFilter):
    title = _('Country')
    parameter_name = 'country'

    def lookups(self, request, model_admin):
        countries_for_capital_frameworks = list(CapitalFramework.objects.all().values_list('country_id', flat=True).distinct())
        countries = Country.objects.filter(id__in=countries_for_capital_frameworks)
        return [(country.id, country.name) for country in countries]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(country__id=self.value())
        return queryset


class ByProductKindForPackagingFilter(admin.SimpleListFilter):
    title = _('Product kind')
    parameter_name = 'product_kind'

    def lookups(self, request, model_admin):
        product_kinds = ProductKind.objects.filter(for_packaging=True, is_enabled=True)
        return [(product_kind.id, product_kind.name) for product_kind in product_kinds]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(product_kind__id=self.value())
        return queryset


class ByCountryForMarketProductSizeStandardFilter(admin.SimpleListFilter):
    title = _('Country')
    parameter_name = 'country'

    def lookups(self, request, model_admin):
        countries_for_market_product_size_standards = list(ProductKindCountryStandard.objects.filter(is_enabled=True).values_list('country_id', flat=True).distinct())
        countries = Country.objects.filter(id__in=countries_for_market_product_size_standards)
        return [(country.id, country.name) for country in countries]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(country__id=self.value())
        return queryset
