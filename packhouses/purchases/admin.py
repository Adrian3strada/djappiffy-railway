from django.contrib import admin
from wagtail.admin.templatetags.wagtailadmin_tags import status

from common.profiles.models import UserProfile
from .models import (Requisition, RequisitionSupply, PurchaseOrder,
                     PurchaseOrderSupply, PurchaseOrderCharge, PurchaseOrderDeduction,
                     PurchaseOrderPayment, ServiceOrder, ServiceOrderCharge, ServiceOrderDeduction,
                     ServiceOrderPayment, PurchaseMassPayment
                     )
from packhouses.catalogs.models import Supply, Provider, Service
from django.utils.translation import gettext_lazy as _
from common.base.decorators import (
    uppercase_formset_charfield, uppercase_alphanumeric_formset_charfield,
    uppercase_form_charfield, uppercase_alphanumeric_form_charfield,
)
from common.base.mixins import (
    ByOrganizationAdminMixin, ByProductForOrganizationAdminMixin,
    DisableInlineRelatedLinksMixin, ByUserAdminMixin, DisableLinksAdminMixin
)
from django.core.exceptions import ObjectDoesNotExist
from .forms import (RequisitionForm, PurchaseOrderForm, PurchaseOrderPaymentForm, RequisitionSupplyForm,
                    ServiceOrderForm, ServiceOrderPaymentForm, PurchaseMassPaymentForm
                    )
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
from django.urls import path
import datetime
from .utils import create_related_payments_and_update_balances
from packhouses.receiving.models import Batch, BatchStatusChange
from django.db.models import OuterRef, Subquery, DateTimeField, ExpressionWrapper, Q, F
from django.utils.timezone import now, timedelta


class RequisitionSupplyInline(DisableInlineRelatedLinksMixin, admin.StackedInline):
    """
    Inline para gestionar los insumos asociados a una requisición.

    Personaliza el queryset para mostrar solo insumos de la organización activa
    y bloquea los campos y eliminación de registros cuando la requisición ya no es editable
    (estados 'closed', 'canceled' o 'ready').
    """

    model = RequisitionSupply
    fields = ('supply', 'quantity', 'unit_category', 'delivery_deadline', 'comments')
    extra = 0

    def _get_parent_obj(self, request):
        """
        Recupera el objeto Requisition padre basado en la URL actual del admin.

        Permite condicionar permisos o estado de edición con base al estatus del padre.
        """
        parent_object_id = request.resolver_match.kwargs.get("object_id")
        if parent_object_id:
            try:
                return Requisition.objects.get(id=parent_object_id)
            except Requisition.DoesNotExist:
                return None
        return None

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Limita el campo 'supply' solo a insumos de la organización activa
        y personaliza su etiqueta para mostrar tipo y nombre.
        """
        if db_field.name == "supply":
            if hasattr(request, 'organization'):
                kwargs["queryset"] = Supply.objects.filter(organization=request.organization)
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda obj: f"{obj.kind.name}: {obj.name}"
            return formfield
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_readonly_fields(self, request, obj=None):
        """
        Hace todos los campos de solo lectura si la requisición está en un estado no editable.
        """
        readonly_fields = list(super().get_readonly_fields(request, obj))
        parent_obj = self._get_parent_obj(request)
        if parent_obj and parent_obj.status in ['closed', 'canceled', 'ready']:
            readonly_fields.extend([
                field.name for field in self.model._meta.fields
                if field.name not in readonly_fields
            ])
        return readonly_fields

    def has_delete_permission(self, request, obj=None):
        """
        Bloquea la eliminación de insumos si la requisición ya fue enviada o cerrada.
        """
        parent_obj = self._get_parent_obj(request)
        if parent_obj and parent_obj.status in ['closed', 'canceled', 'ready']:
            return False
        return super().has_delete_permission(request, obj)

    class Media:
        js = ('js/admin/forms/packhouses/purchases/requisition_supply_inline.js',)


@admin.register(Requisition)
class RequisitionAdmin(ByOrganizationAdminMixin, ByUserAdminMixin):
    """
    Admin de gestión para solicitudes de insumos (Requisition).

    - Permite la edición controlada según el estado ('open', 'ready', 'closed', 'canceled').
    - Facilita la transición rápida de estado mediante un botón 'Guardar y enviar'.
    - Integra generación de PDF y flujos de validación de cambios para una operación segura.
    """

    form = RequisitionForm
    fields = ('ooid', 'status', 'comments', 'save_and_send')
    list_display = ('ooid', 'created_at', 'status', 'generate_actions_buttons')
    readonly_fields = ('ooid', 'status')
    inlines = (RequisitionSupplyInline,)

    def save_model(self, request, obj, form, change):
        """
        Al guardar, cambia el estado a 'ready' si el usuario lo indica mediante 'save_and_send'.
        """
        save_and_send = form.cleaned_data.get('save_and_send', False)
        if save_and_send:
            obj.status = 'ready'
        super().save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        """
        Hace 'ooid' siempre de solo lectura.
        Si la requisición está cerrada, cancelada o enviada ('ready'), vuelve todo el formulario readonly.
        """
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if not obj or (obj and obj.pk):
            if 'ooid' not in readonly_fields:
                readonly_fields.append('ooid')
        if obj and obj.status in ['closed', 'canceled', 'ready']:
            readonly_fields.extend([field for field in self.fields if hasattr(obj, field)])
        return readonly_fields

    def generate_actions_buttons(self, obj):
        """
        Genera botones de acción:
        - Exportar PDF de la requisición.
        - Enviar requisición al área de Compras.

        Utiliza SweetAlert para confirmar las acciones sensibles y personaliza el estilo visual de los botones.
        """
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
    """
    Inline del admin para agregar y editar insumos dentro de una Orden de Compra (PurchaseOrder).

    Características:
    - Dinámicamente bloquea edición/eliminación si la orden ya está cerrada, cancelada o enviada.
    - Ajusta automáticamente el formulario agregando clases CSS para cálculos de frontend (JS).
    - Filtra inteligentemente el listado de insumos disponibles basándose en el estado 'ready' de las requisiciones
      y excluyendo insumos ya utilizados en otras órdenes de compra.
    """

    model = PurchaseOrderSupply
    fields = ('requisition_supply', 'quantity', 'unit_category', 'delivery_deadline', 'unit_price', 'total_price', 'comments')
    readonly_fields = ('total_price', 'comments',)
    extra = 0

    def _get_parent_obj(self, request):
        """
        Obtiene la instancia padre (PurchaseOrder) desde la URL del admin.
        Permite personalizar comportamientos según el estado de la orden.
        """
        parent_object_id = request.resolver_match.kwargs.get("object_id")
        if parent_object_id:
            try:
                return PurchaseOrder.objects.get(id=parent_object_id)
            except PurchaseOrder.DoesNotExist:
                return None
        return None

    def get_readonly_fields(self, request, obj=None):
        """
        Vuelve todos los campos readonly si la orden de compra no está en estado 'open'.
        """
        readonly_fields = list(super().get_readonly_fields(request, obj))
        parent_obj = self._get_parent_obj(request)
        if parent_obj and parent_obj.status in ['closed', 'canceled', 'ready']:
            readonly_fields.extend([
                field.name for field in self.model._meta.fields
                if field.name not in readonly_fields
            ])
        return readonly_fields

    def has_delete_permission(self, request, obj=None):
        """
        Impide borrar insumos si la orden ya no está editable.
        """
        parent_obj = self._get_parent_obj(request)
        if parent_obj and parent_obj.status in ['closed', 'canceled', 'ready']:
            return False
        return super().has_delete_permission(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        """
        Agrega clases CSS a los campos clave para facilitar cálculos dinámicos en frontend.
        """
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['quantity'].widget.attrs.update({'class': 'quantity-field'})
        form.base_fields['unit_price'].widget.attrs.update({'class': 'unit-price-field'})
        form.base_fields['total_price'].widget.attrs.update({'class': 'total-price-field', 'readonly': 'readonly'})
        return form

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Personaliza el campo 'requisition_supply' para:
        - Mostrar solo insumos de requisiciones en estado 'ready'.
        - Excluir insumos ya asociados a otras órdenes de compra.
        - Proporcionar datos adicionales al widget para autollenado en frontend (cantidad, comentarios, unidad, fecha límite).
        """
        if db_field.name == "requisition_supply":
            parent_po_id = request.resolver_match.kwargs.get('object_id')

            used_requisition_supplies = PurchaseOrderSupply.objects.exclude(
                purchase_order_id=parent_po_id
            ).values_list('requisition_supply_id', flat=True)

            queryset = RequisitionSupply.objects.filter(
                requisition__status='ready'
            ).exclude(
                id__in=used_requisition_supplies
            )
            if hasattr(request, 'organization'):
                queryset = queryset.filter(requisition__organization=request.organization)

            kwargs["queryset"] = queryset
            kwargs["widget"] = SelectWidgetWithData(
                model=RequisitionSupply,
                data_fields=["quantity", "comments", "unit_category", "delivery_deadline"]
            )

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def clean(self):
        """
        Valida que la cantidad y el precio unitario sean mayores a cero.
        """
        if self.quantity <= 0:
            raise ValidationError({'quantity': _("Quantity must be greater than 0.")})

        if self.unit_price <= 0:
            raise ValidationError({'unit_price': _("Unit price must be greater than 0.")})

    def save(self, *args, **kwargs):
        """
        Calcula y guarda automáticamente el total_price antes de guardar.
        """
        if self.quantity <= 0:
            raise ValueError("Quantity must be greater than 0.")
        if self.unit_price <= 0:
            raise ValueError("Unit price must be greater than 0.")

        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    class Media:
        js = ('js/admin/forms/packhouses/purchases/purchase_orders_supply.js',)


class PurchaseOrderChargerInline(admin.StackedInline):
    """
    Inline del admin para agregar cargos adicionales (charges) a una Orden de Compra.

    - Restringe edición/borrado si la orden está cancelada.
    - Los cargos se consideran parte del balance final de la orden de compra.
    """

    model = PurchaseOrderCharge
    fields = ('charge', 'amount')
    extra = 0

    def _get_parent_obj(self, request):
        """
        Obtiene la instancia de la PurchaseOrder asociada desde la URL del admin.
        """
        parent_object_id = request.resolver_match.kwargs.get("object_id")
        if parent_object_id:
            try:
                return PurchaseOrder.objects.get(id=parent_object_id)
            except PurchaseOrder.DoesNotExist:
                return None
        return None

    def get_readonly_fields(self, request, obj=None):
        """
        Hace todos los campos de solo lectura si la orden está cancelada.
        """
        readonly_fields = list(super().get_readonly_fields(request, obj))
        parent_obj = self._get_parent_obj(request)
        if parent_obj and parent_obj.status in ['canceled']:
            readonly_fields.extend([
                field.name for field in self.model._meta.fields
                if field.name not in readonly_fields
            ])
        return readonly_fields

    def has_delete_permission(self, request, obj=None):
        """
        Impide eliminar cargos si la orden está cancelada.
        """
        parent_obj = self._get_parent_obj(request)
        if parent_obj and parent_obj.status in ['canceled']:
            return False
        return super().has_delete_permission(request, obj)

class PurchaseOrderDeductionInline(admin.StackedInline):
    """
    Inline del admin para agregar deducciones (descuentos) a una Orden de Compra.

    - Restringe edición/borrado si la orden está cancelada.
    - Las deducciones afectan el balance total a pagar de la orden.
    """

    model = PurchaseOrderDeduction
    fields = ('deduction', 'amount')
    extra = 0

    def _get_parent_obj(self, request):
        """
        Obtiene la instancia de la PurchaseOrder asociada desde la URL del admin.
        """
        parent_object_id = request.resolver_match.kwargs.get("object_id")
        if parent_object_id:
            try:
                return PurchaseOrder.objects.get(id=parent_object_id)
            except PurchaseOrder.DoesNotExist:
                return None
        return None

    def get_readonly_fields(self, request, obj=None):
        """
        Hace todos los campos de solo lectura si la orden está cancelada.
        """
        readonly_fields = list(super().get_readonly_fields(request, obj))
        parent_obj = self._get_parent_obj(request)
        if parent_obj and parent_obj.status in ['canceled']:
            readonly_fields.extend([
                field.name for field in self.model._meta.fields
                if field.name not in readonly_fields
            ])
        return readonly_fields

    def has_delete_permission(self, request, obj=None):
        """
        Impide eliminar deducciones si la orden está cancelada.
        """
        parent_obj = self._get_parent_obj(request)
        if parent_obj and parent_obj.status in ['canceled']:
            return False
        return super().has_delete_permission(request, obj)

class PurchaseOrderPaymentInline(admin.StackedInline):
    """
    Inline del admin para administrar pagos de órdenes de compra.

    Permite registrar pagos, mostrar su información detallada
    y cancelar pagos de forma controlada con confirmación visual (SweetAlert).
    """

    model = PurchaseOrderPayment
    form = PurchaseOrderPaymentForm
    fields = (
        'cancel_button',
        'payment_kind',
        'payment_date',
        'mass_payment_link',
        'amount',
        'bank',
        'comments',
        'additional_inputs',
        'payment_info',
    )
    extra = 0
    can_delete = False
    readonly_fields = ('cancel_button', 'payment_info', 'mass_payment_link')

    def cancel_button(self, obj):
        """
        Genera un botón dinámico para cancelar el pago si no está ya cancelado.

        Usa SweetAlert para pedir confirmación antes de proceder.
        Si ya está cancelado, muestra un estado visual de "Payment canceled".
        """
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
        """
        Muestra información contextual sobre el pago:
        quién lo registró, cuándo se creó, y si fue cancelado, quién lo canceló y cuándo.

        Presenta los datos de forma formateada en el admin.
        """
        if not obj.pk:
            return ""

        created_by = obj.created_by or ""
        created_at = obj.created_at.strftime("%d/%m/%Y %H:%M") if obj.created_at else ""

        if obj.status == "canceled":
            canceled_by = obj.canceled_by or ""
            cancellation_date = obj.cancellation_date.strftime("%d/%m/%Y %H:%M") if obj.cancellation_date else ""
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
            return format_html(
                '<div><span>{}</span>: {}<br><span>{}</span>: {}</div>',
                _("Registered by"), created_by,
                _("Payment date"), created_at
            )

    payment_info.short_description = _("Payment info")

    def mass_payment_link(self, obj):
        if obj.mass_payment:
            url = reverse('admin:purchases_purchasemasspayment_change', args=[obj.mass_payment.id])
            return format_html('<a href="{}">{}</a>', url, f'Mass Payment {obj.mass_payment.id}')
        return "-"

    mass_payment_link.short_description = "Mass Payment"

    class Media:
        """
        Agrega JavaScript personalizado para mejorar la experiencia de edición de pagos.
        """
        js = ('js/admin/forms/packhouses/purchases/purchase_orders_payments.js',)

@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(ByOrganizationAdminMixin, admin.ModelAdmin):
    """
    Admin de Purchase Order que administra órdenes de compra.

    Gestiona entradas relacionadas como insumos, cargos, deducciones y pagos.
    Controla dinámicamente los botones de acción según el estado de la orden
    e integra validaciones de balance financiero en tiempo real.
    """

    form = PurchaseOrderForm
    list_display = ('ooid', 'provider', 'balance_payable', 'currency', 'status', 'created_at', 'user', 'generate_actions_buttons')
    fields = ('ooid', 'provider','payment_date', 'balance_payable', 'currency','tax', 'status', 'comments', 'save_and_send')
    list_filter = ('provider', 'currency', 'status')
    readonly_fields = ('ooid', 'status', 'balance_payable', 'created_at', 'user')
    inlines = [PurchaseOrderRequisitionSupplyInline, PurchaseOrderChargerInline, PurchaseOrderDeductionInline]

    def get_inline_instances(self, request, obj=None):
        """
        Agrega dinámicamente el inline de pagos solo si la orden está cerrada.
        """
        inline_instances = super().get_inline_instances(request, obj)
        if obj and obj.status == "closed":
            inline_instances.append(PurchaseOrderPaymentInline(self.model, self.admin_site))
        return inline_instances

    def generate_actions_buttons(self, obj):
        """
        Crea botones de acciones dinámicos:
        - Generar PDF de la orden.
        - Enviar orden a almacén.
        - Reabrir orden si ya fue enviada.
        - Aplicar pagos si está cerrada.
        """
        purchase_order_supply_pdf = reverse('purchase_order_supply_pdf', args=[obj.pk])

        tooltip_ready = _('Send to Storehouse')
        ready_url = reverse('set_purchase_order_supply_ready', args=[obj.pk])

        tooltip_open = _('Reopen this purchases order')
        open_url = reverse('set_purchase_order_supply_open', args=[obj.pk])

        tooltip_payment = _('Payment application')
        edit_url_with_anchor = reverse(
            "admin:{}_{}_change".format(obj._meta.app_label, obj._meta.model_name),
            args=[obj.pk]
        ) + "#payments-tab"

        set_purchase_order_supply_ready_button = ''
        if obj.status == 'open':
            set_purchase_order_supply_ready_button = format_html(
                '''<a class="button btn-ready-confirm" href="javascript:void(0);" data-toggle="tooltip" title="{}"
                   data-url="{}" data-message="{}" data-confirm="{}" data-cancel="{}" style="color:#4daf50;">
                    <i class="fa-solid fa-paper-plane"></i></a>''',
                tooltip_ready, ready_url, _('Are you sure you want to send this purchases order supply to Storehouse?'), _('Yes, send'), _('No')
            )

        set_purchase_order_supply_open_button = ''
        if obj.status == 'ready':
            set_purchase_order_supply_open_button = format_html(
                '''<a class="button btn-open-confirm" href="javascript:void(0);" data-toggle="tooltip" title="{}"
                   data-url="{}" data-message="{}" data-confirm="{}" data-cancel="{}" style="color:#ffc107;">
                    <i class="fa-solid fa-lock-open"></i></a>''',
                tooltip_open, open_url, _('Are you sure you want to reopen this purchases order?'), _('Yes, reopen'), _('No')
            )

        set_purchase_order_supply_payment_button = ''
        if obj.status == "closed":
            set_purchase_order_supply_payment_button = format_html(
                '''<a class="button" href="{}" data-toggle="tooltip" title="{}" style="color:#000;">
                    <i class="fa-solid fa-dollar-sign"></i></a>''',
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
            set_purchase_order_supply_payment_button, set_purchase_order_supply_ready_button, set_purchase_order_supply_open_button,
            purchase_order_supply_pdf, _('Generate Purchase Order Supply PDF')
        )

    generate_actions_buttons.short_description = _('Actions')
    generate_actions_buttons.allow_tags = True

    def get_readonly_fields(self, request, obj=None):
        """
        Hace campos de solo lectura si la orden ya fue cerrada, cancelada o enviada.
        """
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if not obj or (obj and obj.pk):
            if 'ooid' not in readonly_fields:
                readonly_fields.append('ooid')
        if obj and obj.status in ['closed', 'canceled', 'ready']:
            readonly_fields.extend([field for field in self.fields if hasattr(obj, field)])
        return readonly_fields

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Filtra proveedores disponibles según la organización activa.
        """
        if db_field.name == "provider" and hasattr(request, 'organization'):
            kwargs["queryset"] = Provider.objects.filter(organization=request.organization, is_enabled=True, category='supply_provider')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        """
        Oculta botones de agregar/editar/eliminar relacionados en el proveedor.
        """
        form = super().get_form(request, obj, **kwargs)
        if 'provider' in form.base_fields:
            for attr in ['can_add_related', 'can_change_related', 'can_delete_related', 'can_view_related']:
                setattr(form.base_fields['provider'].widget, attr, False)
        return form

    def save_model(self, request, obj, form, change):
        """
        Asigna automáticamente el usuario creador y permite enviar la orden directamente a almacén.
        """
        if not change:
            obj.user = request.user

        save_and_send = form.cleaned_data.get('save_and_send', False)
        if save_and_send and obj.status == 'open':
            obj.status = 'ready'

        super().save_model(request, obj, form, change)

    def get_urls(self):
        """
        Agrega ruta personalizada para cancelar pagos desde el admin.
        """
        urls = super().get_urls()
        custom_urls = [
            path('cancel-payment/<int:payment_id>/', self.admin_site.admin_view(self.cancel_payment), name='cancel_payment')
        ]
        return custom_urls + urls

    def cancel_payment(self, request, payment_id, *args, **kwargs):
        """
        Lógica para cancelar un pago específico y recalcular el balance automáticamente.
        Si el pago estaba asociado a un Mass Payment, se remueve de la relación y se recalcula el total.
        """
        try:
            payment = PurchaseOrderPayment.objects.get(id=payment_id)

            # Marcar el pago como cancelado
            payment.status = "canceled"
            payment.cancellation_date = timezone.now()
            payment.canceled_by = request.user
            payment.save(update_fields=["status", "cancellation_date", "canceled_by"])

            # Recalcular el balance de la orden de compra
            payment.purchase_order.recalculate_balance(save=True)

            # Si el pago pertenece a un Mass Payment, removerlo de la relación M2M
            if payment.mass_payment:
                mass_payment = payment.mass_payment

                # Quitar del M2M del Mass Payment
                mass_payment.purchase_order.remove(payment.purchase_order)

                # Recalcular el monto total del Mass Payment
                mass_payment.recalculate_amount()

                # Si el Mass Payment quedó sin órdenes, poner el monto a $0.00
                if not mass_payment.purchase_order.exists() and not mass_payment.service_order.exists():
                    mass_payment.amount = Decimal('0.00')
                    mass_payment.save(update_fields=["amount"])

            # Mensaje de éxito
            self.message_user(
                request,
                _(f"Payment canceled successfully. New balance payable: ${payment.purchase_order.balance_payable:.2f}"),
                level=messages.SUCCESS
            )
            purchase_order_id = payment.purchase_order.pk

        except PurchaseOrderPayment.DoesNotExist:
            self.message_user(request, _("Payment not found"), level=messages.ERROR)
            purchase_order_id = None

        # 🔄 Redirigir al tab de pagos
        redirect_url = reverse('admin:purchases_purchaseorder_change', args=[
            purchase_order_id]) + "#payments-tab" if purchase_order_id else request.path + "#payments-tab"
        return HttpResponseRedirect(redirect_url)

    def response_change(self, request, obj):
        """
        Recalcula el balance al guardar cambios, evitando balances negativos.
        """
        balance_data = obj.simulate_balance()
        if balance_data['balance'] < 0:
            if not hasattr(request, '_balance_error_shown'):
                self.message_user(
                    request,
                    _(f"Cannot save this order because the balance would be negative (${balance_data['balance']}). "
                      f"Supplies: ${balance_data['supplies_total']}, "
                      f"Taxes: ${balance_data['tax_amount']}, "
                      f"Charges: ${balance_data['charges_total']}, "
                      f"Deductions: ${balance_data['deductions_total']}, "
                      f"Payments: ${balance_data['payments_total']}")
                    ,
                    level=messages.ERROR
                )
            return HttpResponseRedirect(reverse('admin:purchases_purchaseorder_change', args=[obj.pk]))

        obj.balance_payable = balance_data['balance']
        obj.save(update_fields=['balance_payable'])
        return super().response_change(request, obj)

    def save_related(self, request, form, formsets, change):
        """
        Después de guardar los inlines, actualiza el balance de la orden.
        """
        super().save_related(request, form, formsets, change)

        purchase_order = form.instance
        balance_data = purchase_order.simulate_balance()

        if balance_data['balance'] < 0:
            if not hasattr(request, '_balance_error_shown'):
                request._balance_error_shown = True
                self.message_user(
                    request,
                    _(f"The final balance would be negative (${balance_data['balance']}). "
                      f"Total cost of supplies: ${balance_data['supplies_total']} "
                      f"+ Taxes: ${balance_data['tax_amount']} "
                      f"+ Charges: ${balance_data['charges_total']} "
                      f"- Payments: ${balance_data['payments_total']} "
                      f"- Deductions: ${balance_data['deductions_total']}")
                    ,
                    level=messages.ERROR
                )
            return

        purchase_order.balance_payable = balance_data['balance']
        purchase_order.save(update_fields=['balance_payable'])

    def save_formset(self, request, form, formset, change):
        """
        Valida balances antes de guardar cambios masivos de insumos, cargos, deducciones y pagos.

        Si el balance resultante sería negativo, cancela la operación y lanza advertencias.
        """
        model = formset.model
        purchase_order = form.instance

        if not hasattr(formset, 'cleaned_data'):
            return

        existing_qs = {obj.pk: obj for obj in model.objects.filter(purchase_order=purchase_order)}
        to_delete = []

        for form_data in formset.cleaned_data:
            if form_data.get('DELETE') and form_data.get('id'):
                obj = form_data['id']
                if obj.pk in existing_qs:
                    to_delete.append(existing_qs.pop(obj.pk))

        new_instances = formset.save(commit=False)

        for instance in new_instances:
            existing_qs[instance.pk] = instance

        combined = list(existing_qs.values())

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
                    _(f"The final balance would be negative (${balance}) "
                      f"Total cost of supplies: ${supplies_total} "
                      f"+ Taxes: ${tax_amount} "
                      f"+ Charges: ${charges_total} "
                      f"- Payments: ${payments_total} "
                      f"- Deductions: ${deductions_total}")
                    ,
                    level=messages.ERROR
                )
            return

        for obj in to_delete:
            obj.delete()

        for instance in new_instances:
            if not instance.pk:
                instance.created_by = request.user
            instance.save()

        formset.save_m2m()

    class Media:
        js = ('js/admin/forms/packhouses/purchases/purchase_orders.js',)

class ServiceOrderChargeInline(admin.StackedInline):
    """
    Inline del admin para agregar cargos adicionales a una orden de servicio.
    """

    model = ServiceOrderCharge
    fields = ('charge', 'amount')
    extra = 0

    def _get_parent_obj(self, request):
        parent_object_id = request.resolver_match.kwargs.get("object_id")
        if parent_object_id:
            try:
                return ServiceOrder.objects.get(id=parent_object_id)
            except ServiceOrder.DoesNotExist:
                return None
        return None

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        parent_obj = self._get_parent_obj(request)
        if parent_obj and parent_obj.status in ['canceled']:
            readonly_fields.extend([
                field.name for field in self.model._meta.fields
                if field.name not in readonly_fields
            ])
        return readonly_fields

    def has_delete_permission(self, request, obj=None):
        parent_obj = self._get_parent_obj(request)
        if parent_obj and parent_obj.status in ['canceled']:
            return False
        return super().has_delete_permission(request, obj)

class ServiceOrderDeductionInline(admin.StackedInline):
    """
    Inline del admin para agregar deducciones a una orden de servicio.
    """

    model = ServiceOrderDeduction
    fields = ('deduction', 'amount')
    extra = 0

    def _get_parent_obj(self, request):
        parent_object_id = request.resolver_match.kwargs.get("object_id")
        if parent_object_id:
            try:
                return ServiceOrder.objects.get(id=parent_object_id)
            except ServiceOrder.DoesNotExist:
                return None
        return None

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        parent_obj = self._get_parent_obj(request)
        if parent_obj and parent_obj.status in ['canceled']:
            readonly_fields.extend([
                field.name for field in self.model._meta.fields
                if field.name not in readonly_fields
            ])
        return readonly_fields

    def has_delete_permission(self, request, obj=None):
        parent_obj = self._get_parent_obj(request)
        if parent_obj and parent_obj.status in ['canceled']:
            return False
        return super().has_delete_permission(request, obj)

class ServiceOrderPaymentInline(admin.StackedInline):
    """
    Inline del admin para administrar pagos de órdenes de servicio.
    """

    model = ServiceOrderPayment
    form = ServiceOrderPaymentForm
    fields = (
        'cancel_button',
        'payment_kind',
        'payment_date',
        'mass_payment_link',
        'amount',
        'bank',
        'comments',
        'additional_inputs',
        'payment_info',
    )
    extra = 0
    can_delete = False
    readonly_fields = ('cancel_button', 'payment_info', 'mass_payment_link')

    def cancel_button(self, obj):
        if obj.pk and obj.status != "canceled":
            url = reverse('admin:cancel_service_payment', args=[obj.pk])
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
        if obj.status == "canceled":
            return format_html('<span class="canceled">{}</span>', _('Payment canceled'))

    cancel_button.short_description = ""

    def payment_info(self, obj):
        if not obj.pk:
            return ""

        created_by = obj.created_by or ""
        created_at = obj.created_at.strftime("%d/%m/%Y %H:%M") if obj.created_at else ""

        if obj.status == "canceled":
            canceled_by = obj.canceled_by or ""
            cancellation_date = obj.cancellation_date.strftime("%d/%m/%Y %H:%M") if obj.cancellation_date else ""
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
            return format_html(
                '<div><span>{}</span>: {}<br><span>{}</span>: {}</div>',
                _("Registered by"), created_by,
                _("Payment date"), created_at
            )

    payment_info.short_description = _("Payment info")

    def mass_payment_link(self, obj):
        if obj.mass_payment:
            url = reverse('admin:purchases_purchasemasspayment_change', args=[obj.mass_payment.id])
            return format_html('<a href="{}">{}</a>', url, f'Mass Payment {obj.mass_payment.id}')
        return "-"

    mass_payment_link.short_description = "Mass Payment"

    class Media:
        js = ('js/admin/forms/packhouses/purchases/service_orders_payments.js',)

@admin.register(ServiceOrder)
class ServiceOrderAdmin(DisableLinksAdminMixin, ByOrganizationAdminMixin, admin.ModelAdmin):
    form = ServiceOrderForm
    list_display = (
        'service', 'provider', 'category', 'status', 'total_cost', 'balance_payable', 'currency', 'payment_date'
    )
    fields = (
        'provider', 'service', 'category', 'start_date', 'end_date', 'batch',
        'payment_date', 'cost', 'currency', 'tax', 'total_cost', 'balance_payable', 'status'
    )
    list_filter = ('status', 'provider')
    search_fields = ('provider__name', 'service__name')
    readonly_fields = ('status', 'balance_payable', 'total_cost')
    inlines = [ServiceOrderChargeInline, ServiceOrderDeductionInline, ServiceOrderPaymentInline]

    def get_inline_instances(self, request, obj=None):
        inlines = super().get_inline_instances(request, obj)
        if obj and obj.status == "closed":
            inlines.append(ServiceOrderPaymentInline(self.model, self.admin_site))
        return inlines

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('cancel-service-payment/<int:payment_id>/', self.admin_site.admin_view(self.cancel_service_payment), name='cancel_service_payment')
        ]
        return custom_urls + urls

    def cancel_service_payment(self, request, payment_id, *args, **kwargs):
        """
        Lógica para cancelar un pago específico y recalcular el balance automáticamente.
        Si el pago estaba asociado a un Mass Payment, se remueve de la relación y se recalcula el total.
        """
        try:
            payment = ServiceOrderPayment.objects.get(id=payment_id)

            # Marcar el pago como cancelado
            payment.status = "canceled"
            payment.cancellation_date = timezone.now()
            payment.canceled_by = request.user
            payment.save(update_fields=["status", "cancellation_date", "canceled_by"])

            # Recalcular el balance de la orden de compra
            payment.service_order.recalculate_balance(save=True)

            # Si el pago pertenece a un Mass Payment, removerlo de la relación M2M
            if payment.mass_payment:
                mass_payment = payment.mass_payment

                # Quitar del M2M del Mass Payment
                mass_payment.service_order.remove(payment.service_order)

                # Recalcular el monto total del Mass Payment
                mass_payment.recalculate_amount()

                # Si el Mass Payment quedó sin órdenes, poner el monto a $0.00
                if not mass_payment.service_order.exists():
                    mass_payment.amount = Decimal('0.00')
                    mass_payment.save(update_fields=["amount"])

            # Mensaje de éxito
            self.message_user(
                request,
                _(f"Payment canceled successfully. New balance payable: ${payment.service_order.balance_payable:.2f}"),
                level=messages.SUCCESS
            )
            service_order_id = payment.service_order.pk

        except ServiceOrderPayment.DoesNotExist:
            self.message_user(request, _("Payment not found"), level=messages.ERROR)
            service_order_id = None

        # Redirigir al tab de pagos
        redirect_url = reverse('admin:purchases_serviceorder_change', args=[
            service_order_id]) + "#payments-tab" if service_order_id else request.path + "#payments-tab"
        return HttpResponseRedirect(redirect_url)

    def save_related(self, request, form, formsets, change):
        """
        Guarda los formsets asociados a la orden de servicio y luego
        recalcula total_cost y balance_payable con base en los objetos ya guardados.

        Este method es responsable de asegurar que el balance no sea negativo
        y de reflejar los valores contables correctos en la orden.
        """
        super().save_related(request, form, formsets, change)

        # Obtenemos la instancia ya guardada
        service_order = form.instance

        # Calculamos el balance real basado en objetos ya persistidos
        data = service_order.simulate_balance()

        # Si el balance resulta negativo, lanzamos advertencia (pero no bloqueamos guardado)
        if data['balance'] < 0:
            raise ValidationError(
                _(f"Cannot save the service order because the final balance would be negative (${data['balance']}). "
                  f"Cost: ${data['base_cost']} + Tax: ${data['tax_amount']} + Charges: ${data['charges_total']} "
                  f"- Deductions: ${data['deductions_total']} - Payments: ${data['payments_total']}.")
            )

        # Guardamos los valores contables definitivos en la orden de servicio
        service_order.total_cost = data['total_cost']
        service_order.balance_payable = data['balance']
        service_order.save(update_fields=["total_cost", "balance_payable"])

    def response_change(self, request, obj):
        data = obj.simulate_balance()

        if data['balance'] < 0:
            self.message_user(
                request,
                _(f"Cannot save this service order because the balance would be negative (${data['balance']})."),
                level=messages.ERROR
            )
            return HttpResponseRedirect(reverse('admin:purchases_serviceorder_change', args=[obj.pk]))

        obj.balance_payable = data['balance']
        obj.save(update_fields=['balance_payable'])
        return super().response_change(request, obj)

    def save_formset(self, request, form, formset, change):
        from .models import ServiceOrderCharge, ServiceOrderDeduction, ServiceOrderPayment

        model = formset.model
        service_order = form.instance

        # Verificamos que haya datos limpios del formset (evita errores en formularios vacíos)
        if not hasattr(formset, 'cleaned_data'):
            return

        # Obtenemos instancias existentes de este model relacionadas a la orden de servicio
        existing_qs = {obj.pk: obj for obj in model.objects.filter(service_order=service_order)}
        to_delete = []

        # Detectamos instancias marcadas para eliminación
        for form_data in formset.cleaned_data:
            if form_data.get('DELETE') and form_data.get('id'):
                obj = form_data['id']
                if obj.pk in existing_qs:
                    to_delete.append(existing_qs.pop(obj.pk))

        # Nuevas instancias que vienen del formset pero aún no han sido guardadas
        new_instances = formset.save(commit=False)

        for instance in new_instances:
            existing_qs[instance.pk] = instance

        # Lista completa de instancias que vamos a evaluar
        combined = list(existing_qs.values())

        # Cálculo de componentes del balance
        total_cost = Decimal(service_order.cost or 0)
        total_charges = Decimal('0.00')
        total_deductions = Decimal('0.00')
        total_payments = Decimal('0.00')

        for obj in combined:
            if isinstance(obj, ServiceOrderCharge):
                total_charges += Decimal(obj.amount or 0)
            elif isinstance(obj, ServiceOrderDeduction):
                total_deductions += Decimal(obj.amount or 0)
            elif isinstance(obj, ServiceOrderPayment) and obj.status != 'canceled':
                total_payments += Decimal(obj.amount or 0)

        tax_percent = Decimal(service_order.tax or 0)
        tax_decimal = tax_percent / Decimal('100.00')
        tax_amount = (total_cost * tax_decimal).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        balance = total_cost + tax_amount + total_charges - total_deductions - total_payments
        balance = balance.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        # Validación de integridad contable
        if balance < 0:
            if not hasattr(request, '_balance_error_shown'):
                request._balance_error_shown = True
                self.message_user(
                    request,
                    _(f"The final balance would be negative (${balance}). "
                      f"Cost: ${total_cost} + Tax: ${tax_amount} + Charges: ${total_charges} "
                      f"- Payments: ${total_payments} - Deductions: ${total_deductions}."),
                    level=messages.ERROR
                )
            return

        # Eliminamos instancias marcadas para borrado
        for obj in to_delete:
            obj.delete()

        # Guardamos nuevas instancias (asignando usuario si aplica)
        for instance in new_instances:
            if not instance.pk:
                instance.created_by = request.user
            instance.save()

        formset.save_m2m()

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "provider":
            kwargs["queryset"] = Provider.objects.filter(category="service_provider", is_enabled=True)

        elif db_field.name == "batch":
            now = timezone.now()
            one_month_ago = now - timedelta(days=30)

            # Filtramos los lotes por organización actual
            org = getattr(request, 'organization', None)
            if org:
                batches = Batch.objects.filter(organization=org).select_related('organization')
            else:
                batches = Batch.objects.all()

            def is_batch_valid(batch):
                last_status = batch.last_operational_status_change()
                if not last_status:
                    return False  # Si no hay historial quiere decir que esta pendiente, entonces pasa
                if last_status.new_status in ['canceled', 'pending']:
                    return False
                if last_status.new_status == 'finalized' and last_status.changed_at < one_month_ago:
                    return False
                return True

            valid_batches = [b.pk for b in batches if is_batch_valid(b)]
            kwargs["queryset"] = Batch.objects.filter(pk__in=valid_batches)

        elif db_field.name == "service":
            provider_id = request.GET.get('provider') or request.POST.get('provider')
            if provider_id:
                kwargs["queryset"] = Service.objects.filter(service_provider_id=provider_id, is_enabled=True)
            else:
                kwargs["queryset"] = Service.objects.none()

            # Preseleccionar en modo edición
            if request.resolver_match and request.resolver_match.url_name.endswith('_change'):
                obj_id = request.resolver_match.kwargs.get('object_id')
                if obj_id:
                    from .models import ServiceOrder
                    try:
                        service_order = ServiceOrder.objects.get(id=obj_id)
                        if service_order.service_id:
                            kwargs.setdefault('widget', db_field.formfield().widget)
                            kwargs['widget'].attrs.update({'data-initial-value': service_order.service_id})
                    except ServiceOrder.DoesNotExist:
                        pass

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('provider', 'service', 'organization')

    class Media:
        js = (
            'js/admin/forms/packhouses/purchases/serviceorder_dynamic_service.js',
        )

@admin.register(PurchaseMassPayment)
class PurchaseMassPaymentAdmin(DisableLinksAdminMixin, ByOrganizationAdminMixin, admin.ModelAdmin):
    """
    Admin para gestionar pagos masivos de órdenes de compra.

    Permite registrar pagos masivos y verificar su estado.
    """
    form = PurchaseMassPaymentForm
    fields = ('category', 'provider', 'currency', 'purchase_order', 'service_order', 'payment_kind',
              'additional_inputs', 'bank', 'payment_date', 'amount', 'comments')
    list_display = ('category','provider', 'amount', 'currency', 'payment_date', 'status', 'created_by')
    list_filter = ('category', 'status')
    readonly_fields = ('status', 'created_by', 'created_at', 'canceled_by', 'cancellation_date')

    def save_model(self, request, obj, form, change):
        """
        Guarda el objeto principal (sin relaciones M2M).
        """
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        """
        Se ejecuta después de guardar las relaciones M2M.
        Aquí ya podemos crear los pagos individuales
        """
        super().save_related(request, form, formsets, change)

        if not change:
            create_related_payments_and_update_balances(form.instance)

    class Media:
        js = ('js/admin/forms/packhouses/purchases/purchase_mass_payments.js',)
