from django.contrib import admin
from .models import (Market, KGCostMarket, Product, ProductVariety, ProductVarietySize, ProductQualityKind,
                     ProductVarietySizeKind,
                     ProductVarietyHarvestKind,
                     Bank,
                     ProductProvider,
                     ProductProviderBenefactor,
                     Supply, SupplyKindRelation, ProductProviderBenefactor,
                     )
from django_ckeditor_5.widgets import CKEditor5Widget
import nested_admin
from django import forms
from django.db import models
from nested_admin.nested import NestedTabularInline, NestedStackedInline, NestedModelAdmin
from adminsortable2.admin import SortableAdminMixin, SortableAdminBase, SortableInlineAdminMixin


# Register your models here.


class KGCostMarketInline(admin.TabularInline):
    model = KGCostMarket
    extra = 0


class MarketAdminForm(forms.ModelForm):
    class Meta:
        model = Market
        fields = '__all__'
        widgets = {
            'address_label': CKEditor5Widget(),  # Usa CKEditor para el campo 'address'
        }


@admin.register(Market)
class MarketAdmin(admin.ModelAdmin):
    form = MarketAdminForm
    inlines = [KGCostMarketInline]


class ProductVarietyInline(admin.TabularInline):
    model = ProductVariety
    extra = 0

    formfield_overrides = {
        # Ajusta el Textarea para el campo description con solo 1 línea
        models.TextField: {'widget': forms.Textarea(attrs={'rows': 1})},
    }


@admin.register(ProductQualityKind)
class ProductQualityKindAdmin(admin.ModelAdmin):
    pass


@admin.register(ProductVarietyHarvestKind)
class ProductVarietyHarvestKindAdmin(admin.ModelAdmin):
    pass


@admin.register(ProductVarietySizeKind)
class ProductVarietySizeKindAdmin(admin.ModelAdmin):
    pass


class ProductVarietySizeInline(admin.StackedInline):
    model = ProductVarietySize
    extra = 0

    class Media:
        # js = ('collapsible_stacked_inlines.js',)
        pass


@admin.register(ProductVarietySize)
class ProductVarietySizeAdmin(SortableAdminMixin, admin.ModelAdmin):
    pass


@admin.register(ProductVariety)
class ProductVarietyAdmin(SortableAdminBase, admin.ModelAdmin):
    inlines = [ProductVarietySizeInline]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductVarietyInline]


# Product Providers


@admin.register(Bank)
class BankAdmin(admin.ModelAdmin):
    pass


class ProductProviderBenefactorInline(admin.TabularInline):
    model = ProductProviderBenefactor
    extra = 0


@admin.register(ProductProvider)
class ProductProviderAdmin(admin.ModelAdmin):
    inlines = (ProductProviderBenefactorInline,)


# supplies...


class SupplyAdminForm(forms.ModelForm):
    class Meta:
        model = Supply
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.kind:
            allowed_kinds = SupplyKindRelation.objects.filter(from_kind=self.instance.kind).values_list('to_kind',
                                                                                                        flat=True)
            self.fields['related_supply'].queryset = Supply.objects.filter(kind__in=allowed_kinds)


@admin.register(Supply)
class SupplyAdmin(admin.ModelAdmin):
    form = SupplyAdminForm


@admin.register(SupplyKindRelation)
class SupplyKindRelationAdmin(admin.ModelAdmin):
    list_display = ('from_kind', 'to_kind', 'is_enabled')
    list_filter = ('from_kind', 'to_kind', 'is_enabled')
