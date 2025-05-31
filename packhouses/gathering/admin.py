from django.contrib import admin
from .models import (ScheduleHarvest, ScheduleHarvestHarvestingCrew, ScheduleHarvestVehicle, ScheduleHarvestContainerVehicle)
from packhouses.packhouse_settings.models import (Bank, VehicleOwnershipKind, VehicleFuelKind, VehicleKind,
                                                  VehicleBrand, OrchardCertificationKind, OrchardCertificationVerifier
                                                  )
from common.profiles.models import UserProfile, PackhouseExporterProfile, OrganizationProfile
from django_ckeditor_5.widgets import CKEditor5Widget
from organizations.models import Organization, OrganizationUser
from cities_light.models import Country, Region, SubRegion, City
from django.utils.translation import gettext_lazy as _
from common.widgets import UppercaseTextInputWidget, UppercaseAlphanumericTextInputWidget, AutoGrowingTextareaWidget
from packhouses.catalogs.filters import (StatesForOrganizationCountryFilter, ByCountryForOrganizationMarketsFilter,
                                         ByProductForOrganizationFilter, ByProductSeasonKindForOrganizationFilter,
                                         ByProductVarietyForOrganizationFilter, ByMarketForOrganizationFilter,
                                         ByStateForOrganizationGathererFilter, ByCityForOrganizationGathererFilter,
                                         ByStateForOrganizationFilter, ByCityForOrganizationFilter, ByDistrictForOrganizationFilter,
                                         ByCountryForOrganizationClientsFilter, ByStateForOrganizationClientsFilter,
                                         ByCityForOrganizationClientsFilter,
                                         ByProductVarietiesForOrganizationFilter, ByMarketForOrganizationFilter,
                                         ByProductHarvestSizeKindForOrganizationFilter,
                                         ProductKindForPackagingFilter, ByCountryForOrganizationProvidersFilter,
                                         ByStateForOrganizationProvidersFilter, ByCityForOrganizationProvidersFilter,
                                         ByStateForOrganizationMaquiladoraFilter, ByCityForOrganizationMaquiladoraFilter
                                         )
from packhouses.catalogs.models import (Provider, Gatherer, Maquiladora, Orchard, Product, Market, WeighingScale,
                                        ProductVariety, HarvestingCrew, Vehicle, ProductHarvestSizeKind,
                                        OrchardCertification, Supply, ProductRipeness)
from common.utils import is_instance_used
from adminsortable2.admin import SortableAdminMixin, SortableStackedInline, SortableTabularInline, SortableAdminBase
from common.base.models import ProductKind
from common.base.decorators import uppercase_formset_charfield, uppercase_alphanumeric_formset_charfield
from common.base.decorators import uppercase_form_charfield, uppercase_alphanumeric_form_charfield
from common.base.mixins import (ByOrganizationAdminMixin, ByProductForOrganizationAdminMixin, DisableInlineRelatedLinksMixin)
from common.forms import SelectWidgetWithData
from django import forms
import nested_admin

# Register your models here.

from django.shortcuts import get_object_or_404

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.contrib.admin.widgets import AdminDateWidget
from django.utils.html import format_html
from django.urls import reverse
from .forms import ScheduleHarvestForm, ContainerInlineForm, ContainerInlineFormSet


class HarvestCuttingHarvestingCrewInline(DisableInlineRelatedLinksMixin, nested_admin.NestedStackedInline):
    model = ScheduleHarvestHarvestingCrew
    extra = 0
    min = 1

    @uppercase_formset_charfield('extra_code')
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
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
        js = ('js/admin/forms/packhouses/gathering/harvest_cutting_harvesting_crew_inline.js',)


class HarvestCuttingContainerVehicleInline(nested_admin.NestedTabularInline):
    model = ScheduleHarvestContainerVehicle
    fields = ('harvest_container', 'quantity')
    extra = 0
    formset = ContainerInlineFormSet
    form = ContainerInlineForm

    def get_readonly_fields(self, request, obj=None):
        """ Aplica solo lectura a los campos de contenedor solo si `created_at_model == 'incoming_product'` """
        if obj and isinstance(obj, ScheduleHarvestContainerVehicle):
            # Verificamos el campo 'created_at_model' del contenedor
            if obj.created_at_model == 'incoming_product':
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


class HarvestCuttingVehicleInline(DisableInlineRelatedLinksMixin, nested_admin.NestedStackedInline):
    model = ScheduleHarvestVehicle
    extra = 0
    fields = ('harvest_cutting', 'provider', 'vehicle', 'stamp_number')
    inlines = [HarvestCuttingContainerVehicleInline]

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
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

        if db_field.name == "vehicle":
            kwargs["queryset"] = Vehicle.objects.filter(
                organization=organization,
                is_enabled=True
            )

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    class Media:
        js = ('js/admin/forms/packhouses/gathering/harvest_cutting_vehicle_inline.js',)



@admin.register(ScheduleHarvest)
class ScheduleHarvestAdmin(ByOrganizationAdminMixin, ByProductForOrganizationAdminMixin, nested_admin.NestedModelAdmin):
    form = ScheduleHarvestForm
    fields = ('ooid', 'status', 'is_scheduled', 'harvest_date', 'category', 'gatherer', 'maquiladora', 'product_provider', 'product',
              'product_variety', 'product_phenologies', 'product_ripeness', 'product_harvest_size_kind', 'orchard',
              'market', 'weight_expected', 'weighing_scale', 'meeting_point', 'comments' )
    list_display = ('ooid', 'harvest_date', 'category', 'product_provider',
                    'get_orchard_name', 'get_orchard_code', 'get_orchard_product_producer',
                    'product', 'get_orchard_category', 'product_variety', 'product_phenologies', 'product_ripeness', 'market',
                    'weight_expected', 'status',  'generate_actions_buttons')
    list_filter = ('product_provider', 'category', 'gatherer', 'maquiladora', 'status',)
    readonly_fields = ('ooid', 'status')
    inlines = [HarvestCuttingHarvestingCrewInline, HarvestCuttingVehicleInline]

    def get_orchard_name(self, obj):
        return obj.orchard.name if obj.orchard else None
    get_orchard_name.short_description = _('Orchard')
    get_orchard_name.admin_order_field = 'orchard__name' 

    def get_orchard_code(self, obj):
        return obj.orchard.code if obj.orchard else None
    get_orchard_code.short_description = _('Orchard Code')
    get_orchard_code.admin_order_field = 'orchard__code' 

    def get_orchard_category(self, obj):
        if obj.orchard:
            return obj.orchard.get_category_display()
        return None
    get_orchard_category.short_description = _('Product Category')
    get_orchard_category.admin_order_field = 'orchard__category'

    def get_orchard_product_producer(self, obj):
        return obj.orchard.producer if obj.orchard else None
    get_orchard_product_producer.short_description = _('Product Producer')
    get_orchard_product_producer.admin_order_field = 'orchard__producer'

    def generate_actions_buttons(self, obj):
        pdf_url = reverse('harvest_order_pdf', args=[obj.pk])
        tooltip_harvest_order = _('Generate Harvest Order PDF')
        report_url = reverse('good_harvest_practices_format', args=[obj.pk])
        tooltip_report = _('Good harvest practices format')
        cancel_url = reverse('cancel_schedule_harvest', args=[obj.pk])
        tooltip_cancel = _('Cancel this harvest')
        confirm_cancel_text = _('Are you sure you want to cancel this harvest?')
        confirm_button_text = _('Yes, cancel it')
        cancel_button_text = _('No')

        tooltip_ready = _('Send to Fruit Receiving Area?')
        ready_url = reverse('set_scheduleharvest_ready', args=[obj.pk])
        confirm_ready_text = _('Are you sure you want to send this Harvest to Fruit Receiving Area?')
        confirm_ready_button_text = _('Yes, send')

        cancel_button_html = ''
        set_harvest_ready_button = ''
        if obj.status in ['open', 'ready']:
            cancel_button_html = format_html(
                '''
                <a class="button btn-cancel-confirm" href="javascript:void(0);" data-toggle="tooltip" title="{}"
                data-url="{}" data-message="{}" data-confirm="{}" data-cancel="{}" style="color:red;">
                    <i class="fa-solid fa-ban"></i>
                </a>
                ''',
                tooltip_cancel, cancel_url, confirm_cancel_text, confirm_button_text, cancel_button_text
            ) if obj.status == 'open' else ''

            if obj.status == 'open':
                set_harvest_ready_button = format_html(
                    '''
                    <a class="button btn-ready-confirm" href="javascript:void(0);" data-toggle="tooltip" title="{}"
                    data-url="{}" data-message="{}" data-confirm="{}" data-cancel="{}" style="color:#4daf50;">
                        <i class="fa-solid fa-paper-plane"></i>
                    </a>
                    ''',
                    tooltip_ready, ready_url, confirm_ready_text, confirm_ready_button_text, cancel_button_text
                )


        return format_html(
            '''
            {}
            <a class="button" href="{}" target="_blank" data-toggle="tooltip" title="{}">
                <i class="fa-solid fa-print"></i>
            </a>
            <a class="button" href="{}" target="_blank" data-toggle="tooltip" title="{}">
                <i class="fa-solid fa-file-shield"></i>
            </a>
            {}
            ''',
            set_harvest_ready_button, pdf_url, tooltip_harvest_order,
            report_url, tooltip_report,
            cancel_button_html
        )

    generate_actions_buttons.short_description = _('Actions')
    generate_actions_buttons.allow_tags = True

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'product_provider' in form.base_fields:
            form.base_fields['product_provider'].widget.can_add_related = False
            form.base_fields['product_provider'].widget.can_change_related = False
            form.base_fields['product_provider'].widget.can_delete_related = False
            form.base_fields['product_provider'].widget.can_view_related = False
        if 'product' in form.base_fields:
            form.base_fields['product'].widget.can_add_related = False
            form.base_fields['product'].widget.can_change_related = False
            form.base_fields['product'].widget.can_delete_related = False
            form.base_fields['product'].widget.can_view_related = False
        if 'market' in form.base_fields:
            form.base_fields['market'].widget.can_add_related = False
            form.base_fields['market'].widget.can_change_related = False
            form.base_fields['market'].widget.can_delete_related = False
            form.base_fields['market'].widget.can_view_related = False

        return form

    def get_product_varieties(self, obj):
        return ", ".join([pv.name for pv in obj.product_varieties.all()])
    get_product_varieties.short_description = _('Varieties')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        organization = request.organization if hasattr(request, 'organization') else None
        organization_queryfilter = {'organization': organization, 'is_enabled': True}
        product_organization_queryfilter = {'product__organization': organization, 'is_enabled': True}

        if db_field.name == "product":
            kwargs["queryset"] = Product.objects.filter(**organization_queryfilter)

        if db_field.name == "product_varieties":
            kwargs["queryset"] = ProductVariety.objects.filter(**product_organization_queryfilter)
        
        if db_field.name == "product_ripeness":
            kwargs["queryset"] = ProductRipeness.objects.filter(**product_organization_queryfilter)

        field_filters = {
            "product_provider": {
                "model": Provider,
                "filters": {"category": "product_provider", "is_enabled": True},
            },
            "gatherer": {
                "model": Gatherer,
                "filters": {"is_enabled": True},
            },
            "maquiladora": {
                "model": Maquiladora,
                "filters": {"is_enabled": True},
            },

            "market": {
                "model": Market,
                "filters": {"is_enabled": True},
            },
            "orchard": {
                "model": Orchard,
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

            kwargs["queryset"] = model.objects.filter(
                organization=request.organization,
                **filters
            )

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
        js = ('js/admin/forms/packhouses/gathering/harvest-cutting.js',)



