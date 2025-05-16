from django.contrib import admin, messages
from packhouses.receiving.views import weighing_set_report
from packhouses.gathering.models import ScheduleHarvest, ScheduleHarvestHarvestingCrew, ScheduleHarvestVehicle, ScheduleHarvestContainerVehicle
from packhouses.catalogs.models import (Supply, HarvestingCrew, Vehicle, Provider, Product, ProductVariety, Gatherer, Maquiladora,
                                        Market, Orchard, OrchardCertification, WeighingScale, ProductPhenologyKind, ProductHarvestSizeKind, ProductDryMatterAcceptanceReport,
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
from .forms import (IncomingProductForm, ScheduleHarvestVehicleForm, BaseScheduleHarvestVehicleFormSet, ContainerInlineForm, ContainerInlineFormSet, 
                    BatchForm, WeighingSetForm, WeighingSetInlineFormSet,)
from .filters import (ByOrchardForOrganizationIncomingProductFilter, ByProviderForOrganizationIncomingProductFilter, ByProductForOrganizationIncomingProductFilter,
                      ByCategoryForOrganizationIncomingProductFilter)
from .utils import update_weighing_set_numbers,  CustomScheduleHarvestFormSet
from common.base.decorators import uppercase_formset_charfield, uppercase_alphanumeric_formset_charfield
from common.base.decorators import uppercase_form_charfield, uppercase_alphanumeric_form_charfield
from django.urls import reverse
from django.utils.html import format_html
from django.urls import path, reverse
import nested_admin
from common.base.models import Pest
from django.contrib.admin.templatetags.admin_list import _boolean_icon
from django.db.models import Q
from django import forms
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils.formats import date_format
# from django import forms

# Inlines para datos del corte
class HarvestCuttingContainerVehicleInline(nested_admin.NestedTabularInline):
    model = ScheduleHarvestContainerVehicle
    extra = 0
    formset = ContainerInlineFormSet
    form = ContainerInlineForm
    exclude = ("created_at_model",)

    def get_readonly_fields(self, request, obj=None):
        """ Aplica solo lectura a los campos de contenedor solo si `created_at_model == 'gathering'` """
        if obj and isinstance(obj, ScheduleHarvestContainerVehicle):
            # Verificamos el campo 'created_at_model' del contenedor
            if obj.created_at_model == 'gathering':
                # Retorna todos los campos menos 'created_at_model' como solo lectura
                return [f.name for f in self.model._meta.fields if f.name != 'created_at_model']
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
    max_num = 0
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
            def __init__(self2, *args, **kwargs):
                super().__init__(*args, **kwargs)
                for form in self2.forms:
                    form.fields['weighing_scale'].required = True
        return CustomFormSet

    def get_fields(self, request, obj=None):
        fields = [
            'ooid', 'harvest_date', 'category', 'product_provider', 'product', 'product_variety',
            'product_phenologies', 'product_harvest_size_kind', 'orchard', 'orchard_certifications', 'market',
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
            "orchard_certifications": {
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
        js = ('js/admin/forms/packhouses/receiving/incomingproduct/vehicle_inline.js',
              'js/admin/forms/packhouses/receiving/incomingproduct/schedule_harvest_inline.js')

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
    form = WeighingSetForm
    formset = WeighingSetInlineFormSet

    
    def get_readonly_fields(self, request, obj=None):
        # Si el objeto principal ya existe, se muestra todo como solo lectura.
        if obj:
            return self.fields
        return super().get_readonly_fields(request, obj)

    def has_change_permission(self, request, obj=None):
        if obj:
            return False
        return True
    
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

    # class Media:
    #     js = ('js/admin/forms/packhouses/receiving/incomingproduct/weighing_set_inline.js',)


# Reciba

@admin.register(IncomingProduct)
class IncomingProductAdmin(ByOrganizationAdminMixin, nested_admin.NestedModelAdmin):
    list_display = ('get_scheduleharvest_ooid', 'get_scheduleharvest_harvest_date', 'get_scheduleharvest_category', 'get_scheduleharvest_orchard',
                    'get_scheduleharvest_product_provider', 'get_scheduleharvest_product', 'status','generate_actions_buttons')
    fields = ('phytosanitary_certificate', 'weighing_record_number', 'public_weighing_scale', 'public_weight_result', 'total_weighed_sets',
              'packhouse_weight_result', 'mrl', 'kg_sample', 'containers_assigned', 'full_containers_per_harvest', 'empty_containers', 'missing_containers', 'total_weighed_set_containers',
              'average_per_container', 'comments', 'is_quarantined', 'status')
    list_filter = (ByOrchardForOrganizationIncomingProductFilter, ByProviderForOrganizationIncomingProductFilter, ByProductForOrganizationIncomingProductFilter,
                   ByCategoryForOrganizationIncomingProductFilter)
    search_fields = ('scheduleharvest__ooid',)
    inlines = [WeighingSetInline, ScheduleHarvestInline]
    form = IncomingProductForm
    actions = None

    # Filtrar en el Admin solo los cortes que su status sea distinto a "ready"
    # def get_queryset(self, request):
    #    return super().get_queryset(request).exclude(status="ready")

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

    def get_readonly_fields(self, request, obj=None):
        status = list(self.readonly_fields)
        # Si ya está aceptado, hacer el campo status solo lectura
        if obj and obj.status == 'ready':
            status.append('status')
        return status

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
        update_weighing_set_numbers(form.instance)

    class Media:
         js = ('js/admin/forms/packhouses/receiving/incomingproduct/incoming_product.js',)


# Lotes
class ScheduleHarvestInlineForBatch(CustomNestedStackedInlineMixin, admin.StackedInline):
    model = ScheduleHarvest
    extra = 0
    fields = ('ooid', 'harvest_date', 'category', 'product_provider', 'product', 'product_variety',
        'product_phenologies', 'product_harvest_size_kind', 'orchard', 'orchard_certifications', 'market',
        'weight_expected', 'weighing_scale', 'comments')
    readonly_fields = ('ooid', 'category', 'maquiladora', 'gatherer', 'product', 'product_variety')
    can_delete = False
    can_add = False
    custom_title = _("Schedule Harvest Information")
    inlines = [ScheduleHarvestHarvestingCrewInline, ScheduleHarvestVehicleInline ]

    def get_fields(self, request, obj=None):
        """
        Devuelve la tupla de campos, insertando 'gatherer' o 'maquiladora'
        justo después de 'category' según obj.category.
        """
        base = list(self.fields)
        # encuentra el índice donde va después de 'category':
        idx = base.index('category') + 1

        # si ya existe schedule_harvest (obj es el IncomingProduct):
        sh = ScheduleHarvest.objects.filter(incoming_product=obj).first() if obj else None
        if sh:
            if sh.category == 'gathering':
                base.insert(idx, 'gatherer')
            elif sh.category == 'maquila':
                base.insert(idx, 'maquiladora')
        return tuple(base)

    def get_formset(self, request, obj=None, **kwargs):
        FormSet = super().get_formset(request, obj, **kwargs)
        class CustomFormSet(FormSet, CustomScheduleHarvestFormSet):
            def __init__(self2, *args, **kwargs):
                super().__init__(*args, **kwargs)
                for form in self2.forms:
                    form.fields['weighing_scale'].required = True
        return CustomFormSet

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name in ("product_phenologies", "product_harvest_size_kind", "orchard"):
            obj_id = request.resolver_match.kwargs.get("object_id")
            sh = ScheduleHarvest.objects.filter(incoming_product__batch__pk=obj_id).first()

            if sh:
                pid = sh.product
                if db_field.name == "product_phenologies":
                    qs = ProductPhenologyKind.objects.filter(product=pid, is_enabled=True)
                elif db_field.name == "product_harvest_size_kind":
                    qs = ProductHarvestSizeKind.objects.filter(product=pid, is_enabled=True)
                else:  # "orchard"
                    org = sh.incoming_product.organization
                    qs = Orchard.objects.filter(product=pid, organization=org, is_enabled=True)
            else:
                qs = db_field.related_model.objects.none()

            kwargs["queryset"] = qs

        field_filters = {
            "market": {
                "model": Market,
                "filters": {"is_enabled": True},
            },
            "orchard_certifications": {
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
        js = ('js/admin/forms/packhouses/receiving/incomingproduct/vehicle_inline.js',
              'js/admin/forms/packhouses/receiving/incomingproduct/schedule_harvest_inline.js')

class IncomingProductInline(CustomNestedStackedInlineMixin, admin.StackedInline):
    model = IncomingProduct
    fields = ('phytosanitary_certificate', 'weighing_record_number', 'public_weighing_scale', 'public_weight_result', 'total_weighed_sets',
              'packhouse_weight_result', 'mrl', 'kg_sample', 'containers_assigned', 'full_containers_per_harvest', 'empty_containers', 'missing_containers', 'total_weighed_set_containers',
              'average_per_container', 'comments', 'is_quarantined', 'status')
    readonly_fields = ('status',)
    extra = 0
    max_num = 0
    show_change_link = True
    custom_title = _("Incoming Product Information")
    inlines = [WeighingSetInline, ScheduleHarvestInlineForBatch]

    def has_add_permission(self, request, obj=None):
        return False

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        base_fields = formset.form.base_fields
        if 'public_weighing_scale' in base_fields:
            widget = base_fields['public_weighing_scale'].widget
            for attr in ('can_add_related', 'can_change_related', 'can_delete_related', 'can_view_related'):
                setattr(widget, attr, False)
        return formset

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        update_weighing_set_numbers(form.instance)

@admin.register(Batch)
class BatchAdmin(ByOrganizationAdminMixin, nested_admin.NestedModelAdmin):
    list_display = ('ooid', 'get_scheduleharvest_ooid', 'get_scheduleharvest_product_provider', 'get_scheduleharvest_product', 
                    'get_scheduleharvest_product_variety', 'get_scheduleharvest_product_phenology', 'get_scheduleharvest_orchards',
                    'get_scheduleharvest_harvest_date', 'display_created_at',  'weight_received_display', 'get_batch_available_weight', 
                    'status', 'is_quarantined', 'display_available_for_processing', 'generate_actions_buttons',)
    fields = ['ooid', 'status', 'is_quarantined', 'is_available_for_processing']
    readonly_fields = ['ooid',]
    form = BatchForm
    inlines = [IncomingProductInline]
    list_per_page = 20
    actions = ['action_merge_batches', 'action_merge_into_existing_batch']
    admin.site.disable_action('delete_selected')

    @admin.action(description='Merge batches into a new batch.')
    def action_merge_batches(self, request, queryset):
        if queryset.count() < 2:
            self.message_user(
                request,
                _('Select at least two batches to merge.'),
                level=messages.WARNING
            )
            return

        qs = queryset.select_related('incomingproduct__scheduleharvest')

        # Validar provider/product/variety/phenology/status
        try:
            Batch.validate_merge_batches(qs)
        except ValidationError as e:
            self.message_user(request, e.message, level=messages.ERROR)
            return

        # Unir Lote
        with transaction.atomic():
            parents = [b for b in qs if b.is_parent]
            if len(parents) > 1:
                self.message_user(
                    request,
                    _('Cannot merge batches that already contain merged batches.'),
                    level=messages.ERROR
                )
                return
            if parents:
                destination = parents[0]
                sources = [b for b in qs if b != destination]
            else:
                destination = Batch.objects.create(
                    organization=queryset.first().organization,
                    status='ready',
                )
                sources = list(qs)
            for origin in sources:
                origin.parent = destination
                origin.status = 'ready'
                origin.is_available_for_processing = False
                origin.save(update_fields=[
                    'parent',
                    'status',
                    'is_available_for_processing',
                ])
        url = reverse(
            'admin:%s_%s_change' % (
                destination._meta.app_label,
                destination._meta.model_name
            ),
            args=[destination.pk]
        )

        msg = format_html(
            _('Batches were successfully merged into <a href="{}">batch {}</a>.'),
            url,
            destination.ooid
        )

        self.message_user(request, msg, level=messages.SUCCESS)

    @admin.action(description='Add batches to an existing merged batch.')
    def action_merge_into_existing_batch(self, request, queryset):
        if queryset.count() < 2:
            self.message_user(
                request,
                _('Select at least two batches to merge.'),
                level=messages.WARNING
            )
            return
        qs = queryset.select_related('incomingproduct__scheduleharvest')

        possible_parents = queryset.filter(
            parent__isnull=True, 
            children__isnull=False 
        ).distinct()

        if possible_parents.count() != 1:
            self.message_user(
                request,
                _('Only one merged batch can be selected as destination, but multiple were found.'),
                level=messages.ERROR
            )
            return
        
        parent = possible_parents.first()
        children_to_add = qs.exclude(pk=parent.pk)
        
        # Validar los lotes por añadir con los que ya fueron unidos
        try:
            Batch.validate_add_batches_to_existing_merge(parent, children_to_add)
        except ValidationError as e:
            self.message_user(request, e.message, level=messages.ERROR)
            return

        # Unir lotes al lote existente dentro de una transacción
        try:
            with transaction.atomic():
                for batch in children_to_add:
                    batch.parent = parent
                    batch.parent = parent
                    batch.status = 'ready'
                    batch.save()
        except Exception as e:
            self.message_user(
                request,
                _('An error occurred while merging batches: %s') % str(e),
                level=messages.ERROR
            )
            return
       
        url = reverse(
            'admin:%s_%s_change' % (
                parent._meta.app_label,
                parent._meta.model_name
            ),
            args=[parent.pk]
        )
        msg = format_html(
            _('Batches were successfully merged into <a href="{}">batch {}</a>.'),
            url,
            parent.ooid)
        self.message_user(request, msg, level=messages.SUCCESS)

    def generate_actions_buttons(self, obj):
        pass
    generate_actions_buttons.short_description = _('Actions')
    generate_actions_buttons.allow_tags = True
    

    def display_available_for_processing(self, obj):
        if obj.is_child:
            return ''
        return _boolean_icon(obj.is_available_for_processing)
    display_available_for_processing.short_description = _('Available for Processing')
    display_available_for_processing.admin_order_field = 'is_available_for_processing'

    def get_scheduleharvest_ooid(self, obj):
        batches = (
            obj.children.select_related('incomingproduct__scheduleharvest')
            if obj.is_parent else
            [obj])
        ooids = {
            str(sh.ooid)
            for b in batches
            if (incoming := getattr(b, 'incomingproduct', None))
            and (sh := getattr(incoming, 'scheduleharvest', None))
            and sh.ooid is not None
        }
        return ", ".join(sorted(ooids))
    get_scheduleharvest_ooid.short_description = _('Harvest')
    get_scheduleharvest_ooid.admin_order_field = 'incomingproduct__scheduleharvest__ooid'

    def get_scheduleharvest_harvest_date(self, obj):
        if obj.is_parent:
            fechas = obj.children.filter(
                incomingproduct__scheduleharvest__harvest_date__isnull=False
            ).values_list(
                'incomingproduct__scheduleharvest__harvest_date', flat=True
            )
            unique_dates = sorted({f for f in fechas})
            if not unique_dates:
                date_str = ''
            else:
                salida = [
                    date_format(f, format='DATE_FORMAT', use_l10n=True)
                    for f in unique_dates
                ]
                date_str = salida[0] if len(salida) == 1 else ", ".join(salida)
        else:
            incoming = getattr(obj, 'incomingproduct', None)
            sh = getattr(incoming, 'scheduleharvest', None) if incoming else None
            if sh and sh.harvest_date:
                date_str = date_format(sh.harvest_date,
                                       format='DATE_FORMAT',
                                       use_l10n=True)
            else:
                date_str = ''

        # 2) Devuelve siempre envuelto en un span de ancho mínimo
        return format_html(
            '<span style="display:inline-block; min-width:80px;">{}</span>',
            date_str
        )

    get_scheduleharvest_harvest_date.short_description = _("Schedule Harvest Date")
    get_scheduleharvest_harvest_date.admin_order_field = 'incomingproduct__scheduleharvest__harvest_date'

    def get_scheduleharvest_product(self, obj):
        batches = (
        obj.children.select_related('incomingproduct__scheduleharvest__product')
        if obj.is_parent else
        [obj])
        products = {
            str(sh.product)
            for b in batches
            if (incoming := getattr(b, 'incomingproduct', None))
            and (sh := getattr(incoming, 'scheduleharvest', None))
            and sh.product
        }
        return next(iter(products), '')
    get_scheduleharvest_product.short_description = _('Product')
    get_scheduleharvest_product.admin_order_field = 'incomingproduct__scheduleharvest__product'

    def get_scheduleharvest_orchards(self, obj):
        batches = (
            obj.children.select_related('incomingproduct__scheduleharvest__orchard')
            if obj.is_parent else
            [obj]
        )
        names = {
            str(orch)
            for b in batches
            if (incoming := getattr(b, 'incomingproduct', None))
            and (sh := getattr(incoming, 'scheduleharvest', None))
            and (orch := sh.orchard)
        }
        return ", ".join(sorted(names))
    get_scheduleharvest_orchards.short_description = _('Orchards')
    get_scheduleharvest_orchards.admin_order_field = 'incomingproduct__scheduleharvest__orchard'

    def get_scheduleharvest_product_provider(self, obj):
        batches = (
        obj.children.select_related('incomingproduct__scheduleharvest__product_provider')
        if obj.is_parent else
        [obj])
        product_provider = {
            str(sh.product_provider)
            for b in batches
            if (incoming := getattr(b, 'incomingproduct', None))
            and (sh := getattr(incoming, 'scheduleharvest', None))
            and sh.product_provider
        }
        return next(iter(product_provider), '')
    get_scheduleharvest_product_provider.short_description = _('Product Provider')
    get_scheduleharvest_product_provider.admin_order_field = 'incomingproduct__scheduleharvest__product_provider'

    def weight_received_display(self, obj):
        return f"{obj.weight_received:.3f}" if obj.weight_received else ""
    weight_received_display.short_description = _('Weight Received')

    def get_batch_available_weight(self, obj):
        total = obj.available_weight
        return '{:,.3f}'.format(total) if total else ''
    get_batch_available_weight.short_description = _('Available Weight')

    def get_scheduleharvest_product_variety(self, obj):
        batches = (
        obj.children.select_related('incomingproduct__scheduleharvest__product_variety')
        if obj.is_parent else
        [obj])
        products = {
            str(sh.product_variety)
            for b in batches
            if (incoming := getattr(b, 'incomingproduct', None))
            and (sh := getattr(incoming, 'scheduleharvest', None))
            and sh.product_variety
        }
        return next(iter(products), '')
    get_scheduleharvest_product_variety.short_description = _('Product Variety')
    get_scheduleharvest_product_variety.admin_order_field = 'incomingproduct__scheduleharvest__product'

    def get_scheduleharvest_product_phenology(self, obj):
        batches = (
        obj.children.select_related('incomingproduct__scheduleharvest__product_phenologies')
        if obj.is_parent else
        [obj])
        products = {
            str(sh.product_phenologies)
            for b in batches
            if (incoming := getattr(b, 'incomingproduct', None))
            and (sh := getattr(incoming, 'scheduleharvest', None))
            and sh.product_phenologies
        }
        return next(iter(products), '')
    get_scheduleharvest_product_phenology.short_description = _('Product Phenology')
    get_scheduleharvest_product_phenology.admin_order_field = 'incomingproduct__scheduleharvest__product'

    def display_created_at(self, obj):
        s = date_format(obj.created_at, format='DATETIME_FORMAT', use_l10n=True)
        return format_html(
            '<span style="display:inline-block; min-width:80px;">{}</span>',
            s
        )
    display_created_at.short_description = _("Entry Date")
    display_created_at.admin_order_field = 'created_at'

    class Media:
        js = ('js/admin/forms/packhouses/receiving/batch/incoming_product_for_batch.js',
              'js/admin/forms/packhouses/receiving/batch/batch_operation.js',)


# Inocuidad
class DryMatterInline(nested_admin.NestedTabularInline):
    model = DryMatter
    extra = 0
    fields = ['product_weight', 'paper_weight', 'moisture_weight', 'dry_weight', 'dry_matter']

    class Media:
        js = ('js/admin/forms/packhouses/receiving/food_safety/average.js',)

class InternalInspectionInline(nested_admin.NestedTabularInline):
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
                    kwargs["queryset"] = ProductPest.objects.filter(product=schedule_harvest.product, pest__pest__inside=True)

                except InternalInspection.DoesNotExist:
                    kwargs['queryset'] = ProductPest.objects.none()
            else:
                kwargs['queryset'] = ProductPest.objects.none()

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    class Media:
        js = ('js/admin/forms/packhouses/receiving/food_safety/average.js',)

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
            food_safety_config = ProductFoodSafetyProcess.objects.filter(product=schedule_harvest.product).values_list('procedure__name_model', flat=True)
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
        # Mapeo de nombres de inlines con sus clases
        INLINE_CLASSES = {
            "DryMatter": DryMatterInline,
            "InternalInspection": InternalInspectionInline,
            "VehicleReview": VehicleReviewInline,
            "SampleCollection": SampleCollectionInline,
        }
        inlines_list = []

        if not obj:
            return inlines_list

        try:
            incoming_product = IncomingProduct.objects.filter(batch=obj.batch).first()
            schedule_harvest = ScheduleHarvest.objects.filter(incoming_product=incoming_product).first()
            food_safety_config = ProductFoodSafetyProcess.objects.filter(product=schedule_harvest.product).values_list('procedure__name_model', flat=True)
            inlines_list = [INLINE_CLASSES[inline] for inline in food_safety_config if inline in INLINE_CLASSES]

            if DryMatterInline in inlines_list or InternalInspectionInline in inlines_list:
                inlines_list.append(AverageInline)

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
