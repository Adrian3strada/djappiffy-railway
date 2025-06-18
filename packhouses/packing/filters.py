from django.contrib import admin
from .models import PackingPackage
from packhouses.catalogs.models import Market, ProductSize
from packhouses.receiving.models import Batch
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
