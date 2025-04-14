from django.contrib import admin
from .models import (IncomingProduct, PalletReceived,
                    FoodSafety, FoodSafety, DryMatter, InternalInspection,
                    VehicleReview, SampleCollection, Average,
                    VehicleInspection, VehicleCondition,
                    SensorySpecification, SampleWeight, SamplePest,
                    SampleDisease, SamplePhysicalDamage, SampleResidue,
                    Batch,
                    )
from common.base.mixins import (ByOrganizationAdminMixin, DisableInlineRelatedLinksMixin)
from packhouses.gathering.models import ScheduleHarvest, ScheduleHarvestHarvestingCrew, ScheduleHarvestVehicle
from django.utils.translation import gettext_lazy as _
import nested_admin
from .mixins import CustomNestedStackedInlineMixin, CustomNestedStackedAvgInlineMixin
from .forms import ScheduleHarvestVehicleForm
from nested_admin import NestedStackedInline, NestedTabularInline
from packhouses.catalogs.models import ProductFoodSafetyProcess, ProductPest, ProductDisease, ProductPhysicalDamage, ProductResidue
from common.base.models import Pest
from django import forms

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

@admin.register(Batch)
class BatchAdmin(ByOrganizationAdminMixin, admin.ModelAdmin):
    list_display = ('ooid', 'status',)
    exclude = ('ooid',)

class DryMatterInline(NestedTabularInline):
    model = DryMatter
    extra = 1

    def number(self, obj=None):
        return ''

    readonly_fields = ('number',)
    fields = ['number','product_weight', 'paper_weight', 'moisture_weight', 'dry_weight', 'dry_matter_percentage']

    class Media:
        js = ('js/admin/forms/packhouses/receiving/counter.js',)

class InternalInspectionInline(NestedTabularInline):
    model = InternalInspection
    extra = 1

    def number(self, obj=None):
        return ''

    readonly_fields = ('number',)
    fields = ['number','internal_temperature', 'product_pest']

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "product_pest":
            object_id = request.resolver_match.kwargs.get("object_id")

            if object_id:
                try:
                    food_safety = FoodSafety.objects.get(pk=object_id)
                    incoming_product = IncomingProduct.objects.filter(batch=food_safety.batch).first()
                    schedule_harvest = ScheduleHarvest.objects.filter(incoming_product=incoming_product).first()
                    product = schedule_harvest.product
                    kwargs["queryset"] = ProductPest.objects.filter(product=product, pest__inside=True)

                except InternalInspection.DoesNotExist:
                    kwargs['queryset'] = ProductPest.objects.none()
            else:
                kwargs['queryset'] = ProductPest.objects.none()

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class VehicleInspectionInline(nested_admin.NestedTabularInline):
    model = VehicleInspection
    extra = 0
    min_num = 1
    max_num = 1

    def transport_inspection(self, obj=None):
        return ''

    readonly_fields = ['transport_inspection']
    fields = ['transport_inspection', 'sealed', 'only_the_product', 'free_foreign_matter',
              'free_unusual_odors', 'certificate', 'free_fecal_matter']

class VehicleConditionInline(nested_admin.NestedTabularInline):
    model = VehicleCondition
    extra = 0
    min_num = 1
    max_num=1

    def transport_condition(self, obj=None):
        return ''

    readonly_fields = ['transport_condition']
    fields = ['transport_condition', 'is_clean', 'good_condition', 'broken', 'damaged', 'seal']

class VehicleReviewInline(nested_admin.NestedStackedInline):
    model = VehicleReview
    extra = 0
    inlines = [VehicleInspectionInline, VehicleConditionInline]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "vehicle":
            object_id = request.resolver_match.kwargs.get("object_id")

            food_safety = FoodSafety.objects.get(pk=object_id)
            incoming_product = IncomingProduct.objects.filter(batch=food_safety.batch).first()
            schedule_harvest = ScheduleHarvest.objects.filter(incoming_product=incoming_product).first()
            kwargs["queryset"] = ScheduleHarvestVehicle.objects.filter(harvest_cutting_id=schedule_harvest)
            return super().formfield_for_foreignkey(db_field, request, **kwargs)

    class Media:
        js = ('js/admin/forms/packhouses/receiving/select_vehicle.js',)

class SensorySpecificationInline(nested_admin.NestedTabularInline):
    model = SensorySpecification
    extra = 0
    min_num = 1
    max_num = 1
    can_delete = False

class SampleWeightInline(nested_admin.NestedTabularInline):
    model = SampleWeight
    extra = 0
    min_num = 1

    def number(self, obj=None):
        return ''

    readonly_fields = ('number',)
    fields = ['number', 'weight']

    class Media:
        js = ('js/admin/forms/packhouses/receiving/counter.js',)

class SamplePestForm(forms.ModelForm):
    class Meta:
        model = SamplePest
        fields = ['product_pest', 'sample_pest', 'percentage']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['percentage'].widget.attrs['readonly'] = 'readonly'

class SamplePestInline(nested_admin.NestedTabularInline):
    model = SamplePest
    extra = 0
    fields = ['product_pest', 'sample_pest', 'percentage']
    form = SamplePestForm

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "product_pest":
            object_id = request.resolver_match.kwargs.get("object_id")
            if object_id:
                try:
                    food_safety = FoodSafety.objects.get(pk=object_id)
                    incoming_product = IncomingProduct.objects.filter(batch=food_safety.batch).first()
                    schedule_harvest = ScheduleHarvest.objects.filter(incoming_product=incoming_product).first()
                    kwargs["queryset"] = ProductPest.objects.filter(product=schedule_harvest.product)
                except FoodSafety.DoesNotExist:
                    kwargs['queryset'] = ProductPest.objects.none()
            else:
                kwargs['queryset'] = ProductPest.objects.none()

            return super().formfield_for_foreignkey(db_field, request, **kwargs)

    class Media:
        js = ('js/admin/forms/packhouses/receiving/percentage_pest.js',)

class SampleDiseaseForm(forms.ModelForm):
    class Meta:
        model = SampleDisease
        fields = ['product_disease', 'sample_disease', 'percentage']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['percentage'].widget.attrs['readonly'] = 'readonly'

class SampleDiseaseInline(nested_admin.NestedTabularInline):
    model = SampleDisease
    extra = 0
    fields = ['product_disease', 'sample_disease', 'percentage']
    form = SampleDiseaseForm

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "product_disease":
            object_id = request.resolver_match.kwargs.get("object_id")
            if object_id:
                try:
                    food_safety = FoodSafety.objects.get(pk=object_id)
                    incoming_product = IncomingProduct.objects.filter(batch=food_safety.batch).first()
                    schedule_harvest = ScheduleHarvest.objects.filter(incoming_product=incoming_product).first()
                    kwargs["queryset"] = ProductDisease.objects.filter(product=schedule_harvest.product)
                except FoodSafety.DoesNotExist:
                    kwargs['queryset'] = ProductDisease.objects.none()
            else:
                kwargs['queryset'] = ProductDisease.objects.none()

            return super().formfield_for_foreignkey(db_field, request, **kwargs)

    class Media:
        js = ('js/admin/forms/packhouses/receiving/percentage_disease.js',)

class SamplePhysicalDamageForm(forms.ModelForm):
    class Meta:
        model = SamplePhysicalDamage
        fields = ['product_physical_damage', 'sample_physical_damage', 'percentage']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['percentage'].widget.attrs['readonly'] = 'readonly'

class SamplePhysicalDamageInline(nested_admin.NestedTabularInline):
    model = SamplePhysicalDamage
    extra = 0
    fields = ['product_physical_damage', 'sample_physical_damage', 'percentage']
    form = SamplePhysicalDamageForm

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "product_physical_damage":
            object_id = request.resolver_match.kwargs.get("object_id")
            if object_id:
                try:
                    food_safety = FoodSafety.objects.get(pk=object_id)
                    incoming_product = IncomingProduct.objects.filter(batch=food_safety.batch).first()
                    schedule_harvest = ScheduleHarvest.objects.filter(incoming_product=incoming_product).first()
                    kwargs["queryset"] = ProductPhysicalDamage.objects.filter(product=schedule_harvest.product)
                except FoodSafety.DoesNotExist:
                    kwargs['queryset'] = ProductPhysicalDamage.objects.none()
            else:
                kwargs['queryset'] = ProductPhysicalDamage.objects.none()

            return super().formfield_for_foreignkey(db_field, request, **kwargs)

    class Media:
        js = ('js/admin/forms/packhouses/receiving/percentage_physical_damage.js',)

class SampleResidueForm(forms.ModelForm):
    class Meta:
        model = SampleResidue
        fields = ['product_residue', 'sample_residue', 'percentage']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['percentage'].widget.attrs['readonly'] = 'readonly'

class SampleResidueInline(nested_admin.NestedTabularInline):
    model = SampleResidue
    extra = 0
    fields = ['product_residue', 'sample_residue', 'percentage']
    form = SampleResidueForm

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "product_residue":
            object_id = request.resolver_match.kwargs.get("object_id")
            if object_id:
                try:
                    food_safety = FoodSafety.objects.get(pk=object_id)
                    incoming_product = IncomingProduct.objects.filter(batch=food_safety.batch).first()
                    schedule_harvest = ScheduleHarvest.objects.filter(incoming_product=incoming_product).first()
                    kwargs["queryset"] = ProductResidue.objects.filter(product=schedule_harvest.product)
                except FoodSafety.DoesNotExist:
                    kwargs['queryset'] = ProductResidue.objects.none()
            else:
                kwargs['queryset'] = ProductResidue.objects.none()

            return super().formfield_for_foreignkey(db_field, request, **kwargs)

    class Media:
        js = ('js/admin/forms/packhouses/receiving/percentage_residue.js',)

class SampleCollectionInline(CustomNestedStackedAvgInlineMixin, admin.StackedInline):
    model = SampleCollection
    extra = 1
    min_num = 1
    max_num = 1
    can_delete = False
    inlines = [SampleWeightInline, SamplePestInline, SampleDiseaseInline, SamplePhysicalDamageInline, SampleResidueInline]

    class Media:
        js = ('js/admin/forms/packhouses/receiving/select_sample.js',)

class AverageInline(nested_admin.NestedTabularInline):
    model = Average
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
    "VehicleReview": VehicleReviewInline,
    "SampleCollection": SampleCollectionInline,
    "Average": AverageInline,
}

@admin.register(FoodSafety)
class FoodSafetyAdmin(ByOrganizationAdminMixin, nested_admin.NestedModelAdmin):
    list_display = ('batch',)
    list_filter = ['batch']
    inlines = [DryMatterInline, InternalInspectionInline, VehicleReviewInline, SampleCollectionInline, AverageInline]

    def get_inlines(self, request, obj=None):
        inlines_list = []

        if not obj:
            return inlines_list

        try:
            incoming_product = IncomingProduct.objects.filter(batch=obj.batch).first()
            schedule_harvest = ScheduleHarvest.objects.filter(incoming_product=incoming_product).first()
            food_safety_config = ProductFoodSafetyProcess.objects.filter(product=schedule_harvest.product).values_list('procedure__model', flat=True)
            inlines_list = [INLINE_CLASSES[inline] for inline in food_safety_config if inline in INLINE_CLASSES]

        except ProductFoodSafetyProcess.DoesNotExist:
            return inlines_list

        return inlines_list

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "batch":
            this_organization = request.organization
            obj_id = request.resolver_match.kwargs.get("object_id")
            inocuidad_batch = FoodSafety.objects.filter(organization=this_organization).values_list('batch', flat=True)

            if obj_id:
                food_safety = FoodSafety.objects.get(id=obj_id)
                if food_safety:
                    kwargs["queryset"] = Batch.objects.filter(id=food_safety.batch.id)
                else:
                    kwargs["queryset"] = Batch.objects.none()

            else:
                kwargs["queryset"] = Batch.objects.filter(organization=this_organization).exclude(id__in=inocuidad_batch)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)