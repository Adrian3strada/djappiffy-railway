from django.contrib import admin
from .models import IncomingProduct
from common.base.mixins import (ByOrganizationAdminMixin)
from packhouses.gathering.models import ScheduleHarvest, ScheduleHarvestHarvestingCrew, ScheduleHarvestVehicle
from django.utils.translation import gettext_lazy as _
import nested_admin
from .mixins import CustomNestedStackedInlineMixin
from .forms import ScheduleHarvestVehicleForm

# Register your models here.

class ScheduleHarvestHarvestingCrewInline(nested_admin.NestedTabularInline):
    model = ScheduleHarvestHarvestingCrew
    fields = ('provider', 'harvesting_crew')
    readonly_fields = ('provider', 'harvesting_crew') 
    extra = 0
    can_delete = False 
    show_title = True

class ScheduleHarvestVehicleInline(nested_admin.NestedTabularInline):
    model = ScheduleHarvestVehicle
    form = ScheduleHarvestVehicleForm  
    fields = ('provider', 'vehicle', 'stamp_vehicle_number')
    readonly_fields = ('provider', 'vehicle')
    extra = 0
    can_delete = False
    show_title = True

class ScheduleHarvestInline(CustomNestedStackedInlineMixin, admin.StackedInline):  
    model = ScheduleHarvest
    extra = 0  
    inlines = [ScheduleHarvestHarvestingCrewInline, ScheduleHarvestVehicleInline]
    fields = ('ooid', 'status', 'harvest_date', 'category', 'product_provider', 'product', 'product_variety', 
              'product_phenologies', 'product_harvest_size_kind', 'orchard', 'orchard_certification', 'market', 
              'weight_expected', 'weighing_scale', 'comments')
    readonly_fields = [field.name for field in ScheduleHarvest._meta.fields]  
    can_delete = False  
    can_add = False 
    show_title = False 

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'orchard_certification':  
            kwargs['disabled'] = True  
        return super().formfield_for_manytomany(db_field, request, **kwargs)


@admin.register(IncomingProduct)
class IncomingProductAdmin(ByOrganizationAdminMixin, nested_admin.NestedModelAdmin):
    list_display = ('get_scheduleharvest_ooid', 'status', 'get_scheduleharvest_harvest_date', 'get_scheduleharvest_product', 'get_scheduleharvest_orchard',
                    'guide_number',)  
    fields = ('status', 'guide_number', 'public_weighing_scale', 'public_weight_result', 'packhouse_weight_result', 'weighing_record_number', 'phytosanitary_certificate', 
              'mrl', 'pallets_received', 'kg_sample', 'boxes_assigned', 'full_boxes', 'empty_boxes', 'missing_boxes', 'current_kg')
    inlines = [ScheduleHarvestInline] 

    def get_scheduleharvest_ooid(self, obj):
        schedule_harvest = obj.scheduleharvest 
        return schedule_harvest.ooid if schedule_harvest else None

    def get_scheduleharvest_harvest_date(self, obj):
        schedule_harvest = obj.scheduleharvest
        return schedule_harvest.harvest_date if schedule_harvest else None

    def get_scheduleharvest_product(self, obj):
        schedule_harvest = obj.scheduleharvest
        return schedule_harvest.product if schedule_harvest else None

    def get_scheduleharvest_orchard(self, obj):
        schedule_harvest = obj.scheduleharvest
        return schedule_harvest.orchard if schedule_harvest else None

    get_scheduleharvest_ooid.short_description = _('Harvest Number')
    get_scheduleharvest_harvest_date.short_description = _('Harvest Date')
    get_scheduleharvest_product.short_description = _('Product')
    get_scheduleharvest_orchard.short_description = _('Orchard')

    class Media:
        js = ('js/admin/forms/packhouses/receiving/incoming_product.js',)