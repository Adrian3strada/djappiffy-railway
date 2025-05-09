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
from .filters import (ByMaquiladoraForOrganizationOrderFilter, ByClientForOrganizationOrderFilter,
                      ByLocalDeliveryForOrganizationOrderFilter, ByIncotermsForOrganizationOrderFilter,
                      ByProductForOrganizationOrderFilter, ByProductVarietyForOrganizationOrderFilter)
from common.base.mixins import ByOrganizationAdminMixin
from packhouses.catalogs.models import (Client, Maquiladora, ProductVariety, Market, Product, ProductSize,
                                        ProductPackaging,
                                        ProductPhenologyKind, ProductMarketClass, Packaging, ProductPackagingPallet)
from .models import Order, OrderItemWeight, OrderItemPackaging, OrderItemPallet
from .forms import OrderItemWeightFormSet, OrderItemPackagingFormSet, OrderItemPalletFormSet
from django.utils.safestring import mark_safe
from django.db.models import Max, Min, Q, F
from common.forms import SelectWidgetWithData


# Register your models here.


class OrderItemInlineMixin(admin.StackedInline):
    extra = 0

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        formset.form.base_fields['product_size'].widget.can_add_related = False
        formset.form.base_fields['product_size'].widget.can_change_related = False
        formset.form.base_fields['product_size'].widget.can_delete_related = False
        formset.form.base_fields['product_size'].widget.can_view_related = False
        return formset

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        parent_object_id = request.resolver_match.kwargs.get("object_id")
        parent_object = Order.objects.get(id=parent_object_id) if parent_object_id else None

        client_id = request.POST.get('client') if request.POST else parent_object.client.id if parent_object else None
        product_id = request.POST.get('product') if request.POST else parent_object.product.id if parent_object else None
        client = Client.objects.get(id=client_id) if client_id else None
        product = Product.objects.get(id=product_id) if product_id else None

        if db_field.name == "product_size":
            if client and product:
                kwargs["queryset"] = ProductSize.objects.filter(product=product,
                                                                market=client.market, is_enabled=True)
                formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
                formfield.label_from_instance = lambda \
                    item: f"{item.name} ({item.description})" if item.description else f"{item.name}"
                return formfield
            else:
                kwargs["queryset"] = ProductSize.objects.none()

            print('kwargs["queryset"]', kwargs["queryset"])

        if db_field.name == "product_phenology":
            kwargs["queryset"] = ProductPhenologyKind.objects.none()
            if product:
                kwargs["queryset"] = ProductPhenologyKind.objects.filter(product=product, is_enabled=True)

        if db_field.name == "product_market_class":
            kwargs["queryset"] = ProductMarketClass.objects.none()
            if product and client:
                kwargs["queryset"] = ProductMarketClass.objects.filter(product=product,
                                                                       market=client.market, is_enabled=True)
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda item: f"{item.name}"
            return formfield

        if db_field.name == "product_market_class":
            kwargs["queryset"] = ProductMarketClass.objects.none()
            if product and client:
                kwargs["queryset"] = ProductMarketClass.objects.filter(product=product,
                                                                       market=client.market, is_enabled=True)

        if db_field.name == "product_packaging":
            kwargs["queryset"] = ProductPackaging.objects.none()
            if product and client:
                kwargs["queryset"] = ProductPackaging.objects.filter(product=product,
                                                                     market=client.market, is_enabled=True)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == "amount_price":
            formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
            formfield.widget.attrs['readonly'] = True
            formfield.widget.attrs['class'] = 'readonly'
            formfield.disabled = True
            if request.POST:
                formfield.required = False
            return formfield

        return super().formfield_for_dbfield(db_field, request, **kwargs)


class OrderItemWeightInline(OrderItemInlineMixin):
    model = OrderItemWeight
    formset = OrderItemWeightFormSet

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        return formset

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        parent_object_id = request.resolver_match.kwargs.get("object_id")
        parent_obj = Order.objects.get(id=parent_object_id) if parent_object_id else None

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    class Media:
        js = ('js/admin/forms/packhouses/sales/order_item_weight_inline.js',)


class OrderItemPackagingInline(OrderItemInlineMixin):
    model = OrderItemPackaging
    formset = OrderItemPackagingFormSet

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        formset.form.base_fields['product_packaging'].widget.can_add_related = False
        formset.form.base_fields['product_packaging'].widget.can_change_related = False
        formset.form.base_fields['product_packaging'].widget.can_delete_related = False
        formset.form.base_fields['product_packaging'].widget.can_view_related = False
        return formset

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        parent_object_id = request.resolver_match.kwargs.get("object_id")
        parent_obj = Order.objects.get(id=parent_object_id) if parent_object_id else None

        if db_field.name == "product_packaging":
            kwargs["queryset"] = ProductPackaging.objects.none()
            if parent_obj and parent_obj.product:
                kwargs["queryset"] = ProductPackaging.objects.filter(product=parent_obj.product,
                                                                     market=parent_obj.client.market, is_enabled=True)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    class Media:
        js = ('js/admin/forms/packhouses/sales/order_item_packaging_inline.js',)


class OrderItemPalletInline(OrderItemInlineMixin):
    model = OrderItemPallet
    formset = OrderItemPalletFormSet

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        formset.form.base_fields['product_packaging_pallet'].widget.can_add_related = False
        formset.form.base_fields['product_packaging_pallet'].widget.can_change_related = False
        formset.form.base_fields['product_packaging_pallet'].widget.can_delete_related = False
        formset.form.base_fields['product_packaging_pallet'].widget.can_view_related = False
        return formset

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        parent_object_id = request.resolver_match.kwargs.get("object_id")
        parent_object = Order.objects.get(id=parent_object_id) if parent_object_id else None

        client_id = request.POST.get('client') if request.POST else parent_object.client.id if parent_object else None
        product_id = request.POST.get('product') if request.POST else parent_object.product.id if parent_object else None
        client = Client.objects.get(id=client_id) if client_id else None
        product = Product.objects.get(id=product_id) if product_id else None

        if db_field.name == "product_packaging_pallet":
            kwargs["queryset"] = ProductPackagingPallet.objects.none()
            if client and product:
                kwargs["queryset"] = ProductPackagingPallet.objects.filter(product_packaging__product=product,
                                                                     product_packaging__market=client.market, is_enabled=True)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    class Media:
        js = ('js/admin/forms/packhouses/sales/order_item_pallet_inline.js',)


@admin.register(Order)
class OrderAdmin(ByOrganizationAdminMixin):
    list_display = ('ooid', 'client', 'maquiladora', 'shipment_date', 'delivery_date', 'delivery_kind',
                    'product', 'product_variety', 'order_items_kind', 'status')
    list_filter = ('client_category', ByMaquiladoraForOrganizationOrderFilter, ByClientForOrganizationOrderFilter,
                   'registration_date', 'shipment_date', 'delivery_date', ByLocalDeliveryForOrganizationOrderFilter,
                   ByIncotermsForOrganizationOrderFilter, ByProductForOrganizationOrderFilter,
                   ByProductVarietyForOrganizationOrderFilter, 'order_items_kind', 'status')
    fields = (
        'ooid', 'client_category', 'maquiladora', 'client', 'local_delivery', 'incoterms',
        'registration_date', 'shipment_date', 'delivery_date',
        'product', 'product_variety', 'order_items_kind',
        'observations', 'status'
    )
    ordering = ('-ooid',)
    inlines = [OrderItemWeightInline, OrderItemPackagingInline, OrderItemPalletInline]

    def delivery_kind(self, obj):
        if obj.local_delivery:
            return obj.local_delivery.name
        if obj.incoterms:
            return obj.incoterms.name
        return ""
    delivery_kind.short_description = _('Delivery kind')
    delivery_kind.admin_order_field = 'name'

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'status' in form.base_fields:
            form.base_fields['status'].choices = [choice for choice in form.base_fields['status'].choices if choice[0] != 'closed']
        if not obj or obj.status not in ['closed', 'canceled']:
            form.base_fields['maquiladora'].widget.can_add_related = False
            form.base_fields['maquiladora'].widget.can_change_related = False
            form.base_fields['maquiladora'].widget.can_delete_related = False
            form.base_fields['maquiladora'].widget.can_view_related = False
            form.base_fields['client'].widget.can_add_related = False
            form.base_fields['client'].widget.can_change_related = False
            form.base_fields['client'].widget.can_delete_related = False
            form.base_fields['client'].widget.can_view_related = False
            form.base_fields['local_delivery'].widget.can_add_related = False
            form.base_fields['local_delivery'].widget.can_change_related = False
            form.base_fields['local_delivery'].widget.can_delete_related = False
            form.base_fields['local_delivery'].widget.can_view_related = False
            form.base_fields['incoterms'].widget.can_add_related = False
            form.base_fields['incoterms'].widget.can_change_related = False
            form.base_fields['incoterms'].widget.can_delete_related = False
            form.base_fields['incoterms'].widget.can_view_related = False
            form.base_fields['product'].widget.can_add_related = False
            form.base_fields['product'].widget.can_change_related = False
            form.base_fields['product'].widget.can_delete_related = False
            form.base_fields['product'].widget.can_view_related = False

        return form

    def rendered_observations(self, obj):
        return mark_safe(obj.observations) if obj and obj.observations else ""

    rendered_observations.short_description = _('Observations')

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().readonly_fields

        if not obj:
            readonly_fields += ('status',)

        if obj and obj.pk:
            readonly_fields += ('ooid',)

        # Si el pedido no está abierto, todos los campos son readonly
        if obj and obj.status in ['closed', 'canceled']:
            readonly_fields += self.fields
            readonly_fields += ('rendered_observations',)

        return readonly_fields

    def get_fields(self, request, obj=None):
        fields = list(super().get_fields(request, obj))
        if not obj:
            fields.remove('ooid')

        if obj and obj.status in ['closed', 'canceled']:
            # Reemplazar 'observations' con 'rendered_observations' en modo readonly
            fields[fields.index('observations')] = 'rendered_observations'
        return fields

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        organization = getattr(request, 'organization', None)
        object_id = request.resolver_match.kwargs.get("object_id")
        obj = Order.objects.get(id=object_id) if object_id else None
        queryset_organization_filter = {"organization": organization, "is_enabled": True}
        client_category = request.POST.get('client_category') if request.POST else obj.client_category if obj else None
        client_id = request.POST.get('client') if request.POST else obj.client_id if obj else None

        if db_field.name == "maquiladora":
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.required = True
            if client_category and client_category == 'maquiladora':
                kwargs["queryset"] = Maquiladora.objects.filter(**queryset_organization_filter)
            else:
                kwargs["queryset"] = Maquiladora.objects.none()
                formfield.required = False
            return formfield

        if db_field.name == "client":
            queryset_filter = {"organization": organization, "category": client_category, "is_enabled": True}
            kwargs["queryset"] = Client.objects.filter(**queryset_filter) if client_category else Client.objects.none()

        if db_field.name == "product":
            kwargs["queryset"] = Product.objects.none()
            if organization:
                kwargs["queryset"] = Product.objects.filter(**queryset_organization_filter)

        if db_field.name == "product_variety":
            kwargs["queryset"] = ProductVariety.objects.none()
            if request.POST:
                product_id = request.POST.get('product')
            else:
                product_id = obj.product_id if obj else None
            if product_id:
                kwargs["queryset"] = ProductVariety.objects.filter(product_id=product_id, is_enabled=True)

        if db_field.name == "local_delivery":
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.required = True
            if organization and client_id:
                client = Client.objects.get(id=client_id)
                organization_country = PackhouseExporterProfile.objects.get(organization=organization).country
                if client and client.country == organization_country:
                    formfield.required = True
                else:
                    formfield.required = False
            return formfield

        if db_field.name == "incoterms":
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.required = True
            if organization and client_id:
                client = Client.objects.get(id=client_id)
                organization_country = PackhouseExporterProfile.objects.get(organization=organization).country
                if client and client.country == organization_country:
                    formfield.required = False
                else:
                    formfield.required = True
            return formfield

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    class Media:
        js = ('js/admin/forms/packhouses/sales/order.js',)
        # pass
