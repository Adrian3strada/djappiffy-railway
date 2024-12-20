from django.contrib import admin

from common.billing.models import LegalEntityCategory
from .models import (
    Market, KGCostMarket, MarketClass, MarketStandardProductSize, Product, ProductVariety, ProductVarietySize,
    ProductHarvestKind, ProductProvider, ProductProviderBenefactor,
    ProductProducer, ProductProducerBenefactor, PaymentKind, VehicleOwnershipKind, VehicleKind, VehicleFuelKind,
    Vehicle,
    Gatherer, Client, ClientShipAddress, Maquiladora, MaquiladoraClient, OrchardProductClassificationKind, Orchard,
    OrchardCertificationKind,
    OrchardCertificationVerifier, OrchardCertification, HarvestCrew, SupplyUnitKind, SupplyKind, SupplyKindRelation,
    Supply, Supplier, MeshBagKind, MeshBagFilmKind, MeshBag, ServiceProvider, ServiceProviderBenefactor, Service,
    AuthorityBoxKind, BoxKind, WeighingScale, ColdChamber, Pallet, PalletExpense, ProductPackaging
)
from packhouses.packhouse_settings.models import Bank
from common.profiles.models import UserProfile
from .forms import ProductVarietySizeInlineForm, ProductVarietySizeForm, ProductVarietyInlineFormSet
from django.contrib.admin.widgets import ForeignKeyRawIdWidget
from django_ckeditor_5.widgets import CKEditor5Widget
from django import forms
from django.db import models

from organizations.models import Organization, OrganizationUser
from cities_light.models import Country, Region, City

from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils.html import format_html
from common.widgets import UppercaseTextInputWidget, UppercaseAlphanumericTextInputWidget, AutoGrowingTextareaWidget
from .filters import ProductVarietySizeProductFilter, ProductProviderStateFilter
from django.db.models.functions import Concat
from django.db.models import Value
from common.utils import is_instance_used
from django.core.exceptions import ValidationError
from adminsortable2.admin import SortableAdminMixin


admin.site.unregister(Country)
admin.site.unregister(Region)
admin.site.unregister(City)


class KGCostMarketInline(admin.TabularInline):
    model = KGCostMarket
    extra = 0

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        formset.form.base_fields['name'].widget = UppercaseTextInputWidget()
        return formset


class MarketClassInline(admin.TabularInline):
    model = MarketClass
    extra = 0

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        formset.form.base_fields['name'].widget = UppercaseTextInputWidget()
        return formset


class MarketStandardProductSizeInline(admin.TabularInline):
    model = MarketStandardProductSize
    extra = 0


@admin.register(Market)
class MarketAdmin(admin.ModelAdmin):
    list_display = ('name', 'alias', 'is_enabled')
    list_filter = ('is_enabled',)
    search_fields = ('name', 'alias')
    fields = ('name', 'alias', 'countries', 'management_cost_per_kg', 'is_foreign', 'is_mixable',
              'label_language', 'address_label', 'is_enabled', 'organization')
    inlines = [KGCostMarketInline, MarketClassInline, MarketStandardProductSizeInline]

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'name' in form.base_fields:
            form.base_fields['name'].widget = UppercaseTextInputWidget()
        if 'alias' in form.base_fields:
            form.base_fields['alias'].widget = UppercaseAlphanumericTextInputWidget()
        form.base_fields['address_label'].widget = CKEditor5Widget()
        return form

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj and is_instance_used(obj, exclude=[MarketClass, KGCostMarket, MarketStandardProductSize, Country, Organization]):
            readonly_fields.extend(['name', 'alias', 'countries', 'is_foreign', 'organization'])
        return readonly_fields

    def save_model(self, request, obj, form, change):
        if 'address_label' in form.cleaned_data and form.cleaned_data['address_label'] == '<p>&nbsp;</p>':
            obj.address_label = None
        super().save_model(request, obj, form, change)


class ProductVarietyInline(admin.TabularInline):
    model = ProductVariety
    extra = 0
    fields = ('name', 'description', 'is_enabled')
    formset = ProductVarietyInlineFormSet

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        if 'name' in formset.form.base_fields:
            formset.form.base_fields['name'].widget = UppercaseTextInputWidget()
        return formset


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('kind', 'description', 'is_enabled')
    list_filter = ('is_enabled',)
    search_fields = ('kind__name', 'description')
    fields = ('kind', 'description', 'is_enabled', 'organization')
    inlines = [ProductVarietyInline]

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj and is_instance_used(obj, exclude=[Organization]):
            readonly_fields.extend(['kind', 'organization'])
        return readonly_fields


@admin.register(ProductHarvestKind)
class ProductVarietyHarvestKindAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'product', 'is_enabled', 'order')
    list_filter = ('product', 'is_enabled')
    search_fields = ('name', 'product__kind__name')
    fields = ('name', 'product', 'is_enabled')
    ordering = ['order']


class ProductVarietySizeInline(admin.StackedInline):
    model = ProductVarietySize
    form = ProductVarietySizeInlineForm
    extra = 0

    class Meta:
        fields = '__all__'


@admin.register(ProductVariety)
class ProductVarietyAdmin(admin.ModelAdmin):
    list_display = ('name', 'product', 'description', 'is_enabled')
    list_filter = ('product', 'is_enabled',)
    search_fields = ('name', 'product__kind__name', 'description')
    fields = ('product', 'name', 'description', 'is_enabled')
    inlines = [ProductVarietySizeInline]

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'name' in form.base_fields:
            form.base_fields['name'].widget = UppercaseTextInputWidget()
        return form

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj and is_instance_used(obj, exclude=[Product]):
            readonly_fields.extend(['name', 'product'])
        return readonly_fields


@admin.register(ProductVarietySize)
class ProductVarietySizeAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'product', 'variety', 'market', 'size_kind', 'harvest_kind', 'volume_kind', 'is_enabled',
        'order')
    list_filter = (
        ProductVarietySizeProductFilter, 'variety', 'market', 'size_kind', 'harvest_kind', 'volume_kind',
        'is_enabled'
    )
    search_fields = (
        'name', 'variety__product__kind__name', 'variety__name', 'market__name', 'size_kind__name', 'harvest_kind__name',
        'volume_kind__name'
    )

    form = ProductVarietySizeForm

    def product(self, obj):
        return obj.variety.product.name
    product.short_description = _('Product')
    product.admin_order_field = 'variety__product__kind__name'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "variety":
            kwargs["queryset"] = ProductVariety.objects.select_related('product').all()
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda obj: f"{obj.product.name}: {obj.name}"
            return formfield
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


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
    list_display = ('name', 'alias', 'state', 'city', 'neighborhood', 'address', 'external_number', 'tax_id', 'phone_number', 'is_enabled')
    list_filter = ('state', 'city', 'bank', 'is_enabled')
    search_fields = ('name', 'alias', 'neighborhood', 'address', 'tax_id', 'phone_number')
    fields = ('name', 'alias', 'state', 'city', 'district', 'neighborhood', 'postal_code', 'address', 'external_number', 'internal_number', 'tax_id', 'phone_number', 'bank_account_number', 'bank', 'is_enabled', 'organization')
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
    list_display = ('name', 'alias', 'state', 'city', 'neighborhood', 'address', 'external_number', 'tax_id', 'phone_number', 'is_enabled')
    list_filter = ('state', 'city', 'bank', 'is_enabled')
    search_fields = ('name', 'alias', 'neighborhood', 'address', 'tax_id', 'phone_number')
    fields = ('name', 'alias', 'state', 'city', 'district', 'postal_code', 'neighborhood', 'address', 'external_number', 'internal_number', 'tax_id', 'email', 'phone_number', 'product_provider', 'bank_account_number', 'bank', 'is_enabled', 'organization')
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
        if obj and is_instance_used(obj, exclude=[Region, City, ProductProvider, Bank, Organization, ProductProducerBenefactor]):
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
    list_display = ('name', 'legal_category', 'tax_id', 'market', 'country', 'state', 'city', 'neighborhood', 'address', 'external_number', 'tax_id', 'contact_phone_number', 'is_enabled')
    # list_filter = ('market', 'legal_category', 'country', 'state', 'city', 'payment_kind', 'is_enabled')
    list_filter = ('market', 'legal_category', 'payment_kind', 'is_enabled')
    search_fields = ('name', 'tax_id', 'contact_phone_number')
    fields = ('name', 'market', 'country', 'state', 'city', 'district', 'postal_code', 'neighborhood', 'address', 'external_number', 'internal_number', 'same_ship_address', 'legal_category', 'tax_id', 'fda', 'swift', 'aba', 'clabe', 'bank', 'payment_kind', 'max_money_credit_limit', 'max_days_credit_limit', 'contact_name', 'contact_email', 'contact_phone_number', 'is_enabled', 'organization')
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


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('name', 'kind', 'brand', 'model', 'license_plate', 'serial_number', 'ownership', 'fuel', 'is_enabled')
    list_filter = ('kind', 'brand', 'ownership', 'fuel', 'is_enabled')
    search_fields = ('name', 'model', 'license_plate', 'serial_number', 'comments')
    fields = ('name', 'kind', 'brand', 'model', 'license_plate', 'serial_number', 'color', 'ownership', 'fuel', 'comments', 'is_enabled', 'organization')

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'name' in form.base_fields:
            form.base_fields['name'].widget = UppercaseTextInputWidget()
        if 'license_plate' in form.base_fields:
            form.base_fields['license_plate'].widget = UppercaseTextInputWidget()
        if 'serial_number' in form.base_fields:
            form.base_fields['serial_number'].widget = UppercaseTextInputWidget()
        if 'color' in form.base_fields:
            form.base_fields['color'].widget = UppercaseTextInputWidget()
        return form

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj and is_instance_used(obj, exclude=[Organization]):
            readonly_fields.extend(['name', 'organization'])
        return readonly_fields


@admin.register(Gatherer)
class GathererAdmin(admin.ModelAdmin):
    list_display = ('name', 'zone', 'tax_registry_code', 'state', 'city', 'postal_code', 'address', 'email', 'phone_number', 'vehicle', 'is_enabled')
    list_filter = ('state', 'city', 'vehicle', 'is_enabled')
    search_fields = ('name', 'zone', 'tax_registry_code', 'address', 'email', 'phone_number')
    fields = ('name', 'zone', 'tax_registry_code', 'population_registry_code', 'social_number_code', 'state', 'city', 'district', 'neighborhood', 'postal_code', 'address', 'external_number', 'internal_number', 'email', 'phone_number', 'vehicle', 'is_enabled', 'organization')

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
        if obj and is_instance_used(obj, exclude=[Region, City, Organization]):
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
        js = ('js/admin/forms/packhouses/catalogs/gatherer.js',)


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
    list_display = ('name', 'zone', 'tax_registry_code', 'state', 'city', 'email', 'phone_number', 'vehicle', 'is_enabled')
    list_filter = ('state', 'city', 'vehicle', 'is_enabled')
    search_fields = ('name', 'zone', 'tax_registry_code', 'address', 'email', 'phone_number')
    fields = ('name', 'zone', 'tax_registry_code', 'population_registry_code', 'social_number_code', 'state', 'city', 'district', 'neighborhood', 'postal_code', 'address', 'external_number', 'internal_number', 'email', 'phone_number', 'vehicle', 'is_enabled', 'organization')
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
    extra = 0


@admin.register(Orchard)
class OrchardAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'producer', 'product_classification_kind', 'is_enabled')
    list_filter = ('product_classification_kind', 'safety_authority_registration_date', 'is_enabled')
    search_fields = ('name', 'code', 'producer__name')
    fields = ('name', 'code', 'producer', 'safety_authority_registration_date', 'state', 'city', 'district', 'ha', 'product_classification_kind', 'phytosanitary_certificate', 'is_enabled', 'organization')
    inlines = [OrchardCertificationInline]

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'name' in form.base_fields:
            form.base_fields['name'].widget = UppercaseTextInputWidget()
        return form

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj and is_instance_used(obj, exclude=[ProductProducer, Region, City, OrchardProductClassificationKind, Organization]):
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


class SupplyAdminForm(forms.ModelForm):
    class Meta:
        model = Supply
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.volume_kind:
            allowed_kinds = SupplyKindRelation.objects.filter(from_kind=self.instance.volume_kind).values_list(
                'to_kind', flat=True)
            self.fields['related_supply'].queryset = Supply.objects.filter(kind__in=allowed_kinds)


@admin.register(Supply)
class SupplyAdmin(admin.ModelAdmin):
    form = SupplyAdminForm


@admin.register(SupplyKindRelation)
class SupplyKindRelationAdmin(admin.ModelAdmin):
    list_display = ('from_kind', 'to_kind', 'is_enabled')
    list_filter = ('from_kind', 'to_kind', 'is_enabled')


@admin.register(OrchardCertification)
class OrchardCertificationAdmin(admin.ModelAdmin):
    pass


@admin.register(HarvestCrew)
class HarvestCrewAdmin(admin.ModelAdmin):
    pass


@admin.register(SupplyUnitKind)
class SupplyUnitKindAdmin(admin.ModelAdmin):
    pass


@admin.register(SupplyKind)
class SupplyKindAdmin(admin.ModelAdmin):
    pass


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
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
