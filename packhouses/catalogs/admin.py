from django.contrib import admin
from common.billing.models import LegalEntityCategory
from .models import (
    Market, KGCostMarket, MarketClass, MarketStandardProductSize, Product, ProductVariety, ProductVarietySize,
    ProductHarvestSizeKind, ProductProvider, ProductProviderBenefactor, ProductProducer,
    ProductProducerBenefactor,
    PaymentKind, Vehicle, Gatherer, Client, ClientShipAddress, Maquiladora, MaquiladoraClient,
    OrchardProductClassificationKind, Orchard, OrchardCertification, HarvestingCrewProvider, CrewChief, HarvestingCrew,
    HarvestingCrewBeneficiary, HarvestingPaymentSetting, Supply, SupplyProvider, MeshBagKind, MeshBagFilmKind,
    MeshBag, ServiceProvider, ServiceProviderBenefactor, Service, AuthorityBoxKind, BoxKind, WeighingScale, ColdChamber,
    Pallet, PalletExpense, ProductPackaging, ExportingCompany, Transfer, LocalTransporter,
    BorderToDestinationTransporter, CustomsBroker, Vessel, Airline, InsuranceCompany,
    Provider, ProviderBeneficiary
)

from packhouses.packhouse_settings.models import (Bank, VehicleOwnershipKind, VehicleFuelKind, VehicleKind, VehicleBrand,
                                                  ProductSizeKind, ProductMassVolumeKind)
from common.profiles.models import UserProfile, PackhouseExporterProfile, OrganizationProfile
from .forms import (ProductVarietyInlineFormSet, ProductHarvestSizeKindInlineFormSet,
                    OrchardCertificationForm, HarvestingCrewForm, HarvestingPaymentSettingInlineFormSet)
from django_ckeditor_5.widgets import CKEditor5Widget
from organizations.models import Organization, OrganizationUser
from cities_light.models import Country, Region, SubRegion, City

from django.utils.translation import gettext_lazy as _
from common.widgets import UppercaseTextInputWidget, UppercaseAlphanumericTextInputWidget, AutoGrowingTextareaWidget
from .filters import (StateFilterUserCountry,
                      ByProductForOrganizationFilter, ByProductVarietyForOrganizationFilter,
                      ByMarketForOrganizationFilter, ByProductSizeKindForOrganizationFilter,
                      ByProductMassVolumeKindForOrganizationFilter,
                      ProductKindForPackagingFilter)
from common.utils import is_instance_used
from adminsortable2.admin import SortableAdminMixin, SortableStackedInline, SortableTabularInline, SortableAdminBase
from common.base.models import ProductKind
from common.base.decorators import uppercase_formset_charfield, uppercase_alphanumeric_formset_charfield
from common.base.decorators import uppercase_form_charfield, uppercase_alphanumeric_form_charfield
from common.base.mixins import ByOrganizationAdminMixin, ByProductForOrganizationAdminMixin

admin.site.unregister(Country)
admin.site.unregister(Region)
admin.site.unregister(SubRegion)
admin.site.unregister(City)


# Markets

class KGCostMarketInline(admin.TabularInline):
    model = KGCostMarket
    extra = 0

    # TODO: Revisar si este inline si se va a usar en Market

    @uppercase_formset_charfield('name')
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        return formset


class MarketClassInline(admin.TabularInline):
    model = MarketClass
    extra = 0

    @uppercase_formset_charfield('name')
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        return formset


class MarketStandardProductSizeInline(admin.TabularInline):
    model = MarketStandardProductSize
    ordering = ('order', 'name')
    extra = 0

    @uppercase_formset_charfield('name')
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        return formset


@admin.register(Market)
class MarketAdmin(ByOrganizationAdminMixin):
    list_display = ('name', 'alias', 'is_enabled')
    list_filter = ('is_enabled',)
    search_fields = ('name', 'alias')
    fields = ('name', 'alias', 'countries', 'management_cost_per_kg', 'is_foreign', 'is_mixable',
              'label_language', 'address_label', 'is_enabled')
    inlines = [MarketClassInline, MarketStandardProductSizeInline]

    # TODO: revisar si KGCostMarketInline si va en Market o va por variedad o donde?

    @uppercase_form_charfield('name')
    @uppercase_alphanumeric_form_charfield('alias')
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['address_label'].widget = CKEditor5Widget()
        return form

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj and is_instance_used(obj, exclude=[KGCostMarket, MarketClass, MarketStandardProductSize, Country, Organization]):
            readonly_fields.extend(['name', 'alias', 'countries', 'is_foreign', 'organization'])
        return readonly_fields

    def save_model(self, request, obj, form, change):
        if 'address_label' in form.cleaned_data and form.cleaned_data['address_label'] == '<p>&nbsp;</p>':
            obj.address_label = None
        super().save_model(request, obj, form, change)

# /Markets


# Products

class ProductVarietyInline(admin.TabularInline):
    model = ProductVariety
    extra = 0
    fields = ('name', 'description', 'is_enabled')
    formset = ProductVarietyInlineFormSet

    @uppercase_formset_charfield('name')
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        return formset


class ProductHarvestSizeKindInline(admin.TabularInline):
    model = ProductHarvestSizeKind
    extra = 0
    fields = ('name', 'product', 'is_enabled', 'order')
    ordering = ['order', '-name']
    formset = ProductHarvestSizeKindInlineFormSet

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        return formset


@admin.register(Product)
class ProductAdmin(ByOrganizationAdminMixin):
    list_display = ('name', 'kind', 'description', 'is_enabled')
    list_filter = (ProductKindForPackagingFilter, 'is_enabled',)
    search_fields = ('name', 'kind__name', 'description')
    fields = ('kind', 'name', 'description', 'is_enabled')
    inlines = [ProductVarietyInline, ProductHarvestSizeKindInline]

    @uppercase_form_charfield('name')
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return form

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj and is_instance_used(obj, exclude=[ProductKind, Organization]):
            readonly_fields.extend(['kind', 'name', 'organization'])
        return readonly_fields

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "kind":
            product_kinds = ProductKind.objects.filter(for_packaging=True, is_enabled=True)
            kwargs["queryset"] = product_kinds
            if hasattr(request, 'organization'):
                packhouse_exporter_profile = PackhouseExporterProfile.objects.get(organization=request.organization)
                kwargs["queryset"] = packhouse_exporter_profile.packhouseexportersetting.product_kinds.filter(is_enabled=True)
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            return formfield
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(ProductVariety)
class ProductVarietyAdmin(ByProductForOrganizationAdminMixin):
    list_display = ('name', 'product', 'description', 'is_enabled')
    list_filter = (ByProductForOrganizationFilter, 'is_enabled',)
    search_fields = ('name', 'product__name', 'product__kind__name', 'description')
    fields = ('product', 'name', 'description', 'is_enabled')
    # inlines = [ProductVarietySizeInline]

    @uppercase_form_charfield('name')
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return form

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj and is_instance_used(obj, exclude=[Product]):
            readonly_fields.extend(['name', 'product'])
        return readonly_fields

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "product":
            if hasattr(request, 'organization'):
                kwargs["queryset"] = Product.objects.filter(organization=request.organization, is_enabled=True)
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            return formfield
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(ProductHarvestSizeKind)
class ProductVarietySizeHarvestKindAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'product', 'is_enabled', 'order')
    list_filter = (ByProductForOrganizationFilter, ByProductVarietyForOrganizationFilter, 'is_enabled')
    search_fields = ('name',)
    fields = ('product', 'name', 'is_enabled', 'order')
    ordering = ['order']

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return form

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj and is_instance_used(obj, exclude=[Product, ProductVariety]):
            readonly_fields.extend(['product', 'name'])
        return readonly_fields

    def formfield_for_foreignkey(self, db_field, request, **kwargs):

        if db_field.name == "product":
            if hasattr(request, 'organization'):
                kwargs["queryset"] = Product.objects.filter(organization=request.organization, is_enabled=True)
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            return formfield

        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(ProductVarietySize)
class ProductVarietySizeAdmin(SortableAdminMixin, ByProductForOrganizationAdminMixin):
    list_display = (
        'name', 'product', 'product_variety', 'market', 'product_size_kind', 'product_mass_volume_kind', 'is_enabled',
        'order')
    list_filter = (
        ByProductForOrganizationFilter, ByProductVarietyForOrganizationFilter, ByMarketForOrganizationFilter,
        ByProductSizeKindForOrganizationFilter, ByProductMassVolumeKindForOrganizationFilter,
        'requires_corner_protector', 'is_enabled'
    )
    search_fields = ('name', 'alias', 'product__name', 'product_variety__name')
    ordering = ['order']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        object_id = request.resolver_match.kwargs.get("object_id")
        obj = ProductVarietySize.objects.get(id=object_id) if object_id else None

        if db_field.name == "product":
            if hasattr(request, 'organization'):
                kwargs["queryset"] = Product.objects.filter(organization=request.organization, is_enabled=True)
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            return formfield

        if db_field.name == "product_variety":
            if hasattr(request, 'organization'):
                kwargs["queryset"] = ProductVariety.objects.filter(product__organization=request.organization, is_enabled=True)
                if request.POST:
                    product_id = request.POST.get('product')
                else:
                    product_id = obj.product_id if obj else None
                if product_id:
                    kwargs["queryset"] = kwargs["queryset"].filter(product_id=product_id)
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            return formfield

        if db_field.name == "market":
            if hasattr(request, 'organization'):
                kwargs["queryset"] = Market.objects.filter(organization=request.organization, is_enabled=True)
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            return formfield

        if db_field.name == "market_standard_product_size":
            if hasattr(request, 'organization'):
                kwargs["queryset"] = MarketStandardProductSize.objects.filter(market__organization=request.organization,
                                                                             is_enabled=True)
                if request.POST:
                    market_id = request.POST.get('market')
                else:
                    market_id = obj.market_id if obj else None
                if market_id:
                    kwargs["queryset"] = kwargs["queryset"].filter(market_id=market_id)
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            return formfield


        if db_field.name == "product_harvest_kind":
            if hasattr(request, 'organization'):
                kwargs["queryset"] = ProductHarvestSizeKind.objects.filter(product__organization=request.organization,
                                                                           is_enabled=True)
                if request.POST:
                    product_variety_id = request.POST.get('product_variety')
                else:
                    product_variety_id = obj.product_variety_id if obj else None
                if product_variety_id:
                    kwargs["queryset"] = kwargs["queryset"].filter(product_variety_id=product_variety_id)
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            return formfield

        if db_field.name == "product_size_kind":
            if hasattr(request, 'organization'):
                kwargs["queryset"] = ProductSizeKind.objects.filter(organization=request.organization, is_enabled=True)
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            return formfield

        if db_field.name == "product_mass_volume_kind":
            if hasattr(request, 'organization'):
                kwargs["queryset"] = ProductMassVolumeKind.objects.filter(organization=request.organization, is_enabled=True)
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            return formfield

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    class Media:
        js = ('js/admin/forms/packhouses/catalogs/product_variety_size.js',)


class ProductProviderBenefactorInline(admin.TabularInline):
    model = ProductProviderBenefactor
    extra = 0

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        if 'name' in formset.form.base_fields:
            formset.form.base_fields['name'].widget = UppercaseTextInputWidget()
        return formset


@admin.register(ProductProvider)
class ProductProviderAdmin(admin.ModelAdmin):
    list_display = (
    'name', 'alias', 'state', 'city', 'neighborhood', 'address', 'external_number', 'tax_id', 'phone_number',
    'is_enabled')
    list_filter = ('state', 'city', 'bank', 'is_enabled')
    search_fields = ('name', 'alias', 'neighborhood', 'address', 'tax_id', 'phone_number')
    fields = ('name', 'alias', 'state', 'city', 'district', 'neighborhood', 'postal_code', 'address', 'external_number',
              'internal_number', 'tax_id', 'phone_number', 'bank_account_number', 'bank', 'is_enabled', 'organization')
    inlines = [ProductProviderBenefactorInline]

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'name' in form.base_fields:
            form.base_fields['name'].widget = UppercaseTextInputWidget()
        if 'alias' in form.base_fields:
            form.base_fields['alias'].widget = UppercaseAlphanumericTextInputWidget()
        if 'address' in form.base_fields:
            form.base_fields['address'].widget = UppercaseTextInputWidget()
        if 'tax_id' in form.base_fields:
            form.base_fields['tax_id'].widget = UppercaseTextInputWidget()
        return form

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj and is_instance_used(obj, exclude=[Region, City, Bank, ProductProviderBenefactor, Organization]):
            readonly_fields.extend(['name', 'alias', 'organization'])
        return readonly_fields

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        user_profile = UserProfile.objects.get(user=request.user)
        country = user_profile.country
        if db_field.name == "state":
            kwargs["queryset"] = Region.objects.filter(country=country)
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda obj: obj.name
            return formfield
        elif db_field.name == "city":
            if 'state' in request.GET:
                state_id = request.GET.get('state')
                kwargs["queryset"] = City.objects.filter(region_id=state_id)
            else:
                kwargs["queryset"] = City.objects.filter(country=country)
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda obj: obj.name
            return formfield
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    class Media:
        js = ('js/admin/forms/packhouses/catalogs/product_provider.js',)


class ProductProducerBenefactorInline(admin.TabularInline):
    model = ProductProducerBenefactor
    extra = 0

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        if 'name' in formset.form.base_fields:
            formset.form.base_fields['name'].widget = UppercaseTextInputWidget()
        return formset


@admin.register(ProductProducer)
class ProductProducerAdmin(admin.ModelAdmin):
    list_display = (
    'name', 'alias', 'state', 'city', 'neighborhood', 'address', 'external_number', 'tax_id', 'phone_number',
    'is_enabled')
    list_filter = ('state', 'city', 'bank', 'is_enabled')
    search_fields = ('name', 'alias', 'neighborhood', 'address', 'tax_id', 'phone_number')
    fields = ('name', 'alias', 'state', 'city', 'district', 'postal_code', 'neighborhood', 'address', 'external_number',
              'internal_number', 'tax_id', 'email', 'phone_number', 'product_provider', 'bank_account_number', 'bank',
              'is_enabled', 'organization')
    inlines = [ProductProducerBenefactorInline]

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'name' in form.base_fields:
            form.base_fields['name'].widget = UppercaseTextInputWidget()
        if 'alias' in form.base_fields:
            form.base_fields['alias'].widget = UppercaseAlphanumericTextInputWidget()
        if 'district' in form.base_fields:
            form.base_fields['district'].widget = UppercaseTextInputWidget()
        if 'neighborhood' in form.base_fields:
            form.base_fields['neighborhood'].widget = UppercaseTextInputWidget()
        if 'address' in form.base_fields:
            form.base_fields['address'].widget = UppercaseTextInputWidget()
        if 'tax_id' in form.base_fields:
            form.base_fields['tax_id'].widget = UppercaseTextInputWidget()
        return form

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj and is_instance_used(obj, exclude=[Region, City, ProductProvider, Bank, Organization,
                                                  ProductProducerBenefactor]):
            readonly_fields.extend(['name', 'alias', 'organization'])
        return readonly_fields

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        user_profile = UserProfile.objects.get(user=request.user)
        country = user_profile.country
        if db_field.name == "state":
            kwargs["queryset"] = Region.objects.filter(country=country)
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda obj: obj.name
            return formfield
        elif db_field.name == "city":
            if 'state' in request.GET:
                state_id = request.GET.get('state')
                kwargs["queryset"] = City.objects.filter(region_id=state_id)
            else:
                kwargs["queryset"] = City.objects.filter(country=country)
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda obj: obj.name
            return formfield
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    class Media:
        js = ('js/admin/forms/packhouses/catalogs/product_producer.js',)


class ClientShipAddressInline(admin.StackedInline):
    model = ClientShipAddress
    extra = 1
    min_num = 1
    max_num = 1
    can_delete = False

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        if 'district' in formset.form.base_fields:
            formset.form.base_fields['district'].widget = UppercaseTextInputWidget()
        if 'neighborhood' in formset.form.base_fields:
            formset.form.base_fields['neighborhood'].widget = UppercaseTextInputWidget()
        if 'address' in formset.form.base_fields:
            formset.form.base_fields['address'].widget = UppercaseTextInputWidget()
        return formset

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        object_id = request.resolver_match.kwargs.get("object_id")
        obj = Client.objects.get(id=object_id) if object_id else None

        if db_field.name == "country":
            if request.POST:
                market_id = request.POST.get('market')
            else:
                market_id = obj.market_id if obj else None
            if market_id:
                market_countries_id = Market.objects.get(id=market_id).countries.values_list('id', flat=True)
                kwargs["queryset"] = Country.objects.filter(id__in=market_countries_id)
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
                kwargs["queryset"] = City.objects.filter(region_id=state_id)
            else:
                kwargs["queryset"] = City.objects.none()
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda item: item.name
            return formfield

        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'legal_category', 'tax_id', 'market', 'country', 'state', 'city', 'neighborhood', 'address',
                    'external_number', 'tax_id', 'contact_phone_number', 'is_enabled')
    # list_filter = ('market', 'legal_category', 'country', 'state', 'city', 'payment_kind', 'is_enabled')
    list_filter = ('market', 'legal_category', 'payment_kind', 'is_enabled')
    search_fields = ('name', 'tax_id', 'contact_phone_number')
    fields = ('name', 'market', 'country', 'state', 'city', 'district', 'postal_code', 'neighborhood', 'address',
              'external_number', 'internal_number', 'same_ship_address', 'legal_category', 'tax_id', 'fda', 'swift',
              'aba', 'clabe', 'bank', 'payment_kind', 'max_money_credit_limit', 'max_days_credit_limit', 'contact_name',
              'contact_email', 'contact_phone_number', 'is_enabled', 'organization')
    inlines = [ClientShipAddressInline]

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'name' in form.base_fields:
            form.base_fields['name'].widget = UppercaseTextInputWidget()
        if 'district' in form.base_fields:
            form.base_fields['district'].widget = UppercaseTextInputWidget()
        if 'neighborhood' in form.base_fields:
            form.base_fields['neighborhood'].widget = UppercaseTextInputWidget()
        if 'address' in form.base_fields:
            form.base_fields['address'].widget = UppercaseTextInputWidget()
        if 'contact_name' in form.base_fields:
            form.base_fields['contact_name'].widget = UppercaseTextInputWidget()
        return form

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj and is_instance_used(obj, exclude=[Market, Country, Region, City, LegalEntityCategory, Bank, PaymentKind,
                                                  Organization]):
            readonly_fields.extend(['name', 'organization'])
        return readonly_fields

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        object_id = request.resolver_match.kwargs.get("object_id")
        obj = Client.objects.get(id=object_id) if object_id else None

        if db_field.name == "market":
            kwargs["queryset"] = Market.objects.filter(is_enabled=True)  # TODO: Filtrar por organización
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda item: item.name
            return formfield

        if db_field.name == "country":
            if request.POST:
                market_id = request.POST.get('market')
            else:
                market_id = obj.market_id if obj else None
            if market_id:
                market_countries_id = Market.objects.get(id=market_id).countries.values_list('id', flat=True)
                kwargs["queryset"] = Country.objects.filter(id__in=market_countries_id)
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
                kwargs["queryset"] = City.objects.filter(region_id=state_id)
            else:
                kwargs["queryset"] = City.objects.none()
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda item: item.name
            return formfield

        if db_field.name == "legal_category":
            kwargs["queryset"] = LegalEntityCategory.objects.all()
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda item: item.name
            return formfield

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    class Media:
        js = ('js/admin/forms/packhouses/catalogs/client.js',)


@admin.register(Gatherer)
class GathererAdmin(admin.ModelAdmin):
    list_display = (
    'name', 'zone', 'tax_registry_code', 'state', 'city', 'postal_code', 'address', 'email', 'phone_number', 'vehicle',
    'is_enabled')
    list_filter = (StateFilterUserCountry, 'is_enabled')
    search_fields = ('name', 'zone', 'tax_registry_code', 'address', 'email', 'phone_number')
    fields = (
    'name', 'zone', 'tax_registry_code', 'population_registry_code', 'social_number_code', 'state', 'city', 'district',
    'neighborhood', 'postal_code', 'address', 'external_number', 'internal_number', 'email', 'phone_number', 'vehicle',
    'is_enabled', 'organization')

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'name' in form.base_fields:
            form.base_fields['name'].widget = UppercaseTextInputWidget()
        if 'zone' in form.base_fields:
            form.base_fields['zone'].widget = UppercaseTextInputWidget()
        if 'address' in form.base_fields:
            form.base_fields['address'].widget = UppercaseTextInputWidget()
        return form

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj and is_instance_used(obj, exclude=[Region, Vehicle, City, Organization]):
            readonly_fields.extend(['name', 'organization'])
        return readonly_fields

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        user_profile = UserProfile.objects.get(
            user=request.user)  # TODO: Obtener el país de la organización en lugar del país del usuario
        country = user_profile.country
        object_id = request.resolver_match.kwargs.get("object_id")
        obj = Gatherer.objects.get(id=object_id) if object_id else None

        # Lógica para el campo "state"
        if db_field.name == "state":
            if obj:
                country_id = obj.state.country_id
            else:
                country_id = country.id
            if country_id:
                kwargs["queryset"] = Region.objects.filter(country_id=country_id)
            else:
                kwargs["queryset"] = Region.objects.none()
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda item: item.name
            return formfield

        # Lógica para el campo "city"
        if db_field.name == "city":
            if request.POST:
                state_id = request.POST.get('state')
            else:
                state_id = obj.state.id if obj else None
            if state_id:
                kwargs["queryset"] = City.objects.filter(region_id=state_id)
            else:
                kwargs["queryset"] = City.objects.none()
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda item: item.name
            return formfield

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    class Media:
        js = (
            'js/admin/forms/packhouses/catalogs/gatherer.js',
            'js/admin/forms/packhouses/catalogs/state-city.js',
        )


class MaquiladoraClientInline(admin.StackedInline):
    model = MaquiladoraClient
    extra = 0

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        if 'name' in formset.form.base_fields:
            formset.form.base_fields['name'].widget = UppercaseTextInputWidget()
        if 'tax_id' in formset.form.base_fields:
            formset.form.base_fields['tax_id'].widget = UppercaseTextInputWidget()
        if 'zone' in formset.form.base_fields:
            formset.form.base_fields['zone'].widget = AutoGrowingTextareaWidget()
        if 'district' in formset.form.base_fields:
            formset.form.base_fields['district'].widget = UppercaseTextInputWidget()
        if 'neighborhood' in formset.form.base_fields:
            formset.form.base_fields['neighborhood'].widget = UppercaseTextInputWidget()
        if 'address' in formset.form.base_fields:
            formset.form.base_fields['address'].widget = UppercaseTextInputWidget()
        return formset

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "country":
            market_id = None
            if 'market' in request.GET:
                market_id = request.GET.get('market')
            if market_id:
                market_countries_id = Market.objects.get(id=market_id).countries.all().values_list('id', flat=True)
                kwargs["queryset"] = Country.objects.filter(id__in=market_countries_id)
            else:
                kwargs["queryset"] = Country.objects.none()
        elif db_field.name == "state":
            if 'country' in request.GET:
                country_id = request.GET.get('country')
                kwargs["queryset"] = Region.objects.filter(country_id=country_id)
            else:
                kwargs["queryset"] = Region.objects.none()
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda obj: obj.name
            return formfield
        elif db_field.name == "city":
            if 'state' in request.GET:
                state_id = request.GET.get('state')
                kwargs["queryset"] = City.objects.filter(region_id=state_id)
            else:
                kwargs["queryset"] = City.objects.none()
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda obj: obj.name
            return formfield
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    class Media:
        js = ('js/admin/forms/packhouses/catalogs/maquiladora_client_inline.js',)


@admin.register(Maquiladora)
class MaquiladoraAdmin(admin.ModelAdmin):
    list_display = (
    'name', 'zone', 'tax_registry_code', 'state', 'city', 'email', 'phone_number', 'vehicle', 'is_enabled')
    list_filter = ('state', 'city', 'vehicle', 'is_enabled')
    search_fields = ('name', 'zone', 'tax_registry_code', 'address', 'email', 'phone_number')
    fields = (
    'name', 'zone', 'tax_registry_code', 'population_registry_code', 'social_number_code', 'state', 'city', 'district',
    'neighborhood', 'postal_code', 'address', 'external_number', 'internal_number', 'email', 'phone_number', 'vehicle',
    'is_enabled', 'organization')
    inlines = [MaquiladoraClientInline]

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'name' in form.base_fields:
            form.base_fields['name'].widget = UppercaseTextInputWidget()
        if 'tax_registry_code' in form.base_fields:
            form.base_fields['tax_registry_code'].widget = UppercaseTextInputWidget()
        if 'population_registry_code' in form.base_fields:
            form.base_fields['population_registry_code'].widget = UppercaseTextInputWidget()
        if 'social_number_code' in form.base_fields:
            form.base_fields['social_number_code'].widget = UppercaseTextInputWidget()
        if 'zone' in form.base_fields:
            form.base_fields['zone'].widget = UppercaseTextInputWidget()
        if 'address' in form.base_fields:
            form.base_fields['address'].widget = UppercaseTextInputWidget()
        return form

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj and is_instance_used(obj, exclude=[Region, City, Vehicle, Organization]):
            readonly_fields.extend(['name', 'organization'])
        return readonly_fields

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        user_profile = UserProfile.objects.get(user=request.user)
        country = user_profile.country
        if db_field.name == "state":
            kwargs["queryset"] = Region.objects.filter(country=country)
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda obj: obj.name
            return formfield
        elif db_field.name == "city":
            if 'state' in request.GET:
                state_id = request.GET.get('state')
                kwargs["queryset"] = City.objects.filter(region_id=state_id)
            else:
                kwargs["queryset"] = City.objects.filter(country=country)
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda obj: obj.name
            return formfield
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    class Media:
        js = ('js/admin/forms/packhouses/catalogs/maquiladora.js',)


class OrchardCertificationInline(admin.TabularInline):
    model = OrchardCertification
    form = OrchardCertificationForm
    extra = 0

    class Media:
        js = ('js/admin/forms/packhouses/catalogs/orchard_certification_inline.js',)


@admin.register(Orchard)
class OrchardAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'producer', 'product_classification_kind', 'is_enabled')
    list_filter = ('product_classification_kind', 'safety_authority_registration_date', 'is_enabled')
    search_fields = ('name', 'code', 'producer__name')
    fields = ('name', 'code', 'producer', 'safety_authority_registration_date', 'state', 'city', 'district', 'ha',
              'product_classification_kind', 'phytosanitary_certificate', 'is_enabled', 'organization')
    inlines = [OrchardCertificationInline]

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'name' in form.base_fields:
            form.base_fields['name'].widget = UppercaseTextInputWidget()
        return form

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj and is_instance_used(obj, exclude=[ProductProducer, Region, City, OrchardProductClassificationKind,
                                                  Organization]):
            readonly_fields.extend(['name', 'organization'])
        return readonly_fields

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        object_id = request.resolver_match.kwargs.get("object_id")
        obj = Orchard.objects.get(id=object_id) if object_id else None

        user_profile = UserProfile.objects.get(user=request.user)
        country = user_profile.country

        if db_field.name == "state":
            if country:
                kwargs["queryset"] = Region.objects.filter(country=country)
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
                kwargs["queryset"] = City.objects.filter(region_id=state_id)
            else:
                kwargs["queryset"] = City.objects.none()
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda item: item.name
            return formfield

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    class Media:
        js = ('js/admin/forms/packhouses/catalogs/orchard.js',)


class ServiceProviderBenefactorInline(admin.TabularInline):
    model = ServiceProviderBenefactor
    extra = 0


@admin.register(Supply)
class SupplyAdmin(admin.ModelAdmin):
    list_display = ('name', 'kind', 'is_enabled')
    list_filter = ('kind', 'is_enabled')


@admin.register(OrchardCertification)
class OrchardCertificationAdmin(admin.ModelAdmin):
    pass


class CrewChiefInline(admin.TabularInline):
    model = CrewChief
    extra = 0

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        formset.form.base_fields['name'].widget = UppercaseTextInputWidget()
        return formset


@admin.register(CrewChief)
class CrewChiefAdmin(admin.ModelAdmin):
    @uppercase_form_charfield('name')
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return form


class HarvestingCrewBeneficiaryInline(admin.TabularInline):
    model = HarvestingCrewBeneficiary
    extra = 0

    @uppercase_formset_charfield('name')
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        return formset

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        object_id = request.resolver_match.kwargs.get("object_id")
        obj = OrganizationProfile.objects.get(id=object_id) if object_id else None
        organization_id = None

        if request.POST:
            organization_id = request.POST.get('organization')
        elif obj:
            organization_id = obj.organization.id if obj.organization else None

        if not organization_id:
            organization_id = request.organization.id

        if db_field.name == "bank":
            kwargs["queryset"] = Bank.objects.filter(
                organization_id=organization_id) if organization_id else VehicleKind.objects.all()

        if "queryset" in kwargs:
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda item: item.name
            return formfield

        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class VehicleInline(admin.StackedInline):
    model = Vehicle
    extra = 0

    list_display = (
    'name', 'kind', 'brand', 'model', 'license_plate', 'serial_number', 'ownership', 'fuel', 'is_enabled')
    list_filter = ('kind', 'brand', 'ownership', 'fuel', 'is_enabled')
    search_fields = ('name', 'model', 'license_plate', 'serial_number', 'comments')
    fields = ('name', 'kind', 'brand', 'model', 'license_plate', 'serial_number', 'color', 'scope', 'ownership', 'fuel',
              'comments', 'is_enabled')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        object_id = request.resolver_match.kwargs.get("object_id")
        obj = OrganizationProfile.objects.get(id=object_id) if object_id else None
        organization_id = None

        if request.POST:
            organization_id = request.POST.get('organization')
        elif obj:
            organization_id = obj.organization.id if obj.organization else None

        if not organization_id:
            organization_id = request.organization.id

        if db_field.name == "kind":
            kwargs["queryset"] = VehicleKind.objects.filter(
                organization_id=organization_id) if organization_id else VehicleKind.objects.all()
        if db_field.name == "brand":
            kwargs["queryset"] = VehicleBrand.objects.filter(
                organization_id=organization_id) if organization_id else VehicleBrand.objects.all()
        if db_field.name == "ownership":
            kwargs["queryset"] = VehicleOwnershipKind.objects.filter(
                organization_id=organization_id) if organization_id else VehicleBrand.objects.all()
        if db_field.name == "fuel":
            kwargs["queryset"] = VehicleFuelKind.objects.filter(
                organization_id=organization_id) if organization_id else VehicleBrand.objects.all()

        if "queryset" in kwargs:
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda item: item.name
            return formfield

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    @uppercase_formset_charfield('name')
    @uppercase_formset_charfield('license_plate')
    @uppercase_formset_charfield('serial_number')
    @uppercase_formset_charfield('color')
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        return formset


class HarvestingPaymentSettingInline(admin.StackedInline):
    model = HarvestingPaymentSetting
    min_num = 1
    max_num = 2
    formset = HarvestingPaymentSettingInlineFormSet

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        return formset


@admin.register(HarvestingCrew)
class HarvestingCrewAdmin(admin.ModelAdmin):
    form = HarvestingCrewForm
    list_display = (
    'name', 'harvesting_crew_provider', 'crew_chief', 'certification_name', 'persons_number', 'is_enabled')
    list_filter = ('is_enabled',)
    fields = (
    'harvesting_crew_provider', 'name', 'certification_name', 'crew_chief', 'persons_number', 'comments', 'is_enabled')
    inlines = [HarvestingPaymentSettingInline, ]

    @uppercase_form_charfield('name')
    @uppercase_form_charfield('certification_name')
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return form

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        obj_id = request.resolver_match.kwargs.get("object_id")
        obj = HarvestingCrew.objects.get(id=obj_id) if obj_id else None

        if db_field.name == "crew_chief":
            if request.POST:
                harvesting_crew_provider_id = request.POST.get('harvesting_crew_provider')
            else:
                harvesting_crew_provider_id = obj.harvesting_crew_provider_id if obj else None

            if harvesting_crew_provider_id:
                kwargs["queryset"] = CrewChief.objects.filter(harvesting_crew_provider_id=harvesting_crew_provider_id)
            else:
                kwargs["queryset"] = CrewChief.objects.none()

            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda item: item.name
            return formfield

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    class Media:
        js = ('js/admin/forms/packhouses/catalogs/harvesting_crew.js',)


@admin.register(HarvestingCrewProvider)
class HarvestingCrewProviderAdmin(ByOrganizationAdminMixin):
    inlines = [HarvestingCrewBeneficiaryInline, VehicleInline, CrewChiefInline]
    fields = ('name', 'tax_id', 'is_enabled')

    @uppercase_form_charfield('name')
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return form


@admin.register(SupplyProvider)
class SupplyProviderAdmin(admin.ModelAdmin):
    pass


@admin.register(MeshBagKind)
class MeshBagKindAdmin(admin.ModelAdmin):
    pass


@admin.register(MeshBagFilmKind)
class MeshBagFilmKindAdmin(admin.ModelAdmin):
    pass


@admin.register(MeshBag)
class MeshBagAdmin(admin.ModelAdmin):
    pass


@admin.register(ServiceProvider)
class ServiceProviderAdmin(admin.ModelAdmin):
    inlines = [ServiceProviderBenefactorInline]


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    pass


@admin.register(AuthorityBoxKind)
class AuthorityBoxKindAdmin(admin.ModelAdmin):
    pass


@admin.register(BoxKind)
class BoxKindAdmin(admin.ModelAdmin):
    pass


@admin.register(WeighingScale)
class WeighingScaleAdmin(admin.ModelAdmin):
    pass


@admin.register(ColdChamber)
class ColdChamberAdmin(admin.ModelAdmin):
    pass


@admin.register(Pallet)
class PalletAdmin(admin.ModelAdmin):
    pass


@admin.register(PalletExpense)
class PalletExpenseAdmin(admin.ModelAdmin):
    pass


@admin.register(ProductPackaging)
class ProductPackagingAdmin(admin.ModelAdmin):
    pass


@admin.register(ExportingCompany)
class ExportingCompanyAdmin(admin.ModelAdmin):
    list_display = (
    'name', 'legal_category', 'tax_id', 'city', 'address', 'external_number', 'contact_phone_number', 'is_enabled')
    list_filter = ('country', 'legal_category', 'payment_kind', 'is_enabled')
    search_fields = ('name', 'tax_id', 'contact_phone_number')
    fields = (
    'name', 'country', 'state', 'city', 'district', 'postal_code', 'neighborhood', 'address', 'external_number',
    'internal_number', 'legal_category', 'tax_id', 'clabe', 'bank', 'payment_kind', 'contact_name', 'contact_email',
    'contact_phone_number', 'is_enabled', 'organization')

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'name' in form.base_fields:
            form.base_fields['name'].widget = UppercaseTextInputWidget()
        if 'district' in form.base_fields:
            form.base_fields['district'].widget = UppercaseTextInputWidget()
        if 'neighborhood' in form.base_fields:
            form.base_fields['neighborhood'].widget = UppercaseTextInputWidget()
        if 'address' in form.base_fields:
            form.base_fields['address'].widget = UppercaseTextInputWidget()
        if 'contact_name' in form.base_fields:
            form.base_fields['contact_name'].widget = UppercaseTextInputWidget()
        return form

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        object_id = request.resolver_match.kwargs.get("object_id")
        obj = ExportingCompany.objects.get(id=object_id) if object_id else None

        # Lógica para el campo "country"
        if db_field.name == "country":
            kwargs["queryset"] = Country.objects.all()
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda item: item.name
            return formfield

        # Lógica para el campo "state"
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

        # Lógica para el campo "city"
        if db_field.name == "city":
            if request.POST:
                state_id = request.POST.get('state')
            else:
                state_id = obj.state_id if obj else None
            if state_id:
                kwargs["queryset"] = City.objects.filter(region_id=state_id)
            else:
                kwargs["queryset"] = City.objects.none()
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda item: item.name
            return formfield

        # Lógica para campo "legal_category"
        if db_field.name == "legal_category":
            kwargs["queryset"] = LegalEntityCategory.objects.all()
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda item: item.name
            return formfield

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    class Media:
        js = ('js/admin/forms/packhouses/catalogs/country-state-city.js',)


@admin.register(Transfer)
class TransferAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'name' in form.base_fields:
            form.base_fields['name'].widget = UppercaseTextInputWidget()
        return form


@admin.register(LocalTransporter)
class LocalTransporterAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'name' in form.base_fields:
            form.base_fields['name'].widget = UppercaseTextInputWidget()
        return form


@admin.register(BorderToDestinationTransporter)
class BorderToDestinationTransporterAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'name' in form.base_fields:
            form.base_fields['name'].widget = UppercaseTextInputWidget()
        return form


@admin.register(CustomsBroker)
class CustomsBrokerAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'name' in form.base_fields:
            form.base_fields['name'].widget = UppercaseTextInputWidget()
        return form


@admin.register(Vessel)
class VesselAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'name' in form.base_fields:
            form.base_fields['name'].widget = UppercaseTextInputWidget()
        return form


@admin.register(Airline)
class AirlineAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'name' in form.base_fields:
            form.base_fields['name'].widget = UppercaseTextInputWidget()
        return form


@admin.register(InsuranceCompany)
class InsuranceCompanyAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'name' in form.base_fields:
            form.base_fields['name'].widget = UppercaseTextInputWidget()
        return form


# Providers

class ProviderBeneficiaryInline(admin.StackedInline):
    model = ProviderBeneficiary
    extra = 1
    min_num = 1
    can_delete = True

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        return formset


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_enabled', 'organization')
    list_filter = ('is_enabled',)
    inlines = (ProviderBeneficiaryInline,)


@admin.register(ProviderBeneficiary)
class ProviderBeneficiaryAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'name' in form.base_fields:
            form.base_fields['name'].widget = UppercaseTextInputWidget()
        return form

# /Providers
