from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from .models import DryMatter, InternalInspection, Percentage
from django.db.models import Avg
from decimal import Decimal


@receiver(post_save, sender=DryMatter)
def my_handler(sender, instance, **kwargs):
    average = DryMatter.objects.filter(food_safety=instance.food_safety).aggregate(Avg('dry_matter_percentage'))
    have_percentage = Percentage.objects.filter(name="Dry Matter", food_safety=instance.food_safety).exists()

    if not have_percentage:
        Percentage.objects.create(
                name="Dry Matter",
                percentage=average['dry_matter_percentage__avg'],
                food_safety=instance.food_safety,
            )
    else:
        Percentage.objects.filter(
            name="Dry Matter", 
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
            name="Dry Matter", 
            food_safety=instance.food_safety
            ).update(
                percentage=average['dry_matter_percentage__avg'],
            )
    else:
        Percentage.objects.filter(name="Dry Matter", food_safety=instance.food_safety).delete()