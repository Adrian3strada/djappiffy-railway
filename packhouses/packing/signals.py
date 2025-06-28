from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from .models import PackingPackage
from packhouses.receiving.models import BatchWeightMovement


@receiver(pre_save, sender=PackingPackage)
def handle_packing_package_pre_save(sender, instance, **kwargs):
    if instance.packing_pallet:
        instance.status = 'ready'
    else:
        instance.status = 'open'


@receiver(post_save, sender=PackingPackage)
def handle_packing_package_post_save(sender, instance, created, **kwargs):
    batch = instance.batch  # Asumiendo que PackingPackage tiene una relación con Batch
    if not batch:
        return

    source_data = {
        "model": instance.__class__.__name__,
        "id": instance.pk,
        "weight": instance.packing_package_sum_weight,
    }

    if created:
        # Registrar movimiento con weight negativo al crear
        BatchWeightMovement.objects.create(
            batch=batch,
            weight=-instance.packing_package_sum_weight,
            source=source_data
        )

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
            "weight": instance.packing_package_sum_weight,
        }
    )
