from django.contrib import admin
from .models import (
    Market, KGCostMarket, MarketClass, Product, ProductVariety, ProductVarietySize, ProductQualityKind,
    ProductVarietySizeKind, ProductVarietyHarvestKind, Bank, ProductProvider, ProductProviderBenefactor,
    ProductProducer, ProductProducerBenefactor, PaymentKind, VehicleOwnership, VehicleKind, VehicleFuel, Vehicle,
    Collector, Client, Maquiladora, MaquiladoraClient, OrchardProductClassification, Orchard, OrchardCertificationKind,
    OrchardCertificationVerifier, OrchardCertification, HarvestCrew, SupplyUnitKind, SupplyKind, SupplyKindRelation,
    Supply, Supplier, MeshBagKind, MeshBagFilmKind, MeshBag, ServiceProvider, ServiceProviderBenefactor, Service,
    AuthorityBoxKind, BoxKind, WeighingScale, ColdChamber, Pallet, PalletExpense, ProductPackaging
)
from django_ckeditor_5.widgets import CKEditor5Widget
from django import forms
from django.db import models


class KGCostMarketInline(admin.TabularInline):
    model = KGCostMarket
    extra = 0


class MarketAdminForm(forms.ModelForm):
    class Meta:
        model = Market
        fields = '__all__'
        widgets = {
            'address_label': CKEditor5Widget(),
        }


@admin.register(Market)
class MarketAdmin(admin.ModelAdmin):
    form = MarketAdminForm
    inlines = [KGCostMarketInline]


class ProductVarietyInline(admin.TabularInline):
    model = ProductVariety
    extra = 0
    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(attrs={'rows': 1})},
    }


class ProductVarietySizeInline(admin.StackedInline):
    model = ProductVarietySize
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
        if self.instance and self.instance.kind:
            allowed_kinds = SupplyKindRelation.objects.filter(from_kind=self.instance.kind).values_list('to_kind', flat=True)
            self.fields['related_supply'].queryset = Supply.objects.filter(kind__in=allowed_kinds)


@admin.register(ProductQualityKind)
class ProductQualityKindAdmin(admin.ModelAdmin):
    pass


@admin.register(ProductVarietyHarvestKind)
class ProductVarietyHarvestKindAdmin(admin.ModelAdmin):
    pass


@admin.register(ProductVarietySizeKind)
class ProductVarietySizeKindAdmin(admin.ModelAdmin):
    pass


@admin.register(ProductVarietySize)
class ProductVarietySizeAdmin(admin.ModelAdmin):
    pass


@admin.register(ProductVariety)
class ProductVarietyAdmin(admin.ModelAdmin):
    inlines = [ProductVarietySizeInline]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductVarietyInline]


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


@admin.register(MarketClass)
class MarketClassAdmin(admin.ModelAdmin):
    pass


@admin.register(PaymentKind)
class PaymentKindAdmin(admin.ModelAdmin):
    pass


@admin.register(VehicleOwnership)
class VehicleOwnershipAdmin(admin.ModelAdmin):
    pass


@admin.register(VehicleKind)
class VehicleKindAdmin(admin.ModelAdmin):
    pass


@admin.register(VehicleFuel)
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


@admin.register(Maquiladora)
class MaquiladoraAdmin(admin.ModelAdmin):
    pass


@admin.register(MaquiladoraClient)
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
