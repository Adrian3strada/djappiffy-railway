from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Sum
from decimal import Decimal
from django.core.exceptions import ValidationError
from .models import FruitPurchaseOrder, FruitPurchaseOrderPayment, FruitPurchaseOrderReceipt


def update_receipt_balance(receipt: FruitPurchaseOrderReceipt):
    if not receipt:
        return

    receipt.recalculate_balance_payable()
    try:
        receipt.full_clean()
        receipt.save(update_fields=['balance_payable'])
    except ValidationError as e:
        logger.error("Validation error in signal: %s", e)




@receiver(post_save, sender=FruitPurchaseOrderPayment)
def recalculate_receipt_balance_on_save(sender, instance, **kwargs):
    update_receipt_balance(instance.fruit_purchase_order_receipt)


@receiver(post_delete, sender=FruitPurchaseOrderPayment)
def recalculate_receipt_balance_on_delete(sender, instance, **kwargs):
    update_receipt_balance(instance.fruit_purchase_order_receipt)



def try_close_fruit_purchase_order(order: FruitPurchaseOrder):
    """
    Revisa si la orden puede cerrarse y actualiza su estado si es necesario.
    Una orden puede cerrarse solo si:
    - Tiene al menos un recibo asociado
    - La suma de cantidades coincide exactamente con el peso recibido del lote
    - El total pagado cubre exactamente el costo total de los recibos
    """
    if not order.pk or not order.batch:
        return

    # Verifica que exista al menos un recibo
    if not FruitPurchaseOrderReceipt.objects.filter(fruit_purchase_order=order).exists():
        return

    receipts = FruitPurchaseOrderReceipt.objects.filter(
        fruit_purchase_order=order,
        status__in=['open', 'closed']
    ).select_related('price_category')

    total_quantity = 0.0
    total_cost = Decimal('0.00')

    for receipt in receipts:
        quantity = float(receipt.quantity or 0)
        container_capacity = float(receipt.container_capacity or 1)

        if receipt.price_category and receipt.price_category.is_container:
            quantity *= container_capacity

        total_quantity += quantity
        total_cost += Decimal(receipt.total_cost or 0)

    total_paid = FruitPurchaseOrderPayment.objects.filter(
        fruit_purchase_order=order,
        status__in=['open', 'closed']
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    expected_quantity = float(order.batch.weight_received or 0)

    if total_quantity == expected_quantity and total_paid == total_cost:
        new_status = 'closed'
    else:
        new_status = 'open'

    if order.status != new_status:
        order.status = new_status
        order.save(update_fields=['status'])


@receiver(post_save, sender=FruitPurchaseOrderReceipt)
def handle_receipt_save(sender, instance, created, **kwargs):
    if not created:
        try_close_fruit_purchase_order(instance.fruit_purchase_order)

@receiver(post_save, sender=FruitPurchaseOrderPayment)
def handle_payment_save(sender, instance, **kwargs):
    try_close_fruit_purchase_order(instance.fruit_purchase_order)

@receiver(post_delete, sender=FruitPurchaseOrderReceipt)
def handle_receipt_delete(sender, instance, **kwargs):
    try_close_fruit_purchase_order(instance.fruit_purchase_order)

@receiver(post_delete, sender=FruitPurchaseOrderPayment)
def handle_payment_delete(sender, instance, **kwargs):
    try_close_fruit_purchase_order(instance.fruit_purchase_order)

