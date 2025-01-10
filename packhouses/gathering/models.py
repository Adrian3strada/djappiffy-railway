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
                                                  OrchardProductClassificationKind, OrchardCertificationVerifier,
                                                  OrchardCertificationKind, SupplyKind, SupplyPresentationKind)
from packhouses.catalogs.settings import CLIENT_KIND_CHOICES
from packhouses.catalogs.models import (Provider, Gatherer, Maquiladora, Orchard, Product, ProductVariety,
                                        Market, ProductSeasonKind, ProductHarvestSizeKind, WeighingScale)
from django.db.models import Max, Min
from django.db.models import Q, F

# Create your models here.
class HarvestCutting(models.Model):
    ooid = models.PositiveIntegerField(
        verbose_name=_("Harvest Cutting Number"),
        null=True, blank=True, unique=True
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
    orchard = models.ForeignKey(
        Orchard,
        verbose_name=_("Orchard"),
        on_delete=models.PROTECT,
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
    market = models.ForeignKey(
        Market,
        verbose_name=_("Market"),
        on_delete=models.PROTECT,
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
    organization = models.ForeignKey(
        Organization,
        on_delete=models.PROTECT,
        verbose_name=_('Organization'),
    )

    def __str__(self):
        return f"Harvest Cutting {self.ooid}"

    def save(self, *args, **kwargs):
        if not self.ooid:
            # Usar transacción y bloqueo de fila para evitar condiciones de carrera
            with transaction.atomic():
                last_order = HarvestCutting.objects.select_for_update().filter(organization=self.organization).order_by('-ooid').first()
                if last_order:
                    self.ooid = last_order.ooid + 1
                else:
                    self.ooid = 1
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _('Harvest Cutting')
        verbose_name_plural = _('Harvest Cuttings')
        constraints = [
            models.UniqueConstraint(
                fields=['ooid', 'organization'],
                name='unique_harvest_cutting'
            )
        ]

class HarvestCuttingHarvestingCrew(models.Model):
    harvest_cutting = models.ForeignKey(
        HarvestCutting,
        verbose_name=_("Harvest Cutting"),
        on_delete=models.PROTECT,
    )
    person = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Person"),
        on_delete=models.PROTECT,
    )
