from django.contrib import admin
from cities_light.models import Country, Region, SubRegion, City
from common.profiles.models import UserProfile, OrganizationProfile, PackhouseExporterSetting, PackhouseExporterProfile
from .models import (Product, ProductVariety, Market, ProductHarvestSizeKind, ProductPhenologyKind, ProductMassVolumeKind,
                     Gatherer, PaymentKind, SupplyKind, Supply, ProductPackaging,
                     Provider, Client, CapitalFramework,
                     Maquiladora, WeighingScale, ExportingCompany, CustomsBroker, PalletConfiguration
                     )
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


class ByProductVarietiesForOrganizationFilter(admin.SimpleListFilter):
    title = _('Variety')
    parameter_name = 'product_varieties'

    def lookups(self, request, model_admin):
        product_varietieses = ProductVariety.objects.filter(product__organization=request.organization, is_enabled=True)
        return [(product_variety.id, f"{product_variety.product.name}: {product_variety.name}") for product_variety in product_varietieses]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(product_varieties__id=self.value())
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


class ByMarketsForOrganizationFilter(admin.SimpleListFilter):
    title = _('Market')
    parameter_name = 'markets'

    def lookups(self, request, model_admin):
        marketses = Market.objects.filter(organization=request.organization, is_enabled=True)
        return [(market.id, market.name) for market in marketses]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(markets__id=self.value())
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


class ByClientCapitalFrameworkForOrganizationFilter(admin.SimpleListFilter):
    title = _('Capital framework')
    parameter_name = 'capital_framework'

    def lookups(self, request, model_admin):
        clients_capital_frameworks = list(Client.objects.filter(organization=request.organization, is_enabled=True).values_list('capital_framework', flat=True).distinct())
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
        payment_kinds = PaymentKind.objects.filter(organization=request.organization, is_enabled=True)
        return [(payment_kind.id, payment_kind.name) for payment_kind in payment_kinds]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(payment_kind__id=self.value())
        return queryset


class ByProductHarvestSizeKindForOrganizationFilter(admin.SimpleListFilter):
    title = _('Harvest size kind')
    parameter_name = 'product_harvest_size_kind'

    def lookups(self, request, model_admin):
        product_harvest_size_kinds = ProductHarvestSizeKind.objects.filter(product__organization=request.organization, is_enabled=True)
        return [(product_harvest_size_kind.id, f"{product_harvest_size_kind.product.name}: {product_harvest_size_kind.name}") for product_harvest_size_kind in product_harvest_size_kinds]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(product_harvest_size_kind=self.value())
        return queryset


class ByProductSeasonKindForOrganizationFilter(admin.SimpleListFilter):
    title = _('Phenology')
    parameter_name = 'product_phenology_kind'

    def lookups(self, request, model_admin):
        product_phenology_kinds = ProductPhenologyKind.objects.filter(product__organization=request.organization, is_enabled=True)
        return [(product_phenology_kind.id, f"{product_phenology_kind.product.name}: {product_phenology_kind.name}") for product_phenology_kind in product_phenology_kinds]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(size_kind=self.value())
        return queryset


class ByProductMassVolumeKindForOrganizationFilter(admin.SimpleListFilter):
    title = _('Mass volume Kind')
    parameter_name = 'product_mass_volume_kind'

    def lookups(self, request, model_admin):
        product_mass_volume_kinds = ProductMassVolumeKind.objects.filter(product__organization=request.organization, is_enabled=True)
        return [(product_mass_volume_kind.id, f"{product_mass_volume_kind.product.name}: {product_mass_volume_kind.name}") for product_mass_volume_kind in product_mass_volume_kinds]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(product_mass_volume_kind=self.value())
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
        providers = Provider.objects.filter(organization=request.organization, is_enabled=True, category="service_provider")
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


class BySupplyKindForOrganizationPackagingFilter(admin.SimpleListFilter):
    title = _('Supply Kind')
    parameter_name = 'supply_kind'

    def lookups(self, request, model_admin):
        supply_kinds = SupplyKind.objects.all()
        if hasattr(request, 'organization'):
            main_supply_kind_ids = list(ProductPackaging.objects.filter(organization=request.organization).values_list('main_supply_kind', flat=True).distinct())
            supply_kinds = supply_kinds.filter(id__in=main_supply_kind_ids)
        return [(supply_kind.id, supply_kind.name) for supply_kind in supply_kinds]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(supply_kind__id=self.value())
        return queryset


class BySupplyForOrganizationPackagingFilter(admin.SimpleListFilter):
    title = _('Supply')
    parameter_name = 'supply'

    def lookups(self, request, model_admin):
        supplies = Supply.objects.all()
        if hasattr(request, 'organization'):
            supply_ids = list(ProductPackaging.objects.filter(organization=request.organization).values_list('main_supply', flat=True).distinct())
            supplies = supplies.filter(id__in=supply_ids)
        return [(supply.id, supply.name) for supply in supplies]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(supply__id=self.value())
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
            market_ids = list(set(ProductPackaging.objects.filter(organization=request.organization).values_list('markets', flat=True).distinct()))
            markets = markets.filter(id__in=market_ids).order_by('name')
        return [(market.id, market.name) for market in markets]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(market__id=self.value())
        return queryset



class ByProductForOrganizationPalletConfigurationFilter(admin.SimpleListFilter):
    title = _('Product')
    parameter_name = 'product'

    def lookups(self, request, model_admin):
        products = Product.objects.all()
        if hasattr(request, 'organization'):
            product_ids = list(
                PalletConfiguration.objects.filter(organization=request.organization).values_list('product', flat=True).distinct())
            products = products.filter(id__in=product_ids).order_by('name')
        return [(product.id, product.name) for product in products]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(product__id=self.value())
        return queryset

class ByMarketForOrganizationPalletConfigurationFilter(admin.SimpleListFilter):
    title = _('Market')
    parameter_name = 'market'

    def lookups(self, request, model_admin):
        markets = Market.objects.all()
        if hasattr(request, 'organization'):
            market_ids = list(
                PalletConfiguration.objects.filter(organization=request.organization).values_list('market', flat=True).distinct())
            markets = markets.filter(id__in=market_ids).order_by('name')
        return [(market.id, market.name) for market in markets]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(market__id=self.value())
        return queryset


class ByProductVarietyForOrganizationPalletConfigurationFilter(admin.SimpleListFilter):
    title = _('Product Variety')
    parameter_name = 'product_variety'

    def lookups(self, request, model_admin):
        product_varieties = ProductVariety.objects.all()
        if hasattr(request, 'organization'):
            product_varieties_ids = list(
                PalletConfiguration.objects.filter(organization=request.organization).values_list('product_variety', flat=True).distinct())
            product_varieties = product_varieties.filter(id__in=product_varieties_ids).order_by('name')
        return [(product_variety.id, product_variety.name) for product_variety in product_varieties]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(market__id=self.value())
        return queryset
