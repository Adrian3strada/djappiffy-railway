from django.db import models, transaction
from organizations.models import Organization
from django.utils.translation import gettext_lazy as _
import datetime
from django.core.validators import MinValueValidator, MaxValueValidator
from .utils import get_incoming_product_categories_status
from packhouses.catalogs.models import WeighingScale
from packhouses.catalogs.models import HarvestContainer

# Create your models here.

class IncomingProduct(models.Model):
    status = models.CharField(max_length=20, verbose_name=_('Status'), choices=get_incoming_product_categories_status(), default='pending')
    public_weighing_scale = models.ForeignKey(WeighingScale, verbose_name=_("Public Weighing Scale"), on_delete=models.PROTECT, null=True, blank=True)
    public_weight_result = models.FloatField(default=0, verbose_name=_("Public Weight Result"),)
    packhouse_weight_result = models.FloatField(default=0, verbose_name=_("Packhouse Weight Result"),)
    weighing_record_number = models.CharField(max_length=30, verbose_name=_('Weighing Record Number'),)
    guide_number = models.CharField(max_length=20, verbose_name=_('Guide Number'),)
    pallets_received = models.PositiveIntegerField(default=0, verbose_name=_('Pallets Received'))
    mrl = models.FloatField(default=0, verbose_name=_('Maximum Residue Limit'), null=True, blank=True)
    phytosanitary_certificate = models.CharField(max_length=50, verbose_name=_('Phytosanitary Certificate'), null=True, blank=True)
    kg_sample = models.FloatField(default=0, verbose_name=_("Kg for Sample"), validators=[MinValueValidator(0.00)])
    current_kg_available = models.FloatField(default=0, verbose_name=_("Current Kg Available"),)
    boxes_assigned = models.PositiveIntegerField(default=0, verbose_name=_('Boxes Assigned'))
    empty_boxes = models.PositiveIntegerField(default=0, verbose_name=_('Empty Boxes'))
    full_boxes = models.PositiveIntegerField(default=0, verbose_name=_('Full Boxes'))
    missing_boxes = models.IntegerField(default=0, verbose_name=_('Missing Boxes'))
    average_per_box = models.FloatField(default=0, verbose_name=_("Average per Box"),)
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

class PalletReceived(models.Model):
    ooid = models.PositiveIntegerField(verbose_name=_("Pallet Number"),null=True, blank=True, unique=True)
    # pallet_number = models.PositiveIntegerField(verbose_name=_("Pallet Number"), null=True, blank=True)
    gross_weight = models.FloatField(default=0.0, verbose_name=_("Gross Weight"),)
    total_boxes = models.PositiveIntegerField(default=0, verbose_name=_('Total Boxes'))
    harvest_container = models.ForeignKey(HarvestContainer, on_delete=models.CASCADE)
    container_tare = models.FloatField(default=0.0, verbose_name=_("Container Tare"),)
    platform_tare = models.FloatField(default=0.0, verbose_name=_("Platform Tare"),)
    net_weight = models.FloatField(default=0.0, verbose_name=_("Net Weight"),)
    incoming_product = models.ForeignKey(IncomingProduct, verbose_name=_('Incoming Product'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.ooid}"
    
    def save(self, *args, **kwargs):
        if not self.ooid:
            # Usar transacción y bloqueo de fila para evitar condiciones de carrera
            with transaction.atomic():
                last_order = PalletReceived.objects.select_for_update().order_by('-ooid').first()
                if last_order:
                    self.ooid = last_order.ooid + 1
                else:
                    self.ooid = 1
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _('Pallet Received')
        verbose_name_plural = _('Pallets Received')