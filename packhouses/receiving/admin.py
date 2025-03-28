from django.contrib import admin
from packhouses.gathering.models import ScheduleHarvest, ScheduleHarvestHarvestingCrew, ScheduleHarvestVehicle
from packhouses.catalogs.models import Supply
from packhouses.catalogs.utils import get_harvest_cutting_categories_choices
from .models import IncomingProduct, PalletReceived, PalletContainer
from common.base.mixins import (ByOrganizationAdminMixin)
from django.utils.translation import gettext_lazy as _
from .mixins import CustomNestedStackedInlineMixin
from .forms import ScheduleHarvestVehicleForm
from .filters import (ByOrchardForOrganizationIncomingProductFilter, ByProviderForOrganizationIncomingProductFilter, ByProductForOrganizationIncomingProductFilter,
                      ByCategoryForOrganizationIncomingProductFilter)
from .utils import update_pallet_numbers
from common.base.decorators import uppercase_formset_charfield, uppercase_alphanumeric_formset_charfield
from common.base.decorators import uppercase_form_charfield, uppercase_alphanumeric_form_charfield
import nested_admin

# Inlines para datos del corte
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
    #class Media:
     #   js = ('js/admin/forms/packhouses/receiving/stamp_vehicle_inline.js', )

# Inlines para los pallets
class PalletContainerInline(nested_admin.NestedTabularInline):
    model = PalletContainer
    extra = 0

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        form = formset.form
        for field in form.base_fields.values():
            field.widget.can_add_related = False
            field.widget.can_change_related = False
            field.widget.can_delete_related = False
            field.widget.can_view_related = False
        return formset

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
    fields = ('ooid', 'gross_weight', 'total_boxes', 'container_tare', 'platform_tare', 'net_weight')
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


        return readonly_fields

    class Media:
        js = ('js/admin/forms/packhouses/receiving/pallets_received_inline.js',)

# Reciba
@admin.register(IncomingProduct)
class IncomingProductAdmin(ByOrganizationAdminMixin, nested_admin.NestedModelAdmin):
    list_display = ('get_scheduleharvest_ooid', 'get_scheduleharvest_harvest_date', 'get_scheduleharvest_category', 'get_scheduleharvest_orchard', 'get_scheduleharvest_product_provider',
                    'get_scheduleharvest_product', 'status','generate_actions_buttons')
    fields = ('status', 'phytosanitary_certificate', 'guide_number', 'weighing_record_number', 'public_weighing_scale', 'public_weight_result', 'pallets_received', 'packhouse_weight_result',
              'mrl', 'kg_sample', 'boxes_assigned', 'full_boxes', 'empty_boxes', 'missing_boxes', 'average_per_box', 'current_kg_available')
    list_filter = (ByOrchardForOrganizationIncomingProductFilter, ByProviderForOrganizationIncomingProductFilter, ByProductForOrganizationIncomingProductFilter,
                   ByCategoryForOrganizationIncomingProductFilter)
    search_fields = ('scheduleharvest__ooid',)
    inlines = [PalletReceivedInline, ScheduleHarvestInline]

    # Filtrar en el Admin solo los cortes que su status sea "pending"
    # def get_queryset(self, request):
    #    return super().get_queryset(request).filter(status="pending")

    @uppercase_form_charfield('guide_number')
    @uppercase_form_charfield('weighing_record_number')
    @uppercase_form_charfield('phytosanitary_certificate')
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return form
    
    def has_add_permission(self, request):
        return False 

    def generate_actions_buttons(self, obj):
        pass
    
    generate_actions_buttons.short_description = _('Actions')
    generate_actions_buttons.allow_tags = True

    def get_scheduleharvest_ooid(self, obj):
        schedule_harvest = obj.scheduleharvest
        return schedule_harvest.ooid if schedule_harvest else None

    def get_scheduleharvest_harvest_date(self, obj):
        schedule_harvest = obj.scheduleharvest
        return schedule_harvest.harvest_date if schedule_harvest else None
    
    def get_scheduleharvest_category(self, obj):
        schedule_harvest = obj.scheduleharvest
        choices = dict(get_harvest_cutting_categories_choices())
        return choices.get(schedule_harvest.category, schedule_harvest.category) 

    def get_scheduleharvest_product(self, obj):
        schedule_harvest = obj.scheduleharvest
        return schedule_harvest.product if schedule_harvest else None

    def get_scheduleharvest_orchard(self, obj):
        schedule_harvest = obj.scheduleharvest
        return schedule_harvest.orchard if schedule_harvest else None
    
    def get_scheduleharvest_product_provider(self, obj):
        schedule_harvest = obj.scheduleharvest
        return schedule_harvest.product_provider if schedule_harvest else None

    get_scheduleharvest_ooid.admin_order_field = 'scheduleharvest__ooid'
    get_scheduleharvest_ooid.short_description = _('Harvest Number')
    get_scheduleharvest_harvest_date.admin_order_field = 'scheduleharvest__harvest_date'
    get_scheduleharvest_harvest_date.short_description = _('Harvest Date')
    get_scheduleharvest_product.admin_order_field = 'scheduleharvest__product'
    get_scheduleharvest_product.short_description = _('Product')
    get_scheduleharvest_orchard.admin_order_field = 'scheduleharvest__orchard'
    get_scheduleharvest_orchard.short_description = _('Orchard')
    get_scheduleharvest_product_provider.admin_order_field = 'scheduleharvest__product_provider'
    get_scheduleharvest_product_provider.short_description = _('Product Provider')
    get_scheduleharvest_category.admin_order_field = 'scheduleharvest__category'
    get_scheduleharvest_category.short_description = _('Category')


    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        update_pallet_numbers(form.instance)

    class Media:
        js = ('js/admin/forms/packhouses/receiving/incoming_product.js', )
