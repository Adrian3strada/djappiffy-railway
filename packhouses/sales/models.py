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
from packhouses.catalogs.models import (Market, MarketClass, Client, Maquiladora, Product, ProductSeasonKind,
                                        ProductPackaging,
                                        MarketProductSize)
from packhouses.catalogs.settings import CLIENT_KIND_CHOICES
from django.db.models import Max, Min, Q, F
from .utils import incoterms_choices
from common.base.models import Incoterm, LocalDelivery
import datetime
from .settings import ORDER_ITEMS_PRICE_CATEGORY_CHOICES, ORDER_ITEMS_PRICE_MEASURE_UNIT_CATEGORY_CHOICES



class Order(IncotermsAndLocalDeliveryMarketMixin, models.Model):
    ooid = models.PositiveIntegerField(verbose_name=_("Order ID"))
    client_category = models.CharField(max_length=20, verbose_name=_('Client category'), choices=CLIENT_KIND_CHOICES)
    maquiladora = models.ForeignKey(Maquiladora, verbose_name=_("Maquiladora"), on_delete=models.PROTECT, null=True, blank=True)
    client = models.ForeignKey(Client, verbose_name=_("Client"), on_delete=models.PROTECT)
    registration_date = models.DateField(verbose_name=_('Registration date'), default=datetime.date.today)
    shipment_date = models.DateField(verbose_name=_('Shipment date'), default=datetime.date.today)
    delivery_date = models.DateField(verbose_name=_('Delivery date'))
    local_delivery = models.ForeignKey(LocalDelivery, verbose_name=_('Local delivery'), on_delete=models.PROTECT, null=True, blank=True)
    incoterms = models.ForeignKey(Incoterm, verbose_name=_('Incoterms'), on_delete=models.PROTECT, null=True, blank=True)
    items_price_measure_unit_category = models.CharField(max_length=30, verbose_name=_('items price measure unit'), choices=ORDER_ITEMS_PRICE_MEASURE_UNIT_CATEGORY_CHOICES)
    items_price_category = models.CharField(max_length=30, verbose_name=_('items price category'), choices=ORDER_ITEMS_PRICE_CATEGORY_CHOICES)
    items_packaging = models.ForeignKey(ProductPackaging, verbose_name=_('Items packaging'), on_delete=models.PROTECT, null=True, blank=True)
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


class OrderItem(models.Model):
    """
    Nota: Como la orden tiene un cliente, y el cliente tiene mercado, podemos inferir el mercado a partir
    del cliente.
    necesitamos el product size, entonces tb necesitamos el product; que puede estar filtrado por mercado.

    el mercado lo tengo del cliente
    """

    product = models.ForeignKey(Product, verbose_name=_('Product'), on_delete=models.PROTECT)
    product_size = models.ForeignKey(MarketProductSize, verbose_name=_('Product size'), on_delete=models.PROTECT)
    product_season = models.ForeignKey(ProductSeasonKind, verbose_name=_('Product season'), on_delete=models.PROTECT)
    market_class = models.ForeignKey(MarketClass, verbose_name=_('Market class'), on_delete=models.PROTECT)
    price_category = models.CharField(max_length=20, verbose_name=_('Price category'), choices=ORDER_ITEMS_PRICE_CATEGORY_CHOICES, default='unit')
    product_packaging = models.ForeignKey(ProductPackaging, verbose_name=_('Product packaging'), on_delete=models.PROTECT, null=True, blank=False)
    quantity_per_packaging = models.PositiveIntegerField(verbose_name=_('Quantity per packaging'), default=1)
    quantity = models.DecimalField(verbose_name=_('Quantity'), max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)])
    unit_price = models.DecimalField(verbose_name=_('Price'), max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)])

    order = models.ForeignKey(Order, verbose_name=_('Order'), on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('Order item')
        verbose_name_plural = _('Order items')
