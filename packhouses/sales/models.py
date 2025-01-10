from django.db import models, transaction
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django_ckeditor_5.fields import CKEditor5Field
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.conf import settings
from .utils import order_status_choices, local_delivery_choices

from common.mixins import (
    IncotermsAndLocalDeliveryMarketMixin
)
from organizations.models import Organization
from cities_light.models import City, Country, Region
from packhouses.catalogs.models import Market, Country, Client
from django.db.models import Max, Min, Q, F
from .utils import incoterms_choices
from common.base.models import Incoterm, LocalDelivery



class Order(IncotermsAndLocalDeliveryMarketMixin, models.Model):
    ooid = models.PositiveIntegerField(
        verbose_name=_("Order Number"),
        null=True, blank=True, unique=True
    )
    market = models.ForeignKey(
        Market,
        verbose_name=_("Market"),
        on_delete=models.PROTECT,
    )
    country = models.ForeignKey(Country, verbose_name=_('Country'), on_delete=models.PROTECT, help_text=_(
        'Country of the client, must have a market selected to show the market countries.'))
    client = models.ForeignKey(
        Client,
        verbose_name=_("Client"),
        on_delete=models.PROTECT,
    )
    registration_date = models.DateField(
        verbose_name=_('Registration Date'),
    )
    shipment_date = models.DateField(
        verbose_name=_('Shipment Date'),
    )
    delivery_date = models.DateField(
        verbose_name=_('Delivery Date'),
    )
    local_delivery = models.ForeignKey(
        LocalDelivery,
        verbose_name=_('Local Delivery'),
        on_delete=models.PROTECT,
        null=True, blank=True
    )
    incoterms = models.ForeignKey(
        Incoterm,
        verbose_name=_('Incoterms'),
        on_delete=models.PROTECT,
        null=True, blank=True
    )
    observations = CKEditor5Field(
        blank=True,
        null=True,
        verbose_name=_('Observations'),
    )
    order_status = models.CharField(
        max_length=8,
        verbose_name=_('Status'),
        choices=order_status_choices()
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.PROTECT,
        verbose_name=_('Organization'),
    )

    def __str__(self):
        return f"#{self.ooid} - {self.client} - SHIPMENT: {self.shipment_date} - DELIVERY: {self.delivery_date}"

    def save(self, *args, **kwargs):
        if not self.ooid:
            # Usar transacción y bloqueo de fila para evitar condiciones de carrera
            with transaction.atomic():
                last_order = Order.objects.select_for_update().filter(organization=self.organization).order_by('-ooid').first()
                if last_order:
                    self.ooid = last_order.ooid + 1
                else:
                    self.ooid = 1
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')

