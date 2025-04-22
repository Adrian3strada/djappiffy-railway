from django.contrib import admin
from packhouses.receiving.views import weighing_set_report
from packhouses.gathering.models import ScheduleHarvest, ScheduleHarvestHarvestingCrew, ScheduleHarvestVehicle, ScheduleHarvestContainerVehicle
from packhouses.catalogs.models import (Supply, HarvestingCrew, Vehicle, Provider, Product, ProductVariety, Gatherer, Maquiladora,
                                        Market, Orchard, OrchardCertification, WeighingScale, ProductPhenologyKind, ProductHarvestSizeKind, ProductAdditionalValue,
                                        ProductFoodSafetyProcess, ProductPest, ProductDisease, ProductPhysicalDamage, ProductResidue)
from packhouses.catalogs.utils import get_harvest_cutting_categories_choices
from .models import (IncomingProduct, WeighingSet, WeighingSetContainer,
                    FoodSafety, FoodSafety, DryMatter, InternalInspection,
                    VehicleReview, SampleCollection, Average,
                    VehicleInspection, VehicleCondition,
                    SampleWeight, SamplePest,
                    SampleDisease, SamplePhysicalDamage, SampleResidue,
                    Batch,
                    )
from common.base.mixins import (ByOrganizationAdminMixin, DisableInlineRelatedLinksMixin)
from django.utils.translation import gettext_lazy as _
from .mixins import CustomNestedStackedInlineMixin, CustomNestedStackedAvgInlineMixin
from .forms import (IncomingProductForm, ScheduleHarvestVehicleForm, BaseScheduleHarvestVehicleFormSet, ContainerInlineForm, ContainerInlineFormSet)
from .filters import (ByOrchardForOrganizationIncomingProductFilter, ByProviderForOrganizationIncomingProductFilter, ByProductForOrganizationIncomingProductFilter,
                      ByCategoryForOrganizationIncomingProductFilter)
from .utils import update_pallet_numbers,  CustomScheduleHarvestFormSet
from common.base.decorators import uppercase_formset_charfield, uppercase_alphanumeric_formset_charfield
from common.base.decorators import uppercase_form_charfield, uppercase_alphanumeric_form_charfield
import nested_admin
from django.urls import reverse
from django.utils.html import format_html
from django.urls import path, reverse
from nested_admin import NestedStackedInline, NestedTabularInline
from common.base.models import Pest
# from django import forms

# Inlines para datos del corte
class HarvestCuttingContainerVehicleInline(nested_admin.NestedTabularInline):
    model = ScheduleHarvestContainerVehicle
    extra = 0
    formset = ContainerInlineFormSet
    form = ContainerInlineForm
    exclude = ("created_by",)

    def get_readonly_fields(self, request, obj=None):
        """ Aplica solo lectura a los campos de contenedor solo si `created_by == 'gathering'` """
        if obj and isinstance(obj, ScheduleHarvestContainerVehicle):
            # Verificamos el campo 'created_by' del contenedor
            if obj.created_by == 'gathering':
                # Retorna todos los campos menos 'created_by' como solo lectura
                return [f.name for f in self.model._meta.fields if f.name != 'created_by']
        return []


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
            kwargs["queryset"] = Supply.objects.filter(
                organization=organization,
                is_enabled=True
            )

        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class ScheduleHarvestHarvestingCrewInline(nested_admin.NestedTabularInline):
    model = ScheduleHarvestHarvestingCrew
    fields = ('provider', 'harvesting_crew')
    extra = 0
    show_title = True

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

        if db_field.name == "provider":
            kwargs["queryset"] = Provider.objects.filter(
                organization=organization,
                is_enabled=True,
                category='harvesting_provider'
            )

        if db_field.name == "harvesting_crew":
            kwargs["queryset"] = HarvestingCrew.objects.filter(
                organization=organization,
                is_enabled=True
            )

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class ScheduleHarvestVehicleInline(CustomNestedStackedInlineMixin, admin.StackedInline):
    model = ScheduleHarvestVehicle
    form = ScheduleHarvestVehicleForm
    formset = BaseScheduleHarvestVehicleFormSet
    fields = ('provider', 'vehicle', 'has_arrived', 'guide_number', 'stamp_vehicle_number')  # Agregar el nuevo campo
    extra = 0
    inlines = [HarvestCuttingContainerVehicleInline]

    def get_formset(self, request, obj=None, **kwargs):
        # Obtén el formset base
        formset = super().get_formset(request, obj, **kwargs)

        # Configurar widgets de campos relacionados en el form base
        for field in formset.form.base_fields.values():
            field.widget.can_add_related = False
            field.widget.can_change_related = False
            field.widget.can_delete_related = False
            field.widget.can_view_related = False

        # Definir una clase interna para pasar el request a cada formulario del formset
        class CustomFormSet(formset):
            def _construct_form(self, i, **kwargs_inner):
                kwargs_inner['request'] = request  # Pasar el objeto request
                return super()._construct_form(i, **kwargs_inner)

        return CustomFormSet


    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        organization = None
        if hasattr(request, 'organization'):
            organization = request.organization

        if db_field.name == "provider":
            kwargs["queryset"] = Provider.objects.filter(
                organization=organization,
                is_enabled=True,
                category='harvesting_provider'
            )

        if db_field.name == "vehicle":
            kwargs["queryset"] = Vehicle.objects.filter(
                organization=organization,
                is_enabled=True
            )

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        form_field = super().formfield_for_dbfield(db_field, request, **kwargs)

        if db_field.name == 'guide_number':
            if request.POST:
                has_arrived_str = request.POST.get('has_arrived')
                has_arrived = True if has_arrived_str == 'on' else False
                form_field.required = has_arrived
            else:
                form_field.required = True

        return form_field


class ScheduleHarvestInline(CustomNestedStackedInlineMixin, admin.StackedInline):
    model = ScheduleHarvest
    extra = 0
    inlines = [ScheduleHarvestHarvestingCrewInline, ScheduleHarvestVehicleInline ]
    readonly_fields = ('ooid', 'category', 'maquiladora', 'gatherer', 'product', 'product_variety')
    can_delete = False
    can_add = False
    show_title = False

    def get_formset(self, request, obj=None, **kwargs):
        FormSet = super().get_formset(request, obj, **kwargs)
        class CustomFormSet(FormSet, CustomScheduleHarvestFormSet):
            pass
        return CustomFormSet

    def get_fields(self, request, obj=None):
        fields = [
            'ooid', 'status', 'harvest_date', 'category', 'product_provider', 'product', 'product_variety',
            'product_phenologies', 'product_harvest_size_kind', 'orchard', 'orchard_certification', 'market',
            'weight_expected', 'weighing_scale', 'comments'
        ]
        if obj:
            schedule_harvest = ScheduleHarvest.objects.filter(incoming_product=obj).first()
            if schedule_harvest:
                pos = fields.index('category') + 1
                if schedule_harvest.category == "gathering":
                    fields.insert(pos, 'gatherer')
                elif schedule_harvest.category == "maquila":
                    fields.insert(pos, 'maquiladora')
        return fields

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        organization = request.organization if hasattr(request, "organization") else None
        organization_queryfilter = {"organization": organization, "is_enabled": True}
        product_organization_queryfilter = {"product__organization": organization, "is_enabled": True}

        if db_field.name == "product":
            kwargs["queryset"] = Product.objects.filter(**organization_queryfilter)

        if db_field.name == "product_varieties":
            kwargs["queryset"] = ProductVariety.objects.filter(**product_organization_queryfilter)

        if db_field.name in ("product_phenologies", "product_harvest_size_kind", "orchard"):
            qs_none = db_field.related_model.objects.none()
            obj_id = request.resolver_match.kwargs.get("object_id")
            incoming_product = IncomingProduct.objects.filter(id=obj_id).first() if obj_id else None
            schedule_harvest = (ScheduleHarvest.objects.filter(incoming_product=incoming_product).first()
                                if incoming_product else None)
            mapping = {
                "product_phenologies": (ProductPhenologyKind, "product_phenologies"),
                "product_harvest_size_kind": (ProductHarvestSizeKind, "product_harvest_size_kind"),
                "orchard": (Orchard, None),
            }
            model, field = mapping[db_field.name]
            if db_field.name == "orchard":
                org = incoming_product.organization if incoming_product else None
                prod = schedule_harvest.product if schedule_harvest and hasattr(schedule_harvest, "product") else None
                kwargs["queryset"] = model.objects.filter(organization=org, product=prod, is_enabled=True) if org and prod else qs_none
            else:
                prod_obj = getattr(schedule_harvest, field, None) if schedule_harvest else None
                prod = prod_obj.product if prod_obj else None
                kwargs["queryset"] = model.objects.filter(product=prod, is_enabled=True) if prod else qs_none

        field_filters = {
            "market": {
                "model": Market,
                "filters": {"is_enabled": True},
            },
            "orchard_certification": {
                "model": OrchardCertification,
                "filters": {"is_enabled": True},
            },
            "weighing_scale": {
                "model": WeighingScale,
                "filters": {"is_enabled": True},
            },
        }

        if db_field.name in field_filters and hasattr(request, "organization"):
            model = field_filters[db_field.name]["model"]
            filters = field_filters[db_field.name]["filters"]

            kwargs["queryset"] = model.objects.filter(organization=request.organization, **filters)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    class Media:
        js = ('js/admin/forms/packhouses/receiving/vehicle_inline.js',
              'js/admin/forms/packhouses/receiving/schedule_harvest_inline.js')

# Inlines para los pallets
class WeighingSetContainerInline(nested_admin.NestedTabularInline):
    model = WeighingSetContainer
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

class WeighingSetInline(CustomNestedStackedInlineMixin, admin.StackedInline):
    model = WeighingSet
    inlines = [WeighingSetContainerInline]
    fields = ('ooid', 'provider', 'harvesting_crew', 'gross_weight', 'total_containers', 'container_tare', 'platform_tare', 'net_weight')
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
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        organization = None
        if hasattr(request, 'organization'):
            organization = request.organization

        if db_field.name == "provider":
            kwargs["queryset"] = Provider.objects.filter(
                organization=organization,
                is_enabled=True,
                category='harvesting_provider'
            )

        if db_field.name == "harvesting_crew":
            kwargs["queryset"] = HarvestingCrew.objects.filter(
                organization=organization,
                is_enabled=True
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    class Media:
        js = ('js/admin/forms/packhouses/receiving/weighing_set_inline.js',)

# Reciba
@admin.register(IncomingProduct)
class IncomingProductAdmin(ByOrganizationAdminMixin, nested_admin.NestedModelAdmin):
    list_display = ('get_scheduleharvest_ooid', 'get_scheduleharvest_harvest_date', 'get_scheduleharvest_category', 'get_scheduleharvest_orchard',
                    'get_scheduleharvest_product_provider', 'get_scheduleharvest_product', 'status','generate_actions_buttons')
    fields = ('status', 'phytosanitary_certificate', 'weighing_record_number', 'public_weighing_scale', 'public_weight_result', 'total_weighed_sets',
              'packhouse_weight_result', 'mrl', 'kg_sample', 'containers_assigned', 'full_containers_per_harvest', 'empty_containers', 'missing_containers', 'total_weighed_set_containers',
              'average_per_container', 'current_kg_available', 'comments')
    list_filter = (ByOrchardForOrganizationIncomingProductFilter, ByProviderForOrganizationIncomingProductFilter, ByProductForOrganizationIncomingProductFilter,
                   ByCategoryForOrganizationIncomingProductFilter)
    search_fields = ('scheduleharvest__ooid',)
    inlines = [WeighingSetInline, ScheduleHarvestInline]
    form = IncomingProductForm
    actions = None

    # Filtrar en el Admin solo los cortes que su status sea distinto a "accepted"
    # def get_queryset(self, request):
    #    return super().get_queryset(request).exclude(status="accepted")

    @uppercase_form_charfield('weighing_record_number')
    @uppercase_form_charfield('phytosanitary_certificate')
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'public_weighing_scale' in form.base_fields:
            form.base_fields['public_weighing_scale'].widget.can_add_related = False
            form.base_fields['public_weighing_scale'].widget.can_change_related = False
            form.base_fields['public_weighing_scale'].widget.can_delete_related = False
            form.base_fields['public_weighing_scale'].widget.can_view_related = False
        return form

    def has_add_permission(self, request):
        return False


    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            # Registra la URL custom usando admin_site.admin_view para aplicar permisos y manejo
            path('weighing_set_report/<int:pk>/', self.admin_site.admin_view(weighing_set_report), name='receiving_incomingproduct_weighing_set_report'),
        ]
        # Colocar custom_urls antes o después según convenga para no interferir con otros patrones
        return custom_urls + urls

    def generate_actions_buttons(self, obj):
        # Ahora usamos el namespace 'admin' y el nombre que definimos en get_urls
        pdf_url = reverse('admin:receiving_incomingproduct_weighing_set_report', args=[obj.pk])
        tooltip_weighing_report = _('Generate Weighing Set Report')
        return format_html(
            '''
            <a class="button d-flex justify-content-center align-items-center"
               href="{}" target="_blank" data-toggle="tooltip" title="{}"
               style="display: flex; justify-content: center; align-items: center;">
                <i class="fa-solid fa-print"></i>
            </a>
            ''',
            pdf_url, tooltip_weighing_report
        )

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
         js = ('js/admin/forms/packhouses/receiving/incoming_product.js',)

@admin.register(Batch)
class BatchAdmin(ByOrganizationAdminMixin, admin.ModelAdmin):
    list_display = ('ooid', 'status',)
    exclude = ('ooid',)

class DryMatterInline(NestedTabularInline):
    model = DryMatter
    extra = 0
    fields = ['product_weight', 'paper_weight', 'moisture_weight', 'dry_weight', 'dry_matter_percentage']

class InternalInspectionInline(NestedTabularInline):
    model = InternalInspection
    extra = 0
    fields = ['internal_temperature', 'product_pest']

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "product_pest":
            object_id = request.resolver_match.kwargs.get("object_id")

            if object_id:
                try:
                    food_safety = FoodSafety.objects.get(pk=object_id)
                    incoming_product = IncomingProduct.objects.filter(batch=food_safety.batch).first()
                    schedule_harvest = ScheduleHarvest.objects.filter(incoming_product=incoming_product).first()
                    print(ProductPest.objects.filter(product=schedule_harvest.product, pest__pest__inside=True))
                    kwargs["queryset"] = ProductPest.objects.filter(product=schedule_harvest.product, pest__pest__inside=True)

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
            kwargs["queryset"] = ScheduleHarvestVehicle.objects.filter(harvest_cutting_id=schedule_harvest, has_arrived=True)
            return super().formfield_for_foreignkey(db_field, request, **kwargs)

    class Media:
        js = ('js/admin/forms/packhouses/receiving/food_safety/select_vehicle.js',)

class SampleWeightInline(nested_admin.NestedTabularInline):
    model = SampleWeight
    extra = 0
    fields = ['weight']

class SamplePestInline(nested_admin.NestedTabularInline):
    model = SamplePest
    extra = 0
    fields = ['product_pest', 'sample_pest', 'percentage']
    readonly_fields = ['percentage']

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

class SampleDiseaseInline(nested_admin.NestedTabularInline):
    model = SampleDisease
    extra = 0
    fields = ['product_disease', 'sample_disease', 'percentage']
    readonly_fields = ['percentage']

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

class SamplePhysicalDamageInline(nested_admin.NestedTabularInline):
    model = SamplePhysicalDamage
    extra = 0
    fields = ['product_physical_damage', 'sample_physical_damage', 'percentage']
    readonly_fields = ['percentage']

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

class SampleResidueInline(nested_admin.NestedTabularInline):
    model = SampleResidue
    extra = 0
    fields = ['product_residue', 'sample_residue', 'percentage']
    readonly_fields = ['percentage']

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

class SampleCollectionInline(CustomNestedStackedAvgInlineMixin, admin.StackedInline):
    model = SampleCollection
    extra = 1
    min_num = 1
    max_num = 1
    can_delete = False
    inlines = [SampleWeightInline, SamplePestInline, SampleDiseaseInline, SamplePhysicalDamageInline, SampleResidueInline]

    class Media:
        js = (
            'js/admin/forms/packhouses/receiving/food_safety/select_sample.js', 
            'js/admin/forms/packhouses/receiving/food_safety/percentage.js',
            )

class AverageInline(CustomNestedStackedAvgInlineMixin, admin.StackedInline):
    model = Average
    can_delete = False
    extra = 0
    max_num = 0

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def get_fields(self, request, obj=None):
        include_fields = []

        if not obj:
            return include_fields

        try:
            incoming_product = IncomingProduct.objects.filter(batch=obj.batch).first()
            schedule_harvest = ScheduleHarvest.objects.filter(incoming_product=incoming_product).first()
            food_safety_config = ProductFoodSafetyProcess.objects.filter(product=schedule_harvest.product).values_list('procedure__model', flat=True)
            all_possible_fields = {
                "DryMatter": ['acceptance_report', 'average_dry_matter'],
                "InternalInspection": ['average_internal_temperature'],
            }

            # Detectar qué campos están relacionados con los modelos que NO están en la configuración
            for model, campos in all_possible_fields.items():
                if model in food_safety_config:
                    include_fields.extend(campos)

        except ProductFoodSafetyProcess.DoesNotExist:
            pass

        return include_fields

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

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['batch'].widget.can_add_related = False
        form.base_fields['batch'].widget.can_change_related = False
        form.base_fields['batch'].widget.can_delete_related = False
        form.base_fields['batch'].widget.can_view_related = False

        return form

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
