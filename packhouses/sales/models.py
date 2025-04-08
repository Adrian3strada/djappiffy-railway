from django.db import models, transaction
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django_ckeditor_5.fields import CKEditor5Field
from polymorphic.models import PolymorphicModel

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
from packhouses.catalogs.models import (Market, ProductMarketClass, Client, Maquiladora, Product, ProductVariety,
                                        ProductPhenologyKind,
                                        Packaging, ProductPackaging, ProductPackagingPallet,
                                        ProductSize, ProductRipeness)
from packhouses.catalogs.settings import CLIENT_KIND_CHOICES
from django.db.models import Max, Min, Q, F, Sum
from .utils import incoterms_choices
from common.base.models import Incoterm, LocalDelivery
import datetime
from .settings import ORDER_ITEMS_KIND_CHOICES, ORDER_ITEMS_PRICING_CHOICES



class Order(IncotermsAndLocalDeliveryMarketMixin, models.Model):
    ooid = models.PositiveIntegerField(verbose_name=_("Order ID"))
    client_category = models.CharField(max_length=20, verbose_name=_('Client category'), choices=CLIENT_KIND_CHOICES)
    maquiladora = models.ForeignKey(Maquiladora, verbose_name=_("Maquiladora"), on_delete=models.PROTECT, null=True, blank=False)
    client = models.ForeignKey(Client, verbose_name=_("Client"), on_delete=models.PROTECT)
    local_delivery = models.ForeignKey(LocalDelivery, verbose_name=_('Local delivery'), on_delete=models.PROTECT, null=True, blank=False)
    incoterms = models.ForeignKey(Incoterm, verbose_name=_('Incoterms'), on_delete=models.PROTECT, null=True, blank=False)
    registration_date = models.DateField(verbose_name=_('Registration date'), default=datetime.date.today)
    shipment_date = models.DateField(verbose_name=_('Shipment date'), default=datetime.date.today)
    delivery_date = models.DateField(verbose_name=_('Delivery date'))
    product = models.ForeignKey(Product, verbose_name=_('Product'), on_delete=models.PROTECT)
    product_variety = models.ForeignKey(ProductVariety, verbose_name=_('Product variety'), on_delete=models.PROTECT)
    order_items_kind = models.CharField(max_length=30, verbose_name=_('Order items kind'), choices=ORDER_ITEMS_KIND_CHOICES)
    observations = CKEditor5Field(blank=True, null=True, verbose_name=_('Observations'))
    status = models.CharField(max_length=8, verbose_name=_('Status'), choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT, verbose_name=_('Organization'))

    @property
    def items_count(self):
        if self.order_items_kind == 'product_weight':
            return self.orderitemweight_set.all().count()
        elif self.order_items_kind == 'product_packaging':
            return self.orderitempackaging_set.all().count()
        elif self.order_items_kind == 'product_pallet':
            return self.orderitempallet_set.all().count()
        else:
            return 0

    @property
    def items_total_price(self):
        if self.order_items_kind == 'product_weight':
            return self.orderitemweight_set.aggregate(total_price=Sum('price'))['total_price']
        elif self.order_items_kind == 'product_packaging':
            return self.orderitempackaging_set.aggregate(total_price=Sum('price'))['total_price']
        elif self.order_items_kind == 'product_pallet':
            return self.orderitempallet_set.aggregate(total_price=Sum('price'))['total_price']
        else:
            return 0

    @receiver(post_save, sender='sales.Order')
    def clean_order_items(sender, instance, **kwargs):
        if instance.order_items_kind == 'product_weight':
            instance.orderitempackaging_set.all().delete()
            instance.orderitempallet_set.all().delete()
        elif instance.order_items_kind == 'product_packaging':
            instance.orderitemweight_set.all().delete()
            instance.orderitempallet_set.all().delete()
        elif instance.order_items_kind == 'product_pallet':
            instance.orderitemweight_set.all().delete()
            instance.orderitempackaging_set.all().delete()
        else:
            instance.orderitemweight_set.all().delete()
            instance.orderitempackaging_set.all().delete()
            instance.orderitempallet_set.all().delete()

    def __str__(self):
        return f"#{self.ooid} - {self.client} - SHIPMENT: {self.shipment_date} - DELIVERY: {self.delivery_date}"

    def save(self, *args, **kwargs):
        if not self.pk:
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


class OrderItemWeight(models.Model):
    product_size = models.ForeignKey(ProductSize, verbose_name=_('Product size'), on_delete=models.PROTECT)
    product_phenology = models.ForeignKey(ProductPhenologyKind, verbose_name=_('Product phenology'), on_delete=models.PROTECT, null=True, blank=False)
    product_market_class = models.ForeignKey(ProductMarketClass, verbose_name=_('Product market class'), on_delete=models.PROTECT, null=True, blank=False)
    product_ripeness = models.ForeignKey(ProductRipeness, verbose_name=_('Product ripeness'), on_delete=models.PROTECT, null=True, blank=True)
    quantity = models.FloatField(verbose_name=_('Quantity'), validators=[MinValueValidator(0.01)])
    unit_price = models.FloatField(verbose_name=_('Unit price'), validators=[MinValueValidator(0.01)])
    amount_price = models.DecimalField(verbose_name=_('Amount price'), max_digits=20, decimal_places=2, validators=[MinValueValidator(0.01)], null=True, blank=False)
    order = models.ForeignKey(Order, verbose_name=_('Order'), on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.pk}"

    def clean(self):
        self.amount_price = self.unit_price * self.quantity if self.unit_price and self.quantity else 0
        super().clean()

    class Meta:
        verbose_name = _('Order item by weight')
        verbose_name_plural = _('Order items by weight')


class OrderItemPackaging(models.Model):
    pricing_by = models.CharField(max_length=30, verbose_name=_('Pricing by'), choices=ORDER_ITEMS_PRICING_CHOICES)
    product_size = models.ForeignKey(ProductSize, verbose_name=_('Product size'), on_delete=models.PROTECT, limit_choices_to={'category__in': ['size', 'mix']})
    product_phenology = models.ForeignKey(ProductPhenologyKind, verbose_name=_('Product phenology'), on_delete=models.PROTECT, null=True, blank=False)
    product_market_class = models.ForeignKey(ProductMarketClass, verbose_name=_('Product market class'), on_delete=models.PROTECT, null=True, blank=False)
    product_ripeness = models.ForeignKey(ProductRipeness, verbose_name=_('Product ripeness'), on_delete=models.PROTECT, null=True, blank=True)
    product_packaging = models.ForeignKey(ProductPackaging, verbose_name=_('Product packaging'), on_delete=models.PROTECT)
    product_weight_per_packaging = models.FloatField(verbose_name=_('Product weight per packaging'), validators=[MinValueValidator(0.01)])
    product_presentations_per_packaging = models.PositiveIntegerField(
        verbose_name=_('Product presentations per packaging'), null=True, blank=False)
    product_pieces_per_presentation = models.PositiveIntegerField(
        verbose_name=_('Product pieces per presentation'), null=True, blank=False)
    quantity = models.PositiveIntegerField(verbose_name=_('Quantity'), validators=[MinValueValidator(1)])
    unit_price = models.FloatField(verbose_name=_('Unit price'), validators=[MinValueValidator(0.01)])
    amount_price = models.DecimalField(verbose_name=_('Amount price'), max_digits=20, decimal_places=2, null=True, blank=False)
    order = models.ForeignKey(Order, verbose_name=_('Order'), on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.pk}"

    def clean(self):
        self.amount_price = self.unit_price * self.quantity if self.unit_price and self.quantity else 0
        super().clean()

    class Meta:
        verbose_name = _('Order item by packaging')
        verbose_name_plural = _('Order items by packaging')


class OrderItemPallet(models.Model):
    pricing_by = models.CharField(max_length=30, verbose_name=_('Pricing by'), choices=ORDER_ITEMS_PRICING_CHOICES)
    product_size = models.ForeignKey(ProductSize, verbose_name=_('Product size'), on_delete=models.PROTECT)
    product_phenology = models.ForeignKey(ProductPhenologyKind, verbose_name=_('Product phenology'), on_delete=models.PROTECT, null=True, blank=False)
    product_market_class = models.ForeignKey(ProductMarketClass, verbose_name=_('Product market class'), on_delete=models.PROTECT, null=True, blank=False)
    product_ripeness = models.ForeignKey(ProductRipeness, verbose_name=_('Product ripeness'), on_delete=models.PROTECT, null=True, blank=True)
    product_packaging = models.ForeignKey(ProductPackaging, verbose_name=_('Product packaging'),
                                          on_delete=models.PROTECT, null=True, blank=False)
    product_weight_per_packaging = models.FloatField(verbose_name=_('Product weight per packaging'),
                                                     validators=[MinValueValidator(0.01)])
    product_presentations_per_packaging = models.PositiveIntegerField(
        verbose_name=_('Product presentations per packaging'), null=True, blank=False)
    product_pieces_per_presentation = models.PositiveIntegerField(
        verbose_name=_('Product pieces per presentation'), null=True, blank=False)
    product_packaging_pallet = models.ForeignKey(ProductPackagingPallet, verbose_name=_('Product packaging pallet'),
                                                 on_delete=models.PROTECT, null=True, blank=False)
    product_packaging_quantity_per_pallet = models.PositiveIntegerField(
        verbose_name=_('Product packaging quantity per pallet'),
        validators=[MinValueValidator(1)], null=True, blank=False)
    quantity = models.PositiveIntegerField(verbose_name=_('Quantity'), validators=[MinValueValidator(1)])
    unit_price = models.FloatField(verbose_name=_('Unit price'), validators=[MinValueValidator(0.01)])
    amount_price = models.DecimalField(verbose_name=_('Amount price'), max_digits=20, decimal_places=2, null=True, blank=False)
    order = models.ForeignKey(Order, verbose_name=_('Order'), on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.pk}"

    class Meta:
        verbose_name = _('Order item by pallet')
        verbose_name_plural = _('Order items by pallet')


class OrderItemBak(models.Model):
    product_size = models.ForeignKey(ProductSize, verbose_name=_('Product size'), on_delete=models.PROTECT)
    product_phenology = models.ForeignKey(ProductPhenologyKind, verbose_name=_('Product phenology'), on_delete=models.PROTECT, null=True, blank=False)
    product_market_class = models.ForeignKey(ProductMarketClass, verbose_name=_('Product market class'), on_delete=models.PROTECT, null=True, blank=False)
    product_ripeness = models.ForeignKey(ProductRipeness, verbose_name=_('Product ripeness'), on_delete=models.PROTECT, null=True, blank=True)
    product_packaging = models.ForeignKey(ProductPackaging, verbose_name=_('Product packaging'), on_delete=models.PROTECT, null=True, blank=False)
    product_amount_per_packaging = models.PositiveIntegerField(verbose_name=_('Product amount per packaging'), validators=[MinValueValidator(1)], null=True, blank=False)
    product_packaging_pallet = models.ForeignKey(ProductPackagingPallet, verbose_name=_('Product packaging pallet'),
                                                 on_delete=models.PROTECT, null=True, blank=False)
    product_packaging_quantity_per_pallet = models.PositiveIntegerField(
        verbose_name=_('Product packaging quantity per pallet'),
        validators=[MinValueValidator(1)], null=True, blank=False)
    items_quantity = models.PositiveIntegerField(verbose_name=_('Items quantity'), validators=[MinValueValidator(1)])
    unit_price = models.FloatField(verbose_name=_('Unit price'), validators=[MinValueValidator(0.01)])
    price = models.DecimalField(verbose_name=_('Price'), max_digits=13, decimal_places=2, validators=[MinValueValidator(0.01)], null=False, blank=True)
    order = models.ForeignKey(Order, verbose_name=_('Order'), on_delete=models.CASCADE)

    def __str__(self):
        if self.order and self.order.ooid:
            return f"#{self.order.ooid} - {self.pk}"
        return f"{self.pk}"

    def clean1(self):
        if self.product_size.category in ['waste', 'biomass']:
            self.price = self.unit_price * self.items_quantity

        if self.product_size.category in ['mix']:
            self.price = self.unit_price * self.product_amount_per_packaging * self.items_quantity

        if self.product_size.category in ['size']:
            print("self.product_packaging.category", self.product_packaging.category)
            if self.product_packaging.category == 'packaging':
                self.price = self.unit_price * self.product_amount_per_packaging * self.items_quantity
            if self.product_packaging.category == 'presentation':
                self.price = self.unit_price * self.product_packaging.product_presentations_per_packaging * self.quantity

        super().clean()

    class Meta:
        verbose_name = _('Order item bak')
        verbose_name_plural = _('Order items bak')
