from django.contrib import admin
from common.base.mixins import (
    ByOrganizationAdminMixin, ByProductForOrganizationAdminMixin,
    DisableInlineRelatedLinksMixin, ByUserAdminMixin
)
from .models import StorehouseEntry, StorehouseEntrySupply
from packhouses.purchases.models import PurchaseOrderSupply
from .forms import StorehouseEntrySupplyInlineFormSet
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.contrib import messages



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

        # 👇 Simulamos manualmente el total_price y recalculamos el balance
        for entry_supply in list(storehouse_entry.storehouseentrysupply_set.all()):
            pos = entry_supply.purchase_order_supply
            if entry_supply.received_quantity == 0 and entry_supply.inventoried_quantity == 0:
                continue  # no lo validamos aún
            else:
                new_quantity = entry_supply.received_quantity
                new_total = new_quantity * pos.unit_price
                pos.total_price = new_total

        try:
            # ❌ Lanza error si el balance quedaría negativo (sin guardar aún)
            storehouse_entry.purchase_order.recalculate_balance(save=False, raise_exception=True)
        except ValidationError as e:
            self.message_user(request, e.message, level=messages.ERROR)
            return  # ❌ Cancelamos todo antes de guardar relaciones

        # ✅ Ahora sí, ya que pasó la validación, guardamos todo
        super().save_related(request, form, formsets, change)

        # 💾 Y hacemos los updates de cantidades y flags como ya tenías
        for entry_supply in list(storehouse_entry.storehouseentrysupply_set.all()):
            pos = entry_supply.purchase_order_supply
            if entry_supply.received_quantity == 0 and entry_supply.inventoried_quantity == 0:
                entry_supply.delete()
                if not pos.storehouseentrysupply_set.exists():
                    pos.delete()
            else:
                if not pos.is_in_inventory:
                    pos.is_in_inventory = True
                    pos.save(update_fields=['is_in_inventory'])
                    pos.quantity = entry_supply.received_quantity
                    pos.save(update_fields=['quantity'])
                    pos.total_price = entry_supply.received_quantity * pos.unit_price
                    pos.save(update_fields=['total_price'])

        # 💰 Finalmente guardamos el nuevo balance
        storehouse_entry.purchase_order.recalculate_balance(save=True)

    class Media:
        js = ('js/admin/forms/packhouses/storehouse/storehouse_entry.js',)
