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
    Revisa si la orden puede cerrarse y la actualiza si es necesario.
    """
    if not order.pk or not order.batch:
        return

    # Se verifica si tiene al menos un recibo guardado
    if not FruitPurchaseOrderReceipt.objects.filter(fruit_purchase_order=order).exists():
        return

    receipts = FruitPurchaseOrderReceipt.objects.filter(
        fruit_purchase_order=order,
        status__in=['open', 'closed']
    ).select_related('price_category')

    total_quantity = Decimal('0.00')
    total_cost = Decimal('0.00')

    for receipt in receipts:
        quantity = receipt.quantity or Decimal('0.00')
        container_capacity = receipt.container_capacity or Decimal('1.00')
        if receipt.price_category and receipt.price_category.is_container:
            quantity *= container_capacity
        total_quantity += quantity
        total_cost += receipt.total_cost or Decimal('0.00')

    total_paid = FruitPurchaseOrderPayment.objects.filter(
        fruit_purchase_order=order,
        status__in=['open', 'closed']
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    new_status = 'closed' if (
        total_quantity.quantize(Decimal('0.00')) == Decimal(order.batch.weight_received).quantize(Decimal('0.00')) and
        total_paid == total_cost
    ) else 'open'

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

