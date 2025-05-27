from django.contrib import admin
from .models import (IncomingProduct,)
from common.profiles.models import OrganizationProfile
from packhouses.catalogs.models import Orchard, Provider, Product
from packhouses.gathering.models import ScheduleHarvest
from django.utils.translation import gettext_lazy as _
from django.db.models import Count
from django.utils.translation import gettext_lazy as _
from packhouses.catalogs.utils import get_harvest_cutting_categories_choices

# Filtros personalizados para IncomingProduct
class ByOrchardForOrganizationIncomingProductFilter(admin.SimpleListFilter):
    title = _('Orchard')
    parameter_name = 'scheduleharvest_orchard'
    def has_output(self):
        return True

    def lookups(self, request, model_admin):
        orchards = (ScheduleHarvest.objects.filter( 
            orchard__organization=request.organization, incoming_product__isnull=False).values_list('orchard__id', flat=True)
        )
        orchards = Orchard.objects.filter(id__in=orchards)
        return [(orchard.id, orchard.name) for orchard in orchards]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(scheduleharvest__orchard__id=self.value())
        return queryset
    
class ByProviderForOrganizationIncomingProductFilter(admin.SimpleListFilter):
    title = _('Product Provider')
    parameter_name = 'scheduleharvest_product_provider'

    def has_output(self):
        return True

    def lookups(self, request, model_admin):
        product_providers = (ScheduleHarvest.objects.filter( 
            product_provider__organization=request.organization, incoming_product__isnull=False).values_list('product_provider__id', flat=True)
        )
        product_providers = Provider.objects.filter(id__in=product_providers)
        return [(provider.id, provider.name) for provider in product_providers]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(scheduleharvest__product_provider__id=self.value())
        return queryset

class ByProductForOrganizationIncomingProductFilter(admin.SimpleListFilter):
    title = _('Product')
    parameter_name = 'scheduleharvest_product'

    def has_output(self):
        return True

    def lookups(self, request, model_admin):
        products = (ScheduleHarvest.objects.filter( 
            product__organization=request.organization, incoming_product__isnull=False).values_list('product__id', flat=True)
        )
        products = Product.objects.filter(id__in=products)
        return [(product.id, product.name) for product in products]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(scheduleharvest__product__id=self.value())
        return queryset

class ByCategoryForOrganizationIncomingProductFilter(admin.SimpleListFilter):
    title = _('Category')
    parameter_name = 'scheduleharvest_category'

    def has_output(self):
        return True

    def lookups(self, request, model_admin):
        categories = ScheduleHarvest.objects.filter(
            incoming_product__organization=request.organization,incoming_product__isnull=False
        ).values_list('category', flat=True).distinct()
        choices = list(get_harvest_cutting_categories_choices())
        category_dict = dict(choices)
        
        return [(cat, category_dict.get(cat, cat)) for cat in categories]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(scheduleharvest__category=self.value())
        return queryset


# Filtros personalizados para Batch
class ByOrchardForOrganizationBatchFilter(admin.SimpleListFilter):
    title = _('Orchard')
    parameter_name = 'batch_orchard'
    def has_output(self):
        return True
    
    def lookups(self, request, model_admin):
        orchards = Orchard.objects.filter(
            organization=request.organization,
            scheduleharvest__incoming_product__batch__isnull=False
        ).distinct()
        return [(orchard.id, orchard.name) for orchard in orchards]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(
                incomingproduct__scheduleharvest__orchard__id=self.value()
            )
        return queryset
    
class ByProviderForOrganizationBatchFilter(admin.SimpleListFilter):
    title = _('Product Provider')
    parameter_name = 'batch_product_provider'
    def has_output(self):
        return True

    def lookups(self, request, model_admin):
        providers = Provider.objects.filter(
            organization=request.organization,
            scheduleharvest__incoming_product__batch__isnull=False
        ).distinct()
        return [(provider.id, provider.name) for provider in providers]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(
                incomingproduct__scheduleharvest__product_provider__id=self.value()
            )
        return queryset
    
class ByProductForOrganizationBatchFilter(admin.SimpleListFilter):
    title = _('Product')
    parameter_name = 'batch_product'

    def has_output(self):
        return True

    def lookups(self, request, model_admin):
        products = Product.objects.filter(
            organization=request.organization,
            scheduleharvest__incoming_product__batch__isnull=False
        ).distinct()
        return [(product.id, product.name) for product in products]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(
                incomingproduct__scheduleharvest__product__id=self.value()
            )
        return queryset

class ByCategoryForOrganizationBatchFilter(admin.SimpleListFilter):
    title = _('Category')
    parameter_name = 'batch_category'

    def has_output(self):
        return True

    def lookups(self, request, model_admin):
        categories = ScheduleHarvest.objects.filter(
            incoming_product__batch__organization=request.organization,
            incoming_product__isnull=False
        ).values_list('category', flat=True).distinct()

        choices = list(get_harvest_cutting_categories_choices())
        category_dict = dict(choices)
        
        return [(cat, category_dict.get(cat, cat)) for cat in categories]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(
                incomingproduct__scheduleharvest__category=self.value()
            )
        return queryset