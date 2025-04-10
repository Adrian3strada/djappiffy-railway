from django.contrib import admin
from .models import (IncomingProduct, PalletReceived,
                    FoodSafety, FoodSafety, DryMatter, InternalInspection, 
                    TransportReview, SampleCollection, Percentage,
                    TransportInspection, TransportCondition,
                    SensorySpecification, SampleWeight, SamplePest,
                    SampleDisease, SamplePhysicalDamage, SampleResidue,
                    Lote,
                    )
from common.base.mixins import (ByOrganizationAdminMixin, DisableInlineRelatedLinksMixin)
from packhouses.gathering.models import ScheduleHarvest, ScheduleHarvestHarvestingCrew, ScheduleHarvestVehicle
from django.utils.translation import gettext_lazy as _
import nested_admin
from .mixins import CustomNestedStackedInlineMixin
from .forms import ScheduleHarvestVehicleForm
from nested_admin import NestedStackedInline
from packhouses.catalogs.models import ProductFoodSafetyProcess, ProductPest, ProductDisease, ProductPhysicalDamage, ProductResidue
from common.base.models import Pest

from common.base.mixins import (DisableInlineRelatedLinksMixin)
import nested_admin

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
class PalletReceivedInline(CustomNestedStackedInlineMixin, admin.StackedInline):
    model = PalletReceived
    fields = ('ooid', 'gross_weight', 'total_boxes', 'harvest_container', 'container_tare', 'platform_tare', 'net_weight')
    extra = 0

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        organization = None
        if hasattr(request, 'organization'):
            organization = request.organization

        if db_field.name == "harvest_container":
            kwargs["queryset"] = HarvestContainer.objects.filter(organization=organization, is_enabled=True)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

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
    # list_display = ('get_scheduleharvest_ooid', 'get_scheduleharvest_orchard', 'get_scheduleharvest_harvest_date', 'get_scheduleharvest_product',
    #                 'guide_number', 'status',)
    # fields = ('status', 'phytosanitary_certificate', 'guide_number', 'weighing_record_number', 'public_weighing_scale', 'public_weight_result', 'pallets_received', 'packhouse_weight_result',
    #           'mrl', 'kg_sample', 'boxes_assigned', 'full_boxes', 'empty_boxes', 'missing_boxes', 'average_per_box', 'current_kg_available')
    # inlines = [PalletReceivedInline, ScheduleHarvestInline]
    # # readonly_fields = ('pallets_received', 'boxes_assigned', 'missing_boxes', 'average_per_box', 'current_kg_available')

    # def get_scheduleharvest_ooid(self, obj):
    #     schedule_harvest = obj.scheduleharvest
    #     return schedule_harvest.ooid if schedule_harvest else None

    # def get_scheduleharvest_harvest_date(self, obj):
    #     schedule_harvest = obj.scheduleharvest
    #     return schedule_harvest.harvest_date if schedule_harvest else None

    # def get_scheduleharvest_product(self, obj):
    #     schedule_harvest = obj.scheduleharvest
    #     return schedule_harvest.product if schedule_harvest else None

    # def get_scheduleharvest_orchard(self, obj):
    #     schedule_harvest = obj.scheduleharvest
    #     return schedule_harvest.orchard if schedule_harvest else None

    # get_scheduleharvest_ooid.admin_order_field = 'scheduleharvest__ooid'
    # get_scheduleharvest_ooid.short_description = _('Harvest Number')
    # get_scheduleharvest_harvest_date.admin_order_field = 'scheduleharvest__harvest_date'
    # get_scheduleharvest_harvest_date.short_description = _('Harvest Date')
    # get_scheduleharvest_product.admin_order_field = 'scheduleharvest__product'
    # get_scheduleharvest_product.short_description = _('Product')
    # get_scheduleharvest_orchard.admin_order_field = 'scheduleharvest__orchard'
    # get_scheduleharvest_orchard.short_description = _('Orchard')

    # class Media:
    #     js = ('js/admin/forms/packhouses/receiving/incoming_product.js',)

    list_display = ('borrar',)

@admin.register(Lote)
class LoteAdmin(ByOrganizationAdminMixin, admin.ModelAdmin):
    list_display = ('sample_number',)

class DryMatterInline(nested_admin.NestedTabularInline):
    model = DryMatter
    extra = 1
    fields = ['number', 'product_weight', 'paper_weight', 'moisture_weight', 'dry_weight', 'dry_matter_percentage']
    readonly_fields = ('number',)

class InternalInspectionInline(nested_admin.NestedTabularInline):
    model = InternalInspection
    extra = 1
    fields = ['number', 'internal_temperature', 'product_pest']
    readonly_fields = ('number',)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "product_pest":
            object_id = request.resolver_match.kwargs.get("object_id")

            if object_id:
                try:
                    food_safety = FoodSafety.objects.get(pk=object_id)
                    incoming_product = IncomingProduct.objects.filter(lote=food_safety.lote).first()
                    schedule_harvest = ScheduleHarvest.objects.filter(incoming_product=incoming_product).first()
                    product = schedule_harvest.product
                    kwargs["queryset"] = ProductPest.objects.filter(product=product)

                except InternalInspection.DoesNotExist:
                    kwargs['queryset'] = ProductPest.objects.none()
            else:
                kwargs['queryset'] = ProductPest.objects.none()

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class TransportInspectionInline(nested_admin.NestedTabularInline):
    model = TransportInspection
    extra = 0
    min_num = 1
    max_num = 1
    can_delete = False

    def transport_inspection(self, obj=None):
        return ''

    readonly_fields = ['transport_inspection']
    fields = ['transport_inspection', 'sealed', 'only_the_product', 'free_foreign_matter',
              'free_unusual_odors', 'certificate', 'free_fecal_matter']


class TransportConditionInline(nested_admin.NestedTabularInline):
    model = TransportCondition
    extra = 0
    min_num = 1
    max_num=1
    can_delete = False

    def transport_condition(self, obj=None):
        return ''

    readonly_fields = ['transport_condition']
    fields = ['transport_condition', 'is_clean', 'good_condition', 'broken', 'damaged', 'seal']

class TransportReviewInline(DisableInlineRelatedLinksMixin, nested_admin.NestedStackedInline):
    model = TransportReview
    extra = 0
    inlines = [TransportInspectionInline, TransportConditionInline]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "vehicle":
            object_id = request.resolver_match.kwargs.get("object_id")

            food_safety = FoodSafety.objects.get(pk=object_id)
            incoming_product = IncomingProduct.objects.filter(lote=food_safety.lote).first()
            schedule_harvest = ScheduleHarvest.objects.filter(incoming_product=incoming_product).first()
            kwargs["queryset"] = ScheduleHarvestVehicle.objects.filter(harvest_cutting_id=schedule_harvest)
            return super().formfield_for_foreignkey(db_field, request, **kwargs)

class SensorySpecificationInline(nested_admin.NestedTabularInline):
    model = SensorySpecification
    extra = 0
    min_num = 1
    max_num = 1
    can_delete = False

    # def sensory_specification(self, obj=None):
    #     return ''

    # readonly_fields = ['sensory_specification']
    # fields = ['whole', 'foreign_material', 'insects', 'temperature_damage', 'unusual_odor']

class SampleWeightInline(nested_admin.NestedTabularInline):
    model = SampleWeight
    extra = 0
    min_num = 1
    readonly_fields = ('number',)
    fields = ['number', 'weight']

class SamplePestInline(nested_admin.NestedTabularInline):
    model = SamplePest
    extra = 0
    fields = ['product_pest', 'sample_pest']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "product_pest":
            object_id = request.resolver_match.kwargs.get("object_id")
            if object_id:
                try:
                    food_safety = FoodSafety.objects.get(pk=object_id)
                    incoming_product = IncomingProduct.objects.filter(lote=food_safety.lote).first()
                    schedule_harvest = ScheduleHarvest.objects.filter(incoming_product=incoming_product).first()
                    kwargs["queryset"] = ProductPest.objects.filter(product=schedule_harvest.product)
                except FoodSafety.DoesNotExist:
                    kwargs['queryset'] = ProductPest.objects.none()
            else:
                kwargs['queryset'] = ProductPest.objects.none()

            return super().formfield_for_foreignkey(db_field, request, **kwargs)

    class Media:
        js = ('js/admin/forms/select.js',)


class SampleDiseaseInline(nested_admin.NestedTabularInline):
    model = SampleDisease
    extra = 0
    fields = ['product_disease', 'sample_disease']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "product_disease":
            object_id = request.resolver_match.kwargs.get("object_id")
            if object_id:
                try:
                    food_safety = FoodSafety.objects.get(pk=object_id)
                    incoming_product = IncomingProduct.objects.filter(lote=food_safety.lote).first()
                    schedule_harvest = ScheduleHarvest.objects.filter(incoming_product=incoming_product).first()
                    kwargs["queryset"] = ProductDisease.objects.filter(product=schedule_harvest.product)
                except FoodSafety.DoesNotExist:
                    kwargs['queryset'] = ProductDisease.objects.none()
            else:
                kwargs['queryset'] = ProductDisease.objects.none()

            return super().formfield_for_foreignkey(db_field, request, **kwargs)

class SamplePhysicalDamageInline(nested_admin.NestedTabularInline):
    model = SamplePhysicalDamage
    extra = 0
    fields = ['product_physical_damage', 'sample_physical_damage']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "product_physical_damage":
            object_id = request.resolver_match.kwargs.get("object_id")
            if object_id:
                try:
                    food_safety = FoodSafety.objects.get(pk=object_id)
                    incoming_product = IncomingProduct.objects.filter(lote=food_safety.lote).first()
                    schedule_harvest = ScheduleHarvest.objects.filter(incoming_product=incoming_product).first()
                    kwargs["queryset"] = ProductPhysicalDamage.objects.filter(product=schedule_harvest.product)
                except FoodSafety.DoesNotExist:
                    kwargs['queryset'] = ProductPhysicalDamage.objects.none()
            else:
                kwargs['queryset'] = ProductPhysicalDamage.objects.none()

            return super().formfield_for_foreignkey(db_field, request, **kwargs)

class SampleResidueInline(nested_admin.NestedTabularInline):
    model = SampleResidue
    extra = 0
    fields = ['product_residue', 'sample_residue']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "product_residue":
            object_id = request.resolver_match.kwargs.get("object_id")
            if object_id:
                try:
                    food_safety = FoodSafety.objects.get(pk=object_id)
                    incoming_product = IncomingProduct.objects.filter(lote=food_safety.lote).first()
                    schedule_harvest = ScheduleHarvest.objects.filter(incoming_product=incoming_product).first()
                    kwargs["queryset"] = ProductResidue.objects.filter(product=schedule_harvest.product)
                except FoodSafety.DoesNotExist:
                    kwargs['queryset'] = ProductResidue.objects.none()
            else:
                kwargs['queryset'] = ProductResidue.objects.none()

            return super().formfield_for_foreignkey(db_field, request, **kwargs)

class SampleCollectionInline(DisableInlineRelatedLinksMixin, nested_admin.NestedStackedInline):
    model = SampleCollection
    extra = 1
    min_num = 1
    max_num = 1
    can_delete = False
    inlines = [SensorySpecificationInline, SamplePestInline, SampleDiseaseInline, SamplePhysicalDamageInline, SampleResidueInline, SampleWeightInline]

class PercentageInline(nested_admin.NestedTabularInline):
    model = Percentage
    can_delete = False
    extra = 0
    max_num = 0

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

# Mapeo de nombres de inlines con sus clases
INLINE_CLASSES = {
    "DryMatter": DryMatterInline,
    "InternalInspection": InternalInspectionInline,
    "TransportReview": TransportReviewInline,
    "SampleCollection": SampleCollectionInline,
    "Percentage": PercentageInline,
}

@admin.register(FoodSafety)
class FoodSafetyAdmin(ByOrganizationAdminMixin, nested_admin.NestedModelAdmin):
    list_display = ('lote',)
    list_filter = ['lote']
    inlines = [DryMatterInline, InternalInspectionInline, TransportReviewInline, SampleCollectionInline]

    def get_inlines(self, request, obj=None):
        inlines_list = []

        if not obj:
            return inlines_list

        try:
            incoming_product = IncomingProduct.objects.filter(lote=obj.lote).first()
            schedule_harvest = ScheduleHarvest.objects.filter(incoming_product=incoming_product).first()
            food_safety_config = ProductFoodSafetyProcess.objects.filter(product=schedule_harvest.product).values_list('procedure__model', flat=True)
            inlines_list = [INLINE_CLASSES[inline] for inline in food_safety_config if inline in INLINE_CLASSES]

        except ProductFoodSafetyProcess.DoesNotExist:
            return inlines_list

        return inlines_list

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "lote":
            this_organization = request.organization
            obj_id = request.resolver_match.kwargs.get("object_id")
            inocuidad_lote = FoodSafety.objects.filter(organization=this_organization).values_list('lote', flat=True)

            if obj_id:
                food_safety = FoodSafety.objects.get(id=obj_id)
                if food_safety:
                    kwargs["queryset"] = Lote.objects.filter(id=food_safety.lote.id)
                else:
                    kwargs["queryset"] = Lote.objects.none()

            else:
                kwargs["queryset"] = Lote.objects.filter(organization=this_organization).exclude(id__in=inocuidad_lote)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)