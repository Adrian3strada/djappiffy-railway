from django.contrib import admin
from .models import (HarvestCutting)
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
from packhouses.catalogs.models import (Provider, Gatherer, Maquiladora, Orchard, Product, Market,WeighingScale)
from common.utils import is_instance_used
from adminsortable2.admin import SortableAdminMixin, SortableStackedInline, SortableTabularInline, SortableAdminBase
from common.base.models import ProductKind
from common.base.decorators import uppercase_formset_charfield, uppercase_alphanumeric_formset_charfield
from common.base.decorators import uppercase_form_charfield, uppercase_alphanumeric_form_charfield
from common.base.mixins import ByOrganizationAdminMixin, ByProductForOrganizationAdminMixin
from common.forms import SelectWidgetWithData
from django import forms

# Register your models here.

@admin.register(HarvestCutting)
class HarvestCuttingAdmin(ByOrganizationAdminMixin):
    fields = ('ooid', 'category', 'product_provider', 'gatherer', 'maquiladora','orchard', 'product',
              'product_variety', 'product_season_kind', 'product_harvest_size_kind', 'market', 'weighing_scale',
              'meeting_point')
    list_display = ('ooid', 'category', 'product_provider', 'product','product_variety', 'market', 'product_season_kind')
    list_filter = ('category', 'product_provider','gatherer', 'maquiladora')
    readonly_fields = ('ooid',)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['product_provider'].widget.can_add_related = False
        form.base_fields['product_provider'].widget.can_change_related = False
        form.base_fields['product_provider'].widget.can_delete_related = False
        form.base_fields['product_provider'].widget.can_view_related = False
        return form

    def formfield_for_foreignkey(self, db_field, request, **kwargs):

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
            "orchard": {
                "model": Orchard,
                "filters": {"is_enabled": True},
            },
            "product": {
                "model": Product,
                "filters": {"is_enabled": True},
            },
            "market": {
                "model": Market,
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
