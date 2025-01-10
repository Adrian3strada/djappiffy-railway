from django.contrib import admin
from common.profiles.models import UserProfile, PackhouseExporterProfile, OrganizationProfile
from django_ckeditor_5.widgets import CKEditor5Widget
from organizations.models import Organization, OrganizationUser
from cities_light.models import Country, Region, SubRegion, City
from django.utils.translation import gettext_lazy as _
from common.widgets import UppercaseTextInputWidget, UppercaseAlphanumericTextInputWidget, AutoGrowingTextareaWidget
from common.utils import is_instance_used
from adminsortable2.admin import SortableAdminMixin
from common.base.decorators import uppercase_formset_charfield, uppercase_alphanumeric_formset_charfield
from common.base.decorators import uppercase_form_charfield, uppercase_alphanumeric_form_charfield
from common.base.mixins import ByOrganizationAdminMixin
from packhouses.catalogs.models import Client, Market
from .models import Order
from django.utils.safestring import mark_safe
from common.forms import SelectWidgetWithData





# Register your models here.

@admin.register(Order)
class OrderAdmin(ByOrganizationAdminMixin):
    fields = ('ooid', 'client', 'registration_date', 'shipment_date', 'delivery_date', 'local_delivery', 'incoterms', 'observations', 'order_status')
    list_display = ('ooid', 'client', 'registration_date', 'shipment_date', 'delivery_date', 'incoterms', 'order_status')
    list_filter = ('ooid', 'client', 'registration_date', 'shipment_date', 'delivery_date', 'incoterms', 'order_status')
    ordering = ('-ooid',)

    readonly_fields = ('ooid',)

    def rendered_observations(self, obj):
        return mark_safe(obj.observations) if obj and obj.observations else ""

    rendered_observations.short_description = 'Observations'

    def get_readonly_fields(self, request, obj=None):
        if not obj:
            return self.readonly_fields

        # Si el pedido no está abierto, todos los campos son readonly
        if obj.order_status != 'opened':
            return tuple(self.fields) + ('rendered_observations',)

        return self.readonly_fields

    def get_fields(self, request, obj=None):
        fields = list(super().get_fields(request, obj))
        if obj and obj.order_status != 'opened':
            # Reemplazar 'observations' con 'rendered_observations' en modo readonly
            fields[fields.index('observations')] = 'rendered_observations'
        return fields

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        organization = getattr(request, 'organization', None)
        object_id = request.resolver_match.kwargs.get("object_id")
        obj = Order.objects.get(id=object_id) if object_id else None

        if db_field.name == "market":
            if organization:
                queryset = Market.objects.filter(organization=organization, is_enabled=True)
            elif obj:
                queryset = Market.objects.filter(organization_id=obj.client.organization_id, is_enabled=True)
            else:
                queryset = Market.objects.filter(is_enabled=True)

            kwargs["queryset"] = queryset
            kwargs["widget"] = SelectWidgetWithData(Market, 'is_foreign')

            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda item: item.name
            return formfield


        if db_field.name == "country":
            market_id = request.POST.get('market') if request.POST else (obj.client.market_id if obj else None)
            if market_id:
                market_countries_id = Market.objects.get(id=market_id).countries.values_list('id', flat=True)
                kwargs["queryset"] = Country.objects.filter(id__in=market_countries_id)
            else:
                kwargs["queryset"] = Country.objects.none()
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda item: item.name
            return formfield

        if db_field.name == "client":
            country_id = request.POST.get('country') if request.POST else (obj.country_id if obj else None)
            if country_id:
                kwargs["queryset"] = Client.objects.filter(country_id=country_id)
            else:
                kwargs["queryset"] = Client.objects.none()
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda item: item.name
            if obj and obj.client:
                formfield.initial = obj.client.id
            return formfield

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    class Media:
        js = ('js/admin/forms/packhouses/sales/order.js',)
