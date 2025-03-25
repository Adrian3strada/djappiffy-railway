from django.contrib import admin
from .models import IncomingProduct, PalletReceived, PalletContainer
from common.base.mixins import (ByOrganizationAdminMixin)
from packhouses.gathering.models import ScheduleHarvest, ScheduleHarvestHarvestingCrew, ScheduleHarvestVehicle
from django.utils.translation import gettext_lazy as _
import nested_admin
from .mixins import CustomNestedStackedInlineMixin
from .forms import ScheduleHarvestVehicleForm
from nested_admin import NestedStackedInline
from packhouses.catalogs.models import Supply

# Inlines para el corte
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

# Inline para los pallets

class PalletContainerInline(nested_admin.NestedTabularInline):
    model = PalletContainer
    extra = 0

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        organization = None
        if hasattr(request, 'organization'):
            organization = request.organization

        if db_field.name == "harvest_container":
            kwargs["queryset"] = Supply.objects.filter(organization=organization, is_enabled=True)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class PalletReceivedInline(CustomNestedStackedInlineMixin, admin.StackedInline):
    model = PalletReceived
    inlines = [PalletContainerInline]
    fields = ('ooid', 'gross_weight', 'container_tare', 'platform_tare', 'net_weight')
    extra = 0

    def get_readonly_fields(self, request, obj=None):
        # Obtener los campos readonly predefinidos
        readonly_fields = list(super().get_readonly_fields(request, obj))

        # Campos siempre readonly cuando el objeto no existe
        if not obj:
            readonly_fields.append('ooid')

        # Campos readonly para objetos existentes
        if obj and obj.pk:
            readonly_fields.append('ooid')

        # Si el estado del corte está cerrado o cancelado, todos los campos son readonly
        if obj and obj.status in ['closed', 'canceled']:
            # Filtrar solo los campos definidos en el admin que realmente existen
            readonly_fields.extend([
                field for field in self.fields if hasattr(obj, field)
            ])

        return readonly_fields

    class Media:
        js = ('js/admin/forms/packhouses/receiving/pallets_received_inline.js',)

# Reciba
@admin.register(IncomingProduct)
class IncomingProductAdmin(ByOrganizationAdminMixin, nested_admin.NestedModelAdmin):
    list_display = ('get_scheduleharvest_ooid', 'get_scheduleharvest_orchard', 'get_scheduleharvest_harvest_date', 'get_scheduleharvest_product',
                    'guide_number', 'status',)
    fields = ('status', 'phytosanitary_certificate', 'guide_number', 'weighing_record_number', 'public_weighing_scale', 'public_weight_result', 'pallets_received', 'packhouse_weight_result',
              'mrl', 'kg_sample', 'boxes_assigned', 'full_boxes', 'empty_boxes', 'missing_boxes', 'average_per_box', 'current_kg_available')
    inlines = [PalletReceivedInline, ScheduleHarvestInline]
    # readonly_fields = ('pallets_received', 'boxes_assigned', 'missing_boxes', 'average_per_box', 'current_kg_available')

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

    get_scheduleharvest_ooid.admin_order_field = 'scheduleharvest__ooid'
    get_scheduleharvest_ooid.short_description = _('Harvest Number')
    get_scheduleharvest_harvest_date.admin_order_field = 'scheduleharvest__harvest_date'
    get_scheduleharvest_harvest_date.short_description = _('Harvest Date')
    get_scheduleharvest_product.admin_order_field = 'scheduleharvest__product'
    get_scheduleharvest_product.short_description = _('Product')
    get_scheduleharvest_orchard.admin_order_field = 'scheduleharvest__orchard'
    get_scheduleharvest_orchard.short_description = _('Orchard')

    class Media:
        js = ('js/admin/forms/packhouses/receiving/incoming_product.js', )
