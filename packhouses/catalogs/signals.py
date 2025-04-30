from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from .models import ProductFoodSafetyProcess, Product
from common.base.models import FoodSafetyProcedure

@receiver(post_save, sender=ProductFoodSafetyProcess)
def my_handler(sender, instance, **kwargs):
    
    average = FoodSafetyProcedure.objects.filter(name_model="Average").first()

    if instance.procedure.overall_average:
        have_average = ProductFoodSafetyProcess.objects.filter(product=instance.product, procedure=average).exists()

        if not have_average:
            ProductFoodSafetyProcess.objects.create(
                    product=instance.product,
                    procedure=average,
                    is_enabled=True,
                )
    else:
        process = ProductFoodSafetyProcess.objects.filter(
            product=instance.product,
            procedure__overall_average=True
            )
        
        if not process.exists():
            ProductFoodSafetyProcess.objects.filter(product=instance.product, procedure=average).delete()


@receiver(post_delete, sender=ProductFoodSafetyProcess)
def my_handler(sender, instance, **kwargs):
    average = FoodSafetyProcedure.objects.filter(name_model="Average").first()

    process = ProductFoodSafetyProcess.objects.filter(
        product=instance.product,
        procedure__overall_average=True
        )
    
    if not process.exists():
        ProductFoodSafetyProcess.objects.filter(product=instance.product, procedure=average).delete()