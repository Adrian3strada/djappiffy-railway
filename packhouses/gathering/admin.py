from django.contrib import admin
from .models import (HarvestCutting, HarvestCuttingHarvestingCrew, HarvestCuttingVehicle)
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
from packhouses.catalogs.models import (Provider, Gatherer, Maquiladora, Orchard, Product, Market,WeighingScale,
                                        ProductVariety, HarvestingCrew, Vehicle, ProductHarvestSizeKind)
from common.utils import is_instance_used
from adminsortable2.admin import SortableAdminMixin, SortableStackedInline, SortableTabularInline, SortableAdminBase
from common.base.models import ProductKind
from common.base.decorators import uppercase_formset_charfield, uppercase_alphanumeric_formset_charfield
from common.base.decorators import uppercase_form_charfield, uppercase_alphanumeric_form_charfield
from common.base.mixins import ByOrganizationAdminMixin, ByProductForOrganizationAdminMixin, DisableInlineRelatedLinksMixin
from common.forms import SelectWidgetWithData
from django import forms

# Register your models here.

from django.shortcuts import get_object_or_404

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

class HarvestCuttingHarvestingCrewInline(DisableInlineRelatedLinksMixin, admin.StackedInline):
    model = HarvestCuttingHarvestingCrew
    extra = 0
    min = 1

    @uppercase_formset_charfield('extra_code')
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        return formset

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        parent_object_id = request.resolver_match.kwargs.get("object_id")
        parent_obj = HarvestCutting.objects.get(id=parent_object_id) if parent_object_id else None

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

class HarvestCuttingVehicleInline(DisableInlineRelatedLinksMixin, admin.StackedInline):
    model = HarvestCuttingVehicle
    extra = 1

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

        if db_field.name == "harvesting_crew":
            # Mantener el queryset relacionado con el valor seleccionado previamente
            provider_id = request.GET.get('provider') or request.POST.get('provider')
            selected_value = request.POST.get(f"{db_field.name}")
            if provider_id or selected_value:
                kwargs["queryset"] = HarvestingCrew.objects.filter(
                    Q(provider_id=provider_id) | Q(id=selected_value),
                    organization=organization,
                    is_enabled=True
                )
            else:
                kwargs["queryset"] = HarvestingCrew.objects.none()

        return super().formfield_for_foreignkey(db_field, request, **kwargs)



@admin.register(HarvestCutting)
class HarvestCuttingAdmin(ByOrganizationAdminMixin, ByProductForOrganizationAdminMixin):
    fields = ('ooid', 'harvest_cutting_date', 'category', 'gatherer', 'maquiladora', 'product_provider','product',
              'product_variety', 'product_season_kind', 'product_harvest_size_kind','orchard',  'market', 'weighing_scale',
              'meeting_point')
    list_display = ('ooid', 'category', 'product_provider', 'product','product_variety', 'market', 'product_season_kind')
    list_filter = ('category', 'product_provider','gatherer', 'maquiladora')
    readonly_fields = ('ooid',)
    inlines = [HarvestCuttingHarvestingCrewInline, ]


    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['product_provider'].widget.can_add_related = False
        form.base_fields['product_provider'].widget.can_change_related = False
        form.base_fields['product_provider'].widget.can_delete_related = False
        form.base_fields['product_provider'].widget.can_view_related = False
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

    class Media:
        js = ('js/admin/forms/packhouses/gathering/harvest-cutting.js',)
