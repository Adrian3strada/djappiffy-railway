from decimal import Decimal
from django.db.models import Sum, Q
from django.db.models.functions import Coalesce
from django.core.exceptions import ValidationError
from .models import InventoryTransaction

def get_inventory_balance(supply, organization):
    """
    Devuelve el saldo actual del inventario para un insumo en una organización específica.
    """
    total_entries = InventoryTransaction.objects.filter(
        supply=supply,
        transaction_kind='inbound',
        organization=organization
    ).aggregate(
        total=Coalesce(Sum('quantity'), Decimal('0'))
    )['total']

    total_outputs = InventoryTransaction.objects.filter(
        supply=supply,
        transaction_kind='outbound',
        organization=organization
    ).aggregate(
        total=Coalesce(Sum('quantity'), Decimal('0'))
    )['total']

    return total_entries - total_outputs

def validate_inventory_availability(supply, quantity, organization):
    """
    Valida que haya suficiente inventario para realizar una salida del insumo.
    """
    remaining = get_inventory_balance(supply, organization)

    if remaining < quantity:
        raise ValidationError(f"Not enough inventory available for this supply. Available quantity: {remaining}")

    return remaining

def get_entry_sources_fifo(supply, organization):
    """
    Devuelve una lista de entradas disponibles en orden FIFO, con su saldo restante.
    Considera entradas con y sin `storehouse_entry_supply`.

    Returns:
        List[Dict]: Cada dict contiene:
            - 'entry': InventoryTransaction de entrada
            - 'available_quantity': cantidad restante disponible
    """
    entries = InventoryTransaction.objects.filter(
        supply=supply,
        transaction_kind='inbound',
        organization=organization
    ).order_by('created_at', 'id')

    outputs = InventoryTransaction.objects.filter(
        supply=supply,
        transaction_kind='outbound',
        organization=organization
    ).order_by('created_at', 'id')

    results = []

    # Se separan las salidas que no tienen origen físico
    remaining_output_without_source = outputs.filter(storehouse_entry_supply__isnull=True)
    output_balance = sum([o.quantity for o in remaining_output_without_source])

    for entry in entries:
        if entry.storehouse_entry_supply:
            # Salidas asociadas a esta entrada física
            used_quantity = outputs.filter(
                storehouse_entry_supply=entry.storehouse_entry_supply
            ).aggregate(
                total=Coalesce(Sum('quantity'), Decimal('0'))
            )['total']
        else:
            # Entrada sin origen físico — le restamos lo que quede pendiente de salidas sin origen
            used_quantity = min(entry.quantity, output_balance)
            output_balance -= used_quantity  # descontamos lo que ya asignamos

        available_quantity = entry.quantity - used_quantity

        if available_quantity > 0:
            results.append({
                'entry': entry,
                'available_quantity': available_quantity
            })

    return results

def get_source_for_quantity_fifo(supply, quantity, organization):
    """
    Simula una salida y determina de qué entradas (FIFO) se tomará el inventario.

    Args:
        supply (Supply): Insumo a mover.
        quantity (Decimal): Cantidad total que se desea mover.
        organization (Organization): Organización en contexto.

    Returns:
        List[Dict]: Cada dict contiene:
            - 'entry': transacción de entrada
            - 'take': cantidad que se tomará de esa entrada

    Raises:
        ValidationError: Si no hay inventario suficiente.
    """
    fifo_entries = get_entry_sources_fifo(supply, organization)

    remaining = quantity
    result = []

    for item in fifo_entries:
        if remaining <= 0:
            break

        take = min(item['available_quantity'], remaining)

        result.append({
            'entry': item['entry'],
            'take': take
        })

        remaining -= take

    if remaining > 0:
        raise ValidationError(f"Not enough inventory available for this supply. Missing: {remaining} units.")

    return result
