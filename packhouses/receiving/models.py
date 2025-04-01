from django.db import models, transaction
from organizations.models import Organization
from django.utils.translation import gettext_lazy as _
import datetime
from django.core.validators import MinValueValidator, MaxValueValidator
from .utils import get_incoming_product_categories_status
from packhouses.catalogs.models import WeighingScale, ProductFoodSafetyProcess
from packhouses.catalogs.models import Product

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

class Corte(models.Model):
    product = models.ForeignKey(Product, verbose_name=_('Product'), on_delete=models.PROTECT)

class Lote(models.Model):
    corte = models.ForeignKey(Corte, verbose_name=_('Corte'), on_delete=models.PROTECT)

class FoodSafety(models.Model):
    # corte = models.ForeignKey(corte, verbose_name=_('corte'), on_delete=models.PROTECT)
    lote = models.ForeignKey(Lote, verbose_name=_('lote'), on_delete=models.PROTECT)
    process = models.ForeignKey(ProductFoodSafetyProcess, verbose_name=_('Food Safety Process'), on_delete=models.PROTECT)

class DryMatter(models.Model):
    sample_number = models.IntegerField()
    product_weight = models.DecimalField(max_digits=10, decimal_places=2)
    paper_weight = models.DecimalField(max_digits=10, decimal_places=2)
    moisture_weight = models.DecimalField(max_digits=10, decimal_places=2)
    dry_weight = models.DecimalField(max_digits=10, decimal_places=2)
    dry_matter_percentage = models.DecimalField(max_digits=10, decimal_places=2)
    food_safety = models.ForeignKey(FoodSafety, verbose_name=_('Food Safety'), on_delete=models.PROTECT)

class InternalInspection(models.Model):
    sample_number = models.IntegerField()
    internal_temperature = models.DecimalField(max_digits=10, decimal_places=2)
    food_safety = models.ForeignKey(FoodSafety, verbose_name=_('Food Safety'), on_delete=models.PROTECT)

class Percentage(models.Model):
    dry_matter_percentage = models.DecimalField(max_digits=10, decimal_places=2)
    internal_temperature_percentage = models.DecimalField(max_digits=10, decimal_places=2)
    plant_health_issues  = models.BooleanField(default=False, verbose_name=_('Plant Health Issues'))
    food_safety = models.ForeignKey(FoodSafety, verbose_name=_('Food Safety'), on_delete=models.PROTECT)

class Vehicle(models.Model):
    # vehicle = models.ForeignKey(vehicle, verbose_name=_('vehicle'), on_delete=models.PROTECT)
    food_safety = models.ForeignKey(FoodSafety, verbose_name=_('Food Safety'), on_delete=models.PROTECT)

class VehicleInspection(models.Model):
    sealed  = models.BooleanField(default=False, verbose_name=_('The transport is sealed'))
    only_the_product  = models.BooleanField(default=False, verbose_name=_('The transport carries only the product'))
    free_foreign_matter  = models.BooleanField(default=False, verbose_name=_('The transport is free of foreign matter'))
    free_unusual_odors  = models.BooleanField(default=False, verbose_name=_('The transport is free of unusual odors'))
    certificate  = models.BooleanField(default=False, verbose_name=_('Has a CERTIFICATE'))
    free_fecal_matter  = models.BooleanField(default=False, verbose_name=_('The transport is free of fecal matter'))
    vehicle = models.ForeignKey(Vehicle, verbose_name=_('Vehicle'), on_delete=models.PROTECT)

class VehicleCondition(models.Model):
    clean  = models.BooleanField(default=False, verbose_name=_('Clean'))
    good_condition  = models.BooleanField(default=False, verbose_name=_('Good condition'))
    broken  = models.BooleanField(default=False, verbose_name=_('Broken'))
    damaged  = models.BooleanField(default=False, verbose_name=_('Damaged'))
    seal_number  = models.BooleanField(default=False, verbose_name=_('Seal Number'))
    vehicle = models.ForeignKey(Vehicle, verbose_name=_('Vehicle'), on_delete=models.PROTECT)

class SampleCollection(models.Model):
    food_safety = models.ForeignKey(FoodSafety, verbose_name=_('Food Safety'), on_delete=models.PROTECT)

class SensorySpecification(models.Model):
    whole = models.BooleanField(default=False, verbose_name=_('Whole'))
    foreign_material = models.BooleanField(default=False, verbose_name=_('Foreign Material'))
    insects = models.BooleanField(default=False, verbose_name=_('Insects'))
    temperature_damage = models.BooleanField(default=False, verbose_name=_('Temperature Damage'))
    unusual_odor = models.BooleanField(default=False, verbose_name=_('Unusual Odor'))
    sample_collection = models.ForeignKey(SampleCollection, verbose_name=_('Sample Collection'), on_delete=models.PROTECT)

class SampleWeight(models.Model):
    sample_number = models.IntegerField()
    weight = models.DecimalField(max_digits=10, decimal_places=2)
    sample_collection = models.ForeignKey(SampleCollection, verbose_name=_('Sample Collection'), on_delete=models.PROTECT)

class CropThreat(models.Model):
    sample_number = models.IntegerField()
    food_safety = models.ForeignKey(FoodSafety, verbose_name=_('Food Safety'), on_delete=models.PROTECT)

