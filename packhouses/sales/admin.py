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
from packhouses.catalogs.models import Client, Maquiladora
from .models import Order
from django.utils.safestring import mark_safe
from common.forms import SelectWidgetWithData


# Register your models here.

@admin.register(Order)
class OrderAdmin(ByOrganizationAdminMixin):
    list_display = ('ooid', 'client', 'registration_date', 'shipment_date', 'delivery_date', 'incoterms', 'status')
    list_filter = ('ooid', 'client', 'registration_date', 'shipment_date', 'delivery_date', 'incoterms', 'status')
    fields = (
    'ooid', 'client_category', 'client', 'registration_date', 'shipment_date', 'delivery_date', 'local_delivery',
    'incoterms', 'observations', 'status')
    ordering = ('-ooid',)

    readonly_fields = ('ooid',)

    def rendered_observations(self, obj):
        return mark_safe(obj.observations) if obj and obj.observations else ""

    rendered_observations.short_description = 'Observations'

    def get_readonly_fields(self, request, obj=None):
        if not obj:
            return self.readonly_fields

        # Si el pedido no está abierto, todos los campos son readonly
        if obj.order_status in ['closed', 'canceled']:
            return tuple(self.fields) + ('rendered_observations',)

        return self.readonly_fields

    def get_fields(self, request, obj=None):
        fields = list(super().get_fields(request, obj))
        if obj and obj.order_status in ['closed', 'canceled']:
            # Reemplazar 'observations' con 'rendered_observations' en modo readonly
            fields[fields.index('observations')] = 'rendered_observations'
        return fields

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
        organization = getattr(request, 'organization', None)
        object_id = request.resolver_match.kwargs.get("object_id")
        obj = Order.objects.get(id=object_id) if object_id else None
        queryset_organization_filter = {"organization": organization, "is_enabled": True}

        client_category = request.POST.get('client_category') if request.POST else obj.client_category if obj else None
        client = request.POST.get('client') if request.POST else obj.client if obj else None

        if db_field.name == "maquiladora":

            kwargs["queryset"] = Maquiladora.objects.filter()
            formfield.label_from_instance = lambda item: item.name

        if db_field.name == "client":
            queryset_filter = {"organization": organization, "category": client_category, "is_enabled": True}
            kwargs["queryset"] = Client.objects.filter(**queryset_filter) if client_category else Client.objects.none()
            formfield.label_from_instance = lambda item: item.name

        return formfield

    class Media:
        js = ('js/admin/forms/packhouses/sales/order.js',)
