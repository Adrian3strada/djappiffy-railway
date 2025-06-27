from django.contrib import admin
from .models import PackingPackage, PackingPallet
from packhouses.catalogs.models import Market, ProductSize, Product, Pallet, ProductMarketClass, ProductRipeness, SizePackaging
from packhouses.receiving.models import Batch
from django.utils.translation import gettext_lazy as _
from django.utils.translation import gettext_lazy as _

#


class ByBatchForOrganizationPackingPackageFilter(admin.SimpleListFilter):
    title = _('Batch')
    parameter_name = 'batch'

    def lookups(self, request, model_admin):
        batches = Batch.objects.all()
        if hasattr(request, 'organization'):
            batch_ids = list(set(PackingPackage.objects.filter(organization=request.organization)
                                 .values_list('batch', flat=True).distinct())
                             )
            batches = batches.filter(id__in=batch_ids).order_by('ooid')
        return [(batch.id, batch.__str__()) for batch in batches]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(batch__id=self.value())
        return queryset


class ByMarketForOrganizationPackingPackageFilter(admin.SimpleListFilter):
    title = _('Market')
    parameter_name = 'market'

    def lookups(self, request, model_admin):
        markets = Market.objects.all()
        if hasattr(request, 'organization'):
            lookup_ids = list(set(PackingPackage.objects.filter(organization=request.organization)
                                 .values_list('market', flat=True).distinct())
                             )
            markets = markets.filter(id__in=lookup_ids).order_by('name')
        return [(market.id, market.name) for market in markets]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(market__id=self.value())
        return queryset


class ByProductSizeForOrganizationPackingPackageFilter(admin.SimpleListFilter):
    title = _('Product Size')
    parameter_name = 'product_size'

    def lookups(self, request, model_admin):
        product_sizes = ProductSize.objects.all()
        if hasattr(request, 'organization'):
            lookup_ids = list(set(PackingPackage.objects.filter(organization=request.organization)
                                  .values_list('product_size', flat=True).distinct())
                              )
            product_sizes = product_sizes.filter(id__in=lookup_ids).order_by('name')
        return [(product_size.id, f"{product_size.market.alias}: {product_size.name}") for product_size in product_sizes]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(product_size__id=self.value())
        return queryset


class ByProductMarketClassForOrganizationPackingPackageFilter(admin.SimpleListFilter):
    title = _('Product Market Class')
    parameter_name = 'product_market_class'

    def lookups(self, request, model_admin):
        queryset = ProductMarketClass.objects.all()
        if hasattr(request, 'organization'):
            lookup_ids = list(set(PackingPackage.objects.filter(organization=request.organization)
                                  .values_list('product_market_class', flat=True).distinct()))
            queryset = queryset.filter(id__in=lookup_ids).order_by('name')

        return [(obj.id, obj.name) for obj in queryset]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(product_market_class_id=self.value())
        return queryset


class ByProductRipenessForOrganizationPackingPackageFilter(admin.SimpleListFilter):
    title = _('Product Ripeness')
    parameter_name = 'product_ripeness'

    def lookups(self, request, model_admin):
        queryset = ProductRipeness.objects.all()
        if hasattr(request, 'organization'):
            lookup_ids = list(set(PackingPackage.objects.filter(organization=request.organization)
                                  .values_list('product_ripeness', flat=True).distinct()))
            queryset = queryset.filter(id__in=lookup_ids).order_by('name')

        return [(obj.id, obj.name) for obj in queryset]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(product_ripeness_id=self.value())
        return queryset


class BySizePackagingForOrganizationPackingPackageFilter(admin.SimpleListFilter):
    title = _('Size Packaging')
    parameter_name = 'size_packaging'

    def lookups(self, request, model_admin):
        queryset = SizePackaging.objects.all()
        if hasattr(request, 'organization'):
            lookup_ids = list(set(PackingPackage.objects.filter(organization=request.organization)
                                  .values_list('size_packaging', flat=True).distinct()))
            queryset = queryset.filter(id__in=lookup_ids).order_by('name')

        return [(obj.id, obj.name) for obj in queryset]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(size_packaging_id=self.value())
        return queryset


class ByPackingPalletForOrganizationPackingPackageFilter(admin.SimpleListFilter):
    title = _('Packing Pallet')
    parameter_name = 'packing_pallet'

    def lookups(self, request, model_admin):
        queryset = PackingPallet.objects.all()
        if hasattr(request, 'organization'):
            lookup_ids = list(set(PackingPackage.objects.filter(organization=request.organization)
                                  .values_list('packing_pallet', flat=True).distinct()))
            queryset = queryset.filter(id__in=lookup_ids).order_by('ooid')

        lookups = [(obj.id, obj.ooid) for obj in queryset]
        lookups.append((0, _('Null')))
        return lookups

    def queryset(self, request, queryset):
        if self.value() == '0':  # Filtrar valores nulos
            return queryset.filter(packing_pallet__isnull=True)
        elif self.value():
            return queryset.filter(packing_pallet_id=self.value())
        return queryset


class ByProductForOrganizationPackingPalletFilter(admin.SimpleListFilter):
    title = _('Product')
    parameter_name = 'product'

    def lookups(self, request, model_admin):
        products = Product.objects.all()
        if hasattr(request, 'organization'):
            lookup_ids = list(set(PackingPallet.objects.filter(organization=request.organization)
                                 .values_list('product', flat=True).distinct())
                             )
            products = products.filter(id__in=lookup_ids).order_by('name')
        return [(product.id, product.name) for product in products]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(product__id=self.value())
        return queryset


class ByMarketForOrganizationPackingPalletFilter(admin.SimpleListFilter):
    title = _('Market')
    parameter_name = 'market'

    def lookups(self, request, model_admin):
        markets = Market.objects.all()
        if hasattr(request, 'organization'):
            lookup_ids = list(set(PackingPallet.objects.filter(organization=request.organization)
                                 .values_list('market', flat=True).distinct())
                             )
            markets = markets.filter(id__in=lookup_ids).order_by('name')
        return [(market.id, market.name) for market in markets]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(market__id=self.value())
        return queryset


class ByProductSizeForOrganizationPackingPalletFilter(admin.SimpleListFilter):
    title = _('Product Size')
    parameter_name = 'product_size'

    def lookups(self, request, model_admin):
        product_sizes = ProductSize.objects.all()
        if hasattr(request, 'organization'):
            lookup_ids = list(set(PackingPallet.objects.filter(organization=request.organization)
                                  .values_list('product_sizes', flat=True).distinct())
                              )
            product_sizes = product_sizes.filter(id__in=lookup_ids).order_by('name')
        return [(ps.id, f"{ps.market.alias}: {ps.name}") for ps in product_sizes]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(product_sizes__id=self.value())
        return queryset



class ByPalletForOrganizationPackingPalletFilter(admin.SimpleListFilter):
    title = _('Pallet')
    parameter_name = 'pallet'

    def lookups(self, request, model_admin):
        pallets = Pallet.objects.all()
        if hasattr(request, 'organization'):
            lookup_ids = list(set(PackingPallet.objects.filter(organization=request.organization)
                                  .values_list('pallet', flat=True).distinct())
                              )
            pallets = pallets.filter(id__in=lookup_ids).order_by('name')
        return [(pallet.id, pallet.name) for pallet in pallets]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(pallet__id=self.value())
        return queryset
