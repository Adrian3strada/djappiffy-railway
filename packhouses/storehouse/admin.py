from django.contrib import admin
from common.base.mixins import (
    ByOrganizationAdminMixin, ByProductForOrganizationAdminMixin,
    DisableInlineRelatedLinksMixin, ByUserAdminMixin
)
from .models import StorehouseEntry, StorehouseEntrySupply, InventoryTransaction, AdjustmentInventory
from packhouses.purchases.models import PurchaseOrderSupply
from .forms import StorehouseEntrySupplyInlineFormSet,AdjustmentInventoryForm
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.contrib import messages
from decimal import Decimal
from django.db.models import F, Value, Sum, DecimalField
from django.db.models.functions import Coalesce
from django import forms
from .utils import get_fifo_source_for_quantity
from .reports import export_fifo_report






class StorehouseEntrySupplyInline(admin.StackedInline):
    model = StorehouseEntrySupply
    formset = StorehouseEntrySupplyInlineFormSet
    extra = 0
    can_delete = False

    def get_fields(self, request, obj=None):
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
        if obj and obj.purchase_order.status == "closed":
            # Si está cerrado, todos los campos son de solo lectura (incluyendo los métodos display)
            return self.get_fields(request, obj)
        else:
            # En modo edición, solo el campo que muestra el convertido se muestra como readonly.
            return ('display_converted_inventoried_quantity',)

    def display_inventoried_quantity(self, obj):
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
            unit = obj.purchase_order_supply.requisition_supply.supply.kind.usage_discount_unit_category.unit_category
        return f"{obj.inventoried_quantity} {unit}"
    display_inventoried_quantity.short_description = _("Quantity in Inventory")

    def display_converted_inventoried_quantity(self, obj):
        if not obj.pk:
            return ""
        usage_unit = obj.purchase_order_supply.requisition_supply.supply.kind.usage_discount_unit_category.unit_category
        return f"{obj.converted_inventoried_quantity} {usage_unit}"
    display_converted_inventoried_quantity.short_description = _("Equivalent in inventory for discount")


@admin.register(StorehouseEntry)
class StorehouseEntryAdmin(ByOrganizationAdminMixin):
    inlines = [StorehouseEntrySupplyInline]
    list_display = ('purchase_order', 'created_at', 'user')
    fields = ('purchase_order',)
    readonly_fields = ('created_at', 'user')

    def get_inline_instances(self, request, obj=None):
        inline_instances = super().get_inline_instances(request, obj)
        if obj and obj.purchase_order.status == "closed":
            for inline in inline_instances:
                inline.can_delete = False
                inline.extra = 0
        return inline_instances

    def get_readonly_fields(self, request, obj=None):
        ro_fields = list(self.readonly_fields)
        if obj and obj.purchase_order.status == "closed":
            ro_fields.append('purchase_order')
        return ro_fields

    def get_form(self, request, obj=None, **kwargs):
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
        if db_field.name == 'purchase_order':
            kwargs['queryset'] = db_field.remote_field.model.objects.filter(status='ready')
            if hasattr(request, 'organization'):
                kwargs['queryset'] = kwargs['queryset'].filter(organization=request.organization)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.user = request.user
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        storehouse_entry = form.instance

        # 🔥 Primero guardamos relaciones normales (inlines, etc)
        super().save_related(request, form, formsets, change)

        # 🔥 Ahora actualizamos las cantidades reales de los supplies
        for entry_supply in list(storehouse_entry.storehouseentrysupply_set.all()):
            pos = entry_supply.purchase_order_supply

            if entry_supply.received_quantity == 0 and entry_supply.inventoried_quantity == 0:
                # Si no recibieron nada, lo eliminamos
                entry_supply.delete()
                if not pos.storehouseentrysupply_set.exists():
                    pos.delete()
                continue

            # Actualizamos quantity y total_price con base en lo recibido
            pos.quantity = entry_supply.received_quantity
            pos.total_price = entry_supply.received_quantity * pos.unit_price
            pos.is_in_inventory = True
            pos.save(update_fields=['quantity', 'total_price', 'is_in_inventory'])

            # 🔥 Insertamos la transacción de inventario
            InventoryTransaction.objects.create(
                storehouse_entry_supply=entry_supply,
                supply=entry_supply.purchase_order_supply.requisition_supply.supply,
                transaction_kind='entry',
                transaction_category='purchase',
                quantity=entry_supply.converted_inventoried_quantity,
                created_by=request.user,
                organization=storehouse_entry.organization,
            )

        # 🔥 Recargamos el PurchaseOrder desde la base de datos
        storehouse_entry.purchase_order.refresh_from_db()

        try:
            # 🔥 Ahora recalculamos el balance con datos actualizados
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
            return  # 🔥 No seguimos si el balance quedó negativo

    class Media:
        js = ('js/admin/forms/packhouses/storehouse/storehouse_entry.js',)



@admin.register(AdjustmentInventory)
class AdjustmentInventoryAdmin(ByOrganizationAdminMixin):
    form = AdjustmentInventoryForm
    list_display  = ('transaction_kind', 'transaction_category', 'supply', 'quantity', 'created_at')
    fields = ('transaction_kind', 'transaction_category', 'supply', 'quantity', 'organization', 'created_at')
    readonly_fields = ('created_at',)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        if hasattr(request, 'organization'):
            form.request_organization = request.organization

        # Asegurarnos que 'organization' exista en los fields
        if 'organization' in form.base_fields:
            form.base_fields['organization'].initial = request.organization
            form.base_fields['organization'].widget = forms.HiddenInput()

        # Inyectamos el usuario para usarlo en el form.save()
        form._request_user = request.user

        return form



@admin.register(InventoryTransaction)
class InventoryTransactionAdmin(ByOrganizationAdminMixin):
    list_display = ('supply', 'transaction_kind', 'transaction_category', 'quantity', 'created_at')
    list_filter = ('supply', 'transaction_kind', 'transaction_category')
    actions = [export_fifo_report]

    def has_add_permission(self, request):
        return False  # No permitir crear nuevas desde el admin

    def has_change_permission(self, request, obj=None):
        return False  # No permitir edición

    def has_delete_permission(self, request, obj=None):
        return False  # No permitir eliminación

    def get_readonly_fields(self, request, obj=None):
        return [field.name for field in self.model._meta.fields]

