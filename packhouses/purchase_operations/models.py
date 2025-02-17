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
from common.base.models import ProductKind, CapitalFramework, LegalEntityCategory, Currency
from packhouses.packhouse_settings.models import (Bank, VehicleOwnershipKind,
                                                  PaymentKind, VehicleFuelKind, VehicleKind, VehicleBrand,
                                                  OrchardCertificationVerifier,
                                                  OrchardCertificationKind)
from packhouses.catalogs.models import (SupplyKind,Supply,Provider)
from common.settings import STATUS_CHOICES
from django.contrib.auth import get_user_model
import datetime
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
        constraints = [
            models.UniqueConstraint(fields=['ooid', 'organization'], name='unique_ooid_organization')
        ]


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
    is_enabled = models.BooleanField(
        verbose_name=_("Is enabled"),
        default=True
    )

    def __str__(self):
        return f"(Req. {self.requisition.ooid}) - {self.supply} - {self.quantity}"

    class Meta:
        verbose_name = _("Requisition Supply")
        verbose_name_plural = _("Requisition Supplies")
        ordering = ['-requisition']


class PurchaseOrder(models.Model):
    ooid = models.PositiveIntegerField(
        verbose_name=_("Folio"),
        null=True, blank=True, unique=True
    )
    user = models.ForeignKey(
        User,
        verbose_name=_("User"),
        on_delete=models.PROTECT
    )
    provider = models.ForeignKey(
        Provider,
        verbose_name=_("Provider"),
        on_delete=models.PROTECT
    )
    payment_date = models.DateField(
        verbose_name=_('Payment date'),
        default=datetime.date.today
    )
    currency = models.ForeignKey(
        Currency,
        verbose_name=_("Currency"),
        on_delete=models.PROTECT
    )
    tax = models.DecimalField(
        max_digits=5, decimal_places=2,
        verbose_name=_("Tax (%)"),
        null=True, blank = True
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

    def save(self, *args, **kwargs):
        user = kwargs.pop('user_id', None)
        if not self.ooid:
            # Usar transacción y bloqueo de fila para evitar condiciones de carrera
            with transaction.atomic():
                last_order = PurchaseOrder.objects.select_for_update().filter(organization=self.organization).order_by(
                    '-ooid').first()
                self.ooid = (last_order.ooid + 1) if last_order and last_order.ooid is not None else 1

        if user:
            self.user = user

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.ooid}"

    class Meta:
        verbose_name = _("Purchase Order")
        verbose_name_plural = _("Purchase Orders")
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['ooid', 'organization'], name='unique_ooid_purchase_order_organization')
        ]

class PurchaseOrderSupply(models.Model):
    purchase_order = models.ForeignKey(
        PurchaseOrder,
        verbose_name=_("Purchase Order"),
        on_delete=models.CASCADE
    )
    requisition_supply = models.ForeignKey(
        RequisitionSupply,
        verbose_name=_("Supply"),
        on_delete=models.PROTECT
    )
    quantity = models.DecimalField(
        verbose_name=_("Quantity"),
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    unit_price = models.DecimalField(
        verbose_name=_("Unit Price"),
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    total_price = models.DecimalField(
        verbose_name=_("Total Price"),
        max_digits=12, decimal_places=2,
        editable=False
    )
    comments = models.CharField(
        max_length=255,
        verbose_name=_("Comments"),
        null=True, blank=True
    )

    def __str__(self):
        return f"{self.requisition_supply} - {self.quantity}"

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Purchase Order Supply")
        verbose_name_plural = _("Purchase Order Supplies")
        constraints = [
            models.UniqueConstraint(fields=['purchase_order', 'requisition_supply'], name='unique_purchase_order_supply')
        ]
