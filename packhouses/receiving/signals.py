from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete, pre_save
from .models import DryMatter, InternalInspection, Average, FoodSafety, SampleCollection, SampleWeight, IncomingProduct, Batch, BatchStatusChange
from packhouses.gathering.models import ScheduleHarvest
from packhouses.catalogs.models import ProductFoodSafetyProcess, ProductAdditionalValue
from common.base.models import FoodSafetyProcedure
from django.db.models import Avg
from decimal import Decimal

@receiver(post_save, sender=DryMatter)
def my_handler(sender, instance, **kwargs):
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
def my_handler(sender, instance, **kwargs):
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
def my_handler(sender, instance, **kwargs):
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
def my_handler(sender, instance, **kwargs):
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
def my_handler(sender, instance, **kwargs):

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
            if ProductAdditionalValue.objects.filter(product=schedule_harvest.product).exists():
                Average.objects.create(
                    acceptance_report= ProductAdditionalValue.objects.filter(product=schedule_harvest.product).latest('created_at'),
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
    
    # Registra cambios en operational_status y review_status
    for field in ('operational_status', 'review_status'):
        old = getattr(prev, field)
        new = getattr(instance, field)
        if old != new:
            BatchStatusChange.objects.create(
                batch        = instance,
                organization = org,
                field_name   = field,
                old_status    = old,
                new_status    = new,
            )