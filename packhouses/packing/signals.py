from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from .models import PackingPackage
from packhouses.receiving.models import BatchWeightMovement


@receiver(post_save, sender=PackingPackage)
def handle_packing_package_post_save(sender, instance, created, **kwargs):
    batch = instance.batch  # Asumiendo que PackingPackage tiene una relación con Batch
    if not batch:
        return

    source_data = {
        "model": instance.__class__.__name__,
        "id": instance.pk,
        "previous_weight": None,
        "new_weight": instance.packing_package_sum_weight,
    }

    if created:
        # Registrar movimiento con weight negativo al crear
        BatchWeightMovement.objects.create(
            batch=batch,
            weight=-instance.packing_package_sum_weight,
            source=source_data
        )
    else:
        # Si no es creación, es una actualización
        previous_weight = instance._previous_weight
        if previous_weight != instance.packing_package_sum_weight:
            # Registrar movimiento para revertir el peso anterior y aplicar el nuevo
            BatchWeightMovement.objects.create(
                batch=batch,
                weight=previous_weight,  # Regresar el peso anterior
                source={
                    **source_data,
                    "previous_weight": previous_weight,
                }
            )
            BatchWeightMovement.objects.create(
                batch=batch,
                weight=-instance.packing_package_sum_weight,  # Aplicar el nuevo peso
                source={
                    **source_data,
                    "new_weight": instance.packing_package_sum_weight,
                }
            )


@receiver(pre_save, sender=PackingPackage)
def track_previous_weight(sender, instance, **kwargs):
    if instance.pk:
        try:
            previous_instance = sender.objects.get(pk=instance.pk)
            instance._previous_weight = previous_instance.packing_package_sum_weight
        except sender.DoesNotExist:
            instance._previous_weight = None


@receiver(post_delete, sender=PackingPackage)
def handle_packing_package_post_delete(sender, instance, **kwargs):
    batch = instance.batch  # Asumiendo que PackingPackage tiene una relación con Batch
    if not batch:
        return

    # Registrar movimiento con weight positivo al eliminar
    BatchWeightMovement.objects.create(
        batch=batch,
        weight=instance.packing_package_sum_weight,
        source={
            "model": instance.__class__.__name__,
            "id": instance.pk,
            "previous_weight": instance.packing_package_sum_weight,
            "new_weight": None,
        }
    )
