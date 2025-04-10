from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from .models import DryMatter, InternalInspection, Percentage
from django.db.models import Avg
from decimal import Decimal

modules = {
    "dry_matter" : "Dry Matter",
    "internal_inspections" : "Internal Inspections"
}

@receiver(post_save, sender=DryMatter)
def my_handler(sender, instance, **kwargs):
    average = DryMatter.objects.filter(food_safety=instance.food_safety).aggregate(Avg('dry_matter_percentage'))
    have_percentage = Percentage.objects.filter(name=modules['dry_matter'], food_safety=instance.food_safety).exists()

    if not have_percentage:
        Percentage.objects.create(
                name=modules['dry_matter'],
                percentage=average['dry_matter_percentage__avg'],
                food_safety=instance.food_safety,
            )
    else:
        Percentage.objects.filter(
            name=modules['dry_matter'], 
            food_safety=instance.food_safety
            ).update(
                percentage=average['dry_matter_percentage__avg'],
            )


@receiver(post_delete, sender=DryMatter)
def my_handler(sender, instance, **kwargs):
    have_inspection = DryMatter.objects.filter(food_safety=instance.food_safety).exists()

    if have_inspection:
        average = DryMatter.objects.filter(food_safety=instance.food_safety).aggregate(Avg('dry_matter_percentage'))
        Percentage.objects.filter(
            name=modules['dry_matter'], 
            food_safety=instance.food_safety
            ).update(
                percentage=average['dry_matter_percentage__avg'],
            )
    else:
        Percentage.objects.filter(name=modules['dry_matter'], food_safety=instance.food_safety).delete()

@receiver(post_save, sender=InternalInspection)
def my_handler(sender, instance, **kwargs):
    average = InternalInspection.objects.filter(food_safety=instance.food_safety).aggregate(Avg('internal_temperature'))
    have_percentage = Percentage.objects.filter(name=modules['internal_inspections'], food_safety=instance.food_safety).exists()

    if not have_percentage:
        Percentage.objects.create(
                name=modules['internal_inspections'],
                percentage=average['internal_temperature__avg'],
                food_safety=instance.food_safety,
            )
    else:
        Percentage.objects.filter(
            name=modules['internal_inspections'], 
            food_safety=instance.food_safety
            ).update(
                percentage=average['internal_temperature__avg'],
            )


@receiver(post_delete, sender=InternalInspection)
def my_handler(sender, instance, **kwargs):
    have_inspection = InternalInspection.objects.filter(food_safety=instance.food_safety).exists()

    if have_inspection:
        average = InternalInspection.objects.filter(food_safety=instance.food_safety).aggregate(Avg('internal_temperature'))
        Percentage.objects.filter(
            name=modules['internal_inspections'], 
            food_safety=instance.food_safety
            ).update(
                percentage=average['internal_temperature__avg'],
            )
    else:
        Percentage.objects.filter(name=modules['internal_inspections'], food_safety=instance.food_safety).delete()