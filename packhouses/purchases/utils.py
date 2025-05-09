from .models import PurchaseOrderPayment, ServiceOrderPayment

def create_related_payments_and_update_balances(mass_payment):
    """
    Genera los pagos individuales (purchase o service) a partir de un pago masivo,
    y actualiza el balance de cada orden a 0 si el pago cubre el total pendiente.

    Args:
        mass_payment (PurchaseMassPayment): Objeto con info del pago masivo.
    """
    user = mass_payment.created_by
    common_fields = {
        "payment_date": mass_payment.payment_date,
        "payment_kind": mass_payment.payment_kind,
        "bank": mass_payment.bank,
        "comments": mass_payment.comments,
        "additional_inputs": mass_payment.additional_inputs,
        "status": "closed",
        "created_by": user,
        "mass_payment": mass_payment
    }

    # Órdenes de compra
    for order in mass_payment.purchase_order.all():
        if order.balance_payable <= 0:
            continue  # Ya está saldada, no repetir pagos

        PurchaseOrderPayment.objects.create(
            purchase_order=order,
            amount=order.balance_payable,
            **common_fields
        )

        # Actualiza el balance a 0 si el pago lo cubre
        order.recalculate_balance(save=True)

    # Órdenes de servicio
    for order in mass_payment.service_order.all():
        if order.balance_payable <= 0:
            continue  # Ya está saldada, no repetir pagos

        ServiceOrderPayment.objects.create(
            service_order=order,
            amount=order.balance_payable,
            **common_fields
        )

        # Actualiza el balance a 0 si el pago lo cubre
        order.recalculate_balance(save=True)


def get_name(model, obj_id, default="Not specified"):
    if obj_id:
        try:
            return model.objects.get(id=obj_id).name
        except model.DoesNotExist:
            return f"{default} does not exist"
    return f"{default} not specified"
