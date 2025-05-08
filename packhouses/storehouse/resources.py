from import_export import resources, fields
from .models import InventoryTransaction
from common.base.utils import DehydrationResource, ExportResource, default_excluded_fields
from django.utils.translation import gettext_lazy as _
from datetime import datetime

class InventoryTransactionResource(DehydrationResource, ExportResource):
    inventory_balance_map = {}

    def before_export(self, queryset, *args, **kwargs):
        """
        Antes de exportar, precalculamos el balance FIFO real por insumo.
        """
        # Limpiar balance anterior
        self.inventory_balance_map = {}

        # Ordenamos siempre por fecha e ID
        transactions = queryset.order_by('supply_id', 'created_at', 'id')

        # Diccionario por supply_id
        supply_inventory = {}

        for transaction in transactions:
            supply_id = transaction.supply_id
            quantity = float(transaction.quantity)

            if supply_id not in supply_inventory:
                supply_inventory[supply_id] = 0.0

            if transaction.transaction_kind == 'inbound':
                supply_inventory[supply_id] += quantity
            elif transaction.transaction_kind == 'outbound':
                supply_inventory[supply_id] -= quantity

            self.inventory_balance_map[transaction.pk] = supply_inventory[supply_id]

    def dehydrate_inventory_balance_after_transaction(self, obj):
        """
        Devuelve el balance de inventario después de cada movimiento.
        """
        return self.inventory_balance_map.get(obj.pk, "—")

    def dehydrate_storehouse_entry_supply(self, obj):
        return obj.storehouse_entry_supply.storehouse_entry.purchase_order.ooid if obj.storehouse_entry_supply and obj.storehouse_entry_supply.storehouse_entry and obj.storehouse_entry_supply.storehouse_entry.purchase_order else "-"

    def dehydrate_supply(self, obj):
        return f"{obj.supply.kind.name}: {obj.supply.name}" if obj.supply.name else ""

    def dehydrate_transaction_kind(self, obj):
        if obj.transaction_kind == 'inbound':
            return 'INBOUND'
        elif obj.transaction_kind == 'outbound':
            return 'OUTBOUND'
        else:
            return 'UNKNOWN'

    def dehydrate_transaction_category(self, obj):
        if obj.transaction_category == 'adjustment_inventory':
            return 'ADJUSTMENT INVENTORY'
        elif obj.transaction_category == 'selective_process':
            return 'SELECTIVE PROCESS'
        elif obj.transaction_category == 'repackaging':
            return 'REPACKAGING'
        elif obj.transaction_category == 'purchase':
            return 'PURCHASE'
        elif obj.transaction_category == 'sale':
            return 'SALE'
        elif obj.transaction_category == 'transfer':
            return 'TRANSFER'
        elif obj.transaction_category == 'return':
            return 'RETURN'
        elif obj.transaction_category == 'other':
            return 'OTHER'
        else:
            return 'UNKNOWN'

    inventory_balance_after_transaction = fields.Field(column_name=_('Inventory balance after transaction'))

    class Meta:
        model = InventoryTransaction
        exclude = tuple(default_excluded_fields + ('id',))
        export_order = ('transaction_kind','transaction_category', 'supply',
                        'quantity', 'storehouse_entry_supply', 'created_at', 'created_by', 'inventory_balance_after_transaction')
