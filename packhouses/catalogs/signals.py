from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from .models import ProductFoodSafetyProcess, Product
from common.base.models import FoodSafetyProcedure

@receiver(post_save, sender=ProductFoodSafetyProcess)
def my_handler(sender, instance, **kwargs):
    
    percentage = FoodSafetyProcedure.objects.filter(model="Percentage").values_list('id', flat=True).first()
    
    if instance.procedure.overall_percentage:
        # have_percentage = ProductFoodSafetyProcess.objects.filter(product=instance.product, procedure=percentage).exists()

        # if not have_percentage
        #     ProductFoodSafetyProcess.objects.create(
        #             product=instance.product,
        #             procedure=percentage,
        #             is_enabled=True,
        #         )

        print("Funciona fin")
    else :
        process = ProductFoodSafetyProcess.objects.filter(
            product=instance.product,
            procedure__overall_percentage=True
            )

        if process.exists():
            ProductFoodSafetyProcess.objects.filter(product=instance.product, procedure=percentage).delete()


@receiver(post_delete, sender=ProductFoodSafetyProcess)
def my_handler(sender, **kwargs):
    print("Funciona delete")