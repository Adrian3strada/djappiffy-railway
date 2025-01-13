from django.db import models, transaction
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django_ckeditor_5.fields import CKEditor5Field
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.conf import settings
from .utils import order_status_choices, local_delivery_choices
from common.settings import STATUS_CHOICES

from common.mixins import (
    IncotermsAndLocalDeliveryMarketMixin
)
from organizations.models import Organization
from cities_light.models import City, Country, Region
from packhouses.catalogs.models import Market, Country, Client, Maquiladora
from django.db.models import Max, Min, Q, F
from .utils import incoterms_choices
from common.base.models import Incoterm, LocalDelivery
import datetime

from ..catalogs.settings import CLIENT_KIND_CHOICES


class Order(IncotermsAndLocalDeliveryMarketMixin, models.Model):
    ooid = models.PositiveIntegerField(verbose_name=_("Order Number"))
    client_category = models.CharField(max_length=20, verbose_name=_('Client category'), choices=CLIENT_KIND_CHOICES)
    maquiladora = models.ForeignKey(Maquiladora, verbose_name=_("Maquiladora"), on_delete=models.PROTECT, null=True, blank=True)
    client = models.ForeignKey(Client, verbose_name=_("Client"), on_delete=models.PROTECT)
    registration_date = models.DateField(verbose_name=_('Registration date'), default=datetime.date.today)
    shipment_date = models.DateField(verbose_name=_('Shipment date'), default=datetime.date.today)
    delivery_date = models.DateField(verbose_name=_('Delivery date'))
    local_delivery = models.ForeignKey(LocalDelivery, verbose_name=_('Local delivery'), on_delete=models.PROTECT, null=True, blank=True)
    incoterms = models.ForeignKey(Incoterm, verbose_name=_('Incoterms'), on_delete=models.PROTECT, null=True, blank=True)
    observations = CKEditor5Field(blank=True, null=True, verbose_name=_('Observations'))
    status = models.CharField(max_length=8, verbose_name=_('Status'), choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT, verbose_name=_('Organization'))

    def __str__(self):
        return f"#{self.ooid} - {self.client} - SHIPMENT: {self.shipment_date} - DELIVERY: {self.delivery_date}"

    def save(self, *args, **kwargs):
        if not self.pk:
            # Usar transacción y bloqueo de fila para evitar condiciones de carrera
            with transaction.atomic():
                last_order = Order.objects.select_for_update().filter(organization=self.organization).order_by('ooid').last()
                self.ooid = last_order.ooid + 1 if last_order else 1
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')
        ordering = ['-ooid']
        constraints = [
            models.UniqueConstraint(fields=['ooid', 'organization'], name='order_unique_ooid_organization')
        ]

