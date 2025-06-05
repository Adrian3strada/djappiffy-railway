from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Sum

from .models import FruitPurchaseOrderPayment, FruitPurchaseOrderReceipt


def update_receipt_balance(receipt: FruitPurchaseOrderReceipt):
    """
    Recalcula el balance_payable del recibo restando todos los pagos no cancelados.
    """
    if not receipt:
        return

    total_paid = FruitPurchaseOrderPayment.objects.filter(
        fruit_purchase_order_receipt=receipt,
        status__in=['open', 'closed']
    ).aggregate(total=Sum('amount'))['total'] or 0

    new_balance = receipt.quantity * receipt.unit_price - total_paid
    if receipt.balance_payable != new_balance:
        receipt.balance_payable = new_balance
        receipt.save(update_fields=['balance_payable'])


@receiver(post_save, sender=FruitPurchaseOrderPayment)
def recalculate_receipt_balance_on_save(sender, instance, **kwargs):
    update_receipt_balance(instance.fruit_purchase_order_receipt)


@receiver(post_delete, sender=FruitPurchaseOrderPayment)
def recalculate_receipt_balance_on_delete(sender, instance, **kwargs):
    update_receipt_balance(instance.fruit_purchase_order_receipt)


