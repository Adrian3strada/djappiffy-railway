from django.contrib import admin
from .models import (
    Market, KGCostMarket, MarketClass, MarketStandardProductSize, Product, ProductVariety, ProductVarietySize,
    ProductHarvestKind, ProductProvider, ProductProviderBenefactor,
    ProductProducer, ProductProducerBenefactor, PaymentKind, VehicleOwnershipKind, VehicleKind, VehicleFuelKind,
    Vehicle,
    Collector, Client, Maquilador, MaquiladorClient, OrchardProductClassification, Orchard, OrchardCertificationKind,
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

from organizations.models import Organization
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
    fields = ('name', 'alias', 'country', 'management_cost_per_kg', 'is_foreign', 'is_mixable',
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
        if obj and is_instance_used(obj, exclude=[MarketClass, MarketStandardProductSize, Country, Organization]):
            readonly_fields.extend(['name', 'alias', 'country', 'is_foreign', 'organization'])
        return readonly_fields


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
    list_display = ('name', 'description', 'is_enabled')
    list_filter = ('is_enabled',)
    search_fields = ('name', 'description')
    fields = ('name', 'description', 'is_enabled', 'organization')
    inlines = [ProductVarietyInline]

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'name' in form.base_fields:
            form.base_fields['name'].widget = UppercaseTextInputWidget()
        return form

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj and is_instance_used(obj, exclude=[Organization]):
            readonly_fields.extend(['name', 'organization'])
        return readonly_fields


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
    search_fields = ('name', 'product__name', 'description')
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
        'name', 'variety__product__name', 'variety__name', 'market__name', 'size_kind__name', 'harvest_kind__name',
        'volume_kind__name'
    )

    form = ProductVarietySizeForm

    def product(self, obj):
        return obj.variety.product.name
    product.short_description = _('Product')
    product.admin_order_field = 'variety__product__name'

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
    search_fields = ('name', 'alias', ProductProviderStateFilter, 'neighborhood', 'address', 'tax_id', 'phone_number')
    fields = ('organization', 'name', 'alias', 'state', 'city', 'district', 'neighborhood', 'postal_code', 'address', 'external_number', 'internal_number', 'tax_id', 'phone_number', 'bank_account_number', 'bank', 'is_enabled')
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
        js = ('js/admin/forms/catalogs/product_provider.js',)


class ProductProducerBenefactorInline(admin.TabularInline):
    model = ProductProducerBenefactor
    extra = 0


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


@admin.register(ProductHarvestKind)
class ProductVarietyHarvestKindAdmin(admin.ModelAdmin):
    pass








@admin.register(ProductProducer)
class ProductProducerAdmin(admin.ModelAdmin):
    inlines = [ProductProducerBenefactorInline]


@admin.register(Supply)
class SupplyAdmin(admin.ModelAdmin):
    form = SupplyAdminForm


@admin.register(SupplyKindRelation)
class SupplyKindRelationAdmin(admin.ModelAdmin):
    list_display = ('from_kind', 'to_kind', 'is_enabled')
    list_filter = ('from_kind', 'to_kind', 'is_enabled')


@admin.register(PaymentKind)
class PaymentKindAdmin(admin.ModelAdmin):
    pass


@admin.register(VehicleOwnershipKind)
class VehicleOwnershipAdmin(admin.ModelAdmin):
    pass


@admin.register(VehicleKind)
class VehicleKindAdmin(admin.ModelAdmin):
    pass


@admin.register(VehicleFuelKind)
class VehicleFuelAdmin(admin.ModelAdmin):
    pass


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    pass


@admin.register(Collector)
class CollectorAdmin(admin.ModelAdmin):
    pass


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    pass


@admin.register(Maquilador)
class MaquiladoraAdmin(admin.ModelAdmin):
    pass


@admin.register(MaquiladorClient)
class MaquiladoraClientAdmin(admin.ModelAdmin):
    pass


@admin.register(OrchardProductClassification)
class OrchardProductClassificationAdmin(admin.ModelAdmin):
    pass


@admin.register(Orchard)
class OrchardAdmin(admin.ModelAdmin):
    pass


@admin.register(OrchardCertificationKind)
class OrchardCertificationKindAdmin(admin.ModelAdmin):
    pass


@admin.register(OrchardCertificationVerifier)
class OrchardCertificationVerifierAdmin(admin.ModelAdmin):
    pass


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
