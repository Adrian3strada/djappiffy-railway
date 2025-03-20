from django.contrib import admin
from common.profiles.models import UserProfile  # (Si no se usa, se puede eliminar)
from .models import (Requisition, RequisitionSupply, PurchaseOrder,
                     PurchaseOrderSupply, PurchaseOrderCharge, PurchaseOrderDeduction)
from packhouses.catalogs.models import Supply, Provider
from django.utils.translation import gettext_lazy as _
from common.base.decorators import (
    uppercase_formset_charfield, uppercase_alphanumeric_formset_charfield,
    uppercase_form_charfield, uppercase_alphanumeric_form_charfield,
)
from common.base.mixins import (
    ByOrganizationAdminMixin, ByProductForOrganizationAdminMixin,
    DisableInlineRelatedLinksMixin, ByUserAdminMixin,
)
from django.core.exceptions import ObjectDoesNotExist
from .forms import RequisitionForm, PurchaseOrderForm
from django.utils.html import format_html, format_html_join
from django.urls import reverse
import nested_admin
from common.forms import SelectWidgetWithData
from common.utils import is_instance_used


class RequisitionSupplyInline(DisableInlineRelatedLinksMixin, admin.TabularInline):
    model = RequisitionSupply
    fields = ('supply', 'quantity', 'comments')
    extra = 0

    def _get_parent_obj(self, request):
        """Obtiene el objeto Requisition padre a partir del parámetro object_id."""
        parent_object_id = request.resolver_match.kwargs.get("object_id")
        if parent_object_id:
            try:
                return Requisition.objects.get(id=parent_object_id)
            except Requisition.DoesNotExist:
                return None
        return None

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "supply":
            if hasattr(request, 'organization'):
                kwargs["queryset"] = Supply.objects.filter(organization=request.organization)
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda obj: f"{obj.kind.name}: {obj.name}"
            return formfield
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        parent_obj = self._get_parent_obj(request)
        if parent_obj and parent_obj.status in ['closed', 'canceled', 'ready']:
            # Todos los campos se vuelven de solo lectura si el estado es cerrado, cancelado o listo
            readonly_fields.extend([
                field.name for field in self.model._meta.fields
                if field.name not in readonly_fields
            ])
        return readonly_fields

    def has_delete_permission(self, request, obj=None):
        parent_obj = self._get_parent_obj(request)
        if parent_obj and parent_obj.status in ['closed', 'canceled', 'ready']:
            return False
        return super().has_delete_permission(request, obj)


@admin.register(Requisition)
class RequisitionAdmin(ByOrganizationAdminMixin, ByUserAdminMixin):
    form = RequisitionForm
    fields = ('ooid', 'status', 'comments', 'save_and_send')
    list_display = ('ooid', 'created_at', 'status', 'generate_actions_buttons')
    readonly_fields = ('ooid', 'status')
    inlines = (RequisitionSupplyInline,)

    def save_model(self, request, obj, form, change):
        save_and_send = form.cleaned_data.get('save_and_send', False)
        if save_and_send:
            obj.status = 'ready'
        super().save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        # Asegurar que 'ooid' sea de solo lectura tanto en creación como en edición
        if not obj or (obj and obj.pk):
            if 'ooid' not in readonly_fields:
                readonly_fields.append('ooid')
        if obj and obj.status in ['closed', 'canceled', 'ready']:
            readonly_fields.extend([field for field in self.fields if hasattr(obj, field)])
        return readonly_fields

    def generate_actions_buttons(self, obj):
        requisition_pdf = reverse('requisition_pdf', args=[obj.pk])
        tooltip_requisition_pdf = _('Generate Requisition PDF')

        tooltip_ready = _('Send to Purchase Operations Department')
        ready_url = reverse('set_requisition_ready', args=[obj.pk])
        confirm_ready_text = _('Are you sure you want to send this requisition to Purchase Operations Department?')
        confirm_button_text = _('Yes, send')
        cancel_button_text = _('No')

        set_requisition_ready_button = ''
        if obj.status == 'open':
            set_requisition_ready_button = format_html(
                '''
                <a class="button btn-ready-confirm" href="javascript:void(0);" data-toggle="tooltip" title="{}"
                   data-url="{}" data-message="{}" data-confirm="{}" data-cancel="{}" style="color:#4daf50;">
                    <i class="fa-solid fa-paper-plane"></i>
                </a>
                ''',
                tooltip_ready, ready_url, confirm_ready_text, confirm_button_text, cancel_button_text
            )

        return format_html(
            '''
            <a class="button" href="{}" target="_blank" data-toggle="tooltip" title="{}">
                <i class="fa-solid fa-print"></i>
            </a>
            {}
            ''',
            requisition_pdf, tooltip_requisition_pdf, set_requisition_ready_button
        )

    generate_actions_buttons.short_description = _('Actions')
    generate_actions_buttons.allow_tags = True

    class Media:
        js = ('js/admin/forms/packhouses/purchase/requisition.js',)


class PurchaseOrderRequisitionSupplyInline(admin.StackedInline):
    model = PurchaseOrderSupply
    fields = ('requisition_supply', 'quantity', 'unit_price', 'total_price','comments')
    readonly_fields = ('total_price','comments',)
    extra = 0

    def _get_parent_obj(self, request):
        """Obtiene el objeto Purchase Order padre a partir del parámetro object_id."""
        parent_object_id = request.resolver_match.kwargs.get("object_id")
        if parent_object_id:
            try:
                return PurchaseOrder.objects.get(id=parent_object_id)
            except PurchaseOrder.DoesNotExist:
                return None
        return None

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        parent_obj = self._get_parent_obj(request)
        if parent_obj and parent_obj.status in ['closed', 'canceled', 'ready']:
            # Todos los campos se vuelven de solo lectura si el estado es cerrado, cancelado o listo
            readonly_fields.extend([
                field.name for field in self.model._meta.fields
                if field.name not in readonly_fields
            ])
        return readonly_fields

    def has_delete_permission(self, request, obj=None):
        parent_obj = self._get_parent_obj(request)
        if parent_obj and parent_obj.status in ['closed', 'canceled', 'ready']:
            return False
        return super().has_delete_permission(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Agregar clases o atributos personalizados a los campos
        form.base_fields['quantity'].widget.attrs.update({'class': 'quantity-field'})
        form.base_fields['unit_price'].widget.attrs.update({'class': 'unit-price-field'})
        form.base_fields['total_price'].widget.attrs.update({'class': 'total-price-field', 'readonly': 'readonly'})
        return form

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "requisition_supply":

            # Obtener el ID del Purchase Order actual
            parent_po_id = request.resolver_match.kwargs.get('object_id')

            # Excluir sólo los requisition_supply que están usados en otros PurchaseOrders
            used_requisition_supplies = PurchaseOrderSupply.objects.exclude(
                purchase_order_id=parent_po_id
            ).values_list('requisition_supply_id', flat=True)

            # Filtrar solo las RequisitionSupply con estado 'ready'
            queryset = RequisitionSupply.objects.filter(requisition__status='ready', ).exclude(
                id__in=used_requisition_supplies
            )
            if hasattr(request, 'organization'):
                queryset = queryset.filter(requisition__organization=request.organization)

            kwargs["queryset"] = queryset
            kwargs["widget"] = SelectWidgetWithData(model=RequisitionSupply, data_fields=["quantity", "comments"])


        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    class Media:
        js = ('js/admin/forms/packhouses/purchase/purchase_orders_supply.js',)


class PurchaseOrderChargerInline(admin.StackedInline):
    model = PurchaseOrderCharge
    fields = ('charge', 'amount')
    extra = 0

    def _get_parent_obj(self, request):
        """Obtiene el objeto Purchase Order padre a partir del parámetro object_id."""
        parent_object_id = request.resolver_match.kwargs.get("object_id")
        if parent_object_id:
            try:
                return PurchaseOrder.objects.get(id=parent_object_id)
            except PurchaseOrder.DoesNotExist:
                return None
        return None

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        parent_obj = self._get_parent_obj(request)
        if parent_obj and parent_obj.status in ['closed', 'canceled', 'ready']:
            # Todos los campos se vuelven de solo lectura si el estado es cerrado, cancelado o listo
            readonly_fields.extend([
                field.name for field in self.model._meta.fields
                if field.name not in readonly_fields
            ])
        return readonly_fields

    def has_delete_permission(self, request, obj=None):
        parent_obj = self._get_parent_obj(request)
        if parent_obj and parent_obj.status in ['closed', 'canceled', 'ready']:
            return False
        return super().has_delete_permission(request, obj)

class PurchaseOrderDeductionInline(admin.StackedInline):
    model = PurchaseOrderDeduction
    fields = ('deduction', 'amount')
    extra = 0

    def _get_parent_obj(self, request):
        """Obtiene el objeto Purchase Order padre a partir del parámetro object_id."""
        parent_object_id = request.resolver_match.kwargs.get("object_id")
        if parent_object_id:
            try:
                return PurchaseOrder.objects.get(id=parent_object_id)
            except PurchaseOrder.DoesNotExist:
                return None
        return None

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        parent_obj = self._get_parent_obj(request)
        if parent_obj and parent_obj.status in ['closed', 'canceled', 'ready']:
            # Todos los campos se vuelven de solo lectura si el estado es cerrado, cancelado o listo
            readonly_fields.extend([
                field.name for field in self.model._meta.fields
                if field.name not in readonly_fields
            ])
        return readonly_fields

    def has_delete_permission(self, request, obj=None):
        parent_obj = self._get_parent_obj(request)
        if parent_obj and parent_obj.status in ['closed', 'canceled', 'ready']:
            return False
        return super().has_delete_permission(request, obj)


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(ByOrganizationAdminMixin, admin.ModelAdmin):
    form = PurchaseOrderForm
    list_display = ('ooid', 'provider', 'currency', 'status', 'created_at', 'user', 'generate_actions_buttons')
    fields = ('ooid', 'provider','payment_date','currency','tax', 'status', 'comments', 'save_and_send')
    list_filter = ('provider', 'currency', 'status')
    readonly_fields = ('ooid', 'status')
    inlines = [PurchaseOrderRequisitionSupplyInline, PurchaseOrderChargerInline, PurchaseOrderDeductionInline]


    def generate_actions_buttons(self, obj):
        purchase_order_supply_pdf = reverse('purchase_order_supply_pdf', args=[obj.pk])
        tooltip_purchase_order_supply_pdf = _('Generate Purchase Order Supply PDF')

        tooltip_ready = _('Send to Storehouse')
        ready_url = reverse('set_purchase_order_supply_ready', args=[obj.pk])
        confirm_ready_text = _('Are you sure you want to send this purchase order supply to Storehouse?')
        confirm_button_text = _('Yes, send')
        cancel_button_text = _('No')

        tooltip_open = _('Reopen this purchase order')
        open_url = reverse('set_purchase_order_supply_open', args=[obj.pk])
        confirm_open_text = _(
            'Are you sure you want to reopen this purchase order? It will no longer be available in the storehouse for entry and you can continue editing it.')
        confirm_button_text_open = _('Yes, reopen')

        set_purchase_order_supply_ready_button = ''
        if obj.status == 'open':
            set_purchase_order_supply_ready_button = format_html(
                '''
                <a class="button btn-ready-confirm" href="javascript:void(0);" data-toggle="tooltip" title="{}"
                   data-url="{}" data-message="{}" data-confirm="{}" data-cancel="{}" style="color:#4daf50;">
                    <i class="fa-solid fa-paper-plane"></i>
                </a>
                ''',
                tooltip_ready, ready_url, confirm_ready_text, confirm_button_text, cancel_button_text
            )

        set_purchase_order_supply_open_button = ''
        if obj.status == 'ready':
            set_purchase_order_supply_open_button = format_html(
                '''
                <a class="button btn-open-confirm" href="javascript:void(0);" data-toggle="tooltip" title="{}"
                   data-url="{}" data-message="{}" data-confirm="{}" data-cancel="{}" style="color:#ffc107;">
                    <i class="fa-solid fa-lock-open"></i>
                </a>
                ''',
                tooltip_open, open_url, confirm_open_text, confirm_button_text_open, cancel_button_text
            )

        tooltip_payment = _('Send this purchase order to payments')
        payment_url = reverse('set_purchase_order_supply_payment', args=[obj.pk])
        confirm_payment_text = _(
            'Are you sure you want to send this purchase order to payments?')

        set_purchase_order_supply_payment_button = ''
        if obj.status == "closed" and not obj.is_in_payments:
            set_purchase_order_supply_payment_button = format_html(
                '''
                <a class="button btn-payment-confirm" href="javascript:void(0);" data-toggle="tooltip" title="{}"
                    data-url="{}" data-message="{}" data-confirm="{}" data-cancel="{}" style="color:#000;">
                    <i class="fa-solid fa-dollar-sign"></i>
                </a>
                ''',
                tooltip_payment, payment_url, confirm_payment_text, confirm_button_text, cancel_button_text
            )

        return format_html(
            '''
            {}
            {}
            {}
            <a class="button" href="{}" target="_blank" data-toggle="tooltip" title="{}">
                <i class="fa-solid fa-print"></i>
            </a>
            ''',
            set_purchase_order_supply_payment_button, set_purchase_order_supply_ready_button, set_purchase_order_supply_open_button, purchase_order_supply_pdf, tooltip_purchase_order_supply_pdf
        )

    generate_actions_buttons.short_description = _('Actions')
    generate_actions_buttons.allow_tags = True

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if not obj or (obj and obj.pk):
            if 'ooid' not in readonly_fields:
                readonly_fields.append('ooid')
        if obj and obj.status in ['closed', 'canceled', 'ready']:
            readonly_fields.extend([field for field in self.fields if hasattr(obj, field)])

        return readonly_fields

    def formfield_for_foreignkey(self, db_field, request, **kwargs):

        if db_field.name == "provider":
            if hasattr(request, 'organization'):
                kwargs["queryset"] = Provider.objects.filter(organization=request.organization, is_enabled=True,
                                                category='supply_provider')
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            return formfield
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'provider' in form.base_fields:
            form.base_fields['provider'].widget.can_add_related = False
            form.base_fields['provider'].widget.can_change_related = False
            form.base_fields['provider'].widget.can_delete_related = False
            form.base_fields['provider'].widget.can_view_related = False
        return form

    def save_model(self, request, obj, form, change):
        if not change:
            obj.user = request.user

        save_and_send = form.cleaned_data.get('save_and_send', False)
        if save_and_send:
            obj.status = 'ready'
        super().save_model(request, obj, form, change)

    class Media:
        js = ('js/admin/forms/packhouses/purchase/purchase_orders.js',)
