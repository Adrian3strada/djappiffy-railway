from django.contrib import admin
from .models import (IncomingProduct,)
from common.profiles.models import OrganizationProfile
from packhouses.catalogs.models import Orchard, Provider, Product
from packhouses.gathering.models import ScheduleHarvest
from django.utils.translation import gettext_lazy as _
from django.db.models import Count
from django.utils.translation import gettext_lazy as _
from packhouses.catalogs.utils import get_harvest_cutting_categories_choices
from packhouses.catalogs.settings import ORCHARD_PRODUCT_CLASSIFICATION_CHOICES
from rangefilter.filters import DateRangeFilter

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
    title = _('Harvesting Category')
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

class ByProductProducerForOrganizationIncomingProductFilter(admin.SimpleListFilter):
    title = _('Product Producer')
    parameter_name = 'scheduleharvest__orchard__producer'

    def has_output(self):
        return True
    
    def lookups(self, request, model_admin):
        qs = model_admin.model.objects.filter(
            scheduleharvest__orchard__isnull=False,
            scheduleharvest__orchard__producer__isnull=False,
            scheduleharvest__orchard__organization=request.organization
        ).values_list('scheduleharvest__orchard__producer__id', 
                      'scheduleharvest__orchard__producer__name').distinct()
        return qs

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(
                scheduleharvest__orchard__producer__id=self.value()
            )
        return queryset

class ByProductPhenologyForOrganizationIncomingProductFilter(admin.SimpleListFilter):
    title = _('Product Phenology')
    parameter_name = 'scheduleharvest__product_phenology'  

    def lookups(self, request, model_admin):
        qs = model_admin.model.objects.filter(
            scheduleharvest__product_phenology__isnull=False,
            scheduleharvest__product_phenology__product__organization=request.organization  
        ).values_list('scheduleharvest__product_phenology__id', 'scheduleharvest__product_phenology__name').distinct()
        return qs

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(scheduleharvest__product_phenology__id=self.value())
        return queryset

class ByOrchardProductCategoryForOrganizationIncomingProductFilter(admin.SimpleListFilter):
    title = _('Product Category')
    parameter_name = 'scheduleharvest__orchard_product_category'

    def lookups(self, request, model_admin):
        # Obtener valores únicos de categoría usados
        used_categories = (
            model_admin.model.objects.filter(
                scheduleharvest__orchard__isnull=False,
                scheduleharvest__orchard__category__isnull=False,
                scheduleharvest__orchard__organization=request.organization
            )
            .values_list('scheduleharvest__orchard__category', flat=True)
            .distinct()
        )

        choices_dict = dict(ORCHARD_PRODUCT_CLASSIFICATION_CHOICES)
        return [(cat, choices_dict.get(cat, cat)) for cat in used_categories]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(scheduleharvest__orchard__category=self.value())
        return queryset
    
class ByHarvestingCrewForOrganizationIncomingProductFilter(admin.SimpleListFilter):
    title = _('Harvesting Crew')
    parameter_name = 'scheduleharvest__harvesting_crew'
    
    def lookups(self, request, model_admin):
        crew_ids = (
            model_admin.model.objects.filter(
                scheduleharvest__scheduleharvestharvestingcrew__harvesting_crew__isnull=False,
                scheduleharvest__scheduleharvestharvestingcrew__harvesting_crew__organization=request.organization
            )
            .values_list(
                'scheduleharvest__scheduleharvestharvestingcrew__harvesting_crew__id',
                'scheduleharvest__scheduleharvestharvestingcrew__harvesting_crew__name'
            )
            .distinct()
        )
        return crew_ids

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(
                scheduleharvest__scheduleharvestharvestingcrew__harvesting_crew__id=self.value()
            )
        return queryset

class GathererForIncomingProductFilter(admin.SimpleListFilter):
    title = _('Gatherer')
    parameter_name = 'scheduleharvest__gatherer'

    def lookups(self, request, model_admin):
        qs = model_admin.model.objects.filter(
            scheduleharvest__gatherer__isnull=False
        ).values_list(
            'scheduleharvest__gatherer__id',
            'scheduleharvest__gatherer__name'
        ).distinct()
        return qs

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(
                scheduleharvest__gatherer__id=self.value()
            )
        return queryset

class MaquiladoraForIncomingProductFilter(admin.SimpleListFilter):
    title = _('Maquiladora')
    parameter_name = 'scheduleharvest__maquiladora'

    def lookups(self, request, model_admin):
        qs = model_admin.model.objects.filter(
            scheduleharvest__maquiladora__isnull=False
        ).values_list(
            'scheduleharvest__maquiladora__id',
            'scheduleharvest__maquiladora__name'
        ).distinct()
        return qs

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(
                scheduleharvest__maquiladora__id=self.value()
            )
        return queryset

class ByOrchardCertificationForOrganizationIncomingProductFilter(admin.SimpleListFilter):
    title = _('Orchard Certification')
    parameter_name = 'orchard_certification'

    def lookups(self, request, model_admin):
        certs = model_admin.model.objects.filter(
            scheduleharvest__orchard__orchardcertification__isnull=False,
            scheduleharvest__orchard__organization=request.organization
        ).values_list(
            'scheduleharvest__orchard__orchardcertification__certification_kind__id',
            'scheduleharvest__orchard__orchardcertification__certification_kind__name'
        ).distinct()
        return list(certs)

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(
                scheduleharvest__orchard__orchardcertification__certification_kind__id=self.value()
            ).distinct()
        return queryset

class SchedulingTypeFilter(admin.SimpleListFilter):
    title = _('Scheduling Type')
    parameter_name = 'scheduleharvest_is_scheduled'

    def lookups(self, request, model_admin):
        return [
            ('1', _('Scheduled Harvest')),
            ('0', _('Unscheduled Harvest')),
        ]

    def queryset(self, request, queryset):
        if self.value() == '1':
            return queryset.filter(scheduleharvest__is_scheduled=True)
        if self.value() == '0':
            return queryset.filter(scheduleharvest__is_scheduled=False)
        return queryset
    
class ByProductProducerForOrganizationIncomingProductFilter(admin.SimpleListFilter):
    title = _('Product Producer')
    parameter_name = 'scheduleharvest__orchard__producer'

    def has_output(self):
        return True
    
    def lookups(self, request, model_admin):
        qs = model_admin.model.objects.filter(
            scheduleharvest__orchard__isnull=False,
            scheduleharvest__orchard__producer__isnull=False,
            scheduleharvest__orchard__organization=request.organization
        ).values_list('scheduleharvest__orchard__producer__id', 
                      'scheduleharvest__orchard__producer__name').distinct()
        return qs

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(
                scheduleharvest__orchard__producer__id=self.value()
            )
        return queryset

class ByProductPhenologyForOrganizationIncomingProductFilter(admin.SimpleListFilter):
    title = _('Product Phenology')
    parameter_name = 'scheduleharvest__product_phenology'  

    def lookups(self, request, model_admin):
        qs = model_admin.model.objects.filter(
            scheduleharvest__product_phenology__isnull=False,
            scheduleharvest__product_phenology__product__organization=request.organization  
        ).values_list('scheduleharvest__product_phenology__id', 'scheduleharvest__product_phenology__name').distinct()
        return qs

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(scheduleharvest__product_phenology__id=self.value())
        return queryset

class ByOrchardProductCategoryForOrganizationIncomingProductFilter(admin.SimpleListFilter):
    title = _('Product Category')
    parameter_name = 'scheduleharvest__orchard_product_category'

    def lookups(self, request, model_admin):
        # Obtener valores únicos de categoría usados
        used_categories = (
            model_admin.model.objects.filter(
                scheduleharvest__orchard__isnull=False,
                scheduleharvest__orchard__category__isnull=False,
                scheduleharvest__orchard__organization=request.organization
            )
            .values_list('scheduleharvest__orchard__category', flat=True)
            .distinct()
        )

        choices_dict = dict(ORCHARD_PRODUCT_CLASSIFICATION_CHOICES)
        return [(cat, choices_dict.get(cat, cat)) for cat in used_categories]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(scheduleharvest__orchard__category=self.value())
        return queryset
    
class ByHarvestingCrewForOrganizationIncomingProductFilter(admin.SimpleListFilter):
    title = _('Harvesting Crew')
    parameter_name = 'scheduleharvest__harvesting_crew'
    
    def lookups(self, request, model_admin):
        crew_ids = (
            model_admin.model.objects.filter(
                scheduleharvest__scheduleharvestharvestingcrew__harvesting_crew__isnull=False,
                scheduleharvest__scheduleharvestharvestingcrew__harvesting_crew__organization=request.organization
            )
            .values_list(
                'scheduleharvest__scheduleharvestharvestingcrew__harvesting_crew__id',
                'scheduleharvest__scheduleharvestharvestingcrew__harvesting_crew__name'
            )
            .distinct()
        )
        return crew_ids

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(
                scheduleharvest__scheduleharvestharvestingcrew__harvesting_crew__id=self.value()
            )
        return queryset

class GathererForIncomingProductFilter(admin.SimpleListFilter):
    title = _('Gatherer')
    parameter_name = 'scheduleharvest__gatherer'

    def lookups(self, request, model_admin):
        qs = model_admin.model.objects.filter(
            scheduleharvest__gatherer__isnull=False
        ).values_list(
            'scheduleharvest__gatherer__id',
            'scheduleharvest__gatherer__name'
        ).distinct()
        return qs

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(
                scheduleharvest__gatherer__id=self.value()
            )
        return queryset

class MaquiladoraForIncomingProductFilter(admin.SimpleListFilter):
    title = _('Maquiladora')
    parameter_name = 'scheduleharvest__maquiladora'

    def lookups(self, request, model_admin):
        qs = model_admin.model.objects.filter(
            scheduleharvest__maquiladora__isnull=False
        ).values_list(
            'scheduleharvest__maquiladora__id',
            'scheduleharvest__maquiladora__name'
        ).distinct()
        return qs

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(
                scheduleharvest__maquiladora__id=self.value()
            )
        return queryset

class ByOrchardCertificationForOrganizationIncomingProductFilter(admin.SimpleListFilter):
    title = _('Orchard Certification')
    parameter_name = 'orchard_certification'

    def lookups(self, request, model_admin):
        certs = model_admin.model.objects.filter(
            scheduleharvest__orchard__orchardcertification__isnull=False,
            scheduleharvest__orchard__organization=request.organization
        ).values_list(
            'scheduleharvest__orchard__orchardcertification__certification_kind__id',
            'scheduleharvest__orchard__orchardcertification__certification_kind__name'
        ).distinct()
        return list(certs)

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(
                scheduleharvest__orchard__orchardcertification__certification_kind__id=self.value()
            ).distinct()
        return queryset

class SchedulingTypeFilter(admin.SimpleListFilter):
    title = _('Scheduling Type')
    parameter_name = 'scheduleharvest_is_scheduled'

    def lookups(self, request, model_admin):
        return [
            ('1', _('Scheduled Harvest')),
            ('0', _('Unscheduled Harvest')),
        ]

    def queryset(self, request, queryset):
        if self.value() == '1':
            return queryset.filter(scheduleharvest__is_scheduled=True)
        if self.value() == '0':
            return queryset.filter(scheduleharvest__is_scheduled=False)
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
    parameter_name = 'incomingproduct__scheduleharvest__product_provider'
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
    parameter_name = 'incomingproduct__scheduleharvest__product'

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
            return queryset.filter(incomingproduct__scheduleharvest__product=self.value())
        return queryset

class ByCategoryForOrganizationBatchFilter(admin.SimpleListFilter):
    title = _('Harvesting Category')
    parameter_name = 'incomingproduct__scheduleharvest__category'

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
    
class ByProductProducerForOrganizationBatchFilter(admin.SimpleListFilter):
    title = _('Product Producer')
    parameter_name = 'incomingproduct__scheduleharvest__orchard__producer'

    def has_output(self):
        return True

    def lookups(self, request, model_admin):
        qs = model_admin.model.objects.filter(
            incomingproduct__scheduleharvest__orchard__isnull=False,
            incomingproduct__scheduleharvest__orchard__producer__isnull=False,
            incomingproduct__scheduleharvest__orchard__organization=request.organization
        ).values_list(
            'incomingproduct__scheduleharvest__orchard__producer__id',
            'incomingproduct__scheduleharvest__orchard__producer__name'
        ).distinct()
        return qs

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(
                incomingproduct__scheduleharvest__orchard__producer__id=self.value()
            )
        return queryset

class ByProductPhenologyForOrganizationBatchFilter(admin.SimpleListFilter):
    title = _('Product Phenology')
    parameter_name = 'incomingproduct__scheduleharvest__product_phenology'

    def lookups(self, request, model_admin):
        qs = model_admin.model.objects.filter(
            incomingproduct__scheduleharvest__product_phenology__isnull=False,
            incomingproduct__scheduleharvest__product_phenology__product__organization=request.organization
        ).values_list(
            'incomingproduct__scheduleharvest__product_phenology__id',
            'incomingproduct__scheduleharvest__product_phenology__name'
        ).distinct()
        return qs

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(
                incomingproduct__scheduleharvest__product_phenology__id=self.value()
            )
        return queryset

class ByOrchardProductCategoryForOrganizationBatchFilter(admin.SimpleListFilter):
    title = _('Product Category')
    parameter_name = 'incomingproduct__scheduleharvest__orchard_product_category'

    def lookups(self, request, model_admin):
        # Obtener valores únicos de categoría usados
        used_categories = (
            model_admin.model.objects.filter(
                incomingproduct__scheduleharvest__orchard__isnull=False,
                incomingproduct__scheduleharvest__orchard__category__isnull=False,
                incomingproduct__scheduleharvest__orchard__organization=request.organization
            )
            .values_list('incomingproduct__scheduleharvest__orchard__category', flat=True)
            .distinct()
        )

        choices_dict = dict(ORCHARD_PRODUCT_CLASSIFICATION_CHOICES)
        return [(cat, choices_dict.get(cat, cat)) for cat in used_categories]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(incomingproduct__scheduleharvest__orchard__category=self.value())
        return queryset 

class ByHarvestingCrewForOrganizationBatchFilter(admin.SimpleListFilter):
    title = _('Harvesting Crew')
    parameter_name = 'incomingproduct__scheduleharvest__harvesting_crew'
    
    def lookups(self, request, model_admin):
        crew_ids = (
            model_admin.model.objects.filter(
                incomingproduct__scheduleharvest__scheduleharvestharvestingcrew__harvesting_crew__isnull=False,
                incomingproduct__scheduleharvest__scheduleharvestharvestingcrew__harvesting_crew__organization=request.organization
            )
            .values_list(
                'incomingproduct__scheduleharvest__scheduleharvestharvestingcrew__harvesting_crew__id',
                'incomingproduct__scheduleharvest__scheduleharvestharvestingcrew__harvesting_crew__name'
            )
            .distinct()
        )
        return crew_ids

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(
                incomingproduct__scheduleharvest__scheduleharvestharvestingcrew__harvesting_crew__id=self.value()
            )
        return queryset

class GathererForBatchFilter(admin.SimpleListFilter):
    title = _('Gatherer')
    parameter_name = 'incomingproduct__scheduleharvest__gatherer'

    def lookups(self, request, model_admin):
        qs = model_admin.model.objects.filter(
            incomingproduct__scheduleharvest__gatherer__isnull=False
        ).values_list(
            'incomingproduct__scheduleharvest__gatherer__id',
            'incomingproduct__scheduleharvest__gatherer__name'
        ).distinct()
        return qs

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(
                incomingproduct__scheduleharvest__gatherer__id=self.value()
            )
        return queryset

class MaquiladoraForBatchFilter(admin.SimpleListFilter):
    title = _('Maquiladora')
    parameter_name = 'incomingproduct__scheduleharvest__maquiladora'

    def lookups(self, request, model_admin):
        qs = model_admin.model.objects.filter(
            incomingproduct__scheduleharvest__maquiladora__isnull=False
        ).values_list(
            'incomingproduct__scheduleharvest__maquiladora__id',
            'incomingproduct__scheduleharvest__maquiladora__name'
        ).distinct()
        return qs

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(
                incomingproduct__scheduleharvest__maquiladora__id=self.value()
            )
        return queryset

class ByOrchardCertificationForOrganizationBatchFilter(admin.SimpleListFilter):
    title = _('Orchard Certification')
    parameter_name = 'orchard_certification'

    def lookups(self, request, model_admin):
        certs = model_admin.model.objects.filter(
            incomingproduct__scheduleharvest__orchard__orchardcertification__isnull=False,
            incomingproduct__scheduleharvest__orchard__organization=request.organization
        ).values_list(
            'incomingproduct__scheduleharvest__orchard__orchardcertification__certification_kind__id',
            'incomingproduct__scheduleharvest__orchard__orchardcertification__certification_kind__name'
        ).distinct()
        return list(certs)

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(
                incomingproduct__scheduleharvest__orchard__orchardcertification__certification_kind__id=self.value()
            ).distinct()
        return queryset

class SchedulingTypeForBatchFilter(admin.SimpleListFilter):
    title = _('Scheduling Type')
    parameter_name = 'scheduleharvest_is_scheduled'

    def lookups(self, request, model_admin):
        return [
            ('1', _('Scheduled Harvest')),
            ('0', _('Unscheduled Harvest')),
        ]

    def queryset(self, request, queryset):
        if self.value() == '1':
            return queryset.filter(incomingproduct__scheduleharvest__is_scheduled=True)
        if self.value() == '0':
            return queryset.filter(incomingproduct__scheduleharvest__is_scheduled=False)
        return queryset

class BatchTypeFilter(admin.SimpleListFilter):
    title = _('Batch Type')
    parameter_name = 'batch_type'

    def lookups(self, request, model_admin):
        return [
            ('parent', _('Parent Batch')),
            ('child', _('Child Batch')),
            ('independent', _('Independent Batch')),
        ]

    def queryset(self, request, queryset):
        value = self.value()
        if not value:
            return queryset
        
        # Filtrado manual porque es lógica Python y no del ORM
        batch_ids = []
        for batch in queryset:
            if value == 'parent' and batch.is_parent:
                batch_ids.append(batch.pk)
            elif value == 'child' and batch.is_child and not batch.is_parent:
                batch_ids.append(batch.pk)
            elif value == 'independent' and not batch.is_child and not batch.is_parent:
                batch_ids.append(batch.pk)

        return queryset.filter(pk__in=batch_ids)

# Filtros personalizados para FoodSafety
class ByOrchardCertificationForOrganizationFoodSafetyFilter(admin.SimpleListFilter):
    title = _('Orchard Certification')
    parameter_name = 'orchard_certification'

    def lookups(self, request, model_admin):
        certs = model_admin.model.objects.filter(
            batch__incomingproduct__scheduleharvest__orchard__orchardcertification__isnull=False,
            batch__incomingproduct__scheduleharvest__orchard__organization=request.organization
        ).values_list(
            'batch__incomingproduct__scheduleharvest__orchard__orchardcertification__certification_kind__id',
            'batch__incomingproduct__scheduleharvest__orchard__orchardcertification__certification_kind__name'
        ).distinct()
        return list(certs)

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(
                batch__incomingproduct__scheduleharvest__orchard__orchardcertification__certification_kind__id=self.value()
            ).distinct()
        return queryset

class DateRangeFilter(DateRangeFilter):
    title = 'Received Date'
    template = "admin/rangefilter/date_filter_4_0.html"