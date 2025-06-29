from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from .models import PackingPackage
from packhouses.receiving.models import BatchWeightMovement

# Signals for PackingPackage model to handle weight movements and status updates

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
    else:
        instance.status = 'open'


@receiver(post_save, sender=PackingPackage)
def handle_packing_package_post_save(sender, instance, created, **kwargs):
    if created:
        # Registrar movimiento con weight negativo al crear
        BatchWeightMovement.objects.create(
            batch=instance.batch,
            weight=-instance.packing_package_sum_weight,
            source={
                "model": instance.__class__.__name__,
                "id": instance.pk,
                "weight": instance.packing_package_sum_weight,
            }
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
