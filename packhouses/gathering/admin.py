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
                      ByProductVarietiesForOrganizationFilter, ByMarketsForOrganizationFilter,
                      ByProductMassVolumeKindForOrganizationFilter, ByProductHarvestSizeKindForOrganizationFilter,
                      ProductKindForPackagingFilter, ByCountryForOrganizationProvidersFilter,
                      ByStateForOrganizationProvidersFilter, ByCityForOrganizationProvidersFilter,
                      ByStateForOrganizationMaquiladoraFilter, ByCityForOrganizationMaquiladoraFilter
                      )
from packhouses.catalogs.models import (Provider, Gatherer, Maquiladora, Orchard, Product, Market, WeighingScale,
                                        ProductVariety, HarvestingCrew, Vehicle, ProductHarvestSizeKind, HarvestContainer)
from common.utils import is_instance_used
from adminsortable2.admin import SortableAdminMixin, SortableStackedInline, SortableTabularInline, SortableAdminBase
from common.base.models import ProductKind
from common.base.decorators import uppercase_formset_charfield, uppercase_alphanumeric_formset_charfield
from common.base.decorators import uppercase_form_charfield, uppercase_alphanumeric_form_charfield
from common.base.mixins import ByOrganizationAdminMixin, ByProductForOrganizationAdminMixin, DisableInlineRelatedLinksMixin
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


class HarvestCuttingHarvestingCrewInline(DisableInlineRelatedLinksMixin, nested_admin.NestedStackedInline):
    model = ScheduleHarvestHarvestingCrew
    extra = 0
    min = 1

    @uppercase_formset_charfield('extra_code')
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        return formset


    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        parent_object_id = request.resolver_match.kwargs.get("object_id")
        parent_obj = ScheduleHarvest.objects.get(id=parent_object_id) if parent_object_id else None

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
    extra = 0

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        form = formset.form
        for field in form.base_fields.values():
            field.widget.can_add_related = True
            field.widget.can_change_related = False
            field.widget.can_delete_related = False
            field.widget.can_view_related = False
        return formset

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        parent_object_id = request.resolver_match.kwargs.get("object_id")
        parent_obj = ScheduleHarvestVehicle.objects.get(id=parent_object_id) if parent_object_id else None

        organization = None
        if hasattr(request, 'organization'):
            organization = request.organization

        if db_field.name == "harvest_cutting_container":
            kwargs["queryset"] = HarvestContainer.objects.filter(
                organization=organization,
                is_enabled=True
            )

        return super().formfield_for_foreignkey(db_field, request, **kwargs)




class HarvestCuttingVehicleInline(DisableInlineRelatedLinksMixin, nested_admin.NestedStackedInline):
    model = ScheduleHarvestVehicle
    extra = 0
    inlines = [HarvestCuttingContainerVehicleInline]

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        return formset

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        parent_object_id = request.resolver_match.kwargs.get("object_id")
        parent_obj = Provider.objects.get(id=parent_object_id) if parent_object_id else None

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
class HarvestCuttingAdmin(ByOrganizationAdminMixin, ByProductForOrganizationAdminMixin, nested_admin.NestedModelAdmin):
    fields = ('ooid', 'harvest_date', 'category', 'gatherer', 'maquiladora', 'product_provider', 'product',
              'product_variety', 'product_season_kind', 'product_harvest_size_kind','orchard',  'market',
              'weight_expected', 'weighing_scale','status', 'meeting_point', )
    list_display = ('ooid', 'harvest_date', 'category', 'product_provider', 'product','product_variety', 'market',
                    'product_season_kind', 'weight_expected',  'generate_pdf_button')
    list_filter = ('category', 'product_provider','gatherer', 'maquiladora', )
    readonly_fields = ('ooid',)
    inlines = [HarvestCuttingHarvestingCrewInline, HarvestCuttingVehicleInline]

    def generate_pdf_button(self, obj):
        url = reverse('generate_pdf', args=[obj.pk])  # URL de la vista de generación de PDF
        button_text = str(_("Harvest Order"))
        return format_html(
            '<a class="button" href="{}" target="_blank">{}</a>', url, button_text
        )

    generate_pdf_button.short_description = _('Actions')
    generate_pdf_button.allow_tags = True

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



