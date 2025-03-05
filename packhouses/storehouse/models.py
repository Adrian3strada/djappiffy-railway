from django.core.validators import MinValueValidator
from django.db import models
from organizations.models import Organization
from django.utils.translation import gettext_lazy as _
from packhouses.purchase.models import PurchaseOrder, PurchaseOrderSupply
from packhouses.catalogs.models import Supply
from django.contrib.auth import get_user_model
import datetime
User = get_user_model()


class StorehouseEntry(models.Model):
    purchase_order = models.ForeignKey(
        PurchaseOrder,
        verbose_name=_("Purchase Order"),
        on_delete=models.PROTECT,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created at")
    )
    user = models.ForeignKey(
        User,
        verbose_name=_("User"),
        on_delete=models.PROTECT
    )
    organization = models.ForeignKey(
        Organization,
        verbose_name=_("Organization"),
        on_delete=models.PROTECT
    )

    def __str__(self):
        return f"Entry for {self.purchase_order.ooid}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.purchase_order.status = "closed"
        self.purchase_order.save(update_fields=["status"])

    class Meta:
        verbose_name = _("Storehouse Entry")
        verbose_name_plural = _("Storehouse Entries")
        ordering = ['-created_at']

class StorehouseEntrySupply(models.Model):
    storehouse_entry = models.ForeignKey(
        StorehouseEntry,
        verbose_name=_("Storehouse Entry"),
        on_delete=models.CASCADE
    )
    purchase_order_supply = models.ForeignKey(
        PurchaseOrderSupply,
        verbose_name=_("Purchase Order Supply"),
        on_delete=models.PROTECT
    )
    expected_quantity = models.DecimalField(
        verbose_name=_("Expected Quantity"),
        max_digits=10, decimal_places=2,

    )
    received_quantity = models.DecimalField(
        verbose_name=_("Received Quantity"),
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    comments = models.CharField(
        max_length=255,
        verbose_name=_("Comments"),
        null=True, blank=True
    )

    def save(self, *args, **kwargs):
        if not self.expected_quantity:
            self.expected_quantity = self.purchase_order_supply.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.purchase_order_supply.requisition_supply.supply}"

    class Meta:
        verbose_name = _("Storehouse Entry Supply")
        verbose_name_plural = _("Storehouse Entry Supplies")
        constraints = [
            models.UniqueConstraint(fields=['storehouse_entry', 'purchase_order_supply'], name='unique_storehouse_entry_supply')
        ]
