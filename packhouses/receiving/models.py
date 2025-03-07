from django.db import models
from packhouses.gathering.models import ScheduleHarvest
from organizations.models import Organization
from django.utils.translation import gettext_lazy as _
import datetime
from django.core.validators import MinValueValidator, MaxValueValidator
# Create your models here.

class IncomingProduct(models.Model):
    harvest = models.ForeignKey(ScheduleHarvest, verbose_name=_("Harvest Number"), on_delete=models.PROTECT, null=True, blank=True)
    
    harvest_date = models.DateField(verbose_name=_('Harvest date'), default=datetime.date.today)
    category = models.CharField(max_length=255, verbose_name=_("Category"),)
    product = models.CharField(max_length=255, verbose_name=_("Product"),)
    market = models.CharField(max_length=255, verbose_name=_("Market"),)
    weight_expected = models.FloatField(verbose_name=_("Expected Weight in kilograms"), validators=[MinValueValidator(0.01)])
    orchard =  models.CharField(max_length=255, verbose_name=_("Orchard"),)
    orchard_certification =  models.CharField(max_length=255, verbose_name=_("Orchard Certification"),)
    weighing_scale = models.CharField(max_length=255, verbose_name=_("Weighing Scale"),)
    
    guide_number = models.CharField(max_length=255,)
    pythosanitary_certificate = models.CharField(max_length=255,)
    weighing_record = models.CharField(max_length=255,)
    public_weighing = models.CharField(max_length=255,)
    packhouse_weighing = models.CharField(max_length=255,)
    sample_weight = models.CharField(max_length=255,)
    empty_boxes = models.CharField(max_length=255,)
    full_boxes = models.CharField(max_length=255,)
    missing_boxes = models.CharField(max_length=255,)
    avarage_per_box = models.CharField(max_length=255,)
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT, verbose_name=_('Organization'),)

    def __str__(self):
        return f"{self.harvest}"
    
    class Meta:
        verbose_name = _('Incoming Product')
        verbose_name_plural = _('Incoming Product')
        constraints = [
            models.UniqueConstraint(
                fields=['harvest', 'organization'],
                name='unique_incoming_product_harvest'
            )
        ]