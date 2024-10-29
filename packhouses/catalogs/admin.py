from django.contrib import admin
from .models import (
    Market, KGCostMarket, MarketClass, MarketStandardProductSize, Product, ProductVariety, ProductVarietySize,
    ProductHarvestKind, Bank, ProductProvider, ProductProviderBenefactor,
    ProductProducer, ProductProducerBenefactor, PaymentKind, VehicleOwnershipKind, VehicleKind, VehicleFuelKind,
    Vehicle,
    Collector, Client, Maquilador, MaquiladorClient, OrchardProductClassification, Orchard, OrchardCertificationKind,
    OrchardCertificationVerifier, OrchardCertification, HarvestCrew, SupplyUnitKind, SupplyKind, SupplyKindRelation,
    Supply, Supplier, MeshBagKind, MeshBagFilmKind, MeshBag, ServiceProvider, ServiceProviderBenefactor, Service,
    AuthorityBoxKind, BoxKind, WeighingScale, ColdChamber, Pallet, PalletExpense, ProductPackaging
)
from .forms import ProductVarietySizeForm, ProductVarietySizeInlineForm
from django.contrib.admin.widgets import ForeignKeyRawIdWidget
from django_ckeditor_5.widgets import CKEditor5Widget
from django import forms
from django.db import models

from cities_light.models import Country, Region, City

from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils.html import format_html
from common.widgets import UppercaseTextInputWidget, UppercaseAlphanumericTextInputWidget, AutoGrowingTextareaWidget
from .filters import ProductVarietySizeProductFilter

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

    inlines = [KGCostMarketInline, MarketClassInline, MarketStandardProductSizeInline]

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['name'].widget = UppercaseTextInputWidget()
        form.base_fields['alias'].widget = UppercaseAlphanumericTextInputWidget()
        form.base_fields['address_label'].widget = CKEditor5Widget()
        return form


class ProductVarietyInline(admin.TabularInline):
    model = ProductVariety
    extra = 0

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        formset.form.base_fields['name'].widget = UppercaseTextInputWidget()
        formset.form.base_fields['description'].widget = AutoGrowingTextareaWidget()
        return formset


class ProductVarietySizeInline(admin.StackedInline):
    model = ProductVarietySize
    form = ProductVarietySizeInlineForm
    extra = 0


class ProductProviderBenefactorInline(admin.TabularInline):
    model = ProductProviderBenefactor
    extra = 0


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
        if self.instance and self.instance.product_kind:
            allowed_kinds = SupplyKindRelation.objects.filter(from_kind=self.instance.product_kind).values_list(
                'to_kind', flat=True)
            self.fields['related_supply'].queryset = Supply.objects.filter(kind__in=allowed_kinds)


@admin.register(ProductHarvestKind)
class ProductVarietyHarvestKindAdmin(admin.ModelAdmin):
    pass


@admin.register(ProductVariety)
class ProductVarietyAdmin(admin.ModelAdmin):
    list_display = ('name', 'product', 'description', 'is_enabled')
    list_filter = ('product', 'is_enabled',)
    search_fields = ('name', 'product__name', 'description')
    inlines = [ProductVarietySizeInline]

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['name'].widget = UppercaseTextInputWidget()
        form.base_fields['description'].widget = AutoGrowingTextareaWidget()
        return form

    class Media:
        js = ('js/admin/forms/product_variety_inline_size.js',)


@admin.register(ProductVarietySize)
class ProductVarietySizeAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'product_name', 'variety', 'market', 'quality_kind', 'harvest_kind', 'product_kind', 'is_enabled',
        'order')
    list_filter = (
        'market', ProductVarietySizeProductFilter, 'variety', 'quality_kind', 'harvest_kind', 'product_kind',
        'is_enabled'
    )
    search_fields = (
        'name', 'variety__product__name', 'variety__name', 'market__name', 'quality_kind__name', 'harvest_kind__name',
        'product_kind__name'
    )

    def product_name(self, obj):
        return obj.product_name

    product_name.short_description = _('Product')

    form = ProductVarietySizeForm

    class Media:
        js = ('js/admin/forms/product_variety_size.js',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_enabled')
    list_filter = ('is_enabled',)
    search_fields = ('name', 'description')
    inlines = [ProductVarietyInline]

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['name'].widget = UppercaseTextInputWidget()
        # form.base_fields['description'].widget = AutoGrowingTextareaWidget()
        return form


@admin.register(Bank)
class BankAdmin(admin.ModelAdmin):
    pass


@admin.register(ProductProvider)
class ProductProviderAdmin(admin.ModelAdmin):
    inlines = [ProductProviderBenefactorInline]


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
