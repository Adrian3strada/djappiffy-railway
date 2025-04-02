from django.contrib import admin
from django import forms
from common.billing.models import LegalEntityCategory
from .models import (
    Market, Product, ProductMarketClass, ProductVariety, ProductSize,
    ProductHarvestSizeKind, ProductMarketMeasureUnitManagementCost,
    ProductPhenologyKind, ProductMassVolumeKind,
    PaymentKind, Vehicle, Gatherer, Client, ClientShippingAddress, Maquiladora,
    Orchard, OrchardCertification, CrewChief, HarvestingCrew,
    HarvestingPaymentSetting, Supply, ProductKindCountryStandardPackaging,
    Service, ProductPresentation, Packaging, ProductPackaging, ProductPackagingPallet,
    WeighingScale, ColdChamber,
    Pallet, PalletComplementarySupply,
    ExportingCompany, Transfer, LocalTransporter, ProductPresentationComplementarySupply,
    BorderToDestinationTransporter, CustomsBroker, Vessel, Airline, InsuranceCompany,
    PackagingComplementarySupply, ProductRipeness, ProductPackagingPresentation,
    Provider, ProviderBeneficiary, ProviderFinancialBalance, ExportingCompanyBeneficiary, 
    ProductPest, ProductDisease, ProductPhysicalDamage, ProductResidue, ProductFoodSafetyProcess
)

from packhouses.packhouse_settings.models import (Bank, VehicleOwnershipKind, VehicleFuelKind, VehicleKind,
                                                  VehicleBrand, OrchardCertificationKind, OrchardCertificationVerifier
                                                  )
from common.base.models import Pest, Disease
from common.profiles.models import UserProfile, PackhouseExporterProfile, OrganizationProfile
from .forms import (ProductVarietyInlineFormSet, ProductHarvestSizeKindInlineFormSet,
                    ProductSeasonKindInlineFormSet, ProductMassVolumeKindInlineFormSet,
                    OrchardCertificationForm, HarvestingCrewForm, HarvestingPaymentSettingInlineFormSet,
                    PackagingKindForm, ProviderForm)
from django_ckeditor_5.widgets import CKEditor5Widget
from organizations.models import Organization
from cities_light.models import Country, Region, SubRegion, City
import nested_admin
from django.utils.translation import gettext_lazy as _
from .filters import (StatesForOrganizationCountryFilter, ByCountryForOrganizationMarketsFilter,
                      ByProductForOrganizationFilter, ByProductSeasonKindForOrganizationFilter,
                      ByProductSizeForProductOrganizationFilter, ByPackagingForOrganizationFilter,
                      ByProductVarietyForOrganizationFilter, ByMarketForOrganizationFilter,
                      ByStateForOrganizationGathererFilter, ByCityForOrganizationGathererFilter,
                      ByClientCapitalFrameworkForOrganizationFilter, BySupplyKindForPackagingFilter,
                      BySupplyForOrganizationPackagingFilter, ByProductForOrganizationPackagingFilter,
                      ByMarketForOrganizationPackagingFilter,
                      ByStateForOrganizationFilter, ByCityForOrganizationFilter, ByDistrictForOrganizationFilter,
                      ByCountryForOrganizationClientsFilter, ByStateForOrganizationClientsFilter,
                      ByCityForOrganizationClientsFilter, ByPaymentKindForOrganizationFilter,
                      ByProductVarietiesForOrganizationFilter, ByMarketForOrganizationFilter,
                      ByProductMassVolumeKindForOrganizationFilter, ByProductHarvestSizeKindForOrganizationFilter,
                      ProductKindForPackagingFilter, ByCountryForOrganizationProvidersFilter,
                      ByStateForOrganizationProvidersFilter, ByCityForOrganizationProvidersFilter,
                      ByStateForOrganizationMaquiladoraFilter, ByCityForOrganizationMaquiladoraFilter,
                      ByServiceProviderForOrganizationServiceFilter, ByStateForOrganizationWeighingScaleFilter,
                      ByCityForOrganizationWeighingScaleFilter, ByCountryForOrganizationExportingCompaniesFilter,
                      ByStateForOrganizationExportingCompaniesFilter, ByCityForOrganizationExportingCompaniesFilter,
                      ByCountryForOrganizationCustomsBrokersFilter, ByProductForOrganizationProductPackagingPalletFilter,
                      ByMarketForOrganizationPalletFilter,
                      BySupplyForOrganizationPalletFilter,
                      )
from common.utils import is_instance_used
from adminsortable2.admin import SortableAdminMixin, SortableStackedInline, SortableTabularInline, SortableAdminBase
from common.base.models import (ProductKind, ProductKindCountryStandardSize, CapitalFramework, SupplyKind,
                                ProductKindCountryStandard)
from common.base.decorators import uppercase_formset_charfield, uppercase_alphanumeric_formset_charfield
from common.base.decorators import uppercase_form_charfield, uppercase_alphanumeric_form_charfield
from common.base.mixins import ByOrganizationAdminMixin, ByProductForOrganizationAdminMixin, \
    DisableInlineRelatedLinksMixin
from common.forms import SelectWidgetWithData
from django.db.models import Q, F, Max, Min
from common.base.utils import ReportExportAdminMixin, SheetExportAdminMixin, SheetReportExportAdminMixin
from .views import basic_report
from .resources import (ProductResource, MarketResource, ProductSizeResource, ProviderResource, ClientResource,
                        VehicleResource, GathererResource,
                        MaquiladoraResource, OrchardResource, HarvestingCrewResource, SupplyResource, PackagingResource,
                        ServiceResource, WeighingScaleResource,
                        ColdChamberResource, PalletResource,
                        ExportingCompanyResource, TransferResource, LocalTransporterResource,
                        BorderToDestinationTransporterResource, CustomsBrokerResource, VesselResource, AirlineResource,
                        InsuranceCompanyResource, )

admin.site.unregister(Country)
admin.site.unregister(Region)
admin.site.unregister(SubRegion)
admin.site.unregister(City)

from cities_light.admin import CityAdmin


# @admin.register(City)
class CityAdmin(CityAdmin):
    verbose_name = _('District')
    verbose_name_plural = _('Districts')

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.id <= 144812:
            return [field.name for field in self.model._meta.fields]
        return super().get_readonly_fields(request, obj)


# Markets

@admin.register(Market)
class MarketAdmin(SheetReportExportAdminMixin, ByOrganizationAdminMixin):
    report_function = staticmethod(basic_report)
    resource_classes = [MarketResource]
    list_display = ('name', 'alias', 'get_countries', 'is_mixable', 'is_enabled')
    list_filter = (ByCountryForOrganizationMarketsFilter, 'is_mixable', 'is_enabled',)
    search_fields = ('name', 'alias')
    fields = ('name', 'alias', 'countries', 'is_mixable',
              'label_language', 'address_label', 'is_enabled')

    def get_countries(self, obj):
        return ", ".join([m.name for m in obj.countries.all()])

    get_countries.short_description = _('countries')

    @uppercase_form_charfield('name')
    @uppercase_alphanumeric_form_charfield('alias')
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['address_label'].widget = CKEditor5Widget()
        return form

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj and is_instance_used(obj, exclude=[Country, Organization]):
            readonly_fields.extend(['name', 'alias', 'countries', 'organization'])
        return readonly_fields

    def save_model(self, request, obj, form, change):
        if 'address_label' in form.cleaned_data and form.cleaned_data['address_label'] == '<p>&nbsp;</p>':
            obj.address_label = None
        super().save_model(request, obj, form, change)


# /Markets


# Products


class ProductMarketMeasureUnitManagementCostInline(admin.TabularInline):
    model = ProductMarketMeasureUnitManagementCost
    extra = 0
    fields = ('market', 'measure_unit_management_cost', 'is_enabled')
    verbose_name = _('Management cost')
    verbose_name_plural = _('Management costs')

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        return formset

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        parent_object_id = request.resolver_match.kwargs.get("object_id")
        parent_obj = Product.objects.get(id=parent_object_id) if parent_object_id else None

        organization = request.organization if hasattr(request, 'organization') else None
        organization_queryfilter = {'organization': organization, 'is_enabled': True}

        if db_field.name == "market":
            queryset = Market.objects.none()
            if organization:
                queryset = Market.objects.filter(**organization_queryfilter)
                print("queryset", queryset)
            if parent_obj:
                product_markets = list(parent_obj.markets.all().values_list('id', flat=True))
                print("product_markets", product_markets)
                queryset = queryset.filter(id__in=product_markets)
            kwargs["queryset"] = queryset

        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class ProductMarketClassInline(admin.TabularInline):
    model = ProductMarketClass
    extra = 0
    fields = ('market', 'name', 'is_enabled')
    verbose_name = _('Class')
    verbose_name_plural = _('Classes')

    @uppercase_formset_charfield('name')
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        return formset

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        parent_object_id = request.resolver_match.kwargs.get("object_id")
        parent_obj = Product.objects.get(id=parent_object_id) if parent_object_id else None

        organization = request.organization if hasattr(request, 'organization') else None
        organization_queryfilter = {'organization': organization, 'is_enabled': True}

        if db_field.name == "market":
            queryset = Market.objects.none()
            if organization:
                queryset = Market.objects.filter(**organization_queryfilter)
                print("queryset", queryset)
            if parent_obj:
                product_markets = list(parent_obj.markets.all().values_list('id', flat=True))
                print("product_markets", product_markets)
                queryset = queryset.filter(id__in=product_markets)
            kwargs["queryset"] = queryset

        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class ProductVarietyInline(admin.TabularInline):
    model = ProductVariety
    extra = 0
    fields = ('name', 'alias', 'description', 'is_enabled')
    verbose_name = _('Variety')
    verbose_name_plural = _('Varieties')

    @uppercase_formset_charfield('name')
    @uppercase_alphanumeric_formset_charfield('alias')
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        return formset


class ProductPhenologyKindInline(admin.TabularInline):
    model = ProductPhenologyKind
    extra = 0
    fields = ('name', 'is_enabled', 'sort_order')
    ordering = ['sort_order', 'name']
    verbose_name = _('Phenology')
    verbose_name_plural = _('Phenologies')

    # formset = ProductSeasonKindInlineFormSet

    @uppercase_formset_charfield('name')
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        return formset


class ProductHarvestSizeKindInline(admin.TabularInline):
    model = ProductHarvestSizeKind
    extra = 0
    fields = ('name', 'product', 'is_enabled', 'sort_order')
    ordering = ['sort_order', '-name']
    verbose_name = _('Harvest size')
    verbose_name_plural = _('Harvest sizes')

    # formset = ProductHarvestSizeKindInlineFormSet

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        return formset


class ProductMassVolumeKindInline(admin.TabularInline):
    model = ProductMassVolumeKind
    extra = 0
    fields = ('name', 'is_enabled', 'sort_order')
    ordering = ['sort_order', '-name']
    verbose_name = _('Mass volume')
    verbose_name_plural = _('Mass volumes')

    # formset = ProductMassVolumeKindInlineFormSet

    @uppercase_formset_charfield('name')
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        return formset


class ProductRipenessInline(admin.TabularInline):
    model = ProductRipeness
    extra = 0
    verbose_name = _('Ripeness')
    verbose_name_plural = _('Ripeness')

    @uppercase_formset_charfield('name')
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        return formset

class ProductPestInline(admin.TabularInline):
    model = ProductPest
    extra = 1
    verbose_name = _('Pest')
    verbose_name_plural = _('Pest')

    can_delete = True
    show_change_link = True
    raw_id_fields = ['pest']

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        return formset

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "pest":
            product_id = request.resolver_match.kwargs.get("object_id")

            if product_id:
                try:
                    product = Product.objects.get(pk=product_id)
                    
                    kwargs['queryset'] = Pest.objects.filter(
                        pestproductkind__product_kind=product.kind
                    ).distinct()
                except Product.DoesNotExist:
                    kwargs['queryset'] = Pest.objects.none()
            else:
                kwargs['queryset'] = Pest.objects.none()

            kwargs['widget'] = forms.Select(choices=kwargs['queryset'].values_list('id', 'name'))

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class ProductDiseaseInline(admin.TabularInline):
    model = ProductDisease
    extra = 0
    verbose_name = _('Disease')
    verbose_name_plural = _('Diseases')

    can_delete = True
    show_change_link = False 
    # raw_id_fields = ['disease']

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        return formset

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "disease":
            product_id = request.resolver_match.kwargs.get("object_id")
            print(product_id)

            if product_id:
                try:
                    product = Product.objects.get(pk=product_id)
                    
                    kwargs["queryset"] = Disease.objects.filter(
                        diseaseproductkind__product_kind=product.kind
                    ).distinct()
                except Product.DoesNotExist:
                    kwargs["queryset"] = Disease.objects.none()
            else:
                kwargs["queryset"] = Disease.objects.none()

            kwargs['widget'] = forms.Select(choices=kwargs['queryset'].values_list('id', 'name'))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class ProductPhysicalDamageInline(admin.TabularInline):
    model = ProductPhysicalDamage
    extra = 1
    verbose_name = _('Physical Damage')
    verbose_name_plural = _('Physical Damages')

class ProductResidueInline(admin.TabularInline):
    model = ProductResidue
    extra = 1
    verbose_name = _('Residue')
    verbose_name_plural = _('Residues')

class ProductFoodSafetyProcessInline(admin.TabularInline):
    model = ProductFoodSafetyProcess
    extra = 1
    verbose_name = _('Food Safety Process')
    verbose_name_plural = _('Food Safety Process')

@admin.register(Product)
class ProductAdmin(SheetReportExportAdminMixin, ByOrganizationAdminMixin):
    report_function = staticmethod(basic_report)
    resource_classes = [ProductResource]
    list_display = ('name', 'kind', 'is_enabled')
    list_filter = (ProductKindForPackagingFilter, 'price_measure_unit_category', ByMarketForOrganizationFilter, 'is_enabled',)
    search_fields = ('name', 'kind__name', 'description')
    fields = ('kind', 'name', 'description', 'price_measure_unit_category', 'markets', 'is_enabled')
    inlines = [
               ProductMarketMeasureUnitManagementCostInline, ProductMarketClassInline,
               ProductVarietyInline,
               ProductPhenologyKindInline, ProductHarvestSizeKindInline,
               ProductMassVolumeKindInline, ProductRipenessInline,
               ProductPestInline,
               ProductDiseaseInline, 
               ProductPhysicalDamageInline, 
               ProductResidueInline,
               ProductFoodSafetyProcessInline
               ]

    @uppercase_form_charfield('name')
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'kind' in form.base_fields:
            form.base_fields['kind'].widget.can_add_related = False
            form.base_fields['kind'].widget.can_change_related = False
            form.base_fields['kind'].widget.can_delete_related = False
            form.base_fields['kind'].widget.can_view_related = False
        return form

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj and is_instance_used(obj, exclude=[ProductKind, Market, Organization,
                                                  ProductMarketMeasureUnitManagementCost, ProductMarketClass,
                                                  ProductVariety, ProductPhenologyKind, ProductHarvestSizeKind,
                                                  ProductMassVolumeKind, ProductRipeness]):
            readonly_fields.extend(['kind', 'name', 'price_measure_unit_category', 'markets', 'organization'])
        return readonly_fields

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        organization = request.organization if hasattr(request, 'organization') else None
        organization_queryfilter = {'organization': organization, 'is_enabled': True}

        if db_field.name == "markets":
            kwargs["queryset"] = Market.objects.filter(**organization_queryfilter)

        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "kind":
            product_kinds = ProductKind.objects.filter(for_packaging=True, is_enabled=True)
            kwargs["queryset"] = product_kinds
            if hasattr(request, 'organization'):
                packhouse_exporter_profile = PackhouseExporterProfile.objects.get(organization=request.organization)
                kwargs["queryset"] = packhouse_exporter_profile.packhouseexportersetting.product_kinds.filter(
                    is_enabled=True)
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            return formfield
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    class Media:
        js = ('js/admin/forms/select.js',)


@admin.register(ProductSize)
class ProductSizeAdmin(SortableAdminMixin, ByProductForOrganizationAdminMixin):
    report_function = staticmethod(basic_report)
    resource_classes = [ProductSizeResource]
    list_display = (
        'name', 'alias', 'product', 'get_varieties', 'market', 'is_enabled', 'sort_order')
    list_filter = (
        ByProductForOrganizationFilter, ByProductVarietiesForOrganizationFilter, ByMarketForOrganizationFilter,
        'is_enabled'
    )
    search_fields = ('name', 'alias')
    ordering = ['sort_order']

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        return super().changelist_view(request, extra_context=extra_context)

    def get_varieties(self, obj):
        return ", ".join([m.name for m in obj.varieties.all()])

    get_varieties.admin_order_field = 'varieties__name'
    get_varieties.short_description = _('varieties')

    @uppercase_form_charfield('name')
    @uppercase_alphanumeric_form_charfield('alias')
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return form

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        object_id = request.resolver_match.kwargs.get("object_id")
        obj = ProductSize.objects.get(id=object_id) if object_id else None

        organization = request.organization if hasattr(request, 'organization') else None
        organization_queryfilter = {'organization': organization, 'is_enabled': True}

        if db_field.name == "product":
            kwargs["queryset"] = Product.objects.filter(**organization_queryfilter)

        if db_field.name == "market":
            kwargs["queryset"] = Market.objects.filter(**organization_queryfilter)

        if db_field.name == "standard_size":
            if request.POST:
                product_id = request.POST.get('product')
                market_id = request.POST.get('market')
            else:
                product_id = obj.product_id if obj else None
                market_id = obj.market_id if obj else None
            if product_id and market_id:
                market = Market.objects.get(id=market_id)
                product = Product.objects.get(id=product_id)
                queryset = ProductKindCountryStandardSize.objects.filter(standard__product_kind=product.kind,
                                                                         standard__country_id__in=market.countries.all(),
                                                                         is_enabled=True)
                kwargs["queryset"] = queryset
                formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
                formfield.required = queryset.exists()
                standards = queryset.values_list('standard', flat=True).distinct()
                if market.countries.all().count() > 1:
                    formfield.label_from_instance = lambda item: f"{item.standard.country.name}: {item.name}" + (
                        f"({item.standard.name})" if standards.count() > 1 else "")
                else:
                    formfield.label_from_instance = lambda item: f"{item.name}" + (
                        f"({item.standard.name})" if standards.count() > 1 else "")
                return formfield
            else:
                queryset = ProductKindCountryStandardSize.objects.none()
                kwargs["queryset"] = queryset
                formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
                formfield.required = queryset.exists()
                return formfield

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        object_id = request.resolver_match.kwargs.get("object_id")
        obj = ProductSize.objects.get(id=object_id) if object_id else None

        organization = request.organization if hasattr(request, 'organization') else None
        organization_queryfilter = {'organization': organization, 'is_enabled': True}

        if db_field.name == "varieties":
            if request.POST:
                product_id = request.POST.get('product')
            else:
                product_id = obj.product_id if obj else None
            if product_id:
                kwargs["queryset"] = ProductVariety.objects.filter(product_id=product_id, is_enabled=True)
            else:
                kwargs["queryset"] = ProductVariety.objects.none()

        return super().formfield_for_manytomany(db_field, request, **kwargs)

    class Media:
        js = ('js/admin/forms/packhouses/catalogs/product_size.js',)


class ClientShipAddressInline(admin.StackedInline):
    model = ClientShippingAddress
    extra = 0

    @uppercase_formset_charfield('neighborhood')
    @uppercase_formset_charfield('address')
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        formset.form.base_fields['country'].initial = obj.country if obj and obj.country else None
        return formset

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        parent_object_id = request.resolver_match.kwargs.get("object_id")
        parent_obj = Client.objects.get(id=parent_object_id) if parent_object_id else None
        markets_countries = None

        if request.POST:
            market_id = request.POST.get('market')
        else:
            market_id = parent_obj.market_id if parent_obj else None
        if market_id:
            markets_countries = list(Market.objects.get(id=market_id).countries.all().values_list('id', flat=True))

        if db_field.name == "country":
            if markets_countries:
                kwargs["queryset"] = Country.objects.filter(id__in=markets_countries)
            else:
                kwargs["queryset"] = Country.objects.none()
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda item: item.name
            return formfield

        if db_field.name == "state":
            if markets_countries:
                kwargs["queryset"] = Region.objects.filter(country_id__in=markets_countries)
            else:
                kwargs["queryset"] = Region.objects.none()
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda item: item.name
            return formfield

        if db_field.name == "city":
            if markets_countries:
                kwargs["queryset"] = SubRegion.objects.filter(country_id__in=markets_countries)
            else:
                kwargs["queryset"] = SubRegion.objects.none()
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda item: item.name
            return formfield

        if db_field.name == "district":
            if markets_countries:
                kwargs["queryset"] = City.objects.filter(country_id__in=markets_countries)
            else:
                kwargs["queryset"] = City.objects.none()
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda item: item.name
            return formfield

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    class Media:
        js = ('js/admin/forms/packhouses/catalogs/client_shipping_address_inline.js',)


@admin.register(Client)
class ClientAdmin(SheetReportExportAdminMixin, ByOrganizationAdminMixin):
    report_function = staticmethod(basic_report)
    resource_classes = [ClientResource]
    list_display = (
    'name', 'category', 'tax_id', 'market', 'country_display', 'state_display', 'city_display', 'neighborhood',
    'tax_id', 'contact_phone_number', 'is_enabled')
    list_filter = (ByMarketForOrganizationFilter, 'category', ByCountryForOrganizationClientsFilter,
                   ByStateForOrganizationClientsFilter,
                   ByCityForOrganizationClientsFilter, ByClientCapitalFrameworkForOrganizationFilter,
                   ByPaymentKindForOrganizationFilter, 'is_enabled')
    search_fields = ('name', 'tax_id', 'contact_phone_number')
    fields = (
        'name', 'category', 'market', 'country', 'state', 'city', 'district', 'postal_code', 'neighborhood', 'address',
        'external_number', 'internal_number', 'shipping_address', 'capital_framework',
        'tax_id', 'payment_kind', 'max_money_credit_limit', 'max_days_credit_limit', 'fda', 'swift', 'aba', 'clabe',
        'bank', 'contact_name', 'contact_email', 'contact_phone_number', 'is_enabled')
    inlines = [ClientShipAddressInline]

    def country_display(self, obj):
        return obj.country.name

    country_display.short_description = _('Country')
    country_display.admin_order_field = 'country__name'

    def state_display(self, obj):
        return obj.state.name

    state_display.short_description = _('State')
    state_display.admin_order_field = 'state__name'

    def city_display(self, obj):
        return obj.city.name

    city_display.short_description = _('City')
    city_display.admin_order_field = 'city__name'

    @uppercase_form_charfield('name')
    @uppercase_form_charfield('neighborhood')
    @uppercase_form_charfield('address')
    @uppercase_form_charfield('contact_name')
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        if 'capital_framework' in form.base_fields:
            form.base_fields['capital_framework'].widget.can_add_related = False
            form.base_fields['capital_framework'].widget.can_change_related = False
            form.base_fields['capital_framework'].widget.can_delete_related = False
            form.base_fields['capital_framework'].widget.can_view_related = False

        return form

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj and is_instance_used(obj, exclude=[Market, Country, Region, SubRegion, City, LegalEntityCategory, Bank,
                                                  PaymentKind,
                                                  Organization, ClientShippingAddress]):
            readonly_fields.extend(['name', 'organization'])
        return readonly_fields

    def formfield_for_foreignkey(self, db_field, request, **kwargs):

        organization = getattr(request, 'organization', None)
        object_id = request.resolver_match.kwargs.get("object_id")
        obj = Client.objects.get(id=object_id) if object_id else None
        queryset_organization_filter = {"organization": organization, "is_enabled": True}

        if db_field.name == "market":
            kwargs["queryset"] = Market.objects.filter(**queryset_organization_filter)

        if db_field.name == "country":
            if request.POST:
                market_id = request.POST.get('market')
            else:
                market_id = obj.market_id if obj else None
            if market_id:
                countries = list(Market.objects.get(id=market_id).countries.all().values_list('id', flat=True))
                kwargs["queryset"] = Country.objects.filter(id__in=countries)
            else:
                kwargs["queryset"] = Country.objects.none()
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda item: item.name
            return formfield

        if db_field.name == "state":
            if request.POST:
                country_id = request.POST.get('country')
            else:
                country_id = obj.country_id if obj else None
            if country_id:
                kwargs["queryset"] = Region.objects.filter(country_id=country_id)
            else:
                kwargs["queryset"] = Region.objects.none()
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda item: item.name
            return formfield

        if db_field.name == "city":
            if request.POST:
                state_id = request.POST.get('state')
            else:
                state_id = obj.state_id if obj else None
            if state_id:
                kwargs["queryset"] = SubRegion.objects.filter(region_id=state_id)
            else:
                kwargs["queryset"] = SubRegion.objects.none()
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda item: item.name
            return formfield

        if db_field.name == "district":
            if request.POST:
                city_id = request.POST.get('city')
            else:
                city_id = obj.city_id if obj else None
            if city_id:
                kwargs["queryset"] = City.objects.filter(subregion_id=city_id)
            else:
                kwargs["queryset"] = City.objects.none()
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda item: item.name
            return formfield

        if db_field.name == "shipping_address":
            # TODO: filtrar solo las direcciones de envío del cliente
            kwargs["queryset"] = ClientShippingAddress.objects.filter(client=obj, is_enabled=True)

        if db_field.name == "capital_framework":
            if request.POST:
                country_id = request.POST.get('country')
            else:
                country_id = obj.country_id if obj else None
            if country_id:
                print("country_id", country_id)
                kwargs["queryset"] = CapitalFramework.objects.filter(country_id=country_id)
                print("queryset", kwargs["queryset"])
                formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
                """
                if len(kwargs["queryset"]) > 0:
                    formfield.required = True
                else:
                    formfield.required = False
                """
                formfield.label_from_instance = lambda item: item.code
                return formfield
            else:
                kwargs["queryset"] = CapitalFramework.objects.none()

        if db_field.name == "bank":
            kwargs["queryset"] = Bank.objects.filter(organization=organization, is_enabled=True)

        if db_field.name == "payment_kind":
            kwargs["queryset"] = PaymentKind.objects.filter(organization=organization, is_enabled=True)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    class Media:
        js = (
            'js/admin/forms/packhouses/catalogs/client.js',
        )


@admin.register(Gatherer)
class GathererAdmin(SheetReportExportAdminMixin, ByOrganizationAdminMixin):
    report_function = staticmethod(basic_report)
    resource_classes = [GathererResource]
    list_display = (
        'name', 'zone', 'tax_registry_code', 'state', 'city', 'postal_code', 'address', 'email', 'phone_number',
        'vehicle',
        'is_enabled')
    list_filter = (ByStateForOrganizationGathererFilter, ByCityForOrganizationGathererFilter, 'is_enabled')
    search_fields = ('name', 'zone', 'tax_registry_code', 'address', 'email', 'phone_number')
    fields = (
        'name', 'zone', 'tax_registry_code', 'population_registry_code', 'social_number_code', 'state', 'city',
        'district',
        'neighborhood', 'postal_code', 'address', 'external_number', 'internal_number', 'email', 'phone_number',
        'vehicle',
        'is_enabled')

    @uppercase_form_charfield('name')
    @uppercase_form_charfield('zone')
    @uppercase_form_charfield('address')
    @uppercase_form_charfield('neighborhood')
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return form

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj and is_instance_used(obj, exclude=[Region, Vehicle, City, Organization]):
            readonly_fields.extend(['name', 'organization'])
        return readonly_fields

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        object_id = request.resolver_match.kwargs.get("object_id")
        obj = Gatherer.objects.get(id=object_id) if object_id else None

        organization = None
        if hasattr(request, 'organization'):
            organization = request.organization
        organization_country = PackhouseExporterProfile.objects.get(
            organization=organization).country if organization else None

        field_mapping = {
            "state": (Region, "country", organization_country),
            "city": (SubRegion, "region", request.POST.get('state') if request.POST else obj.state.id if obj else None),
            "district": (City, "subregion", request.POST.get('city') if request.POST else obj.city.id if obj else None),
            "vehicle": (Vehicle, "category", 'packhouse')
        }

        if db_field.name in field_mapping:
            Model, filter_field, filter_value = field_mapping[db_field.name]
            if db_field.name == "vehicle":
                kwargs["queryset"] = Model.objects.filter(category=filter_value, organization=organization,
                                                          is_enabled=True)
            else:
                kwargs["queryset"] = Model.objects.filter(
                    **{f"{filter_field}_id": filter_value}) if filter_value else Model.objects.none()

        formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
        formfield.label_from_instance = lambda item: item.name
        return formfield

    class Media:
        js = (
            'js/admin/forms/common/state-city-district.js',
            'js/admin/forms/packhouses/catalogs/gatherer.js',
        )


@admin.register(Maquiladora)
class MaquiladoraAdmin(SheetReportExportAdminMixin, ByOrganizationAdminMixin):
    report_function = staticmethod(basic_report)
    resource_classes = [MaquiladoraResource]
    list_display = (
        'name', 'zone', 'tax_id', 'get_state_name', 'get_city_name', 'email', 'phone_number', 'is_enabled',)
    list_filter = (ByStateForOrganizationMaquiladoraFilter, ByCityForOrganizationMaquiladoraFilter, 'is_enabled')
    search_fields = ('name', 'zone', 'tax_id', 'address', 'email', 'phone_number')
    fields = (
        'name', 'zone', 'tax_id', 'state', 'city', 'district', 'postal_code',
        'neighborhood', 'address', 'external_number', 'internal_number', 'email', 'phone_number',
        'clients', 'is_enabled',)

    def get_state_name(self, obj):
        return obj.state.name

    get_state_name.short_description = _('State')
    get_state_name.admin_order_field = 'state__name'

    def get_city_name(self, obj):
        return obj.city.name

    get_city_name.short_description = _('City')
    get_city_name.admin_order_field = 'city__name'

    @uppercase_form_charfield('name')
    @uppercase_form_charfield('tax_registry_code')
    @uppercase_form_charfield('population_registry_code')
    @uppercase_form_charfield('social_number_code')
    @uppercase_form_charfield('zone')
    @uppercase_form_charfield('address')
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['clients'].widget.can_add_related = False
        return form

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj and is_instance_used(obj, exclude=[Region, City, Vehicle, Organization]):
            readonly_fields.extend(['name', 'organization'])
        return readonly_fields

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        organization = getattr(request, 'organization', None)
        obj_id = request.resolver_match.kwargs.get("object_id")
        obj = Maquiladora.objects.get(id=obj_id) if obj_id else None
        queryset_organization_filter = {"organization": organization, "is_enabled": True}

        if db_field.name == "state":
            if hasattr(request, 'organization'):
                packhouse_profile = PackhouseExporterProfile.objects.get(organization=request.organization)
                if packhouse_profile:
                    kwargs["queryset"] = Region.objects.filter(country=packhouse_profile.country)
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda item: item.name
            return formfield

        if db_field.name == "city":
            if request.POST:
                state_id = request.POST.get('state')
            else:
                state_id = obj.state_id if obj else None
            if state_id:
                kwargs["queryset"] = SubRegion.objects.filter(region_id=state_id)
            else:
                kwargs["queryset"] = SubRegion.objects.none()
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda item: item.name
            return formfield

        if db_field.name == "district":
            if request.POST:
                city_id = request.POST.get('city')
            else:
                city_id = obj.city_id if obj else None
            if city_id:
                kwargs["queryset"] = City.objects.filter(subregion_id=city_id)
            else:
                kwargs["queryset"] = City.objects.none()
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda item: item.name
            return formfield

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        obj_id = request.resolver_match.kwargs.get("object_id")
        obj = Maquiladora.objects.get(id=obj_id) if obj_id else None

        if db_field.name == "clients":
            if hasattr(request, 'organization'):
                # kwargs["queryset"] = Client.objects.filter(Q(organization=request.organization, is_enabled=True, category="maquiladora") & (Q(maquiladora__isnull=True) | Q(maquiladora=obj)))
                kwargs["queryset"] = Client.objects.filter(Q(organization=request.organization, is_enabled=True, category="maquiladora"))
            else:
                kwargs["queryset"] = Client.objects.none()
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            return formfield

    class Media:
        js = ('js/admin/forms/packhouses/catalogs/maquiladora.js',)


class OrchardCertificationInline(admin.StackedInline):
    model = OrchardCertification
    form = OrchardCertificationForm
    extra = 0

    @uppercase_formset_charfield('extra_code')
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        return formset

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        parent_object_id = request.resolver_match.kwargs.get("object_id")
        parent_obj = Orchard.objects.get(id=parent_object_id) if parent_object_id else None

        organization = None
        if hasattr(request, 'organization'):
            organization = request.organization

        if db_field.name == "certification_kind":
            kwargs["queryset"] = OrchardCertificationKind.objects.filter(organization=organization, is_enabled=True)

        if db_field.name == "verifier":
            kwargs["queryset"] = OrchardCertificationVerifier.objects.filter(organization=organization, is_enabled=True)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    class Media:
        js = ('js/admin/forms/packhouses/catalogs/orchard_certification_inline.js',)


@admin.register(Orchard)
class OrchardAdmin(SheetReportExportAdminMixin, ByOrganizationAdminMixin):
    report_function = staticmethod(basic_report)
    resource_classes = [OrchardResource]
    list_display = ('name', 'code', 'producer', 'get_category', 'is_enabled')
    list_filter = ('category', 'safety_authority_registration_date', 'is_enabled')
    search_fields = ('name', 'code', 'producer__name')
    fields = ('name', 'code', 'category', 'product', 'producer', 'safety_authority_registration_date', 'state', 'city',
              'district', 'ha',
              'sanitary_certificate', 'is_enabled')
    inlines = [OrchardCertificationInline]

    def get_category(self, obj):
        return obj.get_category_display()

    get_category.short_description = _('Category')
    get_category.ordering = 'category'

    @uppercase_form_charfield('name')
    @uppercase_alphanumeric_form_charfield('code')
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['producer'].widget.can_add_related = False
        form.base_fields['producer'].widget.can_change_related = False
        form.base_fields['producer'].widget.can_delete_related = False
        form.base_fields['producer'].widget.can_view_related = False
        return form

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj and is_instance_used(obj, exclude=[Provider, Region, SubRegion, City,
                                                  Organization, OrchardCertification]):
            readonly_fields.extend(['name', 'organization'])
        return readonly_fields

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "product":
            organization = request.organization if hasattr(request, 'organization') else None
            if organization:
                kwargs["queryset"] = Product.objects.filter(organization=organization, is_enabled=True)
            else:
                kwargs["queryset"] = Product.objects.none()
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        object_id = request.resolver_match.kwargs.get("object_id")
        obj = Orchard.objects.get(id=object_id) if object_id else None

        organization = None
        if hasattr(request, 'organization'):
            organization = request.organization
        organization_country = PackhouseExporterProfile.objects.get(
            organization=organization).country if organization else None

        field_mapping = {
            "state": (Region, "country", organization_country),
            "city": (SubRegion, "region", request.POST.get('state') if request.POST else obj.state.id if obj else None),
            "district": (City, "subregion", request.POST.get('city') if request.POST else obj.city.id if obj else None),
            "producer": (Provider, "category", 'product_producer'),
        }

        if db_field.name in field_mapping:
            Model, filter_field, filter_value = field_mapping[db_field.name]
            if db_field.name == "producer":
                kwargs["queryset"] = Model.objects.filter(**{f"{filter_field}": filter_value},
                                                          organization=organization, is_enabled=True)
            else:
                kwargs["queryset"] = Model.objects.filter(
                    **{f"{filter_field}_id": filter_value}) if filter_value else Model.objects.none()

        formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
        formfield.label_from_instance = lambda item: item.name
        return formfield

    class Media:
        js = ('js/admin/forms/common/state-city-district.js',)


@admin.register(Supply)
class SupplyAdmin(SheetReportExportAdminMixin, ByOrganizationAdminMixin):
    report_function = staticmethod(basic_report)
    resource_classes = [SupplyResource]
    list_display = ('name', 'kind', 'capacity_display', 'usage_discount_quantity_display', 'minimum_stock_quantity', 'maximum_stock_quantity', 'is_enabled')
    list_filter = ('kind', 'is_enabled')
    search_fields = ('name',)
    fields = ('kind', 'name', 'capacity', 'usage_discount_quantity', 'minimum_stock_quantity', 'maximum_stock_quantity', 'kg_tare', 'is_enabled')

    def capacity_display(self, obj):
        if obj.capacity and obj.capacity > 0:
            capacity = str(int(obj.capacity) if obj.capacity.is_integer() else obj.capacity)
            units = str(obj.kind.get_capacity_unit_category_display())
            unit = units[:-1] if obj.capacity == 1 and units[-1].lower() == 's' else units
            return f"{capacity} {unit}"
        return "-"
    capacity_display.short_description = _('Capacity')
    capacity_display.admin_order_field = 'capacity'

    def usage_discount_quantity_display(self, obj):
        units = str(obj.kind.get_usage_discount_unit_category_display())
        unit = units[:-1] if obj.usage_discount_quantity == 1 and units[-1].lower() == 's' else units
        return f"{str(obj.usage_discount_quantity)} {unit}"
    usage_discount_quantity_display.short_description = _('Usage discount quantity')
    usage_discount_quantity_display.admin_order_field = 'usage_discount_quantity'

    @uppercase_form_charfield('name')
    @uppercase_alphanumeric_form_charfield('code')
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'kind' in form.base_fields:
            form.base_fields['kind'].widget.can_add_related = False
            form.base_fields['kind'].widget.can_change_related = False
            form.base_fields['kind'].widget.can_delete_related = False
            form.base_fields['kind'].widget.can_view_related = False
        return form

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        obj_id = request.resolver_match.kwargs.get("object_id")
        obj = Supply.objects.get(id=obj_id) if obj_id else None
        print("db_field", db_field)
        print("db_field.name", db_field.name)

        if db_field.name == "kind":
            kwargs["queryset"] = SupplyKind.objects.filter(is_enabled=True)
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda item: item.name
            return formfield

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        obj_id = request.resolver_match.kwargs.get("object_id")
        obj = Supply.objects.get(id=obj_id) if obj_id else None

        if db_field.name == "capacity":
            print("capacity")
            packaging_containment_categories = ['packaging_containment', 'packaging_presentation', 'packaging_separator', 'packaging_storage', 'packhouse_cleaning', 'packhouse_fuel']
            print("packaging_containment_categories", packaging_containment_categories)
            print("request", request)
            if request.POST:
                kind_id = request.POST.get('kind')
            else:
                kind_id = obj.kind_id if obj else None
            print("kind_id", kind_id)
            if kind_id:
                kind = SupplyKind.objects.get(id=kind_id)
                print("KIND", kind)
                if kind.category in packaging_containment_categories:
                    print("kind.category in packaging_containment_categories", kind.category)
                    formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
                    formfield.required = True
                    return formfield
                else:
                    print("else", kind.category)
                    formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
                    formfield.required = False
                    return formfield

        return super().formfield_for_dbfield(db_field, request, **kwargs)

    class Media:
        js = ('js/admin/forms/supply.js',)



class CrewChiefInline(admin.TabularInline):
    model = CrewChief
    extra = 0
    can_delete = True

    @uppercase_formset_charfield('name')
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        return formset


@admin.register(Vehicle)
class VehicleAdmin(SheetReportExportAdminMixin, ByOrganizationAdminMixin):
    report_function = staticmethod(basic_report)
    resource_classes = [VehicleResource]
    list_display = (
        'name', 'category', 'kind', 'brand', 'model', 'license_plate', 'serial_number', 'ownership', 'fuel',
        'is_enabled')
    fields = (
        'name', 'category', 'kind', 'brand', 'model', 'license_plate', 'serial_number', 'color', 'ownership', 'fuel',
        'comments', 'is_enabled')
    list_filter = ('kind', 'brand', 'ownership', 'fuel', 'is_enabled')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Obtener la organización del request
        organization = getattr(request, 'organization', None)

        # Mapeo de campos a modelos
        model_map = {
            "kind": VehicleKind,
            "brand": VehicleBrand,
            "ownership": VehicleOwnershipKind,
            "fuel": VehicleFuelKind,
        }

        if db_field.name in model_map:
            Model = model_map[db_field.name]
            kwargs["queryset"] = Model.objects.filter(is_enabled=True)

            # Si la organización está disponible, filtramos por ella aquellos habilitados
            if organization:
                kwargs["queryset"] = Model.objects.filter(
                    organization=organization,
                    is_enabled=True
                )

        if "queryset" in kwargs:
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda item: item.name
            return formfield

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    @uppercase_form_charfield('name')
    @uppercase_form_charfield('license_plate')
    @uppercase_form_charfield('serial_number')
    @uppercase_form_charfield('color')
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return form


class HarvestingPaymentSettingInline(admin.StackedInline):
    model = HarvestingPaymentSetting
    min_num = 1
    max_num = 2
    formset = HarvestingPaymentSettingInlineFormSet

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        return formset


@admin.register(HarvestingCrew)
class HarvestingCrewAdmin(SheetReportExportAdminMixin, ByOrganizationAdminMixin):
    report_function = staticmethod(basic_report)
    resource_classes = [HarvestingCrewResource]
    form = HarvestingCrewForm
    list_display = ('name', 'provider', 'crew_chief', 'certification_name', 'persons_number', 'is_enabled')
    list_filter = ('provider', 'crew_chief', 'is_enabled')
    fields = ('provider', 'name', 'certification_name', 'crew_chief', 'persons_number', 'comments', 'is_enabled')
    inlines = [HarvestingPaymentSettingInline, ]

    @uppercase_form_charfield('name')
    @uppercase_form_charfield('certification_name')
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return form

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        obj_id = request.resolver_match.kwargs.get("object_id")
        obj = HarvestingCrew.objects.get(id=obj_id) if obj_id else None

        if db_field.name == "provider":
            if hasattr(request, 'organization'):
                kwargs["queryset"] = Provider.objects.filter(organization=request.organization, is_enabled=True,
                                                             category='harvesting_provider')
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            return formfield

        if db_field.name == "crew_chief":
            if request.POST:
                provider_id = request.POST.get('provider')
            else:
                provider_id = obj.provider_id if obj else None

            if provider_id:
                kwargs["queryset"] = CrewChief.objects.filter(provider_id=provider_id, is_enabled=True)
            else:
                kwargs["queryset"] = CrewChief.objects.none()

            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda item: item.name
            return formfield

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    class Media:
        js = ('js/admin/forms/packhouses/catalogs/harvesting_crew.js',)


@admin.register(Service)
class ServiceAdmin(SheetReportExportAdminMixin, ByOrganizationAdminMixin):
    report_function = staticmethod(basic_report)
    resource_classes = [ServiceResource]
    list_display = ('name', 'service_provider', 'is_enabled')
    list_filter = (ByServiceProviderForOrganizationServiceFilter, 'is_enabled')
    search_fields = ('name',)
    fields = ('name', 'service_provider', 'is_enabled',)

    @uppercase_form_charfield('name')
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return form

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "service_provider":
            if hasattr(request, 'organization'):
                kwargs["queryset"] = Provider.objects.filter(organization=request.organization, is_enabled=True,
                                                             category="service_provider")
            else:
                kwargs["queryset"] = Provider.objects.none()
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            return formfield


class ProductPresentationComplementarySupplyInline(admin.TabularInline):
    model = ProductPresentationComplementarySupply
    min_num = 0
    extra = 0
    verbose_name = _('Complementary supply')
    verbose_name_plural = _('Complementary supplies')

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        if 'kind' in formset.form.base_fields:
            formset.form.base_fields['kind'].widget.can_add_related = False
            formset.form.base_fields['kind'].widget.can_change_related = False
            formset.form.base_fields['kind'].widget.can_delete_related = False
            formset.form.base_fields['kind'].widget.can_view_related = False
        if 'supply' in formset.form.base_fields:
            formset.form.base_fields['supply'].widget.can_add_related = False
            formset.form.base_fields['supply'].widget.can_change_related = False
            formset.form.base_fields['supply'].widget.can_delete_related = False
            formset.form.base_fields['supply'].widget.can_view_related = False
        return formset

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        parent_obj_id = request.resolver_match.kwargs.get("object_id")
        parent_obj = ProductPresentation.objects.get(id=parent_obj_id) if parent_obj_id else None
        presentation_complement_categories = ['packaging_presentation_complement']

        if db_field.name == "kind":
            kwargs["queryset"] = SupplyKind.objects.filter(category__in=presentation_complement_categories, is_enabled=True)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    class Media:
        js = ('js/admin/forms/product_presentation_complementary_supply_inline.js',)


@admin.register(ProductPresentation)
class ProductPresentationAdmin(SheetReportExportAdminMixin, ByOrganizationAdminMixin):
    report_function = staticmethod(basic_report)
    # resource_classes = [ProductPresentationResource]
    list_display = ('name', 'product', 'markets_display', 'presentation_supply_kind', 'presentation_supply',
                    'is_enabled')
    list_filter = ('product', 'is_enabled')
    search_fields = ('name',)
    fields = ('product', 'markets', 'presentation_supply_kind', 'presentation_supply', 'name',
              'is_enabled')
    inlines = [ProductPresentationComplementarySupplyInline]

    def markets_display(self, obj):
        return ', '.join([market.name for market in obj.markets.all()])
    markets_display.short_description = _('Markets')
    markets_display.admin_order_field = 'name'

    @uppercase_form_charfield('name')
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'product' in form.base_fields:
            form.base_fields['product'].widget.can_add_related = False
            form.base_fields['product'].widget.can_change_related = False
            form.base_fields['product'].widget.can_delete_related = False
            form.base_fields['product'].widget.can_view_related = False
        if 'markets' in form.base_fields:
            form.base_fields['markets'].widget.can_add_related = False
        if 'presentation_supply_kind' in form.base_fields:
            form.base_fields['presentation_supply_kind'].widget.can_add_related = False
            form.base_fields['presentation_supply_kind'].widget.can_change_related = False
            form.base_fields['presentation_supply_kind'].widget.can_delete_related = False
            form.base_fields['presentation_supply_kind'].widget.can_view_related = False
        if 'presentation_supply' in form.base_fields:
            form.base_fields['presentation_supply'].widget.can_add_related = False
            form.base_fields['presentation_supply'].widget.can_change_related = False
            form.base_fields['presentation_supply'].widget.can_delete_related = False
            form.base_fields['presentation_supply'].widget.can_view_related = False
        return form

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        obj_id = request.resolver_match.kwargs.get("object_id")
        obj = Packaging.objects.get(id=obj_id) if obj_id else None
        organization = request.organization if hasattr(request, 'organization') else None
        organization_queryfilter = {'organization': organization, 'is_enabled': True}

        if db_field.name == "markets":
            kwargs["queryset"] = Market.objects.filter(**organization_queryfilter)

        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "product":
            organization = getattr(request, 'organization', None)
            if organization:
                kwargs["queryset"] = Product.objects.filter(organization=organization, is_enabled=True)
            else:
                kwargs["queryset"] = Product.objects.none()

        if db_field.name == "presentation_supply":
            organization = getattr(request, 'organization', None)
            if organization:
                kwargs["queryset"] = Supply.objects.filter(organization=organization, is_enabled=True)
            else:
                kwargs["queryset"] = Supply.objects.none()

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    class Media:
        js = ('js/admin/forms/product_presentation.js',)


class PackagingComplementarySupplyInline(admin.TabularInline):
    model = PackagingComplementarySupply
    min_num = 0
    extra = 0
    verbose_name = _('Complementary supply')
    verbose_name_plural = _('Complementary supplies')

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        if 'kind' in formset.form.base_fields:
            formset.form.base_fields['kind'].widget.can_add_related = False
            formset.form.base_fields['kind'].widget.can_change_related = False
            formset.form.base_fields['kind'].widget.can_delete_related = False
            formset.form.base_fields['kind'].widget.can_view_related = False
        if 'supply' in formset.form.base_fields:
            formset.form.base_fields['supply'].widget.can_add_related = False
            formset.form.base_fields['supply'].widget.can_change_related = False
            formset.form.base_fields['supply'].widget.can_delete_related = False
            formset.form.base_fields['supply'].widget.can_view_related = False
        return formset

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        parent_obj_id = request.resolver_match.kwargs.get("object_id")
        parent_obj = Packaging.objects.get(id=parent_obj_id) if parent_obj_id else None
        packaging_complement_categories = ['packaging_complement', 'packaging_separator', 'packaging_labeling', 'packaging_storage']

        if db_field.name == "kind":
            kwargs["queryset"] = SupplyKind.objects.filter(category__in=packaging_complement_categories, is_enabled=True)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    class Media:
        js = ('js/admin/forms/packaging_complementary_supply_inline.js',)
        # pass


@admin.register(Packaging)
class PackagingAdmin(SheetReportExportAdminMixin, ByOrganizationAdminMixin):
    report_function = staticmethod(basic_report)
    # resource_classes = [PackagingResource]
    list_filter = (BySupplyKindForPackagingFilter, BySupplyForOrganizationPackagingFilter,
                   ByProductForOrganizationPackagingFilter, ByMarketForOrganizationPackagingFilter,
                   'product_standard_packaging', 'is_enabled')
    list_display = ('name', 'packaging_supply_kind', 'packaging_supply', 'product', 'market',
                    'product_packaging_standard_display', 'is_enabled')
    fields = (
        'market', 'product', 'packaging_supply_kind', 'product_standard_packaging',
        'name', 'packaging_supply', 'is_enabled'
    )
    inlines = (PackagingComplementarySupplyInline,)

    def product_packaging_standard_display(self, obj):
        if obj.product_standard_packaging:
            return f"{obj.product_standard_packaging.name} ({obj.product_standard_packaging.standard.name}: {obj.product_standard_packaging.standard.country})"
        return f"-"
    product_packaging_standard_display.short_description = _('Product packaging standard')
    product_packaging_standard_display.admin_order_field = 'name'

    @uppercase_form_charfield('name')
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'market' in form.base_fields:
            form.base_fields['market'].widget.can_add_related = False
            form.base_fields['market'].widget.can_change_related = False
            form.base_fields['market'].widget.can_delete_related = False
            form.base_fields['market'].widget.can_view_related = False
        if 'product' in form.base_fields:
            form.base_fields['product'].widget.can_add_related = False
            form.base_fields['product'].widget.can_change_related = False
            form.base_fields['product'].widget.can_delete_related = False
            form.base_fields['product'].widget.can_view_related = False
        if 'packaging_supply_kind' in form.base_fields:
            form.base_fields['packaging_supply_kind'].widget.can_add_related = False
            form.base_fields['packaging_supply_kind'].widget.can_change_related = False
            form.base_fields['packaging_supply_kind'].widget.can_delete_related = False
            form.base_fields['packaging_supply_kind'].widget.can_view_related = False
        if 'product_standard_packaging' in form.base_fields:
            form.base_fields['product_standard_packaging'].widget.can_add_related = False
            form.base_fields['product_standard_packaging'].widget.can_change_related = False
            form.base_fields['product_standard_packaging'].widget.can_delete_related = False
            form.base_fields['product_standard_packaging'].widget.can_view_related = False
        if 'packaging_supply' in form.base_fields:
            form.base_fields['packaging_supply'].widget.can_add_related = False
            form.base_fields['packaging_supply'].widget.can_change_related = False
            form.base_fields['packaging_supply'].widget.can_delete_related = False
            form.base_fields['packaging_supply'].widget.can_view_related = False
        return form

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        obj_id = request.resolver_match.kwargs.get("object_id")
        obj = Packaging.objects.get(id=obj_id) if obj_id else None

        organization = request.organization if hasattr(request, 'organization') else None
        packaging_supply_kind = request.POST.get('packaging_supply_kind') if request.POST else obj.packaging_supply_kind if obj else None
        market_id = request.POST.get('market') if request.POST else obj.market_id if obj else None
        product_id = request.POST.get('product') if request.POST else obj.product_id if obj else None
        product_kind = ProductKind.objects.get(id=Product.objects.get(id=product_id).kind_id) if product_id else None

        organization_queryfilter = {'organization': organization, 'is_enabled': True}
        supply_queryfilter = {'organization': organization, 'kind': packaging_supply_kind, 'is_enabled': True}

        if db_field.name == "market":
            if organization:
                kwargs["queryset"] = Market.objects.filter(**organization_queryfilter)
            else:
                kwargs["queryset"] = Market.objects.none()

        if db_field.name == "product":
            if organization:
                kwargs["queryset"] = Product.objects.filter(**organization_queryfilter)
            else:
                kwargs["queryset"] = Product.objects.none()

        if db_field.name == "packaging_supply_kind":
            kwargs["queryset"] = SupplyKind.objects.filter(category='packaging_containment', is_enabled=True)

        if db_field.name == "packaging_supply":
            if packaging_supply_kind:
                kwargs["queryset"] = Supply.objects.filter(**supply_queryfilter)
            else:
                kwargs["queryset"] = Supply.objects.none()

        if db_field.name == "product_standard_packaging":
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.required = True
            if organization and product_kind and market_id:
                market_countries = Market.objects.get(id=market_id).countries.all().values_list('id', flat=True)
                queryset = ProductKindCountryStandardPackaging.objects.filter(standard__product_kind=product_kind, standard__country__in=market_countries)
                kwargs["queryset"] = queryset
                formfield.required = queryset.exists()
            else:
                kwargs["queryset"] = ProductKindCountryStandardPackaging.objects.none()
                formfield.required = False
            return formfield

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    class Media:
        js = ('js/admin/forms/packaging.js',)


class ProductPackagingPresentationInline(admin.TabularInline):
    model = ProductPackagingPresentation
    min_num = 0
    extra = 0
    max_num = 1
    verbose_name = _('Presentation')
    verbose_name_plural = _('Presentations')

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        if 'presentation' in formset.form.base_fields:
            formset.form.base_fields['presentation'].widget.can_add_related = False
            formset.form.base_fields['presentation'].widget.can_change_related = False
            formset.form.base_fields['presentation'].widget.can_delete_related = False
            formset.form.base_fields['presentation'].widget.can_view_related = False
        return formset

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        parent_obj_id = request.resolver_match.kwargs.get("object_id")
        parent_obj = Packaging.objects.get(id=parent_obj_id) if parent_obj_id else None
        organization = request.organization if hasattr(request, 'organization') else None

        if db_field.name == "presentation":
            if organization:
                kwargs["queryset"] = ProductPresentation.objects.filter(organization=organization, is_enabled=True)
            else:
                kwargs["queryset"] = ProductPresentation.objects.none()

        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class ProductPackagingPalletInline(admin.TabularInline):
    model = ProductPackagingPallet
    min_num = 0
    extra = 0
    verbose_name = _('Pallet')
    verbose_name_plural = _('Pallets')

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        if 'pallet' in formset.form.base_fields:
            formset.form.base_fields['pallet'].widget.can_add_related = False
            formset.form.base_fields['pallet'].widget.can_change_related = False
            formset.form.base_fields['pallet'].widget.can_delete_related = False
            formset.form.base_fields['pallet'].widget.can_view_related = True
        return formset

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        parent_obj_id = request.resolver_match.kwargs.get("object_id")
        parent_obj = Packaging.objects.get(id=parent_obj_id) if parent_obj_id else None
        organization = request.organization if hasattr(request, 'organization') else None

        if db_field.name == "pallet":
            kwargs["queryset"] = Pallet.objects.none()
            if organization:
                kwargs["queryset"] = Pallet.objects.filter(organization=organization, is_enabled=True)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    class Media:
        js = ('js/admin/forms/product_packaging_pallet_inline.js',)


@admin.register(ProductPackaging)
class ProductPackagingAdmin(SheetReportExportAdminMixin, ByOrganizationAdminMixin):
    report_function = staticmethod(basic_report)
    # resource_classes = [PackagingResource]
    list_filter = [ByMarketForOrganizationFilter, ByProductForOrganizationFilter,
                   ByProductSizeForProductOrganizationFilter, ByPackagingForOrganizationFilter, 'is_enabled']
    search_fields = ('name', 'alias')
    list_display = ['name', 'alias', 'market', 'product', 'product_size', 'packaging', 'product_amount_per_packaging', 'is_enabled']
    fields = ['category', 'market', 'product', 'product_size', 'packaging', 'product_amount_per_packaging',
              'product_presentation', 'product_presentation_quantity_per_packaging', 'name', 'alias', 'is_enabled']
    inlines = [ProductPackagingPalletInline]

    @uppercase_form_charfield('name')
    @uppercase_alphanumeric_form_charfield('alias')
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'market' in form.base_fields:
            form.base_fields['market'].widget.can_add_related = False
            form.base_fields['market'].widget.can_change_related = False
            form.base_fields['market'].widget.can_delete_related = False
            form.base_fields['market'].widget.can_view_related = False
        if 'product' in form.base_fields:
            form.base_fields['product'].widget.can_add_related = False
            form.base_fields['product'].widget.can_change_related = False
            form.base_fields['product'].widget.can_delete_related = False
            form.base_fields['product'].widget.can_view_related = False
        if 'product_size' in form.base_fields:
            form.base_fields['product_size'].widget.can_add_related = False
            form.base_fields['product_size'].widget.can_change_related = False
            form.base_fields['product_size'].widget.can_delete_related = False
            form.base_fields['product_size'].widget.can_view_related = False
        if 'packaging' in form.base_fields:
            form.base_fields['packaging'].widget.can_add_related = False
            form.base_fields['packaging'].widget.can_change_related = False
            form.base_fields['packaging'].widget.can_delete_related = False
            form.base_fields['packaging'].widget.can_view_related = False
        if 'product_presentation' in form.base_fields:
            form.base_fields['product_presentation'].widget.can_add_related = False
            form.base_fields['product_presentation'].widget.can_change_related = False
            form.base_fields['product_presentation'].widget.can_delete_related = False
            form.base_fields['product_presentation'].widget.can_view_related = False
        return form

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        obj_id = request.resolver_match.kwargs.get("object_id")
        obj = ProductPackaging.objects.get(id=obj_id) if obj_id else None

        organization = request.organization if hasattr(request, 'organization') else None
        market_id = request.POST.get('market') if request.POST else obj.market_id if obj else None
        product_id = request.POST.get('product') if request.POST else obj.product_id if obj else None
        category = request.POST.get('category') if request.POST else obj.category if obj else None

        organization_queryfilter = {'organization': organization, 'is_enabled': True}
        print("organization_queryfilter", organization_queryfilter)

        if db_field.name == "market":
            if organization:
                kwargs["queryset"] = Market.objects.filter(**organization_queryfilter)
            else:
                kwargs["queryset"] = Market.objects.none()

        if db_field.name == "product":
            if organization:
                kwargs["queryset"] = Product.objects.filter(**organization_queryfilter)
            else:
                kwargs["queryset"] = Product.objects.none()

        if db_field.name == "product_size":
            if organization:
                kwargs["queryset"] = ProductSize.objects.filter(Q(product__organization=organization) | Q(market__organization=organization)).filter(is_enabled=True)
            else:
                kwargs["queryset"] = ProductSize.objects.none()

        if db_field.name == "packaging":
            if organization:
                queryset = Packaging.objects.filter(**organization_queryfilter)
                if market_id:
                    queryset = queryset.filter(market=market_id)
                if product_id:
                    queryset = queryset.filter(product_id=product_id)
                kwargs["queryset"] = queryset
            else:
                kwargs["queryset"] = Packaging.objects.none()

        if db_field.name == "product_presentation":
            queryset = ProductPresentation.objects.none()
            if organization:
                queryset = ProductPresentation.objects.filter(**organization_queryfilter)
            kwargs["queryset"] = queryset
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.required = True
            if category == 'packaging' and request.POST:
                formfield.required = False
            return formfield

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        obj_id = request.resolver_match.kwargs.get("object_id")
        obj = ProductPackaging.objects.get(id=obj_id) if obj_id else None

        category = request.POST.get('category') if request.POST else obj.category if obj else None

        if db_field.name == "product_amount_per_packaging":
            formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
            formfield.required = True
            if category == 'presentation' and request.POST:
                formfield.required = False
            return formfield

        if db_field.name == "product_presentation_quantity_per_packaging":
            formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
            formfield.required = True
            if category == 'packaging' and request.POST:
                formfield.required = False
            return formfield

        return super().formfield_for_dbfield(db_field, request, **kwargs)

    class Media:
        js = ('js/admin/forms/product_packaging.js',)


class PalletComplementarySupplyInLine(admin.TabularInline):
    model = PalletComplementarySupply
    extra = 0
    verbose_name = _('Complementary supply')
    verbose_name_plural = _('Complementary supplies')

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        if 'kind' in formset.form.base_fields:
            formset.form.base_fields['kind'].widget.can_add_related = False
            formset.form.base_fields['kind'].widget.can_change_related = False
            formset.form.base_fields['kind'].widget.can_delete_related = False
            formset.form.base_fields['kind'].widget.can_view_related = False
        if 'supply' in formset.form.base_fields:
            formset.form.base_fields['supply'].widget.can_add_related = False
            formset.form.base_fields['supply'].widget.can_change_related = False
            formset.form.base_fields['supply'].widget.can_delete_related = False
            formset.form.base_fields['supply'].widget.can_view_related = True
        return formset

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj and is_instance_used(obj, exclude=[Market, Product, Supply, Organization, PalletComplementarySupply]):
            readonly_fields.extend(['pallet', 'kind', 'supply', 'quantity'])
        return readonly_fields

    def has_delete_permission(self, request, obj=None):
        if obj and is_instance_used(obj, exclude=[Market, Product, Supply, Organization, PalletComplementarySupply]):
            return False
        return super().has_delete_permission(request, obj)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        organization = request.organization if hasattr(request, 'organization') else None

        if db_field.name == "kind":
            kwargs["queryset"] = SupplyKind.objects.filter(category='packaging_pallet_complement', is_enabled=True)

        if db_field.name == "supply":
            if organization:
                kwargs["queryset"] = Supply.objects.filter(organization=organization, is_enabled=True,
                                                           kind__category='packaging_pallet_complement')
            else:
                kwargs["queryset"] = Supply.objects.none()

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    class Media:
        js = ('js/admin/forms/pallet_complementary_supply_inline.js',)


@admin.register(Pallet)
class PalletAdmin(SheetReportExportAdminMixin, ByOrganizationAdminMixin):
    report_function = staticmethod(basic_report)
    resource_classes = [PalletResource]
    list_display = ('name', 'alias', 'market', 'product', 'supply', 'is_enabled')
    list_filter = (ByMarketForOrganizationPalletFilter, ByProductForOrganizationProductPackagingPalletFilter,
                   BySupplyForOrganizationPalletFilter, 'is_enabled')
    fields = ('market', 'product', 'supply', 'name', 'alias', 'is_enabled')
    search_fields = ('name', 'alias')
    inlines = [PalletComplementarySupplyInLine]

    @uppercase_form_charfield('name')
    @uppercase_alphanumeric_form_charfield('alias')
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'market' in form.base_fields:
            form.base_fields['market'].widget.can_add_related = False
            form.base_fields['market'].widget.can_change_related = False
            form.base_fields['market'].widget.can_delete_related = False
            form.base_fields['market'].widget.can_view_related = True
        if 'product' in form.base_fields:
            form.base_fields['product'].widget.can_add_related = False
            form.base_fields['product'].widget.can_change_related = False
            form.base_fields['product'].widget.can_delete_related = False
            form.base_fields['product'].widget.can_view_related = True
        if 'supply' in form.base_fields:
            form.base_fields['supply'].widget.can_add_related = False
            form.base_fields['supply'].widget.can_change_related = False
            form.base_fields['supply'].widget.can_delete_related = False
            form.base_fields['supply'].widget.can_view_related = True
        return form

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj and is_instance_used(obj, exclude=[Market, Product, Supply, Organization, PalletComplementarySupply]):
            readonly_fields.extend(['market', 'product', 'name', 'alias', 'supply'])
        return readonly_fields

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        obj_id = request.resolver_match.kwargs.get("object_id")
        obj = Pallet.objects.get(id=obj_id) if obj_id else None

        organization = request.organization if hasattr(request, 'organization') else None
        organization_queryfilter = {'organization': organization, 'is_enabled': True}

        if db_field.name == "market":
            if organization:
                kwargs["queryset"] = Market.objects.filter(**organization_queryfilter)
            else:
                kwargs["queryset"] = Market.objects.none()

        if db_field.name == "product":
            if organization:
                kwargs["queryset"] = Product.objects.filter(**organization_queryfilter)
            else:
                kwargs["queryset"] = Product.objects.none()

        if db_field.name == "supply":
            if organization:
                kwargs["queryset"] = Supply.objects.filter(**organization_queryfilter, kind__category='packaging_pallet')
            else:
                kwargs["queryset"] = Supply.objects.none()

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    class Media:
        js = ('js/admin/forms/pallet.js',)


@admin.register(WeighingScale)
class WeighingScaleAdmin(SheetReportExportAdminMixin, ByOrganizationAdminMixin):
    report_function = staticmethod(basic_report)
    resource_classes = [WeighingScaleResource]
    list_display = (
        'name', 'number', 'get_state_name', 'get_city_name', 'neighborhood', 'address', 'external_number', 'is_enabled')
    list_filter = (ByStateForOrganizationWeighingScaleFilter, ByCityForOrganizationWeighingScaleFilter, 'is_enabled',)
    search_fields = ('name',)
    fields = (
        'name', 'number', 'state', 'city', 'district', 'neighborhood', 'postal_code', 'address',
        'external_number', 'internal_number', 'comments', 'is_enabled',
    )

    def get_state_name(self, obj):
        return obj.state.name
    get_state_name.short_description = _('State')
    get_state_name.admin_order_field = 'state__name'

    def get_city_name(self, obj):
        return obj.city.name

    get_city_name.short_description = _('City')
    get_city_name.admin_order_field = 'city__name'

    @uppercase_form_charfield('name')
    @uppercase_form_charfield('neighborhood')
    @uppercase_form_charfield('address')
    @uppercase_alphanumeric_form_charfield('number')
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return form

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj and is_instance_used(obj, exclude=[City, Organization]):
            readonly_fields.extend(['name', 'organization'])
        return readonly_fields

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        obj_id = request.resolver_match.kwargs.get("object_id")
        obj = WeighingScale.objects.get(id=obj_id) if obj_id else None

        if db_field.name == "state":
            if hasattr(request, 'organization'):
                packhouse_profile = PackhouseExporterProfile.objects.get(organization=request.organization)
                if packhouse_profile:
                    kwargs["queryset"] = Region.objects.filter(country=packhouse_profile.country)
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda item: item.name
            return formfield

        if db_field.name == "city":
            if request.POST:
                state_id = request.POST.get('state')
            else:
                state_id = obj.state_id if obj else None
            if state_id:
                kwargs["queryset"] = SubRegion.objects.filter(region_id=state_id)
            else:
                kwargs["queryset"] = SubRegion.objects.none()
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda item: item.name
            return formfield

        if db_field.name == "district":
            if request.POST:
                city_id = request.POST.get('city')
            else:
                city_id = obj.city_id if obj else None
            if city_id:
                kwargs["queryset"] = City.objects.filter(subregion_id=city_id)
            else:
                kwargs["queryset"] = City.objects.none()
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda item: item.name
            return formfield

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    class Media:
        js = ('js/admin/forms/common/country-state-city-district.js',)


@admin.register(ColdChamber)
class ColdChamberAdmin(SheetReportExportAdminMixin, ByOrganizationAdminMixin):
    report_function = staticmethod(basic_report)
    resource_classes = [ColdChamberResource]
    list_display = ('name', 'product', 'product_variety', 'market', 'pallet_capacity', 'is_enabled')
    list_filter = (ByMarketForOrganizationFilter, ByProductForOrganizationFilter,
                   ByProductVarietyForOrganizationFilter, 'is_enabled')
    search_fields = ('name',)
    fields = ('name', 'market', 'product', 'product_variety', 'pallet_capacity',
              'freshness_days_alert', 'freshness_days_warning',
              'comments', 'is_enabled')

    @uppercase_form_charfield('name')
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return form

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        obj_id = request.resolver_match.kwargs.get("object_id")
        obj = ColdChamber.objects.get(id=obj_id) if obj_id else None

        organization = request.organization if hasattr(request, 'organization') else None
        product = request.POST.get('product') if request.POST else obj.product if obj else None

        organization_queryfilter = {'organization': organization, 'is_enabled': True}
        product_organization_queryfilter = {'product': product, 'product__organization': organization,
                                            'is_enabled': True}

        if db_field.name == "market":
            kwargs["queryset"] = Market.objects.filter(**organization_queryfilter)
        if db_field.name == "product":
            kwargs["queryset"] = Product.objects.filter(**organization_queryfilter)
        if db_field.name == "product_variety":
            if product:
                kwargs["queryset"] = ProductVariety.objects.filter(**product_organization_queryfilter)
            else:
                kwargs["queryset"] = ProductVariety.objects.none()

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    class Media:
        js = ('js/admin/forms/packhouses/catalogs/cold_chambers.js',)


class ExportingCompanyBeneficiaryInline(admin.StackedInline):
    model = ExportingCompanyBeneficiary
    extra = 0
    can_delete = True

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        return formset


@admin.register(ExportingCompany)
class ExportingCompanyAdmin(SheetReportExportAdminMixin, ByOrganizationAdminMixin):
    report_function = staticmethod(basic_report)
    resource_classes = [ExportingCompanyResource]
    list_display = ('name', 'contact_name', 'tax_id', 'country',
                    'get_state_name', 'get_city_name', 'address',
                    'external_number', 'phone_number', 'is_enabled')
    list_filter = (ByCountryForOrganizationExportingCompaniesFilter, ByStateForOrganizationExportingCompaniesFilter,
                   ByCityForOrganizationExportingCompaniesFilter, 'is_enabled',)
    fields = (
    'name', 'country', 'state', 'city', 'district', 'postal_code', 'neighborhood', 'address', 'external_number',
    'tax_id', 'contact_name', 'email', 'phone_number', 'is_enabled')
    inlines = (ExportingCompanyBeneficiaryInline,)

    def get_state_name(self, obj):
        return obj.state.name

    get_state_name.short_description = _('State')
    get_state_name.admin_order_field = 'state__name'

    def get_city_name(self, obj):
        return obj.city.name

    get_city_name.short_description = _('City')
    get_city_name.admin_order_field = 'city__name'

    @uppercase_form_charfield('name')
    @uppercase_form_charfield('neighborhood')
    @uppercase_form_charfield('address')
    @uppercase_form_charfield('contact_name')
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not obj:
            if hasattr(request, 'organization'):
                packhouse_profile = PackhouseExporterProfile.objects.get(organization=request.organization)
                if packhouse_profile:
                    form.base_fields['country'].initial = packhouse_profile.country
        return form

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        object_id = request.resolver_match.kwargs.get("object_id")
        obj = ExportingCompany.objects.get(id=object_id) if object_id else None

        if db_field.name == "country":
            kwargs["queryset"] = Country.objects.all()
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda item: item.name
            return formfield

        if db_field.name == "state":
            if request.POST:
                country_id = request.POST.get('country')
            else:
                country_id = obj.country_id if obj else None
            if country_id:
                kwargs["queryset"] = Region.objects.filter(country_id=country_id)
            else:
                kwargs["queryset"] = Region.objects.none()
                if hasattr(request, 'organization'):
                    packhouse_profile = PackhouseExporterProfile.objects.get(organization=request.organization)
                    if packhouse_profile:
                        kwargs["queryset"] = Region.objects.filter(country=packhouse_profile.country)
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda item: item.name
            return formfield

        if db_field.name == "city":
            if request.POST:
                state_id = request.POST.get('state')
            else:
                state_id = obj.state_id if obj else None
            if state_id:
                kwargs["queryset"] = SubRegion.objects.filter(region_id=state_id)
            else:
                kwargs["queryset"] = SubRegion.objects.none()
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda item: item.name
            return formfield

        if db_field.name == "district":
            if request.POST:
                city_id = request.POST.get('city')
            else:
                city_id = obj.city_id if obj else None
            if city_id:
                kwargs["queryset"] = City.objects.filter(subregion_id=city_id)
            else:
                kwargs["queryset"] = City.objects.none()
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda item: item.name
            return formfield

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    class Media:
        js = ('js/admin/forms/packhouses/catalogs/country-state-city-district.js',)


@admin.register(Transfer)
class TransferAdmin(SheetReportExportAdminMixin, ByOrganizationAdminMixin):
    report_function = staticmethod(basic_report)
    resource_classes = [TransferResource]
    fields = ('name', 'caat', 'scac', 'is_enabled')
    list_filter = ('is_enabled',)

    @uppercase_form_charfield('name')
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return form


@admin.register(LocalTransporter)
class LocalTransporterAdmin(SheetReportExportAdminMixin, ByOrganizationAdminMixin):
    report_function = staticmethod(basic_report)
    resource_classes = [LocalTransporterResource]
    fields = ('name', 'is_enabled')
    list_filter = ('is_enabled',)

    @uppercase_form_charfield('name')
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return form


@admin.register(BorderToDestinationTransporter)
class BorderToDestinationTransporterAdmin(SheetReportExportAdminMixin, ByOrganizationAdminMixin):
    report_function = staticmethod(basic_report)
    resource_classes = [BorderToDestinationTransporterResource]
    fields = ('name', 'tax_id', 'caat', 'irs', 'scac', 'us_custom_bond', 'is_enabled')
    list_filter = ('is_enabled',)

    @uppercase_form_charfield('name')
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return form


@admin.register(CustomsBroker)
class CustomsBrokerAdmin(SheetReportExportAdminMixin, ByOrganizationAdminMixin):
    report_function = staticmethod(basic_report)
    resource_classes = [CustomsBrokerResource]
    list_display = ('name', 'broker_number', 'country', 'is_enabled')
    fields = ('name', 'broker_number', 'country', 'is_enabled')
    list_filter = (ByCountryForOrganizationCustomsBrokersFilter, 'is_enabled',)

    @uppercase_form_charfield('name')
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return form


@admin.register(Vessel)
class VesselAdmin(SheetReportExportAdminMixin, ByOrganizationAdminMixin):
    report_function = staticmethod(basic_report)
    resource_classes = [VesselResource]
    fields = ('name', 'vessel_number', 'is_enabled')
    list_filter = ('is_enabled',)

    @uppercase_form_charfield('name')
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return form


@admin.register(Airline)
class AirlineAdmin(SheetReportExportAdminMixin, ByOrganizationAdminMixin):
    report_function = staticmethod(basic_report)
    resource_classes = [AirlineResource]
    fields = ('name', 'airline_number', 'is_enabled')
    list_filter = ('is_enabled',)

    @uppercase_form_charfield('name')
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return form


@admin.register(InsuranceCompany)
class InsuranceCompanyAdmin(SheetReportExportAdminMixin, ByOrganizationAdminMixin):
    report_function = staticmethod(basic_report)
    resource_classes = [InsuranceCompanyResource]
    fields = ('name', 'insurance_number', 'is_enabled')
    list_filter = ('is_enabled',)

    @uppercase_form_charfield('name')
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return form


# Providers

class ProviderBeneficiaryInline(admin.StackedInline):
    model = ProviderBeneficiary
    extra = 0

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        return formset

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        object_id = request.resolver_match.kwargs.get("object_id")
        obj = Provider.objects.get(id=object_id) if object_id else None

        if db_field.name == "bank":
            if hasattr(request, 'organization'):
                kwargs["queryset"] = Bank.objects.filter(organization=request.organization, is_enabled=True)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class ProviderBalanceInline(admin.StackedInline):
    model = ProviderFinancialBalance
    min_num = 1
    max_num = 1
    can_delete = False

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        return formset


@admin.register(Provider)
class ProviderAdmin(SheetReportExportAdminMixin, ByOrganizationAdminMixin):
    report_function = staticmethod(basic_report)
    resource_classes = [ProviderResource]
    list_display = ('name', 'category', 'country', 'get_state_name', 'get_city_name', 'tax_id', 'email', 'is_enabled')
    list_filter = ('category', ByCountryForOrganizationProvidersFilter, ByStateForOrganizationProvidersFilter,
                   ByCityForOrganizationProvidersFilter, 'is_enabled',)
    search_fields = ('name', 'neighborhood', 'address', 'tax_id', 'email')
    fields = (
        'name', 'category', 'provider_provider', 'vehicle_provider', 'country', 'state', 'city', 'district',
        'postal_code',
        'neighborhood', 'address', 'external_number', 'internal_number', 'tax_id', 'email', 'phone_number',
        'comments', 'is_enabled')
    inlines = (ProviderBeneficiaryInline, ProviderBalanceInline, CrewChiefInline)
    form = ProviderForm

    def get_state_name(self, obj):
        return obj.state.name

    get_state_name.short_description = _('State')
    get_state_name.admin_order_field = 'state__name'

    def get_city_name(self, obj):
        return obj.city.name

    get_city_name.short_description = _('City')
    get_city_name.admin_order_field = 'city__name'

    @uppercase_form_charfield('name')
    @uppercase_form_charfield('neighborhood')
    @uppercase_form_charfield('address')
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not obj:
            if hasattr(request, 'organization'):
                packhouse_profile = PackhouseExporterProfile.objects.get(organization=request.organization)
                if packhouse_profile:
                    form.base_fields['country'].initial = packhouse_profile.country
        form.base_fields['vehicle_provider'].widget.can_add_related = False
        return form

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        object_id = request.resolver_match.kwargs.get("object_id")
        obj = Provider.objects.get(id=object_id) if object_id else None

        if db_field.name == "provider_provider":
            allowed_provider_provider_categories = {
                'product_provider': [],
                'service_provider': [],
                'supply_provider': [],
                'harvesting_provider': [],
                'product_producer': ['product_provider', ]
            }
            if request.POST:
                category_choice = request.POST.get('category')
            else:
                category_choice = obj.category if obj else None
            if category_choice:
                kwargs["queryset"] = Provider.objects.filter(organization=request.organization,
                                                             category__in=allowed_provider_provider_categories[
                                                                 category_choice],
                                                             is_enabled=True)
            else:
                kwargs["queryset"] = Provider.objects.none()
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda item: item.name
            return formfield

        if db_field.name == "country":
            kwargs["queryset"] = Country.objects.all()
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda item: item.name
            return formfield

        if db_field.name == "state":
            if request.POST:
                country_id = request.POST.get('country')
            else:
                country_id = obj.country_id if obj else None
            if country_id:
                kwargs["queryset"] = Region.objects.filter(country_id=country_id)
            else:
                kwargs["queryset"] = Region.objects.none()
                if hasattr(request, 'organization'):
                    packhouse_profile = PackhouseExporterProfile.objects.get(organization=request.organization)
                    if packhouse_profile:
                        kwargs["queryset"] = Region.objects.filter(country=packhouse_profile.country)
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda item: item.name
            return formfield

        if db_field.name == "city":
            if request.POST:
                state_id = request.POST.get('state')
            else:
                state_id = obj.state_id if obj else None
            if state_id:
                kwargs["queryset"] = SubRegion.objects.filter(region_id=state_id)
            else:
                kwargs["queryset"] = SubRegion.objects.none()
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda item: item.name
            return formfield

        if db_field.name == "district":
            if request.POST:
                city_id = request.POST.get('city')
            else:
                city_id = obj.city_id if obj else None
            if city_id:
                kwargs["queryset"] = City.objects.filter(subregion_id=city_id)
            else:
                kwargs["queryset"] = City.objects.none()
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda item: item.name
            return formfield

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "vehicle_provider":
            if hasattr(request, 'organization'):
                kwargs["queryset"] = Vehicle.objects.filter(organization=request.organization, is_enabled=True)
            else:
                kwargs["queryset"] = Vehicle.objects.none()
            formfield = super().formfield_for_manytomany(db_field, request, **kwargs)
            formfield.label_from_instance = lambda item: item.name
            return formfield

        return super().formfield_for_manytomany(db_field, request, **kwargs)

    class Media:
        js = ('js/admin/forms/common/country-state-city-district.js',
              'js/admin/forms/packhouses/catalogs/provider.js',
              'js/admin/forms/packhouses/catalogs/harvesting_crew_provider.js')


# /Providers

