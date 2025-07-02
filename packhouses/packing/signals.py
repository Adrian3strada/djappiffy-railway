from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from .models import PackingPackage
from packhouses.receiving.models import BatchWeightMovement
from ..storehouse.models import InventoryTransaction, AdjustmentInventory


# Signals for PackingPackage model to handle weight movements and status updates


# Variable temporal para almacenar el estado previo
_package_previous_status = {}

@receiver(pre_save, sender=PackingPackage)
def capture_previous_status(sender, instance, **kwargs):
    if instance.pk:  # Solo para instancias existentes
        previous_instance = PackingPackage.objects.get(pk=instance.pk)
        _package_previous_status[instance.pk] = previous_instance.status


@receiver(pre_save, sender=PackingPackage)
def handle_packing_package_pre_save(sender, instance, **kwargs):
    if instance.pk:  # Solo para instancias existentes
        previous_instance = PackingPackage.objects.get(pk=instance.pk)
        previous_weight = previous_instance.packing_package_sum_weight
        current_weight = instance.packing_package_sum_weight

        if previous_weight != current_weight:
            # Registrar la diferencia de peso con traza
            weight_difference = current_weight - previous_weight
            BatchWeightMovement.objects.create(
                batch=instance.batch,
                weight=-weight_difference,
                source={
                    "model": instance.__class__.__name__,
                    "id": instance.pk,
                    "previous_weight": previous_weight,
                    "current_weight": current_weight,
                }
            )

    # Actualizar el estado según la lógica existente
    if instance.packing_pallet:
        instance.status = 'ready'


@receiver(post_save, sender=PackingPackage)
def handle_packing_package_post_save(sender, instance, created, **kwargs):
    if created:
        # Registrar movimiento con weight negativo al crear
        logger.debug(f"instance.batch available_weight: {instance.batch.available_weight}")
        logger.debug(f"instance.batch packing_package_sum_weight: {instance.packing_package_sum_weight}")
        BatchWeightMovement.objects.create(
            batch=instance.batch,
            weight=-instance.packing_package_sum_weight,
            source={
                "model": instance.__class__.__name__,
                "id": instance.pk,
                "weight": instance.packing_package_sum_weight,
            }
        )
        if instance.status == 'ready':
            for supply in instance.package_supplies:
                print(f"Adjusting supply {supply['supply']} with quantity {supply['quantity']}")
                AdjustmentInventory.objects.create(
                    transaction_kind='outbound',
                    transaction_category='packing',
                    supply=supply['supply'],
                    quantity=supply['quantity'],
                    organization=instance.organization
                )
    else:
        previous_status = _package_previous_status.pop(instance.pk, None)
        if previous_status and previous_status != instance.status:
            if instance.status == 'ready':
                for supply in instance.package_supplies:
                    print(f"Adjusting supply {supply['supply']} with quantity {supply['quantity']}")
                    AdjustmentInventory.objects.create(
                        transaction_kind='outbound',
                        transaction_category='packing',
                        supply=supply['supply'],
                        quantity=supply['quantity'],
                        organization=instance.organization
                    )
            if instance.status == 'open':
                for supply in instance.package_supplies:
                    print(f"Reverting supply {supply['supply']} with quantity {supply['quantity']}")
                    AdjustmentInventory.objects.create(
                        transaction_kind='inbound',
                        transaction_category='return',
                        supply=supply['supply'],
                        quantity=supply['quantity'],
                        organization=instance.organization
                    )


@receiver(post_delete, sender=PackingPackage)
def handle_packing_package_post_delete(sender, instance, **kwargs):
    BatchWeightMovement.objects.create(
        batch=instance.batch,
        weight=instance.packing_package_sum_weight,
        source={
            "model": instance.__class__.__name__,
            "id": instance.pk,
            "weight": instance.packing_package_sum_weight,
        }
    )
    if instance.status == 'ready':
        # Revertir ajustes de inventario al eliminar el paquete
        print("Reverting supplies for deleted package")
        for supply in instance.package_supplies:
            print(f"Reverting supply {supply['supply']} with quantity {supply['quantity']}")
            AdjustmentInventory.objects.create(
                transaction_kind='inbound',
                transaction_category='return',
                supply=supply['supply'],
                quantity=supply['quantity'],
                organization=instance.organization
            )
