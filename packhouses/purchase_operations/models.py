from django.db import models, transaction
from common.profiles.models import UserProfile
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
from common.billing.models import TaxRegime, LegalEntityCategory
from common.base.models import ProductKind
from packhouses.packhouse_settings.models import (Bank, VehicleOwnershipKind,
                                                  PaymentKind, VehicleFuelKind, VehicleKind, VehicleBrand,
                                                  OrchardCertificationVerifier,
                                                  OrchardCertificationKind)
from packhouses.catalogs.models import (SupplyKind,Supply)
from common.settings import STATUS_CHOICES
from django.contrib.auth import get_user_model
User = get_user_model()

# Create your models here.
class Requisition(models.Model):
    ooid = models.PositiveIntegerField(
        verbose_name=_("Folio"),
        null=True, blank=True, unique=True
    )
    user = models.ForeignKey(
        User,
        verbose_name=_("User"),
        on_delete=models.PROTECT
    )
    comments = models.TextField(
        verbose_name=_("Comments"),
        null=True, blank=True
    )
    status = models.CharField(
        max_length=255,
        choices=STATUS_CHOICES,
        default='open',
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))

    organization = models.ForeignKey(
        Organization,
        verbose_name=_("Organization"),
        on_delete=models.PROTECT
    )

    def __str__(self):
        return f"{self.ooid}"

    def save(self, *args, **kwargs):
        user = kwargs.pop('user_id', None)
        if not self.ooid:
            # Usar transacción y bloqueo de fila para evitar condiciones de carrera
            with transaction.atomic():
                last_order = Requisition.objects.select_for_update().filter(organization=self.organization).order_by(
                    '-ooid').first()
                self.ooid = (last_order.ooid + 1) if last_order and last_order.ooid is not None else 1

        if user:
            self.user = user

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Requisition")
        verbose_name_plural = _("Requisitions")
        ordering = ['-ooid']
        unique_together = ['ooid', 'organization']


class RequisitionSupply(models.Model):
    requisition = models.ForeignKey(
        Requisition,
        verbose_name=_("Requisition"),
        on_delete=models.CASCADE
    )
    supply = models.ForeignKey(
        Supply,
        verbose_name=_("Supply"),
        on_delete=models.PROTECT
    )
    quantity = models.DecimalField(
        verbose_name=_("Quantity"),
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    comments = models.CharField(
        max_length=255,
        verbose_name=_("Comments"),
        null=True, blank=True
    )

    def __str__(self):
        return f"{self.supply} - {self.quantity}"

    class Meta:
        verbose_name = _("Requisition Supply")
        verbose_name_plural = _("Requisition Supplies")
