from django.contrib import admin
from common.profiles.models import UserProfile  # (Si no se usa, se puede eliminar)
from .models import (Requisition, RequisitionSupply, PurchaseOrder,
                     PurchaseOrderSupply, PurchaseOrderCharge, PurchaseOrderDeduction,
                     PurchaseOrderPayment)
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
from .forms import RequisitionForm, PurchaseOrderForm, PurchaseOrderPaymentForm, RequisitionSupplyForm
from django.utils.html import format_html, format_html_join
from django.urls import reverse
import nested_admin
from common.forms import SelectWidgetWithData
from common.utils import is_instance_used
from common.base.models import SupplyMeasureUnitCategory
from django.urls import path
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.utils import timezone
from django.db import models
from django.core.exceptions import ValidationError
from django import forms
from decimal import Decimal, ROUND_HALF_UP
from django.db import transaction
from django.contrib.messages import constants as message_constants





class RequisitionSupplyInline(DisableInlineRelatedLinksMixin, admin.StackedInline):
    model = RequisitionSupply
    #form = RequisitionSupplyForm
    fields = ('supply', 'quantity', 'unit_category','delivery_deadline', 'comments')
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

    class Media:
        js = ('js/admin/forms/packhouses/purchases/requisition_supply_inline.js',)


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
        js = ('js/admin/forms/packhouses/purchases/requisition.js',)


class PurchaseOrderRequisitionSupplyInline(admin.StackedInline):
    model = PurchaseOrderSupply
    fields = ('requisition_supply', 'quantity','unit_category','delivery_deadline', 'unit_price', 'total_price','comments')
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
            kwargs["widget"] = SelectWidgetWithData(model=RequisitionSupply, data_fields=["quantity", "comments","unit_category","delivery_deadline"])

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def clean(self):
        if self.quantity <= 0:
            raise ValidationError({'quantity': _("Quantity must be greater than 0.")})

        if self.unit_price <= 0:
            raise ValidationError({'unit_price': _("Unit price must be greater than 0.")})

    def save(self, *args, **kwargs):
        if self.quantity <= 0:
            raise ValueError("Quantity must be greater than 0.")
        if self.unit_price <= 0:
            raise ValueError("Unit price must be greater than 0.")

        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    class Media:
        js = ('js/admin/forms/packhouses/purchases/purchase_orders_supply.js',)


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
        if parent_obj and parent_obj.status in ['canceled',]:
            # Todos los campos se vuelven de solo lectura si el estado es cerrado, cancelado o listo
            readonly_fields.extend([
                field.name for field in self.model._meta.fields
                if field.name not in readonly_fields
            ])
        return readonly_fields

    def has_delete_permission(self, request, obj=None):
        parent_obj = self._get_parent_obj(request)
        if parent_obj and parent_obj.status in ['canceled',]:
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
        if parent_obj and parent_obj.status in ['canceled',]:
            # Todos los campos se vuelven de solo lectura si el estado es cerrado, cancelado o listo
            readonly_fields.extend([
                field.name for field in self.model._meta.fields
                if field.name not in readonly_fields
            ])
        return readonly_fields

    def has_delete_permission(self, request, obj=None):
        parent_obj = self._get_parent_obj(request)
        if parent_obj and parent_obj.status in ['canceled',]:
            return False
        return super().has_delete_permission(request, obj)


class PurchaseOrderPaymentInline(admin.StackedInline):
    model = PurchaseOrderPayment
    form = PurchaseOrderPaymentForm
    fields = (
        'cancel_button',
        'payment_kind',
        'payment_date',
        'amount',
        'bank',
        'comments',
        'additional_inputs',
        'payment_info',
    )
    extra = 0
    can_delete = False
    # Estos campos se mostrarán de solo lectura:
    readonly_fields = ('cancel_button', 'payment_info',)

    def cancel_button(self, obj):
        if obj.pk and obj.status != "canceled":
            url = reverse('admin:cancel_payment', args=[obj.pk])
            title = _("Are you sure you want to cancel this payment?")
            confirm_text = _("Yes, cancel")
            cancel_text = _("No, keep it")
            button_label = _("Cancel payment")
            return format_html(
                '<a class="button" href="{0}" onclick="event.preventDefault(); '
                'Swal.fire({{ '
                'title: \'{1}\', '
                'icon: \'warning\', '
                'showCancelButton: true, '
                'confirmButtonText: \'{2}\', '
                'cancelButtonText: \'{3}\', '
                'confirmButtonColor: \'#d33\' '
                '}}).then((result) => {{ if (result.isConfirmed) {{ '
                'window.location.href=\'{0}\'; '
                '}} }});">{4}</a>',
                url, title, confirm_text, cancel_text, button_label
            )
        if not obj.pk:
            return ""
        if obj.pk and obj.status == "canceled":
            return format_html('<span class="canceled">{}</span>', _('Payment canceled'))

    cancel_button.short_description = ""

    def payment_info(self, obj):
        if not obj.pk:
            return ""
        if obj.status == "canceled":
            canceled_by = obj.canceled_by if obj.canceled_by else ""
            cancellation_date = obj.cancellation_date.strftime("%d/%m/%Y %H:%M") if obj.cancellation_date else ""
            created_at = obj.created_at.strftime("%d/%m/%Y %H:%M") if obj.created_at else ""
            created_by = obj.created_by if obj.created_by else ""
            added_by_info = format_html(
                '<div><span>{}</span>: {}<br><span>{}</span>: {}</div>',
                _("Registered by"), created_by,
                _("Payment date"), created_at
            )
            return format_html(
                '{}<div><span>{}</span>: {}<br><span>{}</span>: {} Hrs.</div>',
                added_by_info, _("Canceled by"), canceled_by,
                _("Cancellation date"), cancellation_date
            )
        else:
            created_by = obj.created_by if obj.created_by else ""
            created_at = obj.created_at.strftime("%d/%m/%Y %H:%M") if obj.created_at else ""
            return format_html(
                '<div><span>{}</span>: {}<br><span>{}</span>: {}</div>',
                _("Registered by"), created_by,
                _("Payment date"), created_at
            )

    payment_info.short_description = _("Payment info")

    class Media:
        js = ('js/admin/forms/packhouses/purchases/purchase_orders_payments.js',)

@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(ByOrganizationAdminMixin, admin.ModelAdmin):
    form = PurchaseOrderForm
    list_display = ('ooid', 'provider', 'balance_payable', 'currency', 'status', 'created_at', 'user', 'generate_actions_buttons')
    fields = ('ooid', 'provider','payment_date', 'balance_payable', 'currency','tax', 'status', 'comments', 'save_and_send')
    list_filter = ('provider', 'currency', 'status')
    readonly_fields = ('ooid', 'status', 'balance_payable', 'created_at', 'user')
    inlines = [PurchaseOrderRequisitionSupplyInline, PurchaseOrderChargerInline, PurchaseOrderDeductionInline]


    def get_inline_instances(self, request, obj=None):
        inline_instances = super().get_inline_instances(request, obj)
        # Mostrar PurchaseOrderPaymentInline solo si el status es "closed"
        if obj and obj.status == "closed":
            inline_instances.append(PurchaseOrderPaymentInline(self.model, self.admin_site))

        return inline_instances

    def generate_actions_buttons(self, obj):
        purchase_order_supply_pdf = reverse('purchase_order_supply_pdf', args=[obj.pk])
        tooltip_purchase_order_supply_pdf = _('Generate Purchase Order Supply PDF')

        tooltip_ready = _('Send to Storehouse')
        ready_url = reverse('set_purchase_order_supply_ready', args=[obj.pk])
        confirm_ready_text = _('Are you sure you want to send this purchases order supply to Storehouse?')
        confirm_button_text = _('Yes, send')
        cancel_button_text = _('No')

        tooltip_open = _('Reopen this purchases order')
        open_url = reverse('set_purchase_order_supply_open', args=[obj.pk])
        confirm_open_text = _(
            'Are you sure you want to reopen this purchases order? It will no longer be available in the storehouse for entry and you can continue editing it.')
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

        tooltip_payment = _('Payment application')
        set_purchase_order_supply_payment_button = ''
        if obj.status == "closed":
            edit_url = reverse(
                "admin:{}_{}_change".format(obj._meta.app_label, obj._meta.model_name),
                args=[obj.pk]
            )
            edit_url_with_anchor = f"{edit_url}#payments-tab"
            set_purchase_order_supply_payment_button = format_html(
                '''
                <a class="button" href="{}" data-toggle="tooltip" title="{}" style="color:#000;">
                    <i class="fa-solid fa-dollar-sign"></i>
                </a>
                ''',
                edit_url_with_anchor, tooltip_payment
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
        if save_and_send and obj.status == 'open':
            obj.status = 'ready'

        super().save_model(request, obj, form, change)

    def get_urls(self):
        # Obtener primero las URLs originales del admin
        urls = super().get_urls()
        # Definir URLs personalizadas
        custom_urls = [
            path(
                'cancel-payment/<int:payment_id>/',
                self.admin_site.admin_view(self.cancel_payment),
                name='cancel_payment'
            ),
        ]
        return custom_urls + urls

    def cancel_payment(self, request, payment_id, *args, **kwargs):
        try:
            payment = PurchaseOrderPayment.objects.get(id=payment_id)
            payment.status = "canceled"
            payment.cancellation_date = timezone.now()
            payment.canceled_by = request.user
            payment.save(update_fields=["status", "cancellation_date", "canceled_by"])
            payment.purchase_order.recalculate_balance(save=True)
            self.message_user(request, _(f"Payment canceled successfully. New balance payable: ${payment.purchase_order.balance_payable:.2f}"),
                              level=messages.SUCCESS)
            # Obtenemos el ID del Purchase Order asociado
            purchase_order_id = payment.purchase_order.pk
        except PurchaseOrderPayment.DoesNotExist:
            self.message_user(request, _("Payment not found"), level=messages.ERROR)
            purchase_order_id = None

        if purchase_order_id:
            # Construimos la URL de cambio del Purchase Order y le agregamos el fragmento #payments-tab
            redirect_url = reverse('admin:purchases_purchaseorder_change', args=[purchase_order_id]) + "#payments-tab"
        else:
            redirect_url = request.path + "#payments-tab"
        return HttpResponseRedirect(redirect_url)


    def response_change(self, request, obj):
        balance_data = obj.simulate_balance()

        if balance_data['balance'] < 0:
            if not hasattr(request, '_balance_error_shown'):
                self.message_user(
                    request,
                    _(f"No se puede guardar esta orden porque el balance sería negativo (${balance_data['balance']}). "
                      f"Insumos: ${balance_data['supplies_total']}, "
                      f"Impuestos: ${balance_data['tax_amount']}, "
                      f"Cargos: ${balance_data['charges_total']}, "
                      f"Deducciones: ${balance_data['deductions_total']}, "
                      f"Pagos: ${balance_data['payments_total']}"),
                    level=messages.ERROR
                )
            url = reverse('admin:purchases_purchaseorder_change', args=[obj.pk])
            return HttpResponseRedirect(url)

        obj.balance_payable = balance_data['balance']
        obj.save(update_fields=['balance_payable'])
        return super().response_change(request, obj)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)

        purchase_order = form.instance
        balance_data = purchase_order.simulate_balance()

        if balance_data['balance'] < 0:
            if not hasattr(request, '_balance_error_shown'):
                request._balance_error_shown = True
                self.message_user(
                    request,
                    _(f"El balance final sería negativo (${balance_data['balance']}). "
                      f"Costo total de Insumos: ${balance_data['supplies_total']} "
                      f"+ Impuestos: ${balance_data['tax_amount']} "
                      f"+ Cargos: ${balance_data['charges_total']} "
                      f"- Pagos: ${balance_data['payments_total']} "
                      f"- Deducciones: ${balance_data['deductions_total']}"),
                    level=messages.ERROR
                )
            return  # No seguimos si hay error

        # ⚡ Aquí ACTUALIZAMOS directamente el balance
        purchase_order.balance_payable = balance_data['balance']
        purchase_order.save(update_fields=['balance_payable'])

    def save_formset(self, request, form, formset, change):

        model = formset.model
        purchase_order = form.instance

        if not hasattr(formset, 'cleaned_data'):
            return

        # Cargamos objetos actuales
        existing_qs = {obj.pk: obj for obj in model.objects.filter(purchase_order=purchase_order)}

        # Lista de objetos marcados para eliminar
        to_delete = []

        for form_data in formset.cleaned_data:
            if form_data.get('DELETE') and form_data.get('id'):
                obj = form_data['id']
                if obj.pk in existing_qs:
                    to_delete.append(existing_qs.pop(obj.pk))  # lo quitamos y lo marcamos para borrar

        # Nuevas instancias sin guardar aún
        new_instances = formset.save(commit=False)

        for instance in new_instances:
            existing_qs[instance.pk] = instance  # reemplazamos si ya existía

        combined = list(existing_qs.values())

        # Cálculo de totales (simulación)
        total_supplies = Decimal('0.00')
        total_charges = Decimal('0.00')
        total_deductions = Decimal('0.00')
        total_payments = Decimal('0.00')

        for obj in combined:
            if isinstance(obj, PurchaseOrderSupply):
                total_supplies += Decimal(obj.total_price or 0)
            elif isinstance(obj, PurchaseOrderCharge):
                total_charges += Decimal(obj.amount or 0)
            elif isinstance(obj, PurchaseOrderDeduction):
                total_deductions += Decimal(obj.amount or 0)
            elif isinstance(obj, PurchaseOrderPayment) and obj.status != 'canceled':
                total_payments += Decimal(obj.amount or 0)

        other_data = purchase_order.simulate_balance()

        supplies_total = total_supplies if model == PurchaseOrderSupply else other_data['supplies_total']
        charges_total = total_charges if model == PurchaseOrderCharge else other_data['charges_total']
        deductions_total = total_deductions if model == PurchaseOrderDeduction else other_data['deductions_total']
        payments_total = total_payments if model == PurchaseOrderPayment else other_data['payments_total']

        tax_percent = Decimal(purchase_order.tax or 0)
        tax_decimal = tax_percent / Decimal('100.00')
        tax_amount = (supplies_total * tax_decimal).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        balance = supplies_total + tax_amount + charges_total - deductions_total - payments_total
        balance = balance.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        if balance < 0:
            if not hasattr(request, '_balance_error_shown'):
                request._balance_error_shown = True
                self.message_user(
                    request,
                    _(f"El balance final sería negativo (${balance}) "
                      f"Costo total de Insumos: ${supplies_total} "
                      f"+ Impuestos: ${tax_amount} "
                      f"+ Cargos: ${charges_total} "
                      f"- Pagos: ${payments_total} "
                      f"- Deducciones: ${deductions_total}"),
                    level=messages.ERROR
                )
            return  # no guardar

        #Primero eliminamos los que fueron marcados para DELETE
        for obj in to_delete:
            obj.delete()

        #Ahora sí se guarda los nuevos o modificados
        for instance in new_instances:
            if not instance.pk:
                instance.created_by = request.user
            instance.save()

        formset.save_m2m()


    class Media:
        js = ('js/admin/forms/packhouses/purchases/purchase_orders.js',)

