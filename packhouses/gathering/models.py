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
from common.billing.models import TaxRegime, LegalEntityCategory
from packhouses.catalogs.utils import vehicle_year_choices, vehicle_validate_year, get_type_choices, get_payment_choices, \
    get_vehicle_category_choices, get_provider_categories_choices, get_harvest_cutting_categories_choices
from django.core.exceptions import ValidationError
from common.base.models import ProductKind
from packhouses.packhouse_settings.models import (Bank, VehicleOwnershipKind,
                                                  PaymentKind, VehicleFuelKind, VehicleKind, VehicleBrand,
                                                  OrchardCertificationVerifier,
                                                  OrchardCertificationKind)
from packhouses.catalogs.settings import CLIENT_KIND_CHOICES
from packhouses.catalogs.models import (Provider, Gatherer, Maquiladora, Orchard, Product, ProductVariety,
                                        Market, ProductSeasonKind, ProductHarvestSizeKind, WeighingScale,
                                        HarvestingCrew, Vehicle, HarvestContainer)
from django.db.models import Max, Min
from django.db.models import Q, F
import datetime
from common.settings import STATUS_CHOICES




# Create your models here.
class ScheduleHarvest(models.Model):
    ooid = models.PositiveIntegerField(
        verbose_name=_("Harvest Number"),
        null=True, blank=True, unique=True
    )
    harvest_date = models.DateField(
        verbose_name=_('Harvest date'),
        default=datetime.date.today
    )
    product_provider = models.ForeignKey(
        Provider,
        verbose_name=_("Product provider"),
        on_delete=models.PROTECT,
        null=True, blank=True
    )
    category = models.CharField(
        max_length=255,
         choices=get_harvest_cutting_categories_choices(),
        verbose_name=_("Category"),
    )
    gatherer = models.ForeignKey(
        Gatherer,
        verbose_name=_("Gatherer"),
        on_delete=models.PROTECT,
        null=True, blank=True
    )
    maquiladora = models.ForeignKey(
        Maquiladora,
        verbose_name=_("Maquiladora"),
        on_delete=models.PROTECT,
        null=True, blank=True
    )
    product = models.ForeignKey(
        Product,
        verbose_name=_("Product"),
        on_delete=models.PROTECT,
    )
    product_variety = models.ForeignKey(
        ProductVariety,
        verbose_name=_("Product Variety"),
        on_delete=models.PROTECT,
    )
    product_season_kind = models.ForeignKey(
        ProductSeasonKind,
        verbose_name=_("Product season"),
        on_delete=models.PROTECT
    )
    product_harvest_size_kind = models.ForeignKey(
        ProductHarvestSizeKind,
        verbose_name=_("Product harvest size"),
        on_delete=models.PROTECT
    )
    orchard = models.ForeignKey(
        Orchard,
        verbose_name=_("Orchard"),
        on_delete=models.PROTECT,
    )
    market = models.ForeignKey(
        Market,
        verbose_name=_("Market"),
        on_delete=models.PROTECT,
    )
    weight_expected = models.FloatField(
        verbose_name=_("Expected Weight in kilograms"),
        validators=[MinValueValidator(0.01)]
    )
    weighing_scale = models.ForeignKey(
        WeighingScale,
        verbose_name=_("Weighing Scale"),
        on_delete=models.PROTECT,
    )
    meeting_point = models.CharField(
        max_length=255,
        verbose_name=_("Meeting Point for the Harvest Cutting"),
        null=True, blank=True
    )
    status = models.CharField(max_length=8, verbose_name=_('Status'), choices=STATUS_CHOICES, default='open')
    reason_change_date = models.TextField(blank=True, null=True, verbose_name=_('Reason for date change'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    organization = models.ForeignKey(
        Organization,
        on_delete=models.PROTECT,
        verbose_name=_('Organization'),
    )



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
    harvest_cutting = models.ForeignKey(
        ScheduleHarvest,
        verbose_name=_("Schedule Harvest"),
        on_delete=models.PROTECT,
    )
    provider = models.ForeignKey(
        Provider,
        verbose_name=_('Harvesting Crew Provider'),
        on_delete=models.PROTECT,
    )
    harvesting_crew = models.ForeignKey(
        HarvestingCrew,
        verbose_name=_("Harvesting Crew"),
        on_delete=models.PROTECT,
    )

    def __str__(self):
        return f"{self.provider.name} : {self.harvesting_crew.name}"

    class Meta:
        verbose_name = _('Harvesting Crew')
        verbose_name_plural = _('Harvesting Crews')

class ScheduleHarvestVehicle(models.Model):
    harvest_cutting = models.ForeignKey(
        ScheduleHarvest,
        verbose_name=_("Harvest Cutting"),
        on_delete=models.PROTECT,
    )
    provider = models.ForeignKey(
        Provider,
        verbose_name=_('Harvesting Crew Provider'),
        on_delete=models.PROTECT,
    )
    vehicle = models.ForeignKey(
        Vehicle,
        verbose_name=_("Vehicle"),
        on_delete=models.PROTECT,
    )
    stamp_number = models.CharField(
        max_length=20,
        verbose_name=_("Stamp Number"),
    )

    def __str__(self):
        return f"{self.vehicle.license_plate} / {self.vehicle.name}"

    class Meta:
        verbose_name = _('Vehicle')
        verbose_name_plural = _('Vehicles')



class ScheduleHarvestContainerVehicle(models.Model):
    harvest_cutting = models.ForeignKey(ScheduleHarvestVehicle, on_delete=models.CASCADE)
    harvest_cutting_container = models.ForeignKey(HarvestContainer, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return ""


