import tablib
from django.http import HttpResponse
from .models import InventoryTransaction
from datetime import datetime
from django.utils.translation import gettext_lazy as _


def strip_tz(value):
    """
    Removes timezone info from datetime if present.
    """
    if isinstance(value, datetime) and value.tzinfo:
        return value.replace(tzinfo=None)
    return value


def export_fifo_report(modeladmin, request, queryset):
    """
    Exports a FIFO report of inventory outputs, showing the source entry for each transaction.
    Only applies to 'output' transactions.
    """
    headers = (
        _("Output date"), _("Supply"), _("Category"), _("Kind"), _("Quantity"),
        _("Linked entry"), _("Entry date"), _("Created by"), _("Organization")
    )
    data = []

    transactions = InventoryTransaction.objects.filter(
        id__in=queryset.values_list('id', flat=True),
        transaction_kind='output'
    ).select_related(
        'supply',
        'storehouse_entry_supply__storehouse_entry__purchase_order',
        'created_by',
        'organization'
    )

    for t in transactions:
        entry = t.storehouse_entry_supply

        output_date = strip_tz(t.created_at)
        entry_date = strip_tz(entry.storehouse_entry.created_at) if entry and entry.storehouse_entry else "—"

        data.append((
            output_date,
            t.supply.name,
            t.transaction_category,
            t.transaction_kind,
            float(t.quantity),
            entry.storehouse_entry.purchase_order.ooid if entry and entry.storehouse_entry else "—",
            entry_date,
            t.created_by.get_full_name() if t.created_by else "—",
            t.organization.name if t.organization else "—",
        ))

    dataset = tablib.Dataset(*data, headers=headers)
    response = HttpResponse(
        dataset.xlsx,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="outputs_report.xlsx"'
    return response

export_fifo_report.short_description = _("Export Output Report")
