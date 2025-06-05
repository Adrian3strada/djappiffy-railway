from django.db import models, transaction
from common.mixins import (CleanKindAndOrganizationMixin, CleanNameAndOrganizationMixin, CleanProductMixin,
                           CleanNameOrAliasAndOrganizationMixin, CleanNameAndMarketMixin, CleanNameAndProductMixin,
                           CleanNameAndProviderMixin, CleanNameAndCategoryAndOrganizationMixin,
                           CleanProductVarietyMixin, CleanNameAndAliasProductMixin,
                           CleanNameAndCodeAndOrganizationMixin,
                           CleanNameAndVarietyAndMarketAndVolumeKindMixin, CleanNameAndMaquiladoraMixin)
from organizations.models import Organization
from cities_light.models import City, Country, Region, SubRegion
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django_ckeditor_5.fields import CKEditor5Field
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from packhouses.catalogs.utils import vehicle_year_choices, vehicle_validate_year, get_type_choices, get_payment_choices, \
    get_vehicle_category_choices, get_provider_categories_choices, get_harvest_cutting_categories_choices
from django.core.exceptions import ValidationError
from common.base.models import ProductKind, CapitalFramework, LegalEntityCategory
from packhouses.packhouse_settings.models import (Bank, VehicleOwnershipKind,
                                                  PaymentKind, VehicleFuelKind, VehicleKind, VehicleBrand,
                                                  OrchardCertificationVerifier,
                                                  OrchardCertificationKind)
from packhouses.catalogs.settings import CLIENT_KIND_CHOICES
from packhouses.catalogs.models import (Provider, Gatherer, Maquiladora, Orchard, Product, ProductVariety,
                                        Market, ProductPhenologyKind, ProductHarvestSizeKind, WeighingScale,
                                        HarvestingCrew, Vehicle, OrchardCertification, Supply, ProductRipeness)
from django.db.models import Max, Min
from django.db.models import Q, F, Sum
import datetime
from common.settings import STATUS_CHOICES
from packhouses.receiving.models import IncomingProduct
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from decimal import Decimal, ROUND_DOWN

# Create your models here.
class ScheduleHarvest(models.Model):
    ooid = models.PositiveIntegerField(verbose_name=_("Harvest Number"), null=True, blank=True, unique=True)
    harvest_date = models.DateField(verbose_name=_('Harvest date'), default=datetime.date.today)
    product_provider = models.ForeignKey(Provider, verbose_name=_("Product provider"), on_delete=models.PROTECT, null=True, blank=True)
    category = models.CharField(max_length=255, choices=get_harvest_cutting_categories_choices(), verbose_name=_("Category"),)
    gatherer = models.ForeignKey(Gatherer, verbose_name=_("Gatherer"), on_delete=models.PROTECT, null=True, blank=True)
    maquiladora = models.ForeignKey(Maquiladora, verbose_name=_("Maquiladora"), on_delete=models.PROTECT, null=True, blank=True)
    product = models.ForeignKey(Product, verbose_name=_("Product"), on_delete=models.PROTECT,)
    product_variety = models.ForeignKey(ProductVariety, verbose_name=_("Product Variety"), on_delete=models.PROTECT,)
    product_phenologies = models.ForeignKey(ProductPhenologyKind, verbose_name=_("Product phenology"), on_delete=models.PROTECT)
    product_ripeness = models.ForeignKey(ProductRipeness, verbose_name=_("Product ripeness"), on_delete=models.PROTECT, null=True,blank=True)
    product_harvest_size_kind = models.ForeignKey(ProductHarvestSizeKind, verbose_name=_("Product harvest size"), on_delete=models.PROTECT)
    orchard = models.ForeignKey(Orchard, verbose_name=_("Orchard"), on_delete=models.PROTECT,)
    market = models.ForeignKey(Market, verbose_name=_("Market"), on_delete=models.PROTECT,)
    weight_expected = models.FloatField(verbose_name=_("Expected Weight in kilograms"), validators=[MinValueValidator(0.01)])
    weighing_scale = models.ForeignKey(WeighingScale, verbose_name=_("Weighing Scale"), on_delete=models.PROTECT, null=True, blank=True)
    meeting_point = models.CharField(max_length=255, verbose_name=_("Meeting Point for the Harvest Cutting"), null=True, blank=True)
    status = models.CharField(max_length=8, verbose_name=_('Status'), choices=STATUS_CHOICES, default='open')
    comments = models.TextField(verbose_name=_('Comments'), blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    is_scheduled = models.BooleanField(default=True, verbose_name=_("Was it scheduled?"))
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT,verbose_name=_('Organization'),)
    incoming_product = models.OneToOneField(IncomingProduct, on_delete=models.SET_NULL, null=True, blank=True)

    @property
    def containers_assigned(self):
        vehicles = self.scheduleharvestvehicle_set.all()

        return ScheduleHarvestContainerVehicle.objects.filter(
            schedule_harvest_vehicle__in=vehicles
        ).aggregate(total=Sum('quantity'))['total'] or 0

    def __str__(self):
        return f"{self.ooid}"

    def save(self, *args, **kwargs):
        if not self.ooid:
            # Usar transacción y bloqueo de fila para evitar condiciones de carrera
            with transaction.atomic():
                last_order = ScheduleHarvest.objects.select_for_update().filter(organization=self.organization).order_by('-ooid').first()
                if last_order:
                    self.ooid = last_order.ooid + 1
                else:
                    self.ooid = 1
        super().save(*args, **kwargs)

    def recalc_weight_expected(self):
        total = Decimal('0')
        for veh in self.scheduleharvestvehicle_set.all():
            for cont in veh.scheduleharvestcontainervehicle_set.all():
                harvest_container = cont.harvest_container
                if (
                    harvest_container is not None and
                    harvest_container.capacity is not None and
                    cont.quantity is not None
                ):
                    try:
                        quantity = Decimal(cont.quantity)
                        capacity = Decimal(harvest_container.capacity)
                        total += quantity * capacity
                    except (ValueError, TypeError, ArithmeticError):
                        continue
        total = total.quantize(Decimal('0.001'), rounding=ROUND_DOWN)
        self.weight_expected = float(total)
        self.save(update_fields=['weight_expected'])

    class Meta:
        verbose_name = _('Schedule Harvest')
        verbose_name_plural = _('Schedule Harvests')
        constraints = [
            models.UniqueConstraint(
                fields=['ooid', 'organization'],
                name='unique_schedule_harvest'
            )
        ]

class ScheduleHarvestHarvestingCrew(models.Model):
    schedule_harvest = models.ForeignKey(
        ScheduleHarvest,
        verbose_name=_("Schedule Harvest"),
        on_delete=models.CASCADE,
    )
    provider = models.ForeignKey(
        Provider,
        verbose_name=_('Harvesting Crew Provider'),
        on_delete=models.CASCADE,
    )
    harvesting_crew = models.ForeignKey(
        HarvestingCrew,
        verbose_name=_("Harvesting Crew"),
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f"{self.provider.name} : {self.harvesting_crew.name}"

    class Meta:
        verbose_name = _('Harvesting Crew')
        verbose_name_plural = _('Harvesting Crews')

class ScheduleHarvestVehicle(models.Model):
    schedule_harvest = models.ForeignKey(
        ScheduleHarvest,
        verbose_name=_("Harvest Cutting"),
        on_delete=models.CASCADE,
    )
    provider = models.ForeignKey(
        Provider,
        verbose_name=_('Harvesting Crew Provider'),
        on_delete=models.CASCADE,
    )
    vehicle = models.ForeignKey(
        Vehicle,
        verbose_name=_("Vehicle"),
        on_delete=models.CASCADE,
    )
    guide_number = models.CharField(
        max_length=20,
        verbose_name=_('Guide Number'),
        null= True,
        blank=False,
        )
    stamp_number = models.CharField(
        max_length=20,
        verbose_name=_("Stamp Number"),
    )
    has_arrived = models.BooleanField(
        default=False,
        verbose_name=_('Vehicle has Arrived')
    )

    def __str__(self):
        return f"{self.vehicle.license_plate} / {self.vehicle.name}"

    class Meta:
        verbose_name = _('Vehicle')
        verbose_name_plural = _('Vehicles')



class ScheduleHarvestContainerVehicle(models.Model):
    schedule_harvest_vehicle = models.ForeignKey(ScheduleHarvestVehicle, on_delete=models.CASCADE)
    harvest_container = models.ForeignKey(
        Supply,
        on_delete=models.CASCADE,
        limit_choices_to={'kind__category': 'harvest_container'},
        verbose_name=_('Harvest Containments')
    )
    quantity = models.PositiveIntegerField()
    full_containers = models.PositiveIntegerField(default=0, verbose_name=_('Full containments'))
    empty_containers = models.PositiveIntegerField(default=0,verbose_name=_('Empty containments'))
    missing_containers = models.IntegerField(default=0, verbose_name=_('Missing containments'))
    created_at_model = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return ""

    class Meta:
        verbose_name = _('Schedule Harvest Containment Vehicle')
        verbose_name_plural = _('Schedule Harvest Containment Vehicle')


@receiver(post_save, sender=ScheduleHarvestContainerVehicle)
def set_created_from_app1(sender, instance, created, **kwargs):
    if created and not instance.created_at_model:
        instance.created_at_model = 'gathering'
        instance.save()

@receiver(post_save, sender=ScheduleHarvestVehicle)
@receiver(post_delete, sender=ScheduleHarvestVehicle)
def on_vehicle_change(sender, instance, **kwargs):
    instance.schedule_harvest.recalc_weight_expected()

@receiver(post_save, sender=ScheduleHarvestContainerVehicle)
@receiver(post_delete, sender=ScheduleHarvestContainerVehicle)
def on_container_change(sender, instance, **kwargs):
    instance.schedule_harvest_vehicle.schedule_harvest.recalc_weight_expected()
