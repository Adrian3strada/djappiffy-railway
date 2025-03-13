from django.db import models
from organizations.models import Organization
from django.utils.translation import gettext_lazy as _
import datetime
from django.core.validators import MinValueValidator, MaxValueValidator
from .utils import get_incoming_product_categories_status
from packhouses.catalogs.models import WeighingScale

# Create your models here.

class IncomingProduct(models.Model):
    status = models.CharField(max_length=20, verbose_name=_('Status'), choices=get_incoming_product_categories_status(), default='pending')
    public_weighing_scale = models.ForeignKey(WeighingScale, verbose_name=_("Public Weighing Scale"), on_delete=models.PROTECT,)
    public_weight_result = models.FloatField(verbose_name=_("Public Weight Result"), validators=[MinValueValidator(0.01)])
    packhouse_weight_result = models.FloatField(verbose_name=_("Packhouse Weight Result"), validators=[MinValueValidator(0.01)])
    weighing_record_number = models.CharField(max_length=30, verbose_name=_('Weighing Record Number'),)
    guide_number = models.CharField(max_length=20, verbose_name=_('Weighing Record Number'),)
    received_pallets = models.PositiveIntegerField(default=0, verbose_name=_('Received Pallets'))
    mrl = models.FloatField(default=0, verbose_name=_('Maximum Residue Limit'))
    kg_sample = models.FloatField(verbose_name=_("Kg for Sample"), validators=[MinValueValidator(0.00)])
    pythosanitary_certificate = models.CharField(max_length=50)
    current_kg = models.FloatField(verbose_name=_("Current Kg"),)
    boxes_assigned = models.PositiveIntegerField(default=0, verbose_name=_('Boxes Assigned'))
    empty_boxes = models.PositiveIntegerField(default=0, verbose_name=_('Empty Boxes'))
    full_boxes = models.PositiveIntegerField(default=0, verbose_name=_('Full Boxes'))
    missing_boxes = models.PositiveIntegerField(default=0, verbose_name=_('Missing Boxes'))
    average_per_box = models.FloatField(verbose_name=_("Packhouse Weight Result"), validators=[MinValueValidator(0.01)])
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT, verbose_name=_('Organization'),)

    def __str__(self):
        from packhouses.gathering.models import ScheduleHarvest

        schedule_harvest = ScheduleHarvest.objects.filter(incoming_product=self).first()
        if schedule_harvest:
            return f"{schedule_harvest.ooid} - {schedule_harvest.orchard}"  
    
    class Meta:
        verbose_name = _('Incoming Product')
        verbose_name_plural = _('Incoming Product')
        """constraints = [
            models.UniqueConstraint(
                fields=['harvest', 'organization'],
                name='unique_incoming_product_harvest'
            )
        ]"""