from django.db import models, transaction
from organizations.models import Organization
from django.utils.translation import gettext_lazy as _
import datetime
from django.core.validators import MinValueValidator, MaxValueValidator
from .utils import get_incoming_product_categories_status
from packhouses.catalogs.models import WeighingScale, Supply, HarvestingCrew, Provider

# Create your models here.

class IncomingProduct(models.Model):
    status = models.CharField(max_length=20, verbose_name=_('Status'), choices=get_incoming_product_categories_status(), default='pending')
    public_weighing_scale = models.ForeignKey(WeighingScale, verbose_name=_("Public Weighing Scale"), on_delete=models.PROTECT, null=True, blank=False)
    public_weight_result = models.FloatField(default=0, verbose_name=_("Public Weight Result"),)
    packhouse_weight_result = models.FloatField(default=0, verbose_name=_("Packhouse Weight Result"),)
    weighing_record_number = models.CharField(max_length=30, verbose_name=_('Weighing Record Number'),)
    total_weighed_sets = models.PositiveIntegerField(default=0, verbose_name=_('Total Weighed Sets'))
    mrl = models.FloatField(default=0, verbose_name=_('Maximum Residue Limit'), null=True, blank=True)
    phytosanitary_certificate = models.CharField(max_length=50, verbose_name=_('Phytosanitary Certificate'), null=True, blank=True)
    kg_sample = models.FloatField(default=0, verbose_name=_("Kg for Sample"), validators=[MinValueValidator(0.00)])
    current_kg_available = models.FloatField(default=0, verbose_name=_("Current Kg Available"),)
    containers_assigned = models.PositiveIntegerField(default=0, verbose_name=_('Containments Assigned'), help_text=_('Containments assigned per harvest'))
    empty_containers = models.PositiveIntegerField(default=0, verbose_name=_('Empty Containments'), help_text=_('Empty containments per harvest'))
    total_weighed_set_containers = models.PositiveIntegerField(default=0, verbose_name=_('Total Weighed Set Containments'))
    full_containers_per_harvest = models.PositiveIntegerField(default=0, verbose_name=_('Full Containments per Harvest'),)
    missing_containers = models.IntegerField(default=0, verbose_name=_('Missing Containments'), help_text=_('Missing containments per harvest'))
    average_per_container = models.FloatField(default=0, verbose_name=_("Average per Container"), help_text=_('Based on packhouse weight result and weighed set containments'))
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT, verbose_name=_('Organization'),)
    comments = models.TextField(verbose_name=_('Comments'), blank=True, null=True)
    
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

class WeighingSet(models.Model):
    ooid = models.PositiveIntegerField(verbose_name=_("ID"),null=True, blank=True)
    provider = models.ForeignKey(Provider, verbose_name=_('Harvesting Crew Provider'),on_delete=models.CASCADE,)
    harvesting_crew = models.ForeignKey(HarvestingCrew, verbose_name=_("Harvesting Crew"), on_delete=models.CASCADE,)
    gross_weight = models.FloatField(default=0.0, verbose_name=_("Gross Weight"),)
    total_containers = models.PositiveIntegerField(default=0, verbose_name=_('Total Containments'))
    container_tare = models.FloatField(default=0.0, verbose_name=_("Container Tare"),)
    platform_tare = models.FloatField(default=0.0, verbose_name=_("Platform Tare"),)
    net_weight = models.FloatField(default=0.0, verbose_name=_("Net Weight"),)
    incoming_product = models.ForeignKey(IncomingProduct, verbose_name=_('Incoming Product'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.ooid}"

    class Meta:
        verbose_name = _('Weighing Set')
        verbose_name_plural = _('Weighing Sets')
        constraints = [
            models.UniqueConstraint(fields=['incoming_product', 'ooid'], name='weighing_unique_incomingproduct')
        ]

class WeighingSetContainer(models.Model):
    harvest_container = models.ForeignKey(Supply,on_delete=models.CASCADE, limit_choices_to={'kind__category': 'harvest_container'}, verbose_name=_('Harvest Containments'))
    quantity = models.PositiveIntegerField(default=0, verbose_name=_('Quantity'))
    weighing_set = models.ForeignKey(WeighingSet, verbose_name=_('Incoming Product'), on_delete=models.CASCADE, null=True, blank=True)
    class Meta:
        verbose_name = _('Weighing Set Containment')
        verbose_name_plural = _('Weighing Sets Containments')