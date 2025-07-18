from django.contrib import admin
from wagtail.admin.templatetags.wagtailadmin_tags import status

from common.profiles.models import UserProfile
from .models import (Requisition, RequisitionSupply, PurchaseOrder,
                     PurchaseOrderSupply, PurchaseOrderCharge, PurchaseOrderDeduction,
                     PurchaseOrderPayment, ServiceOrder, ServiceOrderCharge, ServiceOrderDeduction,
                     ServiceOrderPayment, PurchaseMassPayment, FruitPurchaseOrder, FruitPurchaseOrderReceipt, FruitPurchaseOrderPayment
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
                    ServiceOrderForm, ServiceOrderPaymentForm, PurchaseMassPaymentForm, FruitOrderPaymentForm,
                    FruitPaymentInlineFormSet, FruitPurchaseOrderReceiptForm, FruitPurchaseOrderReceiptInlineFormset
                    )
from django.utils.html import format_html, format_html_join, mark_safe
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
from django.http import JsonResponse
from .views import CancelMassPaymentView
from common.mixins import ReadOnlyIfCanceledMixin



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


class PurchaseOrderChargerInline(ReadOnlyIfCanceledMixin, admin.StackedInline):
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

    def has_delete_permission(self, request, obj=None):
        """
        Impide eliminar cargos si la orden está cancelada.
        """
        parent_obj = self._get_parent_obj(request)
        if parent_obj and parent_obj.status in ['canceled']:
            return False
        return super().has_delete_permission(request, obj)

class PurchaseOrderDeductionInline(ReadOnlyIfCanceledMixin,admin.StackedInline):
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
        'bank',
        'additional_inputs',
        'amount',
        'payment_date',
        'proof_of_payment',
        'mass_payment_link',
        'comments',
        'payment_info',
    )
    extra = 0
    can_delete = False
    readonly_fields = ('cancel_button',
                       'payment_info',
                       'mass_payment_link')

    def get_formset(self, request, obj=None, **kwargs):
        """
        Sobreescribe el metodo para eliminar el campo 'proof_of_payment' en modo edición.
        """
        formset = super().get_formset(request, obj, **kwargs)

        # Sobreescribimos el metodo `__init__` del formset de manera correcta
        original_init = formset.__init__

        def formset_init(instance_self, *args, **kargs):
            original_init(instance_self, *args, **kargs)

            # Recorremos los formularios para identificar si ya tienen un ID (es decir, ya existen en la DB)
            for form in instance_self.forms:
                if form.instance.pk:  # Si el objeto ya existe (tiene ID en la BD)
                    if 'proof_of_payment' in form.fields:
                        form.fields['proof_of_payment'].widget.attrs['disabled'] = True

        formset.__init__ = formset_init
        return formset

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
            return format_html('<a href="{}">{}</a>', url, f'Mass Payment {obj.mass_payment.ooid}')
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
    list_display = ('ooid', 'provider', 'total_cost', 'balance_payable', 'currency', 'status', 'created_at', 'user', 'generate_actions_buttons')
    fields = ('ooid', 'provider','payment_date', 'currency','tax', 'status', 'total_cost', 'balance_payable', 'comments', 'save_and_send')
    list_filter = ('provider', 'currency', 'status')
    readonly_fields = ('ooid', 'status', 'balance_payable', 'created_at', 'user', 'total_cost')
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
            with transaction.atomic():
                payment = PurchaseOrderPayment.objects.select_for_update().get(id=payment_id)

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
        except Exception as e:
            # En caso de error, se revierte la transacción completa
            transaction.set_rollback(True)
            self.message_user(
                request,
                _(f"An error occurred while canceling the payment: {str(e)}"),
                level=messages.ERROR
            )
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

        # Actualizamos el balance y el total_cost
        purchase_order.balance_payable = balance_data['balance']
        purchase_order.total_cost = balance_data['total_cost']
        purchase_order.save(update_fields=['balance_payable', 'total_cost'])

    def save_formset(self, request, form, formset, change):
        """
        Valida balances antes de guardar cambios masivos de insumos, cargos, deducciones y pagos.

        Si el balance resultante sería negativo, cancela la operación y lanza advertencias.
        También se actualiza el `total_cost` correctamente, incluyendo:
        - Supplies
        - Charges
        - Taxes
        - Deductions
        - Pagos realizados (excepto los cancelados)
        """
        model = formset.model
        purchase_order = form.instance

        if not hasattr(formset, 'cleaned_data'):
            return

        # Se obtienen los objetos que ya existen en la base de datos
        existing_qs = {obj.pk: obj for obj in model.objects.filter(purchase_order=purchase_order)}
        to_delete = []

        for form_data in formset.cleaned_data:
            if form_data.get('DELETE') and form_data.get('id'):
                obj = form_data['id']
                if obj.pk in existing_qs:
                    to_delete.append(existing_qs.pop(obj.pk))

        # Nuevas instancias (no están guardadas en la BD todavía)
        new_instances = formset.save(commit=False)

        # Se actualiza el diccionario para manejar tanto existentes como nuevas
        for instance in new_instances:
            existing_qs[instance.pk] = instance

        # Lista completa de objetos a evaluar (tanto guardados como nuevos)
        combined = list(existing_qs.values())

        # --- Cálculo de componentes actuales en la BD ---
        total_supplies = purchase_order.purchaseordersupply_set.aggregate(
            total=models.Sum('total_price')
        )['total'] or Decimal('0.00')

        total_charges = purchase_order.purchaseordercharge_set.aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')

        total_deductions = purchase_order.purchaseorderdeduction_set.aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')

        total_payments = purchase_order.purchaseorderpayment_set.exclude(
            status='canceled'
        ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00')

        # Solo sumamos los objetos del formset si son NUEVOS o han cambiado,
        # para evitar duplicidad con los ya guardados.
        for obj in combined:
            if isinstance(obj, PurchaseOrderSupply):
                total_supplies += Decimal(obj.total_price or 0)
            elif isinstance(obj, PurchaseOrderCharge):
                total_charges += Decimal(obj.amount or 0)
            elif isinstance(obj, PurchaseOrderDeduction):
                total_deductions += Decimal(obj.amount or 0)
            elif isinstance(obj, PurchaseOrderPayment) and obj.status != 'canceled':
                if not obj.pk:  # Solo los que son nuevos (aún no tienen ID en la BD)
                    total_payments += Decimal(obj.amount or 0)

        # Cálculo de los impuestos y el costo total
        tax_percent = Decimal(purchase_order.tax or 0)
        tax_decimal = tax_percent / Decimal('100.00')
        tax_amount = (total_supplies * tax_decimal).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        # Cálculo del total cost y balance
        total_cost = total_supplies + tax_amount + total_charges - total_deductions
        total_cost = total_cost.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        balance = total_cost - total_payments
        balance = balance.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        # Validación de integridad contable
        if balance < 0:
            if not hasattr(request, '_balance_error_shown'):
                request._balance_error_shown = True
                self.message_user(
                    request,
                    _(f"The final balance would be negative (${balance}) "
                      f"Total cost of supplies: ${total_supplies} "
                      f"+ Taxes: ${tax_amount} "
                      f"+ Charges: ${total_charges} "
                      f"- Payments: ${total_payments} "
                      f"- Deductions: ${total_deductions}"),
                    level=messages.ERROR
                )
            return

        # Eliminación de instancias marcadas para borrar
        for obj in to_delete:
            obj.delete()

        # Guardado de nuevas instancias
        for instance in new_instances:
            if not instance.pk:
                instance.created_by = request.user
            instance.save()

        formset.save_m2m()

        # Actualización del modelo principal
        purchase_order.total_cost = total_cost
        purchase_order.balance_payable = balance
        purchase_order.save(update_fields=['total_cost', 'balance_payable'])

    class Media:
        js = ('js/admin/forms/packhouses/purchases/purchase_orders.js',)

class ServiceOrderChargeInline(ReadOnlyIfCanceledMixin, admin.StackedInline):
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

    def has_delete_permission(self, request, obj=None):
        parent_obj = self._get_parent_obj(request)
        if parent_obj and parent_obj.status in ['canceled']:
            return False
        return super().has_delete_permission(request, obj)

class ServiceOrderDeductionInline(ReadOnlyIfCanceledMixin, admin.StackedInline):
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
        'bank',
        'additional_inputs',
        'amount',
        'payment_date',
        'proof_of_payment',
        'mass_payment_link',
        'comments',
        'payment_info',
    )
    extra = 0
    can_delete = False
    readonly_fields = ('cancel_button', 'payment_info', 'mass_payment_link')

    def get_formset(self, request, obj=None, **kwargs):
        """
        Sobreescribe el metodo para eliminar el campo 'proof_of_payment' en modo edición.
        """
        formset = super().get_formset(request, obj, **kwargs)

        # Sobreescribimos el metodo `__init__` del formset de manera correcta
        original_init = formset.__init__

        def formset_init(instance_self, *args, **kargs):
            original_init(instance_self, *args, **kargs)

            # Recorremos los formularios para identificar si ya tienen un ID (es decir, ya existen en la DB)
            for form in instance_self.forms:
                if form.instance.pk:  # Si el objeto ya existe (tiene ID en la BD)
                    if 'proof_of_payment' in form.fields:
                        form.fields['proof_of_payment'].widget.attrs['disabled'] = True

        formset.__init__ = formset_init
        return formset

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
            return format_html('<a href="{}">{}</a>', url, f'Mass Payment {obj.mass_payment.ooid}')
        return "-"

    mass_payment_link.short_description = "Mass Payment"

    class Media:
        js = ('js/admin/forms/packhouses/purchases/service_orders_payments.js',)

@admin.register(ServiceOrder)
class ServiceOrderAdmin(DisableLinksAdminMixin, ByOrganizationAdminMixin, admin.ModelAdmin):
    form = ServiceOrderForm
    list_display = (
        'ooid', 'provider', 'service', 'category', 'total_cost', 'balance_payable',
        'currency', 'status', 'payment_date',
    )
    fields = (
        'ooid','provider', 'service', 'category', 'start_date', 'end_date', 'batch',
        'payment_date', 'cost', 'currency', 'tax', 'total_cost', 'balance_payable', 'status', 'created_at', 'created_by',
    )
    list_filter = ('status', 'provider')
    search_fields = ('provider__name', 'service__name')
    readonly_fields = ('ooid','status', 'balance_payable', 'total_cost', 'created_at', 'created_by')
    inlines = [ServiceOrderChargeInline, ServiceOrderDeductionInline, ServiceOrderPaymentInline]

    def get_readonly_fields(self, request, obj=None):
        """
        Si el objeto ya existe, se marcan todos los campos como readonly.
        """
        if obj:
            return [field.name for field in self.model._meta.fields]
        return super().get_readonly_fields(request, obj)

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
            with transaction.atomic():
                payment = ServiceOrderPayment.objects.select_for_update().get(id=payment_id)

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
        except Exception as e:
            # Si ocurre un error, se revierte la transacción completa
            transaction.set_rollback(True)
            self.message_user(request, _(f"An error occurred while canceling the payment: {str(e)}"),
                              level=messages.ERROR)
            service_order_id = None

        # Redirigir al tab de pagos
        redirect_url = reverse('admin:purchases_serviceorder_change', args=[
            service_order_id]) + "#payments-tab" if service_order_id else request.path + "#payments-tab"
        return HttpResponseRedirect(redirect_url)

    def save_model(self, request, obj, form, change):
        """
        Guarda el objeto principal (sin relaciones M2M).
        """
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

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
                batches = Batch.objects.filter(
                    organization=org,
                    parent__isnull=True
                ).select_related('organization')
            else:
                batches = Batch.objects.all()

            def is_batch_valid(batch):
                last_status = batch.last_status_change()
                if not last_status:
                    return False  # Si no hay historial quiere decir que esta pendiente (open), entonces pasa
                if last_status.new_status in ['canceled', 'open']:
                    return False
                if last_status.new_status == 'closed' and last_status.created_at < one_month_ago:
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

    Permite registrar pagos masivos, verificar su estado y realizar acciones como
    imprimir reporte y cancelar el pago masivo.
    """
    form = PurchaseMassPaymentForm
    fields = ('cancel_status','ooid', 'category', 'provider', 'currency', 'purchase_order', 'service_order', 'payment_kind',
              'bank', 'additional_inputs', 'amount', 'payment_date', 'proof_of_payment', 'comments')
    list_display = (
    'ooid', 'category', 'provider', 'amount', 'currency', 'payment_date', 'status', 'created_by', 'generate_actions_buttons')
    list_filter = ('category', 'status')
    readonly_fields = ('ooid', 'status', 'created_by', 'created_at', 'canceled_by', 'cancellation_date', 'cancel_status')

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
        """
        super().save_related(request, form, formsets, change)

        if not change:
            create_related_payments_and_update_balances(form.instance)

    def generate_actions_buttons(self, obj):
        """
        Genera los botones de "Imprimir Reporte" y "Cancelar Pago".
        """
        #mass_payment_pdf = reverse('mass_payment_pdf', args=[obj.pk])
        mass_payment_pdf = '#'
        tooltip_mass_payment_pdf = _('Generate Mass Payment PDF')
        cancel_button_text = _('No')

        # Botón de Imprimir Reporte
        print_button = format_html(
            '''<a class="button" href="{}" target="_blank" data-toggle="tooltip" title="{}">
                <i class="fa-solid fa-print"></i>
            </a>''',
            mass_payment_pdf, tooltip_mass_payment_pdf
        )

        tooltip_cancel_masspayment = _('Cancel Mass Payment')
        cancel_url = reverse('set_masspayment_cancel', args=[obj.pk])
        confirm_cancel_text = _('Are you sure you want to cancel this mass payment?')
        confirm_button_text = _('Yes, cancel')

        # Botón de Cancelar Pago (solo si no está cancelado)
        set_masspayment_cancel_button = ''
        if obj.status != 'canceled':
            set_masspayment_cancel_button = format_html(
                '''
                <a class="button btn-cancel-confirm" href="javascript:void(0);" data-toggle="tooltip" title="{}"
                   data-url="{}" data-message="{}" data-confirm="{}" data-cancel="{}" style="color:red;">
                    <i class="fa-solid fa-ban"></i>
                </a>
                ''',
                tooltip_cancel_masspayment, cancel_url, confirm_cancel_text, confirm_button_text, cancel_button_text
            )



        return format_html('{}{}', print_button, set_masspayment_cancel_button)

    generate_actions_buttons.short_description = _("Actions")
    generate_actions_buttons.allow_tags = True

    def get_urls(self):
        """
        Agrega las URLs personalizadas para cancelar e imprimir.
        """
        urls = super().get_urls()
        custom_urls = [
            path('cancel-mass-payment/<int:pk>/', self.admin_site.admin_view(CancelMassPaymentView.as_view()),
                 name='set_masspayment_cancel'),
        ]
        return custom_urls + urls

    def print_mass_payment(self, request, pk, *args, **kwargs):
        """
        Lógica para generar el reporte del Mass Payment.
        """
        # TODO: lógica para generar el reporte.
        self.message_user(request, f"Report generation for Mass Payment {pk} is not implemented yet.",
                          level=messages.INFO)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    def cancel_status(self, obj):
        """
        Genera un link dinámico para cancelar el Mass Payment si no está cancelado.
        Si está cancelado, muestra un mensaje visual.
        """
        if not obj.pk:
            return ""

        if obj.status == "canceled":
            # Si está cancelado, muestra el texto de cancelado
            return format_html('<span class="canceled">{}</span>', _('Payment canceled'))
        else:
            # Si no está cancelado, genera el enlace
            url = reverse('set_masspayment_cancel', args=[obj.pk])
            title = _("Are you sure you want to cancel this mass payment?")
            confirm_text = _("Yes, cancel")
            cancel_text = _("No")
            button_label = _("Cancel Mass Payment")

            return format_html(
                '''
                <a class="button btn-cancel-confirm" href="javascript:void(0);" data-toggle="tooltip"
                   title="{0}" data-url="{1}" data-message="{2}" data-confirm="{3}" data-cancel="{4}">
                    {5}
                </a>
                ''',
                title,
                url,
                title,
                confirm_text,
                cancel_text,
                button_label
            )

    cancel_status.short_description = ""

    class Media:
        js = ('js/admin/forms/packhouses/purchases/purchase_mass_payments.js',)


class FruitPurchaseOrderReceiptInline(DisableInlineRelatedLinksMixin, admin.StackedInline):
    """
    Inline del admin para agregar recibos a una orden de compra de frutas.
    No permite agregar nuevos si la orden está cerrada o cancelada.
    """
    model = FruitPurchaseOrderReceipt
    form = FruitPurchaseOrderReceiptForm
    formset = FruitPurchaseOrderReceiptInlineFormset
    readonly_fields = ('ooid','status', 'created_at', 'created_by', 'created_at', 'cancellation_date', 'canceled_by')
    extra = 0
    min_num = 1
    can_delete = False

    def get_extra(self, request, obj=None, **kwargs):
        """
        No agrega formularios vacíos si la orden está cerrada o cancelada.
        """
        if obj and obj.status in ['closed', 'canceled']:
            return 0
        return super().get_extra(request, obj, **kwargs)

    def has_add_permission(self, request, obj=None):
        """
        No permite agregar nuevos recibos si la orden está cerrada o cancelada.
        """
        if obj and obj.status in ['closed', 'canceled']:
            return False
        return super().has_add_permission(request, obj)

    class Media:
        js = ('js/admin/forms/packhouses/purchases/fruit_purchase_order_receipt.js',)


class FruitPaymentInline(DisableInlineRelatedLinksMixin, admin.StackedInline):
    """
    Inline del admin para agregar pagos a una orden de compra de frutas.
    """
    model = FruitPurchaseOrderPayment
    form = FruitOrderPaymentForm
    formset = FruitPaymentInlineFormSet
    fields = (
        'cancel_button',
        'fruit_purchase_order_receipt',
        'amount',
        'payment_kind',
        'bank',
        'additional_inputs',
        'payment_date',
        'proof_of_payment',
        'comments',
        'payment_info',
    )
    extra = 0
    can_delete = False
    readonly_fields = ('cancel_button', 'payment_info')

    def save_model(self, request, obj, form, change):
        """
        Guarda el objeto principal (sin relaciones M2M).
        """
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        """
        Filtra los recibos mostrados en el campo fruit_purchase_order_receipt
        para que solo muestre los que pertenecen a la orden padre.
        """
        field = super().formfield_for_foreignkey(db_field, request, **kwargs)

        if db_field.name == 'fruit_purchase_order_receipt' and hasattr(request, 'fruit_purchase_order_obj'):
            fruit_order = request.fruit_purchase_order_obj
            if fruit_order and fruit_order.pk:
                field.queryset = field.queryset.filter(fruit_purchase_order=fruit_order)
            else:
                field.queryset = field.queryset.none()

        return field

    def get_formset(self, request, obj=None, **kwargs):
        """
        Pasa la orden de compra al formset para filtrar correctamente los receipts.
        También desactiva proof_of_payment si el payment ya existe.
        """
        kwargs['formset'] = self.formset
        base_formset_class = super().get_formset(request, obj, **kwargs)

        class CustomFormset(base_formset_class):
            def __init__(self2, *args, **kwargs2):
                kwargs2['fruit_purchase_order'] = obj
                super().__init__(*args, **kwargs2)

                for form in self2.forms:
                    if form.instance.pk and 'proof_of_payment' in form.fields:
                        form.fields['proof_of_payment'].widget.attrs['disabled'] = True

        return CustomFormset

    def cancel_button(self, obj):
        if obj.pk and obj.status != "canceled":
            url = reverse('admin:cancel_fruit_payment', args=[obj.pk])
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

    def get_extra(self, request, obj=None, **kwargs):
        """
        No agrega formularios vacíos si la orden está cerrada o cancelada.
        """
        if obj and obj.status in ['closed', 'canceled']:
            return 0
        return super().get_extra(request, obj, **kwargs)

    def has_add_permission(self, request, obj=None):
        """
        No permite agregar nuevos recibos si la orden está cerrada o cancelada.
        """
        if obj and obj.status in ['closed', 'canceled']:
            return False
        return super().has_add_permission(request, obj)

    class Media:
        js = ('js/admin/forms/packhouses/purchases/fruit_orders_payments.js',)


@admin.register(FruitPurchaseOrder)
class FruitPurchaseOrderAdmin(DisableLinksAdminMixin, ByOrganizationAdminMixin, admin.ModelAdmin):
    """
    Admin para gestionar órdenes de compra de frutas.
    Permite registrar órdenes de compra de fruta, verificar su estado y realizar acciones como
    imprimir reporte y cancelar la orden.
    """
    list_display = (
        'ooid', 'batch', 'category', 'status', 'created_at', 'created_by'
    )
    fields = (
        'ooid','category', 'batch', 'status', 'created_at', 'created_by',
    )
    list_filter = ('category','status')
    readonly_fields = ('ooid','status', 'created_at', 'created_by')
    inlines = [FruitPurchaseOrderReceiptInline, FruitPaymentInline ]

    def get_formset(self, request, obj=None, **kwargs):
        """
        Inyecta el objeto padre en el request para que los inlines puedan filtrar
        según la orden de compra actual.
        """
        request.fruit_purchase_order_obj = obj
        return super().get_formset(request, obj, **kwargs)

    def get_readonly_fields(self, request, obj=None):
        readonly = list(super().get_readonly_fields(request, obj))

        if obj and (obj.fruitpurchaseorderreceipt_set.exists() or obj.fruitpurchaseorderpayment_set.exists()):
            readonly.append("batch")
            readonly.append("category")

        return readonly

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Filtra proveedores disponibles según la organización activa y el estado del lote (batch).
        """
        if db_field.name == "batch" and hasattr(request, 'organization'):
            org = getattr(request, 'organization', None)
            if org:
                batches = Batch.objects.filter(
                    organization=org,
                    parent__isnull=True
                ).select_related('organization')
            else:
                batches = Batch.objects.all()

            def is_batch_valid(batch):
                last_status = batch.last_status_change()
                if not last_status:
                    return False
                if last_status.new_status in ['canceled', 'open']:
                    return False
                if last_status.new_status == 'closed':
                    return False
                return True

            # Batches ya usados por este modelo
            used_batch_ids = self.model.objects.values_list('batch_id', flat=True)

            # Filtra por estado y uso
            valid_batch_ids = [
                b.pk for b in batches
                if is_batch_valid(b) and b.pk not in used_batch_ids
            ]

            kwargs["queryset"] = Batch.objects.filter(pk__in=valid_batch_ids)

            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)

            def label_from_instance(obj):
                provider = obj.harvest_product_provider or obj.yield_producer
                provider_str = str(provider) if provider else "No provider"
                date_str = obj.incomingproduct.scheduleharvest.created_at.strftime(
                    '%d/%m/%Y') if obj.incomingproduct and obj.incomingproduct.scheduleharvest else "No date"
                return f"{obj.ooid} :: {provider_str} - {date_str}"

            formfield.label_from_instance = label_from_instance
            return formfield

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        """
        Guarda el objeto principal (sin relaciones M2M).
        """
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        """
        Maneja el guardado de formsets personalizados.
        Asigna automáticamente el usuario que creó los registros cuando se agregan desde el inline.
        """
        if formset.model == FruitPurchaseOrderPayment:
            for inline_form in formset.forms:
                try:
                    instance = inline_form.save(commit=False)
                    instance.full_clean()
                except ValidationError as e:
                    inline_form.add_error(None, e)
                    return

            instances = formset.save(commit=False)
            for obj in instances:
                if not obj.pk and hasattr(obj, 'created_by'):
                    obj.save(user=request.user)  # Pasa el usuario aquí
                else:
                    obj.save()
            formset.save_m2m()

            for obj in formset.deleted_objects:
                obj.delete()
            return

        if formset.model == FruitPurchaseOrderReceipt:
            instances = formset.save(commit=False)
            for obj in instances:
                if not obj.pk:
                    obj.created_by = request.user
                obj.save()
            for obj in formset.deleted_objects:
                obj.delete()
            formset.save_m2m()
            return

        return formset.save()

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('cancel-fruit-payment/<int:payment_id>/', self.admin_site.admin_view(self.cancel_fruit_payment), name='cancel_fruit_payment')
        ]
        return custom_urls + urls

    def cancel_fruit_payment(self, request, payment_id, *args, **kwargs):
        """
        Cancela un pago de una orden de compra de fruta y recalcula el balance del recibo asociado.
        """
        fruit_order_id = None

        try:
            with transaction.atomic():
                payment = FruitPurchaseOrderPayment.objects.select_for_update().get(id=payment_id)

                # Marcar como cancelado
                payment.status = "canceled"
                payment.cancellation_date = timezone.now()
                payment.canceled_by = request.user
                payment.save(update_fields=["status", "cancellation_date", "canceled_by"])

                self.message_user(
                    request,
                    _(f"Payment canceled successfully. New balance payable: ${payment.fruit_purchase_order_receipt.balance_payable:.2f}"),
                    level=messages.SUCCESS
                )

                fruit_order_id = payment.fruit_purchase_order_id

        except FruitPurchaseOrderPayment.DoesNotExist:
            self.message_user(request, _("Payment not found."), level=messages.ERROR)

        except Exception as e:
            transaction.set_rollback(True)
            self.message_user(
                request,
                _(f"An error occurred while canceling the payment: {str(e)}"),
                level=messages.ERROR
            )

        # Redirigir al tab de pagos
        redirect_url = (
            reverse("admin:purchases_fruitpurchaseorder_change", args=[fruit_order_id]) + "#payments-tab"
            if fruit_order_id else request.path + "#payments-tab"
        )
        return HttpResponseRedirect(redirect_url)
