from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete, pre_save, pre_delete
from .models import (DryMatter, InternalInspection, Average, FoodSafety, SampleCollection, SampleWeight, 
                     IncomingProduct, Batch, BatchStatusChange, WeighingSetContainer, WeighingSet, BatchWeightMovement)
from packhouses.gathering.models import ScheduleHarvest
from packhouses.catalogs.models import ProductFoodSafetyProcess, ProductDryMatterAcceptanceReport
from common.base.models import FoodSafetyProcedure
from django.db.models import Avg
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

@receiver(post_save, sender=DryMatter)
def add_avg_dry_matter(sender, instance, **kwargs):
    average = DryMatter.objects.filter(food_safety=instance.food_safety).aggregate(Avg('dry_matter'))
    have_average = Average.objects.filter(food_safety=instance.food_safety).exists()

    if not have_average:
        Average.objects.create(
                average_dry_matter=average['dry_matter__avg'],
                food_safety=instance.food_safety,
            )
    else:
        Average.objects.filter(
            food_safety=instance.food_safety
            ).update(
                average_dry_matter=average['dry_matter__avg'],
            )

@receiver(post_delete, sender=DryMatter)
def delete_avg_dry_matter(sender, instance, **kwargs):
    have_inspection = DryMatter.objects.filter(food_safety=instance.food_safety).exists()

    if have_inspection:
        average = DryMatter.objects.filter(food_safety=instance.food_safety).aggregate(Avg('dry_matter'))
        Average.objects.filter(
            food_safety=instance.food_safety
            ).update(
                average_dry_matter=average['dry_matter__avg'],
            )
    else:
        Average.objects.filter(
            food_safety=instance.food_safety
            ).update(
                average_dry_matter=0,
            )

@receiver(post_save, sender=InternalInspection)
def add_avg_internal_temperature(sender, instance, **kwargs):
    average = InternalInspection.objects.filter(food_safety=instance.food_safety).aggregate(Avg('internal_temperature'))
    have_average = Average.objects.filter(food_safety=instance.food_safety).exists()

    if not have_average:
        Average.objects.create(
                average_internal_temperature=average['internal_temperature__avg'],
                food_safety=instance.food_safety,
            )
    else:
        Average.objects.filter(
            food_safety=instance.food_safety
            ).update(
                average_internal_temperature=average['internal_temperature__avg'],
            )


@receiver(post_delete, sender=InternalInspection)
def delete_avg_internal_temperature(sender, instance, **kwargs):
    have_inspection = InternalInspection.objects.filter(food_safety=instance.food_safety).exists()

    if have_inspection:
        average = InternalInspection.objects.filter(food_safety=instance.food_safety).aggregate(Avg('internal_temperature'))
        Average.objects.filter(
            food_safety=instance.food_safety
            ).update(
                average_internal_temperature=average['internal_temperature__avg'],
            )
    else:
        Average.objects.filter(
            food_safety=instance.food_safety
            ).update(
                average_internal_temperature=0,
            )

@receiver(post_save, sender=FoodSafety)
def add_food_safety(sender, instance, **kwargs):

    incoming_product = IncomingProduct.objects.filter(batch=instance.batch).first()
    schedule_harvest = ScheduleHarvest.objects.filter(incoming_product=incoming_product).first()

    food_safety_averaga = ProductFoodSafetyProcess.objects.filter(product=schedule_harvest.product, procedure__name_model__in=['DryMatter', 'InternalInspection']).exists()
    food_safety_sample_collection = ProductFoodSafetyProcess.objects.filter(product=schedule_harvest.product, procedure__name_model__in=['SampleCollection']).exists()

    if food_safety_sample_collection:
        have_sample_colletion = SampleCollection.objects.filter(food_safety=instance.id).exists()

        if not have_sample_colletion:
            SampleCollection.objects.create(
                    whole=False,
                    foreign_material=False,
                    insects=False,
                    temperature_damage=False,
                    unusual_odor=False,
                    food_safety=instance,
                )

    if food_safety_averaga:
        have_average = Average.objects.filter(food_safety=instance.id).exists()
        
        if not have_average:
            if ProductDryMatterAcceptanceReport.objects.filter(product=schedule_harvest.product).exists():
                Average.objects.create(
                    acceptance_report= ProductDryMatterAcceptanceReport.objects.filter(product=schedule_harvest.product).latest('created_at'),
                    food_safety=instance,
                )
            else:
                Average.objects.create(
                    food_safety=instance,
                )
 
@receiver(pre_save, sender=Batch)
def batch_status_changes(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        prev = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return
    org  = instance.organization
    
    # Registra cambios en el estado del lote
    if prev.status != instance.status:
        BatchStatusChange.objects.create(
            batch        = instance,
            organization = org,
            field_name   = 'status',
            old_status   = prev.status,
            new_status   = instance.status,
        )

# Calculo de peso neto de pesadas (WeighingSet)
@receiver([post_save, post_delete], sender=WeighingSetContainer)
def update_weighing_set_totals(sender, instance, **kwargs):
    try:
        parent = instance.weighing_set
    except WeighingSet.DoesNotExist:
        return

    if not parent or not parent.pk:
        return

    # ✅ Evitamos ejecutar si aún no hay datos clave (como el peso bruto)
    if parent.gross_weight is None or parent.platform_tare is None:
        return

    # ✅ Calculamos datos agregados de los contenedores
    containers = parent.weighingsetcontainer_set.all()

    total_tare = sum(
        c.quantity * (c.harvest_container.kg_tare or 0)
        for c in containers
    )
    total_qty = sum(c.quantity or 0 for c in containers)

    # ✅ Calculamos net_weight
    gross = parent.gross_weight or 0
    tare = total_tare or 0
    platform = parent.platform_tare or 0
    net = gross - tare - platform

    # ✅ Actualizamos los campos relacionados
    parent.container_tare = total_tare
    parent.total_containers = total_qty
    parent.net_weight = net
    parent.save(update_fields=["container_tare", "total_containers", "net_weight"])

        
@receiver(post_save, sender=WeighingSet)
def handle_weighing_set_post_save(sender, instance, created, **kwargs):
    # Registrar movimiento de peso si existe net_weight y un batch relacionado
    if instance.net_weight > 0 and instance.incoming_product.batch is not None:
        batch = instance.incoming_product.batch
        source_data = {
            "model": instance.__class__.__name__,
            "id": instance.pk,
            "gross_weight": instance.gross_weight,
            "container_tare": instance.container_tare,
            "platform_tare": instance.platform_tare,
        }
        # Verifica si ya existe movimiento para evitar duplicados
        already_exists = BatchWeightMovement.objects.filter(
            batch=batch,
            source__model= instance.__class__.__name__,
            source__id=instance.pk
        ).exists()

        if not already_exists:
            BatchWeightMovement.objects.create(
                batch=batch,
                weight=instance.net_weight,
                source=source_data
            )

@receiver(post_delete, sender=WeighingSet)
def handle_post_delete_weighing_set(sender, instance, **kwargs):
    # Registrar eliminación de pesada solo si tiene un batch relacionado
    if instance.incoming_product.batch:
        batch = instance.incoming_product.batch
        source_data = {
            "model": instance.__class__.__name__,
            "id": instance.pk,
            "gross_weight": instance.gross_weight,
            "container_tare": instance.container_tare,
            "platform_tare": instance.platform_tare,
        }
        BatchWeightMovement.objects.create(
                batch=batch,
                weight= -instance.net_weight,
                source=source_data
            )


@receiver([post_save, post_delete], sender=WeighingSet)
@receiver([post_save, post_delete], sender=WeighingSetContainer)
def recalculate_weighingset_change(sender, instance, **kwargs):
    incoming = None

    if isinstance(instance, WeighingSet):
        incoming = instance.incoming_product

    elif isinstance(instance, WeighingSetContainer):
        weighing_set_id = getattr(instance, 'weighing_set_id', None)
        if weighing_set_id:
            try:
                weighing_set = WeighingSet.objects.only("incoming_product_id").get(pk=weighing_set_id)
                incoming = weighing_set.incoming_product
            except WeighingSet.DoesNotExist:
                incoming = None

    if incoming:
        incoming.recalculate_weighing_data()
