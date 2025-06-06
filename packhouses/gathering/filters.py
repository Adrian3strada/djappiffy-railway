from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import ScheduleHarvest
from packhouses.catalogs.models import OrchardCertification
from packhouses.catalogs.settings import ORCHARD_PRODUCT_CLASSIFICATION_CHOICES
from rangefilter.filters import DateRangeFilter

class ByProductProviderForOrganizationScheduleHarvestFilter(admin.SimpleListFilter):
    title = _('Product Prodiver')
    parameter_name = 'scheduleharvest_product_provider'

    def has_output(self):
        return True
    
    def lookups(self, request, model_admin):
        used_providers = (
            model_admin.model.objects.filter(
                product_provider__category='product_provider',
                product_provider__is_enabled=True,
                product_provider__organization=request.organization
            )
            .values_list('product_provider__id', 'product_provider__name')
            .distinct()
        )
        return used_providers

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(product_provider__id=self.value())
        return queryset
    
class ByOrchardProductProducerForOrganizationScheduleHarvestFilter(admin.SimpleListFilter):
    title = _('Product Producer')
    parameter_name = 'scheduleharvest_product_producer'

    def has_output(self):
        return True
    
    def lookups(self, request, model_admin):
        qs = model_admin.model.objects.filter(
            orchard__isnull=False,
            orchard__producer__isnull=False,
            orchard__organization=request.organization
        ).values_list('orchard__producer__id', 'orchard__producer__name').distinct()
        return qs

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(orchard__producer__id=self.value())
        return queryset
    
class ByHarvestingCrewForOrganizationScheduleHarvestFilter(admin.SimpleListFilter):
    title = _('Harvesting Crew')
    parameter_name = 'harvesting_crew'
    
    def lookups(self, request, model_admin):
        crew_ids = (
            model_admin.model.objects.filter(
                scheduleharvestharvestingcrew__harvesting_crew__isnull=False,
                scheduleharvestharvestingcrew__harvesting_crew__organization=request.organization
            )
            .values_list(
                'scheduleharvestharvestingcrew__harvesting_crew__id',
                'scheduleharvestharvestingcrew__harvesting_crew__name'
            )
            .distinct()
        )
        return crew_ids

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(
                scheduleharvestharvestingcrew__harvesting_crew__id=self.value()
            )
        return queryset
    
class ByProductForOrganizationScheduleHarvestFilter(admin.SimpleListFilter):
    title = _('Product')
    parameter_name = 'product'

    def lookups(self, request, model_admin):
        qs = model_admin.model.objects.filter(
            product__isnull=False,
            product__organization=request.organization
        ).values_list('product__id', 'product__name').distinct()
        return qs

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(product__id=self.value())
        return queryset
    
class ByProductVarietyForOrganizationScheduleHarvestFilter(admin.SimpleListFilter):
    title = _('Product Variety')
    parameter_name = 'product_variety'  

    def lookups(self, request, model_admin):
        qs = model_admin.model.objects.filter(
            product_variety__isnull=False,
            product_variety__product__organization=request.organization  
        ).values_list('product_variety__id', 'product_variety__name').distinct()
        return qs

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(product_variety__id=self.value())
        return queryset
    
class ByProductPhenologyForOrganizationScheduleHarvestFilter(admin.SimpleListFilter):
    title = _('Product Phenology')
    parameter_name = 'product_phenology'  

    def lookups(self, request, model_admin):
        qs = model_admin.model.objects.filter(
            product_phenology__isnull=False,
            product_phenology__product__organization=request.organization  
        ).values_list('product_phenology__id', 'product_phenology__name').distinct()
        return qs

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(product_phenology__id=self.value())
        return queryset
    
   
class ByOrchardProductCategoryForOrganizationScheduleHarvestFilter(admin.SimpleListFilter):
    title = _('Product Category')
    parameter_name = 'orchard_product_category'

    def lookups(self, request, model_admin):
        # Obtener valores únicos de categoría usados
        used_categories = (
            model_admin.model.objects.filter(
                orchard__isnull=False,
                orchard__category__isnull=False,
                orchard__organization=request.organization
            )
            .values_list('orchard__category', flat=True)
            .distinct()
        )

        choices_dict = dict(ORCHARD_PRODUCT_CLASSIFICATION_CHOICES)
        return [(cat, choices_dict.get(cat, cat)) for cat in used_categories]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(orchard__category=self.value())
        return queryset
    
class HarvestingCategoryFilter(admin.SimpleListFilter):
    title = _('Harvesting Category') 
    parameter_name = 'category'     

    def lookups(self, request, model_admin):
        return ScheduleHarvest._meta.get_field('category').choices

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(category=self.value())
        return queryset

class GathererFilter(admin.SimpleListFilter):
    title = _('Gatherer')
    parameter_name = 'gatherer'

    def lookups(self, request, model_admin):
        qs = model_admin.model.objects.filter(
            gatherer__isnull=False
        ).values_list('gatherer__id', 'gatherer__name').distinct()
        return qs

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(gatherer__id=self.value())
        return queryset
    
class MaquiladoraFilter(admin.SimpleListFilter):
    title = _('Maquiladora')
    parameter_name = 'maquiladora'

    def lookups(self, request, model_admin):
        qs = model_admin.model.objects.filter(
            maquiladora__isnull=False
        ).values_list('maquiladora__id', 'maquiladora__name').distinct()
        return qs

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(maquiladora__id=self.value())
        return queryset

class SchedulingTypeFilter(admin.SimpleListFilter):
    title = _('Scheduling Type')
    parameter_name = 'is_scheduled'

    def lookups(self, request, model_admin):
        return [
            ('1', _('Scheduled Harvest')),
            ('0', _('Unscheduled Harvest')),
        ]

    def queryset(self, request, queryset):
        if self.value() == '1':
            return queryset.filter(is_scheduled=True)
        if self.value() == '0':
            return queryset.filter(is_scheduled=False)
        return queryset

class ByOrchardCertificationForOrganizationScheduleHarvestFilter(admin.SimpleListFilter):
    title = _('Orchard Certification')
    parameter_name = 'orchard_certification'

    def lookups(self, request, model_admin):
        certs = OrchardCertification.objects.filter(
            orchard__scheduleharvest__isnull=False,
            orchard__organization=request.organization
        ).values_list(
            'certification_kind__id',
            'certification_kind__name'
        ).distinct()

        return list(certs)

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(
                orchard__orchardcertification__certification_kind__id=self.value()
            ).distinct()
        return queryset

class GatheringDateRangeFilter(DateRangeFilter):
    template = "admin/rangefilter/date_filter_4_0.html"