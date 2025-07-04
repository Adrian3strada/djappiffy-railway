from django.contrib import admin
from cities_light.models import Country, Region, SubRegion, City
from common.profiles.models import UserProfile, OrganizationProfile, PackhouseExporterSetting, PackhouseExporterProfile
from .models import (Product, ProductVariety, Market, ProductHarvestSizeKind, ProductPhenologyKind,
                     Gatherer, PaymentKind, Supply, ProductPackaging, ProductSize,
                     Provider, Client, CapitalFramework, SizePackaging, ProductPresentation,
                     Maquiladora, WeighingScale, ExportingCompany, CustomsBroker, Pallet,
                     ProductKindCountryStandardPackaging
                     )
from common.base.models import ProductKind, SupplyKind
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
        products = Product.objects.none()
        if hasattr(request, 'organization'):
            products = Product.objects.filter(organization=request.organization)
        return [(product.id, product.name) for product in products]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(product__id=self.value())
        return queryset


class ByProductForOrganizationProductSizeFilter(ByProductForOrganizationFilter):
    def lookups(self, request, model_admin):
        products = Product.objects.none()
        if hasattr(request, 'organization'):
            productsize_relatedlist = list(ProductSize.objects.filter(product__organization=request.organization).values_list('product', flat=True).distinct())
            products = Product.objects.filter(id__in=productsize_relatedlist).order_by('name')
        return [(product.id, product.name) for product in products]


class ByProductSizeForOrganizationFilter(admin.SimpleListFilter):
    title = _('Product size')
    parameter_name = 'product_size'

    def lookups(self, request, model_admin):
        product_size_relatedlist = ProductSize.objects.filter(organization=request.organization)
        return [(product_size.id, product_size.name) for product_size in product_size_relatedlist]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(product_size__id=self.value())
        return queryset


class ByProductSizeForOrganizationSizePackagingFilter(ByProductSizeForOrganizationFilter):
    def lookups(self, request, model_admin):
        product_sizes = ProductSize.objects.none()
        if hasattr(request, 'organization'):
            product_size_relatedlist = list(SizePackaging.objects.filter(organization=request.organization).values_list('product_size', flat=True).distinct())
            product_sizes = ProductSize.objects.filter(id__in=product_size_relatedlist).order_by('name')
        return [(product_size.id, f"{product_size.name} ({product_size.product.name}: {product_size.market.alias})") for product_size in product_sizes]


class ByProductSizeForProductOrganizationFilter(admin.SimpleListFilter):
    title = _('Product Size')
    parameter_name = 'product_size'

    def lookups(self, request, model_admin):
        product_sizes = ProductSize.objects.filter(product__organization=request.organization)
        return [(product_size.id, f"{product_size.name} ({product_size.product.name}: {product_size.market.alias})") for product_size in product_sizes]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(product_size__id=self.value())
        return queryset


class ByPackagingForOrganizationFilter(admin.SimpleListFilter):
    title = _('Packaging')
    parameter_name = 'packaging'

    def lookups(self, request, model_admin):
        packagings = ProductPackaging.objects.filter(organization=request.organization)
        return [(packaging.id, packaging.name) for packaging in packagings]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(packaging__id=self.value())
        return queryset


class ByPackagingForOrganizationSizePackagingFilter(admin.SimpleListFilter):
    title = _('Product Packaging')
    parameter_name = 'product_packaging'

    def lookups(self, request, model_admin):
        packagings = ProductPackaging.objects.none()
        if hasattr(request, 'organization'):
            packaging_relatedlist = list(
                SizePackaging.objects.filter(organization=request.organization)
                .values_list('product_packaging', flat=True)
                .distinct()
            )
            packagings = ProductPackaging.objects.filter(id__in=packaging_relatedlist).order_by('name')

        return [
            (
                packaging.id,
                f"{packaging.name} - ({packaging.country_standard_packaging.standard.name if packaging.country_standard_packaging and packaging.country_standard_packaging.standard and packaging.country_standard_packaging.standard.name else '-'}: {packaging.country_standard_packaging})"
            )
            for packaging in packagings
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(product_packaging_id=self.value())
        return queryset



class ByProductPresentationForOrganizationSizePackagingFilter(admin.SimpleListFilter):
    title = _('Product Presentation')
    parameter_name = 'product_presentation'

    def lookups(self, request, model_admin):
        presentations = ProductPresentation.objects.none()
        if hasattr(request, 'organization'):
            presentation_ids = list(
                SizePackaging.objects.filter(organization=request.organization)
                .values_list('product_presentation', flat=True)
                .distinct()
            )
            presentations = ProductPresentation.objects.filter(id__in=presentation_ids).order_by('name')

        return [(presentation.id, presentation.name) for presentation in presentations]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(product_presentation_id=self.value())
        return queryset


class ByProductVarietiesForOrganizationFilter(admin.SimpleListFilter):
    title = _('Variety')
    parameter_name = 'product_varieties'

    def lookups(self, request, model_admin):
        product_varietieses = ProductVariety.objects.filter(product__organization=request.organization)
        return [(product_variety.id, f"{product_variety.product.name}: {product_variety.name}") for product_variety in product_varietieses]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(product_varieties__id=self.value())
        return queryset


class ByProductVarietiesForOrganizationProductSizeFilter(admin.SimpleListFilter):
    title = _('Variety')
    parameter_name = 'product_variety'
    
    def lookups(self, request, model_admin):
        varieties = ProductVariety.objects.none()
        if hasattr(request, 'organization'):
            varieties_ids = ProductSize.objects.filter(
                product__organization=request.organization
            ).values_list('varieties', flat=True).distinct()
            varieties = ProductVariety.objects.filter(id__in=varieties_ids).order_by('name')
        return [(variety.id, f"{variety.product.name}: {variety.name}") for variety in varieties]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(varieties__id=self.value())
        return queryset


class ByProductVarietyForOrganizationFilter(admin.SimpleListFilter):
    title = _('Product Variety')
    parameter_name = 'product_variety'

    def lookups(self, request, model_admin):
        product_varieties = ProductVariety.objects.filter(product__organization=request.organization)
        return [(product_variety.id, f"{product_variety.product.name}: {product_variety.name}") for product_variety in product_varieties]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(product_variety__id=self.value())
        return queryset


class ByMarketForOrganizationFilter(admin.SimpleListFilter):
    title = _('Market')
    parameter_name = 'markets'

    def lookups(self, request, model_admin):
        markets = Market.objects.filter(organization=request.organization)
        return [(market.id, market.name) for market in markets]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(market__id=self.value())
        return queryset

class ByMarketsForOrganizationFilter(admin.SimpleListFilter):
    title = _('Market')
    parameter_name = 'markets'

    def lookups(self, request, model_admin):
        markets = Market.objects.filter(organization=request.organization)
        return [(market.id, market.name) for market in markets]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(markets__id=self.value())
        return queryset


class ByMarketForOrganizationProductSizeFilter(ByMarketForOrganizationFilter):
    def lookups(self, request, model_admin):
        markets = Product.objects.none()
        if hasattr(request, 'organization'):
            productsize_relatedlist = list(ProductSize.objects.filter(product__organization=request.organization).values_list('market', flat=True).distinct())
            markets = Market.objects.filter(id__in=productsize_relatedlist).order_by('name')
        return [(market.id, market.name) for market in markets]


class ByClientCapitalFrameworkForOrganizationFilter(admin.SimpleListFilter):
    title = _('Capital framework')
    parameter_name = 'capital_framework'

    def lookups(self, request, model_admin):
        clients_capital_frameworks = list(Client.objects.filter(organization=request.organization).values_list('capital_framework', flat=True).distinct())
        capital_frameworks = CapitalFramework.objects.filter(id__in=clients_capital_frameworks)
        return [(capital_framework.id, capital_framework.code) for capital_framework in capital_frameworks]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(capital_framework__id=self.value())
        return queryset


class ByPaymentKindForOrganizationFilter(admin.SimpleListFilter):
    title = _('Payment kind')
    parameter_name = 'payment_kind'

    def lookups(self, request, model_admin):
        payment_kinds = PaymentKind.objects.filter(organization=request.organization)
        return [(payment_kind.id, payment_kind.name) for payment_kind in payment_kinds]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(payment_kind__id=self.value())
        return queryset


class ByProductHarvestSizeKindForOrganizationFilter(admin.SimpleListFilter):
    title = _('Harvest size kind')
    parameter_name = 'product_harvest_size_kind'

    def lookups(self, request, model_admin):
        product_harvest_size_kinds = ProductHarvestSizeKind.objects.filter(product__organization=request.organization)
        return [(product_harvest_size_kind.id, f"{product_harvest_size_kind.product.name}: {product_harvest_size_kind.name}") for product_harvest_size_kind in product_harvest_size_kinds]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(product_harvest_size_kind=self.value())
        return queryset


class ByProductSeasonKindForOrganizationFilter(admin.SimpleListFilter):
    title = _('Phenology')
    parameter_name = 'product_phenology_kind'

    def lookups(self, request, model_admin):
        product_phenology_kinds = ProductPhenologyKind.objects.filter(product__organization=request.organization)
        return [(product_phenology_kind.id, f"{product_phenology_kind.product.name}: {product_phenology_kind.name}") for product_phenology_kind in product_phenology_kinds]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(size_kind=self.value())
        return queryset


class StatesForOrganizationCountryFilter(admin.SimpleListFilter):
    title = 'State'
    parameter_name = 'state'

    def lookups(self, request, model_admin):
        if hasattr(request, 'organization'):
            organization_profile = OrganizationProfile.objects.get(organization=request.organization)
            country = organization_profile.country
            states = Region.objects.filter(country_id=country.id)
            return [(state.id, state.name) for state in states]
        return Region.objects.none()

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(state__id=self.value())
        return queryset


class ByCountryForOrganizationMarketsFilter(admin.SimpleListFilter):
    title = _('Country')
    parameter_name = 'countries'

    def lookups(self, request, model_admin):
        countries = Country.objects.all()
        if hasattr(request, 'organization'):
            organization_markets_country_ids = list(
                Market.objects.filter(organization=request.organization).values_list('countries', flat=True).distinct())
            countries = countries.filter(id__in=organization_markets_country_ids)
        return [(country.id, country.name) for country in countries]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(countries__id=self.value())
        return queryset


class ByCountryForOrganizationProvidersFilter(admin.SimpleListFilter):
    title = _('Country')
    parameter_name = 'country'

    def lookups(self, request, model_admin):
        countries = Country.objects.all()
        if hasattr(request, 'organization'):
            organization_providers_country_ids = list(
                Provider.objects.filter(organization=request.organization).values_list('country', flat=True).distinct())
            countries = countries.filter(id__in=organization_providers_country_ids).order_by('name')
        return [(country.id, country.name) for country in countries]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(country__id=self.value())
        return queryset


class ByStateForOrganizationProvidersFilter(admin.SimpleListFilter):
    title = _('State')
    parameter_name = 'state'

    def lookups(self, request, model_admin):
        states = Region.objects.all()
        if hasattr(request, 'organization'):
            organization_providers_state_ids = list(
                Provider.objects.filter(organization=request.organization).values_list('state', flat=True).distinct())
            states = states.filter(id__in=organization_providers_state_ids).order_by('country__name', 'name')
        return [(state.id, f"{state.country.name}: {state.name}") for state in states]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(state__id=self.value())
        return queryset


class ByCityForOrganizationProvidersFilter(admin.SimpleListFilter):
    title = _('City')
    parameter_name = 'city'

    def lookups(self, request, model_admin):
        cities = SubRegion.objects.all()
        if hasattr(request, 'organization'):
            organization_providers_city_ids = list(
                Provider.objects.filter(organization=request.organization).values_list('city', flat=True).distinct())
            cities = cities.filter(id__in=organization_providers_city_ids).order_by('country__name', 'region__name', 'name')
        return [(city.id, f"{city.country.name}: {city.region.name}: {city.name}") for city in cities]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(city__id=self.value())
        return queryset


# Clientes


class ByCountryForOrganizationClientsFilter(admin.SimpleListFilter):
    title = _('Country')
    parameter_name = 'country'

    def lookups(self, request, model_admin):
        countries = Country.objects.all()
        if hasattr(request, 'organization'):
            country_ids = list(
                Client.objects.filter(organization=request.organization).values_list('country', flat=True).distinct())
            countries = countries.filter(id__in=country_ids).order_by('name')
        return [(country.id, country.name) for country in countries]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(country__id=self.value())
        return queryset


class ByStateForOrganizationClientsFilter(admin.SimpleListFilter):
    title = _('State')
    parameter_name = 'state'

    def lookups(self, request, model_admin):
        states = Region.objects.all()
        if hasattr(request, 'organization'):
            state_ids = list(
                Client.objects.filter(organization=request.organization).values_list('state', flat=True).distinct())
            states = states.filter(id__in=state_ids).order_by('country__name', 'name')
        return [(state.id, f"{state.country.name}: {state.name}") for state in states]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(state__id=self.value())
        return queryset


class ByCityForOrganizationClientsFilter(admin.SimpleListFilter):
    title = _('City')
    parameter_name = 'city'

    def lookups(self, request, model_admin):
        cities = SubRegion.objects.all()
        if hasattr(request, 'organization'):
            organization_providers_city_ids = list(
                Client.objects.filter(organization=request.organization).values_list('city', flat=True).distinct())
            cities = cities.filter(id__in=organization_providers_city_ids).order_by('country__name', 'region__name', 'name')
        return [(city.id, f"{city.country.name}: {city.region.name}: {city.name}") for city in cities]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(city__id=self.value())
        return queryset

# /Clientes


class ByStateForOrganizationGathererFilter(admin.SimpleListFilter):
    title = _('State')
    parameter_name = 'state'

    def lookups(self, request, model_admin):
        states = Region.objects.all()
        if hasattr(request, 'organization'):
            organization_gatherers_state_ids = list(Gatherer.objects.filter(organization=request.organization).values_list('state', flat=True).distinct())
            states = states.filter(id__in=organization_gatherers_state_ids).order_by('name')
        return [(state.id, state.name) for state in states]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(state__id=self.value())
        return queryset


class ByCityForOrganizationGathererFilter(admin.SimpleListFilter):
    title = _('City')
    parameter_name = 'city'

    def lookups(self, request, model_admin):
        cities = SubRegion.objects.all()
        if hasattr(request, 'organization'):
            organization_gatherers_city_ids = list(Gatherer.objects.filter(organization=request.organization).values_list('city', flat=True).distinct())
            cities = cities.filter(id__in=organization_gatherers_city_ids).order_by('region__name', 'name')
        return [(city.id, f"{city.region.name}: {city.name}") for city in cities]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(city__id=self.value())
        return queryset


class ByStateForOrganizationFilter(admin.SimpleListFilter):
    title = _('State')
    parameter_name = 'state'

    def lookups(self, request, model_admin):
        states = Region.objects.all()
        if hasattr(request, 'organization'):
            packhouse_profile = PackhouseExporterProfile.objects.get(organization=request.organization)
            country = packhouse_profile.country
            states = states.filter(country=country)
        return [(state.id, state.name) for state in states]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(state__id=self.value())
        return queryset


class ByCityForOrganizationFilter(admin.SimpleListFilter):
    title = _('City')
    parameter_name = 'city'

    def lookups(self, request, model_admin):
        cities = SubRegion.objects.all()
        if hasattr(request, 'organization'):
            packhouse_profile = PackhouseExporterProfile.objects.get(organization=request.organization)
            country = packhouse_profile.country
            cities = cities.filter(country=country).order_by('region__name', 'name')
        return [(city.id, f"{city.region.name}: {city.name}") for city in cities]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(city__id=self.value())
        return queryset


class ByDistrictForOrganizationFilter(admin.SimpleListFilter):
    title = _('District')
    parameter_name = 'district'

    def lookups(self, request, model_admin):
        districts = City.objects.all()
        if hasattr(request, 'organization'):
            packhouse_profile = PackhouseExporterProfile.objects.get(organization=request.organization)
            country = packhouse_profile.country
            districts = districts.filter(country=country, subregion__isnull=False).order_by('region__name', 'subregion__name', 'name')
        return [(district.id, f"{district.region.name} - {district.subregion.name}: {district.name}") for district in districts]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(district__id=self.value())
        return queryset

class ByStateForOrganizationMaquiladoraFilter(admin.SimpleListFilter):
    title = _('State')
    parameter_name = 'state'

    def lookups(self, request, model_admin):
        states = Region.objects.all()
        if hasattr(request, 'organization'):
            organization_maquiladora_state_ids = list(
                Maquiladora.objects.filter(organization=request.organization).values_list('state', flat=True).distinct())
            states = states.filter(id__in=organization_maquiladora_state_ids).order_by('country__name', 'name')
        return [(state.id, state.name) for state in states]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(state__id=self.value())
        return queryset


class ByCityForOrganizationMaquiladoraFilter(admin.SimpleListFilter):
    title = _('City')
    parameter_name = 'city'

    def lookups(self, request, model_admin):
        cities = SubRegion.objects.all()
        if hasattr(request, 'organization'):
            organization_maquiladora_city_ids = list(
                Maquiladora.objects.filter(organization=request.organization).values_list('city', flat=True).distinct())
            cities = cities.filter(id__in=organization_maquiladora_city_ids).order_by('country__name', 'region__name', 'name')
        return [(city.id, f" {city.region.name}: {city.name}") for city in cities]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(city__id=self.value())
        return queryset

class ByServiceProviderForOrganizationServiceFilter(admin.SimpleListFilter):
    title = _('Provider')
    parameter_name = 'provider'

    def lookups(self, request, model_admin):
        providers = Provider.objects.filter(organization=request.organization, category="service_provider")
        return [(provider.id, provider.name) for provider in providers]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(service_provider=self.value())
        return queryset

class ByStateForOrganizationWeighingScaleFilter(admin.SimpleListFilter):
    title = _('State')
    parameter_name = 'state'

    def lookups(self, request, model_admin):
        states = Region.objects.all()
        if hasattr(request, 'organization'):
            organization_maquiladora_state_ids = list(
                WeighingScale.objects.filter(organization=request.organization).values_list('state', flat=True).distinct())
            states = states.filter(id__in=organization_maquiladora_state_ids).order_by('country__name', 'name')
        return [(state.id, state.name) for state in states]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(state__id=self.value())
        return queryset

class ByCityForOrganizationWeighingScaleFilter(admin.SimpleListFilter):
    title = _('City')
    parameter_name = 'city'

    def lookups(self, request, model_admin):
        cities = SubRegion.objects.all()
        if hasattr(request, 'organization'):
            organization_maquiladora_city_ids = list(
                WeighingScale.objects.filter(organization=request.organization).values_list('city', flat=True).distinct())
            cities = cities.filter(id__in=organization_maquiladora_city_ids).order_by('country__name', 'region__name', 'name')
        return [(city.id, f" {city.region.name}: {city.name}") for city in cities]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(city__id=self.value())
        return queryset


class ByCountryForOrganizationExportingCompaniesFilter(admin.SimpleListFilter):
    title = _('Country')
    parameter_name = 'country'

    def lookups(self, request, model_admin):
        countries = Country.objects.all()
        if hasattr(request, 'organization'):
            country_ids = list(
                ExportingCompany.objects.filter(organization=request.organization).values_list('country', flat=True).distinct())
            countries = countries.filter(id__in=country_ids).order_by('name')
        return [(country.id, country.name) for country in countries]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(country__id=self.value())
        return queryset

class ByStateForOrganizationExportingCompaniesFilter(admin.SimpleListFilter):
    title = _('State')
    parameter_name = 'state'

    def lookups(self, request, model_admin):
        states = Region.objects.all()
        if hasattr(request, 'organization'):
            state_ids = list(
                ExportingCompany.objects.filter(organization=request.organization).values_list('state', flat=True).distinct())
            states = states.filter(id__in=state_ids).order_by('country__name', 'name')
        return [(state.id, f"{state.country.name}: {state.name}") for state in states]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(state__id=self.value())
        return queryset


class ByCityForOrganizationExportingCompaniesFilter(admin.SimpleListFilter):
    title = _('City')
    parameter_name = 'city'

    def lookups(self, request, model_admin):
        cities = SubRegion.objects.all()
        if hasattr(request, 'organization'):
            organization_providers_city_ids = list(
                ExportingCompany.objects.filter(organization=request.organization).values_list('city', flat=True).distinct())
            cities = cities.filter(id__in=organization_providers_city_ids).order_by('country__name', 'region__name', 'name')
        return [(city.id, f"{city.country.name}: {city.region.name}: {city.name}") for city in cities]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(city__id=self.value())
        return queryset

class ByCountryForOrganizationCustomsBrokersFilter(admin.SimpleListFilter):
    title = _('Country')
    parameter_name = 'country'

    def lookups(self, request, model_admin):
        countries = Country.objects.all()
        if hasattr(request, 'organization'):
            country_ids = list(
                CustomsBroker.objects.filter(organization=request.organization).values_list('country', flat=True).distinct())
            countries = countries.filter(id__in=country_ids).order_by('name')
        return [(country.id, country.name) for country in countries]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(country__id=self.value())
        return queryset


class BySupplyKindForPackagingFilter(admin.SimpleListFilter):
    title = _('Supply Kind')
    parameter_name = 'supply_kind'

    def lookups(self, request, model_admin):
        supply_kinds = SupplyKind.objects.all()
        if hasattr(request, 'organization'):
            main_supply_kind_ids = list(ProductPackaging.objects.filter(organization=request.organization).values_list(
                'packaging_supply_kind', flat=True).distinct())
            supply_kinds = supply_kinds.filter(id__in=main_supply_kind_ids)
        return [(supply_kind.id, supply_kind.name) for supply_kind in supply_kinds]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(packaging_supply_kind__id=self.value())
        return queryset


class BySupplyForOrganizationPackagingFilter(admin.SimpleListFilter):
    title = _('Supply')
    parameter_name = 'supply'

    def lookups(self, request, model_admin):
        supplies = Supply.objects.all()
        if hasattr(request, 'organization'):
            supply_ids = list(ProductPackaging.objects.filter(organization=request.organization).values_list(
                'packaging_supply', flat=True).distinct())
            supplies = supplies.filter(id__in=supply_ids)
        return [(supply.id, supply.name) for supply in supplies]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(packaging_supply__id=self.value())
        return queryset


class ByProductForOrganizationPackagingFilter(admin.SimpleListFilter):
    title = _('Product')
    parameter_name = 'product'

    def lookups(self, request, model_admin):
        products = Product.objects.all()
        if hasattr(request, 'organization'):
            product_ids = list(
                ProductPackaging.objects.filter(organization=request.organization).values_list('product', flat=True).distinct())
            products = products.filter(id__in=product_ids).order_by('name')
        return [(product.id, product.name) for product in products]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(product__id=self.value())
        return queryset


class ByMarketForOrganizationPackagingFilter(admin.SimpleListFilter):
    title = _('Market')
    parameter_name = 'market'

    def lookups(self, request, model_admin):
        markets = Market.objects.all()
        if hasattr(request, 'organization'):
            market_ids = list(set(ProductPackaging.objects.filter(organization=request.organization).values_list('market', flat=True).distinct()))
            markets = markets.filter(id__in=market_ids).order_by('name')
        return [(market.id, market.name) for market in markets]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(market__id=self.value())
        return queryset


class ByProductKindCountryStandardPackagingForOrganizationPackagingFilter(admin.SimpleListFilter):
    title = _('Country standard packaging')
    parameter_name = 'country_standard_packaging'

    def lookups(self, request, model_admin):
        country_standard_packaging = ProductKindCountryStandardPackaging.objects.all()
        if hasattr(request, 'organization'):
            market_ids = list(set(ProductPackaging.objects.filter(organization=request.organization).values_list('country_standard_packaging', flat=True).distinct()))
            country_standard_packaging = country_standard_packaging.filter(id__in=market_ids).order_by('name')
        return [(country_standard_packaging.id, country_standard_packaging.name) for country_standard_packaging in country_standard_packaging]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(market__id=self.value())
        return queryset


# TODO: remover jul25
class ByProductForOrganizationProductPackagingPalletFilter(admin.SimpleListFilter):
    title = _('Product')
    parameter_name = 'product'

    def lookups(self, request, model_admin):
        products = Product.objects.all()
        if hasattr(request, 'organization'):
            product_ids = list(
                Pallet.objects.filter(organization=request.organization).values_list('product', flat=True).distinct())
            products = products.filter(id__in=product_ids).order_by('name')
        return [(product.id, product.name) for product in products]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(product__id=self.value())
        return queryset



class ByMarketForOrganizationPalletFilter(admin.SimpleListFilter):
    title = _('Market')
    parameter_name = 'markets'

    def lookups(self, request, model_admin):
        markets = Market.objects.none()
        if hasattr(request, 'organization'):
            market_ids = list(Pallet.objects.filter(organization=request.organization).values_list('market', flat=True).distinct())
            markets = Market.objects.filter(id__in=market_ids).order_by('name')
        return [(market.id, market.name) for market in markets]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(market__id=self.value())
        return queryset


class BySupplyForOrganizationPalletFilter(admin.SimpleListFilter):
    title = _('Supply')
    parameter_name = 'supply'

    def lookups(self, request, model_admin):
        supplies = Supply.objects.all()
        if hasattr(request, 'organization'):
            distinct_supplies = list(
                Pallet.objects.filter(organization=request.organization).values_list('supply', flat=True).distinct())
            supplies = supplies.filter(id__in=distinct_supplies).order_by('name')
        return [(supply.id, supply.name) for supply in supplies]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(supply__id=self.value())
        return queryset
