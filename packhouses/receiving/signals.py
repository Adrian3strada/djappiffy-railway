from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from .models import DryMatter, InternalInspection, Average
from django.db.models import Avg
from decimal import Decimal

modules = {
    "dry_matter" : "Dry Matter",
    "internal_inspections" : "Internal Inspections"
}

@receiver(post_save, sender=DryMatter)
def my_handler(sender, instance, **kwargs):
    average = DryMatter.objects.filter(food_safety=instance.food_safety).aggregate(Avg('dry_matter_percentage'))
    have_average = Average.objects.filter(name=modules['dry_matter'], food_safety=instance.food_safety).exists()

    if not have_average:
        Average.objects.create(
                name=modules['dry_matter'],
                average=average['dry_matter_percentage__avg'],
                food_safety=instance.food_safety,
            )
    else:
        Average.objects.filter(
            name=modules['dry_matter'], 
            food_safety=instance.food_safety
            ).update(
                average=average['dry_matter_percentage__avg'],
            )


@receiver(post_delete, sender=DryMatter)
def my_handler(sender, instance, **kwargs):
    have_inspection = DryMatter.objects.filter(food_safety=instance.food_safety).exists()

    if have_inspection:
        average = DryMatter.objects.filter(food_safety=instance.food_safety).aggregate(Avg('dry_matter_percentage'))
        Average.objects.filter(
            name=modules['dry_matter'], 
            food_safety=instance.food_safety
            ).update(
                average=average['dry_matter_percentage__avg'],
            )
    else:
        Average.objects.filter(
            name=modules['dry_matter'], 
            food_safety=instance.food_safety
            ).update(
                average=0,
            )

@receiver(post_save, sender=InternalInspection)
def my_handler(sender, instance, **kwargs):
    average = InternalInspection.objects.filter(food_safety=instance.food_safety).aggregate(Avg('internal_temperature'))
    have_average = Average.objects.filter(name=modules['internal_inspections'], food_safety=instance.food_safety).exists()

    if not have_average:
        Average.objects.create(
                name=modules['internal_inspections'],
                average=average['internal_temperature__avg'],
                food_safety=instance.food_safety,
            )
    else:
        Average.objects.filter(
            name=modules['internal_inspections'], 
            food_safety=instance.food_safety
            ).update(
                average=average['internal_temperature__avg'],
            )


@receiver(post_delete, sender=InternalInspection)
def my_handler(sender, instance, **kwargs):
    have_inspection = InternalInspection.objects.filter(food_safety=instance.food_safety).exists()

    if have_inspection:
        average = InternalInspection.objects.filter(food_safety=instance.food_safety).aggregate(Avg('internal_temperature'))
        Average.objects.filter(
            name=modules['internal_inspections'], 
            food_safety=instance.food_safety
            ).update(
                average=average['internal_temperature__avg'],
            )
    else:
        Average.objects.filter(
            name=modules['internal_inspections'], 
            food_safety=instance.food_safety
            ).update(
                average=0,
            )