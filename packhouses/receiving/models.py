from django.db import models, transaction
from organizations.models import Organization
from django.utils.translation import gettext_lazy as _
import datetime
from django.core.validators import MinValueValidator, MaxValueValidator
from .utils import get_incoming_product_categories_status
from packhouses.catalogs.models import WeighingScale, Supply, HarvestingCrew, Provider, ProductFoodSafetyProcess, Product, Vehicle, ProductPest, ProductDisease, ProductPhysicalDamage, ProductResidue
from common.base.models import Pest

# Create your models here.
class Batch(models.Model):
    status = models.CharField(max_length=20, verbose_name=_('Status'))
    ooid = models.PositiveIntegerField(verbose_name=_("Harvest Number"), null=True, blank=True, unique=True)
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT, verbose_name=_('Organization'),)

    def __str__(self):
        return f"{self.ooid}"

    def save(self, *args, **kwargs):
        if not self.ooid:
            # Usar transacción y bloqueo de fila para evitar condiciones de carrera
            with transaction.atomic():
                last_order = Batch.objects.select_for_update().filter(organization=self.organization).order_by('-ooid').first()
                if last_order:
                    self.ooid = last_order.ooid + 1
                else:
                    self.ooid = 1
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _('Batch')
        verbose_name_plural = _('Batches')

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
    batch = models.ForeignKey(Batch, on_delete=models.PROTECT, verbose_name=_('Batch'), null=True, blank=True)
    comments = models.TextField(verbose_name=_("Comments"), blank=True, null=True)

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

    def save(self, *args, **kwargs):
        if not self.ooid:
            # Usar transacción y bloqueo de fila para evitar condiciones de carrera
            with transaction.atomic():
                last_order = Batch.objects.select_for_update().filter(organization=self.organization).order_by('-ooid').first()
                if last_order:
                    self.ooid = last_order.ooid + 1
                else:
                    self.ooid = 1
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _('Batch')
        verbose_name_plural = _('Batches')


class WeighingSetContainer(models.Model):
    harvest_container = models.ForeignKey(Supply,on_delete=models.CASCADE, limit_choices_to={'kind__category': 'harvest_container'}, verbose_name=_('Harvest Containments'))
    quantity = models.PositiveIntegerField(default=0, verbose_name=_('Quantity'))
    weighing_set = models.ForeignKey(WeighingSet, verbose_name=_('Incoming Product'), on_delete=models.CASCADE, null=True, blank=True)
    class Meta:
        verbose_name = _('Weighing Set Containment')
        verbose_name_plural = _('Weighing Sets Containments')

class FoodSafety(models.Model):
    batch = models.OneToOneField(Batch, verbose_name=_('Batch'), on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT, verbose_name=_('Organization'),)

    def __str__(self):
        return f"{self.batch}"

    class Meta:
        verbose_name = _('Food Safety')
        verbose_name_plural = _('Food Safeties')

class DryMatter(models.Model):
    product_weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    paper_weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    moisture_weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    dry_weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    dry_matter_percentage = models.DecimalField(max_digits=10, decimal_places=2)
    food_safety = models.ForeignKey(FoodSafety, verbose_name=_('Food Safety'), on_delete=models.CASCADE)

    def __str__(self):
        return f""

    class Meta:
        verbose_name = _('Dry Matter')
        verbose_name_plural = _('Dry Matters')

class InternalInspection(models.Model):
    internal_temperature = models.DecimalField(max_digits=10, decimal_places=2)
    product_pest = models.ManyToManyField(ProductPest, verbose_name=_('Pests'), blank=True)
    food_safety = models.ForeignKey(FoodSafety, verbose_name=_('Food Safety'), on_delete=models.CASCADE)

    def __str__(self):
        return f""

    class Meta:
        verbose_name = _('Internal Inspection')
        verbose_name_plural = _('Internal Inspections')

class Average(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    average = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Average'))
    food_safety = models.ForeignKey(FoodSafety, verbose_name=_('Food Safety'), on_delete=models.CASCADE)

    def __str__(self):
        return f""

    class Meta:
        verbose_name = _('Average')
        verbose_name_plural = _('Averages')

class VehicleReview(models.Model):
    vehicle = models.ForeignKey('gathering.ScheduleHarvestVehicle', verbose_name=_('Vehicle'), on_delete=models.CASCADE)
    food_safety = models.ForeignKey(FoodSafety, verbose_name=_('Food Safety'), on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.vehicle} / {self.vehicle.stamp_number}"

    class Meta:
        verbose_name = _('Vehicle Review')
        verbose_name_plural = _('Vehicle Reviews')

class VehicleInspection(models.Model):
    sealed = models.BooleanField(default=False, verbose_name=_('The vehicle is sealed'))
    only_the_product = models.BooleanField(default=False, verbose_name=_('The vehicle carries only the product'))
    free_foreign_matter = models.BooleanField(default=False, verbose_name=_('The vehicle is free of foreign matter'))
    free_unusual_odors = models.BooleanField(default=False, verbose_name=_('The vehicle is free of unusual odors'))
    certificate = models.BooleanField(default=False, verbose_name=_('Has a CERTIFICATE'))
    free_fecal_matter = models.BooleanField(default=False, verbose_name=_('The vehicle is free of fecal matter'))
    vehicle_review = models.ForeignKey(VehicleReview, verbose_name=_('Vehicle Review'), on_delete=models.CASCADE)

    def __str__(self):
        return f""

    class Meta:
        verbose_name = _('Vehicle Inspection')
        verbose_name_plural = _('Vehicle Inspections')

class VehicleCondition(models.Model):
    is_clean = models.BooleanField(default=False, verbose_name=_('It is clean'))
    good_condition = models.BooleanField(default=False, verbose_name=_('Good condition'))
    broken = models.BooleanField(default=False, verbose_name=_('Broken'))
    damaged = models.BooleanField(default=False, verbose_name=_('Damaged'))
    seal = models.BooleanField(default=False, verbose_name=_('Seal'))
    vehicle_review = models.ForeignKey(VehicleReview, verbose_name=_('Vehicle Review'), on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('Vehicle Condition')
        verbose_name_plural = _('Vehicle Conditions')

    def __str__(self):
        return f""

class SampleCollection(models.Model):
    whole = models.BooleanField(default=False, verbose_name=_('Whole'))
    foreign_material = models.BooleanField(default=False, verbose_name=_('Foreign Material'))
    insects = models.BooleanField(default=False, verbose_name=_('Insects'))
    temperature_damage = models.BooleanField(default=False, verbose_name=_('Temperature Damage'))
    unusual_odor = models.BooleanField(default=False, verbose_name=_('Unusual Odor'))
    food_safety = models.ForeignKey(FoodSafety, verbose_name=_('Food Safety'), on_delete=models.CASCADE)

    def __str__(self):
        return f""

    class Meta:
        verbose_name = _('Sample Collection')
        verbose_name_plural = _('Sample Collections')

class SensorySpecification(models.Model):
    whole = models.BooleanField(default=False, verbose_name=_('Whole'))
    foreign_material = models.BooleanField(default=False, verbose_name=_('Foreign Material'))
    insects = models.BooleanField(default=False, verbose_name=_('Insects'))
    temperature_damage = models.BooleanField(default=False, verbose_name=_('Temperature Damage'))
    unusual_odor = models.BooleanField(default=False, verbose_name=_('Unusual Odor'))
    sample_collection = models.ForeignKey(SampleCollection, verbose_name=_('Sample Collection'), on_delete=models.CASCADE)

    def __str__(self):
        return f""

    class Meta:
        verbose_name = _('Sensory Specification')
        verbose_name_plural = _('Sensory Specifications')

class SampleWeight(models.Model):
    weight = models.DecimalField(max_digits=10, decimal_places=2)
    sample_collection = models.ForeignKey(SampleCollection, verbose_name=_('Sample Collection'), on_delete=models.CASCADE)

    def __str__(self):
        return f""

    class Meta:
        verbose_name = _('Sample Weight')
        verbose_name_plural = _('Sample Weights')

class SamplePest(models.Model):
    sample_pest = models.IntegerField(verbose_name=_('Samples With Pests'))
    product_pest = models.ForeignKey(ProductPest, verbose_name=_('Pest'), on_delete=models.CASCADE)
    percentage = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Percentage'), null=True)
    sample_collection = models.ForeignKey(SampleCollection, verbose_name=_('Sample Collection'), on_delete=models.CASCADE)

    def __str__(self):
        return f""

class SampleDisease(models.Model):
    sample_disease = models.IntegerField(verbose_name=_('Samples With Diseases'))
    product_disease = models.ForeignKey(ProductDisease, verbose_name=_('Disease'), on_delete=models.CASCADE)
    percentage = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Percentage'), null=True)
    sample_collection = models.ForeignKey(SampleCollection, verbose_name=_('Sample Collection'), on_delete=models.CASCADE)

    def __str__(self):
        return f""

class SamplePhysicalDamage(models.Model):
    sample_physical_damage = models.IntegerField(verbose_name=_('Samples With Physical Damage'))
    product_physical_damage = models.ForeignKey(ProductPhysicalDamage, verbose_name=_('Physical Damage'), on_delete=models.CASCADE)
    percentage = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Percentage'), null=True)
    sample_collection = models.ForeignKey(SampleCollection, verbose_name=_('Sample Collection'), on_delete=models.CASCADE)

    def __str__(self):
        return f""

class SampleResidue(models.Model):
    sample_residue = models.IntegerField(verbose_name=_('Samples With Residue'))
    product_residue = models.ForeignKey(ProductResidue, verbose_name=_('Residue'), on_delete=models.CASCADE)
    percentage = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Percentage'), null=True)
    sample_collection = models.ForeignKey(SampleCollection, verbose_name=_('Sample Collection'), on_delete=models.CASCADE)

    def __str__(self):
        return f""
