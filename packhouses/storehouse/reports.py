import tablib
from django.http import HttpResponse
from .models import InventoryTransaction
from datetime import datetime
from django.utils.translation import gettext_lazy as _

def strip_tz(value):
    """
    Elimina la información de zona horaria de un objeto datetime si está presente.
    """

    if isinstance(value, datetime) and value.tzinfo:
        return value.replace(tzinfo=None)
    return value

def export_fifo_report(modeladmin, request, queryset):
    """
    Exporta un reporte detallado de las transacciones de inventario (entradas y salidas),
    mostrando el balance de inventario después de cada movimiento.
    """

    headers = (
        _("Transaction date"), _("Supply"), _("Transaction category"), _("Transaction kind"), _("Quantity"),
        _("Linked entry or purchase order"), _("Reference date"), _("Created by"),
        _("Inventory balance after transaction")
    )
    data = []

    # Cargamos todas las transacciones seleccionadas, no sólo outputs
    transactions = InventoryTransaction.objects.filter(
        id__in=queryset.values_list('id', flat=True),
    ).select_related(
        'supply',
        'storehouse_entry_supply__storehouse_entry__purchase_order',
        'created_by',
        'organization'
    ).order_by('created_at', 'id')  # FIFO real

    # Simulador de inventarios por insumo
    inventory_simulated = {}

    for t in transactions:
        supply_id = t.supply_id
        quantity = float(t.quantity)
        kind = t.transaction_kind

        if supply_id not in inventory_simulated:
            inventory_simulated[supply_id] = 0.0

        if kind == 'inbound':
            inventory_simulated[supply_id] += quantity  # entradas suman
        elif kind == 'outbound':
            inventory_simulated[supply_id] -= quantity  # salidas restan

        entry = t.storehouse_entry_supply

        # Fecha de referencia
        reference_date = "-"
        if kind == 'outbound' and t:
            reference_date = strip_tz(t.created_at)
        elif kind == 'inbound' and t:
            reference_date = strip_tz(t.created_at)

        # Identificador relacionado
        linked_reference = "-"
        if kind == 'outbound' and entry and entry.storehouse_entry and entry.storehouse_entry.purchase_order:
            linked_reference = entry.storehouse_entry.purchase_order.ooid
        elif kind == 'inbound' and entry and entry.storehouse_entry and entry.storehouse_entry.purchase_order:
            linked_reference = entry.storehouse_entry.purchase_order.ooid

        supply = f"{t.supply.kind.name}: {t.supply.name}"

        data.append((
            strip_tz(t.created_at),
            supply,
            t.transaction_category,
            kind,
            quantity,
            linked_reference,
            reference_date,
            t.created_by if t.created_by else "—",
            inventory_simulated[supply_id],
        ))

    dataset = tablib.Dataset(*data, headers=headers)
    response = HttpResponse(
        dataset.xlsx,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="inventory_movements_report.xlsx"'
    return response

export_fifo_report.short_description = _("Export Inventory Movements Report")
