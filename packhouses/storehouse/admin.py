from django.contrib import admin
from common.base.mixins import (
    ByOrganizationAdminMixin, ByProductForOrganizationAdminMixin,
    DisableInlineRelatedLinksMixin, ByUserAdminMixin
)
from .models import StorehouseEntry, StorehouseEntrySupply, InventoryTransaction, AdjustmentInventory
from packhouses.purchases.models import PurchaseOrderSupply
from .forms import StorehouseEntrySupplyInlineFormSet,AdjustmentInventoryForm, StorehouseEntryForm
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.contrib import messages
from decimal import Decimal
from django.db.models import F, Value, Sum, DecimalField
from django.db.models.functions import Coalesce
from django import forms
from .utils import get_source_for_quantity_fifo
from .reports import export_fifo_report
from .filters import OrganizationSupplyFilter
from common.base.utils import ReportExportAdminMixin, SheetExportAdminMixin, SheetReportExportAdminMixin
from packhouses.catalogs.views import basic_report
from .resources import InventoryTransactionResource




class StorehouseEntrySupplyInline(admin.StackedInline):
    """
    Admin Inline para StorehouseEntrySupply.

    Permite registrar las cantidades recibidas versus esperadas de insumos en una entrada de almacén.
    Ajusta los campos y permisos de edición automáticamente según el estado de la orden de compra relacionada.
    """

    model = StorehouseEntrySupply
    formset = StorehouseEntrySupplyInlineFormSet
    extra = 0
    can_delete = False

    def get_fields(self, request, obj=None):
        """
        Define qué campos mostrar dependiendo si la orden de compra está cerrada o no.

        - Si está cerrada, muestra solo cantidades y comentarios en modo lectura.
        - Si está abierta, permite editar cantidad inventariada.
        """
        if obj and obj.purchase_order.status == "closed":
            return (
                'purchase_order_supply',
                'expected_quantity',
                'received_quantity',
                'display_inventoried_quantity',
                'display_converted_inventoried_quantity',
                'comments',
            )
        else:
            return (
                'purchase_order_supply',
                'expected_quantity',
                'received_quantity',
                'inventoried_quantity',
                'comments',
            )

    def get_readonly_fields(self, request, obj=None):
        """
        Define campos de solo lectura dependiendo del estado de la orden de compra.

        - Cerrado: todos los campos son readonly.
        - Abierto: solo el campo de inventario convertido es readonly.
        """
        if obj and obj.purchase_order.status == "closed":
            return self.get_fields(request, obj)
        else:
            return ('display_converted_inventoried_quantity',)

    def display_inventoried_quantity(self, obj):
        """
        Devuelve la cantidad inventariada en unidades interpretables (metros, kilos, litros).
        """
        if not obj.pk:
            return ""
        usage_unit = obj.purchase_order_supply.requisition_supply.supply.kind.usage_discount_unit_category.unit_category
        if usage_unit == "cm":
            unit = "meters"
        elif usage_unit == "gr":
            unit = "kg"
        elif usage_unit == "ml":
            unit = "liters"
        else:
            unit = usage_unit
        return f"{obj.inventoried_quantity} {unit}"

    display_inventoried_quantity.short_description = _("Quantity in Inventory")

    def display_converted_inventoried_quantity(self, obj):
        """
        Devuelve la cantidad convertida equivalente, respetando la unidad de uso del insumo.
        """
        if not obj.pk:
            return ""
        usage_unit = obj.purchase_order_supply.requisition_supply.supply.kind.usage_discount_unit_category.unit_category
        return f"{obj.converted_inventoried_quantity} {usage_unit}"

    display_converted_inventoried_quantity.short_description = _("Equivalent in inventory for discount")


@admin.register(StorehouseEntry)
class StorehouseEntryAdmin(ByOrganizationAdminMixin):
    """
    Admin de StorehouseEntry.

    Permite registrar entradas de almacén ligadas a órdenes de compra,
    actualizando dinámicamente cantidades, precios y transacciones de inventario.
    También recalcula automáticamente el balance de la orden de compra al recibir insumos.
    """
    form = StorehouseEntryForm
    inlines = [StorehouseEntrySupplyInline]
    list_display = ('purchase_order', 'created_at', 'user')
    fields = ('purchase_order',)
    readonly_fields = ('created_at', 'user')

    def get_inline_instances(self, request, obj=None):
        """
        Si la orden de compra está cerrada, deshabilita agregar/eliminar líneas en la entrada.
        """
        inline_instances = super().get_inline_instances(request, obj)
        if obj and obj.purchase_order.status == "closed":
            for inline in inline_instances:
                inline.can_delete = False
                inline.extra = 0
        return inline_instances

    def get_readonly_fields(self, request, obj=None):
        """
        Hace que el campo 'purchase_order' sea de solo lectura si la entrada ya está cerrada.
        """
        ro_fields = list(self.readonly_fields)
        if obj and obj.purchase_order.status == "closed":
            ro_fields.append('purchase_order')
        return ro_fields

    def get_form(self, request, obj=None, **kwargs):
        """
        Elimina los botones de relación (add/change/delete) para evitar crear órdenes nuevas desde aquí.
        """
        form = super().get_form(request, obj, **kwargs)
        for field in form.base_fields.values():
            widget = getattr(field, 'widget', None)
            if widget:
                widget.can_add_related = False
                widget.can_change_related = False
                widget.can_delete_related = False
                widget.can_view_related = False
        return form

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Limita las órdenes de compra disponibles solo a las que están en estado 'ready'.
        """
        if db_field.name == 'purchase_order':
            kwargs['queryset'] = db_field.remote_field.model.objects.filter(status='ready')
            if hasattr(request, 'organization'):
                kwargs['queryset'] = kwargs['queryset'].filter(organization=request.organization)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        """
        Asigna automáticamente el usuario creador si es una nueva entrada.
        """
        if not change:
            obj.user = request.user
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        """
        Al guardar los StorehouseEntrySupply:
        - Actualiza cantidades recibidas en la orden de compra.
        - Crea transacciones de inventario por cada insumo.
        - Recalcula el balance de la PurchaseOrder para reflejar lo realmente recibido.
        """
        storehouse_entry = form.instance

        # Guardamos primero relaciones normales
        super().save_related(request, form, formsets, change)

        for entry_supply in list(storehouse_entry.storehouseentrysupply_set.all()):
            pos = entry_supply.purchase_order_supply

            if entry_supply.received_quantity == 0 and entry_supply.inventoried_quantity == 0:
                # Borra si no se recibió nada
                entry_supply.delete()
                if not pos.storehouseentrysupply_set.exists():
                    pos.delete()
                continue

            # Actualiza datos reales en el supply relacionado
            pos.quantity = entry_supply.received_quantity
            pos.total_price = entry_supply.received_quantity * pos.unit_price
            pos.is_in_inventory = True
            pos.save(update_fields=['quantity', 'total_price', 'is_in_inventory'])

            # Registra la entrada en inventario
            InventoryTransaction.objects.create(
                storehouse_entry_supply=entry_supply,
                supply=entry_supply.purchase_order_supply.requisition_supply.supply,
                transaction_kind='inbound',
                transaction_category='purchase',
                quantity=entry_supply.converted_inventoried_quantity,
                created_by=request.user,
                organization=storehouse_entry.organization,
            )

        # Refrescamos el estado actual de la orden de compra
        storehouse_entry.purchase_order.refresh_from_db()

        try:
            # Recalcula el balance tomando en cuenta lo efectivamente recibido
            storehouse_entry.purchase_order.recalculate_balance(save=True)

            self.message_user(
                request,
                _(f"Purchase Order balance updated successfully based on received quantities."),
                level=messages.SUCCESS
            )

        except ValidationError as e:
            self.message_user(
                request,
                e.message,
                level=messages.ERROR
            )
            return

    class Media:
        js = ('js/admin/forms/packhouses/storehouse/storehouse_entry.js',)


@admin.register(AdjustmentInventory)
class AdjustmentInventoryAdmin(ByOrganizationAdminMixin):
    """
    Admin para gestionar ajustes manuales de inventario.

    Permite registrar entradas o salidas extraordinarias de insumos,
    asignando automáticamente la organización y el usuario actual en el proceso de guardado.
    """

    form = AdjustmentInventoryForm
    list_display  = ('transaction_kind', 'transaction_category', 'supply', 'quantity', 'created_at')
    fields = ('transaction_kind', 'transaction_category', 'supply', 'quantity', 'organization', 'created_at')
    readonly_fields = ('created_at',)

    def get_form(self, request, obj=None, **kwargs):
        """
        Personaliza el formulario para:
        - Forzar la organización del request.
        - Ocultar el campo 'organization' al usuario.
        - Inyectar el usuario actual para su uso en el form.save().
        """
        form = super().get_form(request, obj, **kwargs)

        if hasattr(request, 'organization'):
            form.request_organization = request.organization

        if 'organization' in form.base_fields:
            form.base_fields['organization'].initial = request.organization
            form.base_fields['organization'].widget = forms.HiddenInput()

        form._request_user = request.user

        return form



@admin.register(InventoryTransaction)
class InventoryTransactionAdmin(SheetReportExportAdminMixin,ByOrganizationAdminMixin):
    """
    Admin de transacciones de inventario.

    Se configura completamente en modo lectura: no permite crear, editar ni eliminar registros manualmente.
    Incluye exportación de reportes FIFO para movimientos de salida.
    """
    report_function = staticmethod(basic_report)
    resource_classes = [InventoryTransactionResource]
    list_display = ('supply', 'transaction_kind', 'transaction_category', 'quantity', 'created_at', 'created_by')
    list_filter = (OrganizationSupplyFilter, 'transaction_kind', 'transaction_category',)
    #actions = [export_fifo_report]
    ordering = ('created_at',)

    def has_add_permission(self, request):
        """
        Bloquea la opción de crear nuevas transacciones manualmente.
        """
        return False

    def has_change_permission(self, request, obj=None):
        """
        Bloquea la edición manual de transacciones ya registradas.
        """
        return False

    def has_delete_permission(self, request, obj=None):
        """
        Bloquea la eliminación manual de transacciones.
        """
        return False

    def get_readonly_fields(self, request, obj=None):
        """
        Hace todos los campos de la transacción de solo lectura en el admin.
        """
        return [field.name for field in self.model._meta.fields]
