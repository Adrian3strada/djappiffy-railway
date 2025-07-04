from django.contrib import admin, messages
from packhouses.receiving.views import weighing_set_report, export_weighing_labels, export_batch_record
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
                    BatchForm, WeighingSetForm, WeighingSetInlineFormSet, WeighingSetContainerInlineFormSet, BaseIncomingProductInlineFormSet)
from .filters import (ByOrchardForOrganizationIncomingProductFilter, ByProviderForOrganizationIncomingProductFilter, ByProductForOrganizationIncomingProductFilter,
                      ByCategoryForOrganizationIncomingProductFilter, ByProductProducerForOrganizationIncomingProductFilter, ByOrchardForOrganizationBatchFilter,
                      ByProviderForOrganizationBatchFilter, ByProductPhenologyForOrganizationIncomingProductFilter, ByOrchardProductCategoryForOrganizationIncomingProductFilter,
                      MaquiladoraForIncomingProductFilter, ByOrchardCertificationForOrganizationIncomingProductFilter, SchedulingTypeFilter,
                      ByHarvestingCrewForOrganizationIncomingProductFilter, GathererForIncomingProductFilter,
                      ByCategoryForOrganizationIncomingProductFilter, ByProductProducerForOrganizationIncomingProductFilter, ByOrchardForOrganizationBatchFilter,
                      ByProviderForOrganizationBatchFilter, ByProductPhenologyForOrganizationIncomingProductFilter, ByOrchardProductCategoryForOrganizationIncomingProductFilter,
                      MaquiladoraForIncomingProductFilter, ByOrchardCertificationForOrganizationIncomingProductFilter, SchedulingTypeFilter,
                      ByHarvestingCrewForOrganizationIncomingProductFilter, GathererForIncomingProductFilter,
                      ByProductForOrganizationBatchFilter, ByCategoryForOrganizationBatchFilter, ByProductProducerForOrganizationBatchFilter,
                      ByProductPhenologyForOrganizationBatchFilter, ByOrchardProductCategoryForOrganizationBatchFilter, ByHarvestingCrewForOrganizationBatchFilter,
                      GathererForBatchFilter, MaquiladoraForBatchFilter, ByOrchardCertificationForOrganizationBatchFilter, SchedulingTypeForBatchFilter, BatchTypeFilter,
                      ByOrchardCertificationForOrganizationFoodSafetyFilter)
from .utils import update_weighing_set_numbers,  CustomScheduleHarvestFormSet
from common.base.decorators import uppercase_formset_charfield, uppercase_alphanumeric_formset_charfield
from common.base.decorators import uppercase_form_charfield, uppercase_alphanumeric_form_charfield
from django.urls import reverse
from django.utils.html import format_html
from django.urls import path, reverse
import nested_admin
from common.base.models import Pest
from django.db.models import Q
from django import forms
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils.formats import date_format
from .mixins import IncomingProductMetricsMixin, BatchDisplayMixin
from common.base.utils import SheetReportExportAdminMixin
from .views import basic_report
from .resources import IncomingProductResource, BatchResource
from .filters import DateRangeFilter
from django.db.models import Sum, F
from common.settings import STATUS_CHOICES

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

    class Media:
        js = ('js/admin/forms/packhouses/receiving/incomingproduct/schedule_harvest_crew_inline.js',)


class ScheduleHarvestVehicleInline(CustomNestedStackedInlineMixin, admin.StackedInline):
    model = ScheduleHarvestVehicle
    form = ScheduleHarvestVehicleForm
    formset = BaseScheduleHarvestVehicleFormSet
    fields = ('provider', 'vehicle', 'has_arrived', 'guide_number', 'stamp_vehicle_number')  # Agregar el nuevo campo
    extra = 0
    max_num = 0
    inlines = [HarvestCuttingContainerVehicleInline]
    readonly_fields = ('provider',)

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)

        # Deshabilitar los enlaces relacionados
        for field in formset.form.base_fields.values():
            field.widget.can_add_related = False
            field.widget.can_change_related = False
            field.widget.can_delete_related = False
            field.widget.can_view_related = False

        class CustomFormSet(formset):
            def _construct_form(self, i, **kwargs_inner):
                kwargs_inner['request'] = request
                form = super()._construct_form(i, **kwargs_inner)

                # Filtrar vehículos según el provider de la instancia
                if form.instance and form.instance.provider_id:
                    provider = form.instance.provider
                    filtered_qs = Vehicle.objects.filter(
                        organization=request.organization,
                        is_enabled=True,
                        provider=provider
                    ).distinct()

                    form.fields['vehicle'].queryset = filtered_qs
                else:
                    form.fields['vehicle'].queryset = Vehicle.objects.none()

                return form

        return CustomFormSet

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        organization = getattr(request, 'organization', None)

        if db_field.name == "provider":
            kwargs["queryset"] = Provider.objects.filter(
                organization=organization,
                is_enabled=True,
                category='harvesting_provider'
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
    readonly_fields = ('ooid','is_scheduled', 'category', 'maquiladora', 'gatherer', 'product', 'product_variety', 'orchard',)
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
            'ooid', 'is_scheduled', 'harvest_date', 'category', 'product_provider', 'product', 'product_variety',
            'product_phenology', 'product_harvest_size_kind', 'orchard', 'market',
            'weight_expected', 'comments'
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

        if db_field.name in ("product_phenology", "product_harvest_size_kind", "orchard"):
            qs_none = db_field.related_model.objects.none()
            obj_id = request.resolver_match.kwargs.get("object_id")
            incoming_product = IncomingProduct.objects.filter(id=obj_id).first() if obj_id else None
            schedule_harvest = (ScheduleHarvest.objects.filter(incoming_product=incoming_product).first()
                                if incoming_product else None)
            mapping = {
                "product_phenology": (ProductPhenologyKind, "product_phenology"),
                "product_harvest_size_kind": (ProductHarvestSizeKind, "product_harvest_size_kind"),
                "orchard": (Orchard, None),
            }
            model, field = mapping[db_field.name]
            if db_field.name == "orchard":
                org = incoming_product.organization if incoming_product else None
                prod = schedule_harvest.product if schedule_harvest and hasattr(schedule_harvest, "product") else None
                kwargs["queryset"] = model.objects.filter(organization=org, products=prod, is_enabled=True) if org and prod else qs_none
            else:
                prod_obj = getattr(schedule_harvest, field, None) if schedule_harvest else None
                prod = prod_obj.product if prod_obj else None
                kwargs["queryset"] = model.objects.filter(product=prod, is_enabled=True) if prod else qs_none

        field_filters = {
            "market": {
                "model": Market,
                "filters": {"is_enabled": True},
            },
            "product_provider": {
                "model": Provider,
                "filters": {"category": "product_provider", "is_enabled": True},
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
              'js/admin/forms/packhouses/receiving/incomingproduct/schedule_harvest_inline.js', )

# Inlines para los pallets
class WeighingSetContainerInline(nested_admin.NestedTabularInline):
    model = WeighingSetContainer
    formset = WeighingSetContainerInlineFormSet
    extra = 0

    def get_max_num(self, request, obj=None, **kwargs):
        if obj and getattr(obj, 'protected', False):
            return 0
        return super().get_max_num(request, obj, **kwargs)

    def get_readonly_fields(self, request, obj=None):
        # Si se está editando un IncomingProduct existente, los campos son solo lectura
        if obj and obj.pk:
            return [f.name for f in self.model._meta.fields if f.name != 'id']
        return super().get_readonly_fields(request, obj)

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
    fields = ('ooid', 'harvesting_crew', 'gross_weight', 'total_containers', 'container_tare',
              'platform_tare', 'net_weight',)
    extra = 0
    form = WeighingSetForm
    formset = WeighingSetInlineFormSet

    def has_change_permission(self, request, obj=None):
        if obj:
            return False
        return True

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

        if db_field.name == "harvesting_crew":
            kwargs["queryset"] = HarvestingCrew.objects.filter(
                organization=organization,
                is_enabled=True
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    class Media:
        js = ('js/admin/forms/packhouses/receiving/incomingproduct/weighing_set_inline.js',)


# Reciba
@admin.register(IncomingProduct)
class IncomingProductAdmin(SheetReportExportAdminMixin, IncomingProductMetricsMixin, ByOrganizationAdminMixin, nested_admin.NestedModelAdmin):
    list_display = ('get_scheduleharvest_ooid', 'get_scheduleharvest_harvest_date', 'created_at', 'get_scheduleharvest_product_provider',
                    'get_scheduleharvest_category', 'get_scheduleharvest_orchard', 'get_orchard_code',
                    'get_scheduleharvest_orchard_product_producer', 'get_scheduleharvest_product', 'get_orchard_category',
                    'get_scheduleharvest_product_variety', 'get_scheduleharvest_product_phenology', 'get_scheduleharvest_product_ripeness',
                    'get_scheduleharvest_market', 'get_total_net_weight',
                    'status','generate_actions_buttons')
    fields = ('mrl', 'phytosanitary_certificate', 'weighing_record_number', 'public_weighing_scale', 'public_weight_result',
              'kg_sample', *IncomingProductMetricsMixin.readonly_fields,
              'comments', 'is_quarantined','status')
    list_filter = (('created_at', DateRangeFilter), ByProviderForOrganizationIncomingProductFilter, ByProductProducerForOrganizationIncomingProductFilter,
                   ByProductForOrganizationIncomingProductFilter,ByProductPhenologyForOrganizationIncomingProductFilter,
                   ByOrchardProductCategoryForOrganizationIncomingProductFilter, ByHarvestingCrewForOrganizationIncomingProductFilter,
                   ByCategoryForOrganizationIncomingProductFilter, GathererForIncomingProductFilter, MaquiladoraForIncomingProductFilter,
                   ByOrchardCertificationForOrganizationIncomingProductFilter, SchedulingTypeFilter, 'status')
    search_fields = ('scheduleharvest__ooid',)
    readonly_fields = IncomingProductMetricsMixin.readonly_fields
    report_function = staticmethod(basic_report)
    resource_classes = [IncomingProductResource]
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
            path('weighing_set_report/<uuid:uuid>/', self.admin_site.admin_view(weighing_set_report), name='receiving_incomingproduct_weighing_set_report'),
        ]
        return custom_urls + urls

    def generate_actions_buttons(self, obj):
        pdf_url = reverse('admin:receiving_incomingproduct_weighing_set_report', args=[obj.uuid])
        tooltip_weighing_report = _('Generate Weighing Set Report')
        return format_html(
            '''
            <a class="button d-flex justify-content-center align-items-center"
               href="{}" target="_blank" data-toggle="tooltip" title="{}"
               style="display: flex; justify-content: center; align-items: center;">
                <i class="fa-solid fa-scale-balanced"></i>
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
        return schedule_harvest.orchard.name if schedule_harvest else None

    def get_scheduleharvest_product_provider(self, obj):
        schedule_harvest = obj.scheduleharvest
        return schedule_harvest.product_provider if schedule_harvest else None

    def get_scheduleharvest_orchard_product_producer(self, obj):
        schedule_harvest = obj.scheduleharvest
        return schedule_harvest.orchard.producer if schedule_harvest else None

    def get_orchard_code(self, obj):
        return obj.scheduleharvest.orchard.code if obj.scheduleharvest.orchard else None

    def get_orchard_category(self, obj):
        if obj.scheduleharvest.orchard:
            return obj.scheduleharvest.orchard.get_category_display()
        return None

    def get_scheduleharvest_product_variety(self, obj):
        return obj.scheduleharvest.product_variety if obj.scheduleharvest else None

    def get_scheduleharvest_product_phenology(self, obj):
        return obj.scheduleharvest.product_phenology if obj.scheduleharvest else None

    def get_scheduleharvest_product_ripeness(self, obj):
        return obj.scheduleharvest.product_ripeness if obj.scheduleharvest else None

    def get_scheduleharvest_market(self, obj):
        return obj.scheduleharvest.market if obj.scheduleharvest else None

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(total_net_weight_sum=Sum('weighingset__net_weight'))

    def get_total_net_weight(self, obj):
        return obj.total_net_weight_sum

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
    get_scheduleharvest_orchard_product_producer.admin_order_field = 'scheduleharvest__orchard__producer'
    get_scheduleharvest_orchard_product_producer.short_description = _('Product Producer')
    get_orchard_code.short_description = _('Orchard Code')
    get_orchard_code.admin_order_field = 'scheduleharvest__orchard__code'
    get_orchard_category.short_description = _('Product Category')
    get_orchard_category.admin_order_field = 'scheduleharvest__orchard__category'
    get_scheduleharvest_product_variety.short_description = _('Product Variety')
    get_scheduleharvest_product_variety.admin_order_field = 'scheduleharvest__product_variety'
    get_scheduleharvest_product_phenology.short_description = _('Product Phenology')
    get_scheduleharvest_product_phenology.admin_order_field = 'scheduleharvest__product_phenology'
    get_scheduleharvest_product_ripeness.short_description = _('Product Ripeness')
    get_scheduleharvest_product_ripeness.admin_order_field = 'scheduleharvest__product_ripeness'
    get_scheduleharvest_market.short_description = _('Market')
    get_scheduleharvest_market.admin_order_field = 'scheduleharvest__market'
    get_total_net_weight.short_description = 'Net Weight Received'
    get_total_net_weight.admin_order_field = 'total_net_weight_sum'

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        update_weighing_set_numbers(form.instance)

    class Media:
         js = ('js/admin/forms/packhouses/receiving/incomingproduct/incoming_product.js',)


# Lotes
class ScheduleHarvestInlineForBatch(CustomNestedStackedInlineMixin, admin.StackedInline):
    model = ScheduleHarvest
    extra = 0
    fields = ('ooid', 'is_scheduled', 'harvest_date', 'category', 'product_provider', 'product', 'product_variety',
        'product_phenology', 'product_harvest_size_kind', 'orchard', 'market',
        'weight_expected', 'comments')
    readonly_fields = ('ooid', 'is_scheduled', 'category', 'maquiladora', 'gatherer', 'product', 'product_variety', 'orchard')
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
            pass
        return CustomFormSet

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name in ("product_phenology", "product_harvest_size_kind", "orchard"):
            obj_id = request.resolver_match.kwargs.get("object_id")
            sh = ScheduleHarvest.objects.filter(incoming_product__batch__pk=obj_id).first()

            if sh:
                pid = sh.product
                if db_field.name == "product_phenology":
                    qs = ProductPhenologyKind.objects.filter(product=pid, is_enabled=True)
                elif db_field.name == "product_harvest_size_kind":
                    qs = ProductHarvestSizeKind.objects.filter(product=pid, is_enabled=True)
                else:  # "orchard"
                    org = sh.incoming_product.organization
                    qs = Orchard.objects.filter(products=pid, organization=org, is_enabled=True) #
            else:
                qs = db_field.related_model.objects.none()

            kwargs["queryset"] = qs

        field_filters = {
            "market": {
                "model": Market,
                "filters": {"is_enabled": True},
            },
            "product_provider": {
                "model": Provider,
                "filters": {"category": "product_provider", "is_enabled": True},
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
              'js/admin/forms/packhouses/receiving/incomingproduct/schedule_harvest_inline.js',
              'js/admin/forms/packhouses/receiving/incomingproduct/schedule_harvest_crew_inline.js')


class IncomingProductInline(IncomingProductMetricsMixin, CustomNestedStackedInlineMixin, admin.StackedInline):
    model = IncomingProduct
    fields = ('mrl', 'phytosanitary_certificate', 'weighing_record_number', 'public_weighing_scale', 'public_weight_result',
              'kg_sample', *IncomingProductMetricsMixin.readonly_fields,
              'comments', 'is_quarantined','status')
    readonly_fields = ('status',)
    extra = 0
    max_num = 0
    show_change_link = True
    formset = BaseIncomingProductInlineFormSet
    custom_title = _("Incoming Product Information")
    inlines = [WeighingSetInline, ScheduleHarvestInlineForBatch]
    readonly_fields = IncomingProductMetricsMixin.readonly_fields + ('is_quarantined', 'status')

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
class BatchAdmin(SheetReportExportAdminMixin, ByOrganizationAdminMixin, BatchDisplayMixin, nested_admin.NestedModelAdmin):
    list_display = ('ooid', 'get_scheduleharvest_ooid', 'get_scheduleharvest_harvest_date', 'display_created_at', 'get_scheduleharvest_product_provider',
                    'get_scheduleharvest_orchards', 'get_orchard_code', 'get_orchard_product_producer', 'get_scheduleharvest_product', 'get_orchard_category',
                    'get_scheduleharvest_product_variety', 'get_scheduleharvest_product_phenology', 'get_product_ripeness', 'get_batch_merge_status',
                    'weight_received_display', 'get_batch_available_weight', 'display_available_for_processing', 'status', 'generate_actions_buttons',
                    )
    form = BatchForm
    inlines = [IncomingProductInline]
    list_filter = (('created_at', DateRangeFilter),ByProviderForOrganizationBatchFilter, ByProductProducerForOrganizationBatchFilter, ByProductForOrganizationBatchFilter,
                   ByProductPhenologyForOrganizationBatchFilter, ByOrchardProductCategoryForOrganizationBatchFilter, ByHarvestingCrewForOrganizationBatchFilter,
                   ByCategoryForOrganizationBatchFilter, GathererForBatchFilter, MaquiladoraForBatchFilter, ByOrchardCertificationForOrganizationBatchFilter,
                   SchedulingTypeForBatchFilter, 'is_available_for_processing', BatchTypeFilter, 'status',)
    list_per_page = 20
    search_fields = ('ooid',)
    report_function = staticmethod(basic_report)
    resource_classes = [BatchResource]
    actions = ['action_merge_batches', 'action_merge_into_existing_batch', 'action_unmerge_all_batches',
               'action_unmerge_selected_batches']
    admin.site.disable_action('delete_selected')

    def has_add_permission(self, request):
        return False

    def get_weight_fields(self, is_parent):
        base = ['display_own_weight_received', 'display_own_net_received']
        extra = ['display_weight_received', 'display_available_weight'] if is_parent else []
        return base + extra

    def get_fieldsets(self, request, obj=None):
        fields = ['ooid', 'status', 'is_available_for_processing', 'display_batch_role']
        fields += self.get_weight_fields(obj.is_parent if obj else False)
        return ((_('Batch Info'), {'fields': fields}),)

    def get_readonly_fields(self, request, obj=None):
        return ['ooid', 'display_batch_role'] + self.get_weight_fields(obj.is_parent if obj else False)

    @admin.action(description=_('Merge selected batches into a single batch group'))
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

        try:
            parent_batch = Batch.merge_batches(qs)
        except Exception as e:
            self.message_user(
                request,
                _('An unexpected error occurred while merging batches: %s') % str(e),
                level=messages.ERROR
            )
            return

        url = reverse(
            'admin:%s_%s_change' % (
                parent_batch._meta.app_label,
                parent_batch._meta.model_name
            ),
            args=[parent_batch.pk]
        )

        msg = format_html(
            _('Batches were successfully merged into <a href="{}">batch {}</a>.'),
            url,
            parent_batch.ooid
        )

        self.message_user(request, msg, level=messages.SUCCESS)

    @admin.action(description=_('Merge batches to an existing batch group.'))
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

        if possible_parents.count() == 0:
            self.message_user(
                request,
                _('You must select exactly one merged batch (a batch that already has batches merged into) as the destination.'),
                level=messages.ERROR
            )
            return

        if possible_parents.count() > 1:
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
            self.message_user(
                request,
                _('Validation error: %s') % e.message,
                level=messages.ERROR
            )
            return

        # Unir lotes al lote existente dentro de una transacción
        try:
            Batch.add_batches_to_merge(parent, children_to_add)
        except Exception as e:
            self.message_user(
                request,
                _('An error occurred while saving batches: %s') % str(e),
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

    @admin.action(description=_('Unmerge all batches from this parent'))
    def action_unmerge_all_batches(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(
                request,
                _('Please select only one parent batch to unmerge.'),
                level=messages.WARNING
            )
            return
        parent_batch = queryset.first()
        try:
            Batch.unmerge_all_children(parent_batch)
            self.message_user(
                request,
                _('All child batches of batch %(ooid)s were successfully unmerged.') % {'ooid': parent_batch.ooid},
                level=messages.SUCCESS
            )
        except ValidationError as e:
            self.message_user(
                request,
                e.message,
                level=messages.ERROR
            )

    @admin.action(description=_('Unmerge selected batches from parent.'))
    def action_unmerge_selected_batches(self, request, queryset):
        try:
            Batch.unmerge_selected_children(queryset)
            ooids = ', '.join(str(batch.ooid) for batch in queryset)
            self.message_user(
                request,
                _('The following batches were successfully unmerged: %(ooids)s.') % {'ooids': ooids},
                level=messages.SUCCESS
            )
        except ValidationError as e:
            self.message_user(
                request,
                e.message,
                level=messages.ERROR
            )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('weighing_set_report/<uuid:uuid>/', self.admin_site.admin_view(weighing_set_report), {'source': 'batch'}, name='receiving_batch_weighing_set_report'),
            path('weighing_labels/<uuid:uuid>/', self.admin_site.admin_view(export_weighing_labels), name='receiving_batch_export_weighing_labels'),
            path('batch_record/<uuid:uuid>/', self.admin_site.admin_view(export_batch_record), name='receiving_batch_export_batch_record'),
        ]
        return custom_urls + urls

    def generate_actions_buttons(self, obj):
        weighing_labels_url = reverse('weighing_set_labels', args=[obj.uuid])
        tooltip_weighing_labels = _('Weighing Set Labels')
        batch_record_url = reverse('batch_record_report', args=[obj.uuid])
        tooltip_batch_record = _('Generate Batch Record')
        weighing_report_url = reverse('batch_weighing_set_report', args=[obj.uuid])
        tooltip_weighing_report = _('Generate Weighing Set Report')


        return format_html(
            '''
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <a class="button"
                href="{}" target="_blank" data-toggle="tooltip" title="{}"
                style="display: inline-flex; justify-content: center; align-items: center;">
                    <i class="fa-solid fa-file"></i>
                </a>
                <a class="button"
                href="{}" target="_blank" data-toggle="tooltip" title="{}"
                style="display: inline-flex; justify-content: center; align-items: center;">
                    <i class="fa-solid fa-scale-balanced"></i>
                </a>
                <a class="button"
                href="{}" target="_blank" data-toggle="tooltip" title="{}"
                style="display: inline-flex; justify-content: center; align-items: center;">
                    <i class="fa-solid fa-tags"></i>
                </a>
            </div>
            ''',
            batch_record_url,   tooltip_batch_record,
            weighing_report_url, tooltip_weighing_report,
            weighing_labels_url, tooltip_weighing_labels,
        )


    generate_actions_buttons.short_description = _('Actions')
    generate_actions_buttons.allow_tags = True

    def display_created_at(self, obj):
        s = date_format(obj.created_at, format='DATETIME_FORMAT', use_l10n=True)
        return format_html(
            '<span style="display:inline-block; min-width:80px;">{}</span>',
            s
        )
    display_created_at.short_description = _("Entry Date")
    display_created_at.admin_order_field = 'created_at'

    class Media:
        js = ('js/admin/forms/packhouses/receiving/batch/batch_operation.js',
              'js/admin/forms/packhouses/receiving/batch/weighingset_inline_for_batch.js',)


# Inocuidad
class DryMatterInline(nested_admin.NestedTabularInline):
    model = DryMatter
    extra = 0
    fields = ['product_weight', 'paper_weight', 'moisture_weight', 'dry_weight', 'dry_matter']

    class Media:
        js = ('js/admin/forms/packhouses/receiving/food_safety/average.js',)

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.status == 'closed':
            return [field.name for field in self.model._meta.fields if field.name != 'id']
        return super().get_readonly_fields(request, obj)

    def has_change_permission(self, request, obj=None):
        if obj and obj.status == 'closed':
            return request.method in ['GET']
        return super().has_change_permission(request, obj)

    def has_add_permission(self, request, obj):
        if obj and obj.status == 'closed':
            return False
        return super().has_add_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj and obj.status == 'closed':
            return False
        return super().has_delete_permission(request, obj)

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

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.status == 'closed':
            fields = [field.name for field in self.model._meta.fields if field.name != 'id']
            m2m_fields = [field.name for field in self.model._meta.many_to_many]
            return fields + m2m_fields
        return super().get_readonly_fields(request, obj)

    def has_change_permission(self, request, obj=None):
        if obj and obj.status == 'closed':
            return request.method in ['GET']
        return super().has_change_permission(request, obj)

    def has_add_permission(self, request, obj):
        if obj and obj.status == 'closed':
            return False
        return super().has_add_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj and obj.status == 'closed':
            return False
        return super().has_delete_permission(request, obj)

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

    def get_readonly_fields(self, request, obj=None):
        object_id = request.resolver_match.kwargs.get("object_id")
        if object_id:
            food_safety = FoodSafety.objects.get(pk=object_id)
            if food_safety.status == 'closed':
                return ['transport_inspection'] + [f.name for f in self.model._meta.fields if f.name != 'id']
        return super().get_readonly_fields(request, obj)

    def has_change_permission(self, request, obj=None):
        object_id = request.resolver_match.kwargs.get("object_id")
        if object_id:
            food_safety = FoodSafety.objects.get(pk=object_id)
            if food_safety.status == 'closed':
                return request.method in ['GET']
        return super().has_change_permission(request, obj)

    def has_add_permission(self, request, obj):
        object_id = request.resolver_match.kwargs.get("object_id")
        if object_id:
            food_safety = FoodSafety.objects.get(pk=object_id)
            if food_safety.status == 'closed':
                return False
        return super().has_add_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        object_id = request.resolver_match.kwargs.get("object_id")
        if object_id:
            food_safety = FoodSafety.objects.get(pk=object_id)
            if food_safety.status == 'closed':
                return False
        return super().has_delete_permission(request, obj)

class VehicleConditionInline(nested_admin.NestedTabularInline):
    model = VehicleCondition
    extra = 0
    min_num = 1
    max_num=1

    def transport_condition(self, obj=None):
        return ''

    readonly_fields = ['transport_condition']
    fields = ['transport_condition', 'is_clean', 'good_condition', 'broken', 'damaged', 'seal']

    def get_readonly_fields(self, request, obj=None):
        object_id = request.resolver_match.kwargs.get("object_id")
        if object_id:
            food_safety = FoodSafety.objects.get(pk=object_id)
            if food_safety.status == 'closed':
                return ['transport_condition'] + [f.name for f in self.model._meta.fields if f.name != 'id']
        return super().get_readonly_fields(request, obj)

    def has_change_permission(self, request, obj=None):
        object_id = request.resolver_match.kwargs.get("object_id")
        if object_id:
            food_safety = FoodSafety.objects.get(pk=object_id)
            if food_safety.status == 'closed':
                return request.method in ['GET']
        return super().has_change_permission(request, obj)

    def has_add_permission(self, request, obj):
        object_id = request.resolver_match.kwargs.get("object_id")
        if object_id:
            food_safety = FoodSafety.objects.get(pk=object_id)
            if food_safety.status == 'closed':
                return False
        return super().has_add_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        object_id = request.resolver_match.kwargs.get("object_id")
        if object_id:
            food_safety = FoodSafety.objects.get(pk=object_id)
            if food_safety.status == 'closed':
                return False
        return super().has_delete_permission(request, obj)

class VehicleReviewInline(nested_admin.NestedStackedInline):
    model = VehicleReview
    extra = 0
    inlines = [VehicleInspectionInline, VehicleConditionInline]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)

        if db_field.name == "vehicle":
            object_id = request.resolver_match.kwargs.get("object_id")

            food_safety = FoodSafety.objects.get(pk=object_id)
            incoming_product = IncomingProduct.objects.filter(batch=food_safety.batch).first()
            schedule_harvest = ScheduleHarvest.objects.filter(incoming_product=incoming_product).first()
            kwargs["queryset"] = ScheduleHarvestVehicle.objects.filter(schedule_harvest_id=schedule_harvest, has_arrived=True)
            return super().formfield_for_foreignkey(db_field, request, **kwargs)

    class Media:
        js = ('js/admin/forms/packhouses/receiving/food_safety/select_vehicle.js',)

class SampleWeightInline(nested_admin.NestedTabularInline):
    model = SampleWeight
    extra = 0
    fields = ['weight']

    def get_readonly_fields(self, request, obj=None):
        object_id = request.resolver_match.kwargs.get("object_id")
        if object_id:
            food_safety = FoodSafety.objects.get(pk=object_id)
            if food_safety.status == 'closed':
                return [f.name for f in self.model._meta.fields if f.name != 'id']
        return super().get_readonly_fields(request, obj)

    def has_change_permission(self, request, obj=None):
        object_id = request.resolver_match.kwargs.get("object_id")
        if object_id:
            food_safety = FoodSafety.objects.get(pk=object_id)
            if food_safety.status == 'closed':
                return request.method in ['GET']
        return super().has_change_permission(request, obj)

    def has_add_permission(self, request, obj):
        object_id = request.resolver_match.kwargs.get("object_id")
        if object_id:
            food_safety = FoodSafety.objects.get(pk=object_id)
            if food_safety.status == 'closed':
                return False
        return super().has_add_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        object_id = request.resolver_match.kwargs.get("object_id")
        if object_id:
            food_safety = FoodSafety.objects.get(pk=object_id)
            if food_safety.status == 'closed':
                return False
        return super().has_delete_permission(request, obj)

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

    def get_readonly_fields(self, request, obj=None):
        object_id = request.resolver_match.kwargs.get("object_id")
        if object_id:
            food_safety = FoodSafety.objects.get(pk=object_id)
            if food_safety.status == 'closed':
                return [f.name for f in self.model._meta.fields if f.name != 'id']
        return super().get_readonly_fields(request, obj)

    def has_change_permission(self, request, obj=None):
        object_id = request.resolver_match.kwargs.get("object_id")
        if object_id:
            food_safety = FoodSafety.objects.get(pk=object_id)
            if food_safety.status == 'closed':
                return request.method in ['GET']
        return super().has_change_permission(request, obj)

    def has_add_permission(self, request, obj):
        object_id = request.resolver_match.kwargs.get("object_id")
        if object_id:
            food_safety = FoodSafety.objects.get(pk=object_id)
            if food_safety.status == 'closed':
                return False
        return super().has_add_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        object_id = request.resolver_match.kwargs.get("object_id")
        if object_id:
            food_safety = FoodSafety.objects.get(pk=object_id)
            if food_safety.status == 'closed':
                return False
        return super().has_delete_permission(request, obj)

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

    def get_readonly_fields(self, request, obj=None):
        object_id = request.resolver_match.kwargs.get("object_id")
        if object_id:
            food_safety = FoodSafety.objects.get(pk=object_id)
            if food_safety.status == 'closed':
                return [f.name for f in self.model._meta.fields if f.name != 'id']
        return super().get_readonly_fields(request, obj)

    def has_change_permission(self, request, obj=None):
        object_id = request.resolver_match.kwargs.get("object_id")
        if object_id:
            food_safety = FoodSafety.objects.get(pk=object_id)
            if food_safety.status == 'closed':
                return request.method in ['GET']
        return super().has_change_permission(request, obj)

    def has_add_permission(self, request, obj):
        object_id = request.resolver_match.kwargs.get("object_id")
        if object_id:
            food_safety = FoodSafety.objects.get(pk=object_id)
            if food_safety.status == 'closed':
                return False
        return super().has_add_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        object_id = request.resolver_match.kwargs.get("object_id")
        if object_id:
            food_safety = FoodSafety.objects.get(pk=object_id)
            if food_safety.status == 'closed':
                return False
        return super().has_delete_permission(request, obj)

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

    def get_readonly_fields(self, request, obj=None):
        object_id = request.resolver_match.kwargs.get("object_id")
        if object_id:
            food_safety = FoodSafety.objects.get(pk=object_id)
            if food_safety.status == 'closed':
                return [f.name for f in self.model._meta.fields if f.name != 'id']
        return super().get_readonly_fields(request, obj)

    def has_change_permission(self, request, obj=None):
        object_id = request.resolver_match.kwargs.get("object_id")
        if object_id:
            food_safety = FoodSafety.objects.get(pk=object_id)
            if food_safety.status == 'closed':
                return request.method in ['GET']
        return super().has_change_permission(request, obj)

    def has_add_permission(self, request, obj):
        object_id = request.resolver_match.kwargs.get("object_id")
        if object_id:
            food_safety = FoodSafety.objects.get(pk=object_id)
            if food_safety.status == 'closed':
                return False
        return super().has_add_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        object_id = request.resolver_match.kwargs.get("object_id")
        if object_id:
            food_safety = FoodSafety.objects.get(pk=object_id)
            if food_safety.status == 'closed':
                return False
        return super().has_delete_permission(request, obj)

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

    def get_readonly_fields(self, request, obj=None):
        object_id = request.resolver_match.kwargs.get("object_id")
        if object_id:
            food_safety = FoodSafety.objects.get(pk=object_id)
            if food_safety.status == 'closed':
                return [f.name for f in self.model._meta.fields if f.name != 'id']
        return super().get_readonly_fields(request, obj)

    def has_change_permission(self, request, obj=None):
        object_id = request.resolver_match.kwargs.get("object_id")
        if object_id:
            food_safety = FoodSafety.objects.get(pk=object_id)
            if food_safety.status == 'closed':
                return request.method in ['GET']
        return super().has_change_permission(request, obj)

    def has_add_permission(self, request, obj):
        object_id = request.resolver_match.kwargs.get("object_id")
        if object_id:
            food_safety = FoodSafety.objects.get(pk=object_id)
            if food_safety.status == 'closed':
                return False
        return super().has_add_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        object_id = request.resolver_match.kwargs.get("object_id")
        if object_id:
            food_safety = FoodSafety.objects.get(pk=object_id)
            if food_safety.status == 'closed':
                return False
        return super().has_delete_permission(request, obj)

class SampleCollectionInline(CustomNestedStackedAvgInlineMixin, admin.StackedInline):
    model = SampleCollection
    extra = 1
    min_num = 1
    max_num = 1
    can_delete = False
    inlines = [SampleWeightInline, SamplePestInline, SampleDiseaseInline, SamplePhysicalDamageInline, SampleResidueInline]

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.status == 'closed':
            return [field.name for field in self.model._meta.fields if field.name != 'id']
        return super().get_readonly_fields(request, obj)

    def has_change_permission(self, request, obj=None):
        # Check if the object is provided and its status is 'closed'
        if obj and obj.status == 'closed':
            return request.method in ['GET']

        # Handle the case where object_id is retrieved from request
        object_id = request.resolver_match.kwargs.get("object_id")
        if object_id:
            food_safety = FoodSafety.objects.get(pk=object_id)
            if food_safety.status == 'closed':
                return request.method in ['GET']

        # Default behavior
        return super().has_change_permission(request, obj)

    def has_add_permission(self, request, obj):
        if obj and obj.status == 'closed':
            return False
        return super().has_add_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj and obj.status == 'closed':
            return False
        return super().has_delete_permission(request, obj)

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

class FoodSafetyForm(forms.ModelForm):
    class Meta:
        model = FoodSafety
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        allowed_statuses = ['open', 'closed']
        if 'status' in self.fields:
            self.fields['status'].choices = [
                (key, label) for key, label in STATUS_CHOICES if key in allowed_statuses
            ]

@admin.register(FoodSafety)
class FoodSafetyAdmin(ByOrganizationAdminMixin, nested_admin.NestedModelAdmin):
    list_display = ('get_batch_ooid', 'get_scheduleharvest_ooid', 'get_scheduleharvest_harvest_date', 'get_batch_entry_date',
                    'get_product_provider', 'get_orchard', 'get_orchard_product_producer', 'get_product', 'get_orchard_category',
                    'get_product_variety', 'get_product_phenology', 'get_product_ripeness', 'get_batch_received_weight', 'status',
                    'generate_actions_buttons')
    list_filter = (('created_at', DateRangeFilter), ByOrchardCertificationForOrganizationFoodSafetyFilter)
    search_fields = ('Batch',)
    form = FoodSafetyForm
    inlines = [DryMatterInline, InternalInspectionInline, VehicleReviewInline, SampleCollectionInline, AverageInline]

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.status == 'closed':
            exclude = {'id', 'created_at'}
            return [field.name for field in self.model._meta.fields if field.name not in exclude]
        return super().get_readonly_fields(request, obj)

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if obj is None:
            return [f for f in fields if f != 'status']
        return fields

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        if 'batch' in form.base_fields:
            widget = form.base_fields['batch'].widget
            widget.can_add_related = False
            widget.can_change_related = False
            widget.can_delete_related = False
            widget.can_view_related = False

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

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'batch_record/<uuid:uuid>/',
                self.admin_site.admin_view(export_batch_record),
                name='food_safety_batch_export_batch_record',
            ),
        ]
        return custom_urls + urls

    def generate_actions_buttons(self, obj):
        record_url = reverse('food_safety_record_report', args=[obj.batch.uuid])

        tooltip = _('Batch and Food Safety Record')

        return format_html(
            '''
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <a class="button"
                href="{}" target="_blank" data-toggle="tooltip" title="{}"
                style="display: inline-flex; justify-content: center; align-items: center;">
                    <i class="fa-solid fa-file"></i>
                </a>
            </div>
            ''',
            record_url, tooltip,
        )
    generate_actions_buttons.short_description = _('Actions')
    generate_actions_buttons.allow_tags = True


    def get_batch_ooid(self, obj):
        return obj.batch.ooid if obj.batch else "-"
    get_batch_ooid.short_description = _('Batch Number')
    get_batch_ooid.admin_order_field = 'batch__ooid'

    def get_scheduleharvest_ooid(self, obj):
        return obj.batch.incomingproduct.scheduleharvest.ooid if obj.batch.incomingproduct.scheduleharvest else "-"
    get_scheduleharvest_ooid.short_description = _('Harvest Number')
    get_scheduleharvest_ooid.admin_order_field = 'batch__incomingproduct__scheduleharvest__ooid'

    def get_scheduleharvest_harvest_date(self, obj):
        harvest_date = obj.batch.incomingproduct.scheduleharvest.harvest_date if obj.batch.incomingproduct.scheduleharvest else None
        date_str = date_format(harvest_date, format='DATE_FORMAT', use_l10n=True) if harvest_date else ''
        return format_html('<span style="display:inline-block; min-width:80px;">{}</span>', date_str)
    get_scheduleharvest_harvest_date.short_description = _("Schedule Harvest Date")
    get_scheduleharvest_harvest_date.admin_order_field = 'batch__incomingproduct__scheduleharvest__harvest_date'

    def get_batch_entry_date(self, obj):
        entry_date = obj.batch.created_at if obj.batch else None
        date_str = date_format(entry_date, format='DATE_FORMAT', use_l10n=True) if entry_date else ''
        return format_html('<span style="display:inline-block; min-width:80px;">{}</span>', date_str)
    get_batch_entry_date.short_description = _("Batch Entry Date")
    get_batch_entry_date.admin_order_field = 'batch__incomingproduct__scheduleharvest__harvest_date'

    def get_product_provider(self, obj):
        provider = obj.batch.incomingproduct.scheduleharvest.product_provider if obj.batch.incomingproduct.scheduleharvest else None
        return str(provider) if provider else ''
    get_product_provider.short_description = _('Product Provider')
    get_product_provider.admin_order_field = 'batch__incomingproduct__scheduleharvest__product_provider'

    def get_orchard(self, obj):
        orchard = obj.batch.incomingproduct.scheduleharvest.orchard if obj.batch.incomingproduct.scheduleharvest else None
        return orchard.name if orchard else ''
    get_orchard.short_description = _('Orchard')
    get_orchard.admin_order_field = 'batch__incomingproduct__scheduleharvest__orchard'

    def get_orchard_code(self, obj):
        orchard = obj.batch.incomingproduct.scheduleharvest.orchard.code if obj.batch.incomingproduct.scheduleharvest else None
        return orchard.name if orchard else ''
    get_orchard_code.short_description = _('Orchard')
    get_orchard_code.admin_order_field = 'batch__incomingproduct__scheduleharvest__orchard__code'

    def get_orchard_product_producer(self, obj):
        orchard = obj.batch.incomingproduct.scheduleharvest.orchard if obj.batch.incomingproduct.scheduleharvest else None
        return orchard.producer if orchard else None
    get_orchard_product_producer.admin_order_field = 'batch__incomingproduct__scheduleharvest__orchard__producer'
    get_orchard_product_producer.short_description = _('Product Producer')

    def get_product(self, obj):
        product = obj.batch.incomingproduct.scheduleharvest.product if obj.batch.incomingproduct.scheduleharvest else None
        return str(product) if product else ''
    get_product.short_description = _('Product')
    get_product.admin_order_field = 'batch__incomingproduct__scheduleharvest__product'

    def get_orchard_category(self, obj):
        if obj.batch.incomingproduct.scheduleharvest.orchard:
            return obj.batch.incomingproduct.scheduleharvest.orchard.get_category_display()
        return None
    get_orchard_category.short_description = _('Product Category')
    get_orchard_category.admin_order_field = 'batch__incomingproduct__scheduleharvest__orchard__category'

    def get_product_variety(self, obj):
        product = obj.batch.incomingproduct.scheduleharvest.product_variety if obj.batch.incomingproduct.scheduleharvest else None
        return str(product) if product else ''
    get_product_variety.short_description = _('Product Variety')
    get_product_variety.admin_order_field = 'batch__incomingproduct__scheduleharvest__product_variety'

    def get_product_phenology(self, obj):
        product = obj.batch.incomingproduct.scheduleharvest.product_phenology if obj.batch.incomingproduct.scheduleharvest else None
        return str(product) if product else ''
    get_product_phenology.short_description = _('Product Phenology')
    get_product_phenology.admin_order_field = 'batch__incomingproduct__scheduleharvest__product_phenology'

    def get_product_ripeness(self, obj):
        product = obj.batch.incomingproduct.scheduleharvest.product_ripeness if obj.batch.incomingproduct.scheduleharvest else None
        return str(product) if product else ''
    get_product_ripeness.short_description = _('Product Ripeness')
    get_product_ripeness.admin_order_field = 'batch__incomingproduct__scheduleharvest__product_ripeness'

    def get_batch_received_weight(self, obj):
        return obj.batch.family_ingress_weight if obj.batch else "-"
    get_batch_received_weight.short_description = _('Received Weight')
