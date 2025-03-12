from django.db import models
from organizations.models import Organization
from django.utils.translation import gettext_lazy as _
import datetime
from django.core.validators import MinValueValidator, MaxValueValidator
from .utils import get_incoming_product_categories_status

# Create your models here.

class IncomingProduct(models.Model):
    status = models.CharField(max_length=20, verbose_name=_('Status'), choices=get_incoming_product_categories_status(), null=True, blank=True)
    guide_number = models.CharField(max_length=255,null=True, blank=True)
    pythosanitary_certificate = models.CharField(max_length=255,null=True, blank=True)
    weighing_record = models.CharField(max_length=255,null=True, blank=True)
    public_weighing = models.CharField(max_length=255, null=True, blank=True)
    packhouse_weighing = models.CharField(max_length=255,null=True, blank=True)
    sample_weight = models.CharField(max_length=255,null=True, blank=True)
    empty_boxes = models.CharField(max_length=255,null=True, blank=True)
    full_boxes = models.CharField(max_length=255,null=True, blank=True)
    missing_boxes = models.CharField(max_length=255,null=True, blank=True)
    avarage_per_box = models.CharField(max_length=255,null=True, blank=True)
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT, verbose_name=_('Organization'),)

    def __str__(self):
        from packhouses.gathering.models import ScheduleHarvest

        schedule_harvest = ScheduleHarvest.objects.filter(incoming_product=self).first()  # Obtenemos el primer registro relacionado
        if schedule_harvest:
            return f"{schedule_harvest.ooid} - {schedule_harvest.orchard}"  
        return str(self.guide_number) 
    
    class Meta:
        verbose_name = _('Incoming Product')
        verbose_name_plural = _('Incoming Product')
        """constraints = [
            models.UniqueConstraint(
                fields=['harvest', 'organization'],
                name='unique_incoming_product_harvest'
            )
        ]"""