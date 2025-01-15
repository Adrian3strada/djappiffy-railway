from django.utils.translation import gettext_lazy as _
from django.db import models
from wagtail.models import Orderable
from organizations.models import Organization
from cities_light.models import City, Country, Region

# Create your models here.


class ProductKind(models.Model):
    name = models.CharField(max_length=255, unique=True)
    for_packaging = models.BooleanField(default=False)
    for_orchard = models.BooleanField(default=False)
    for_eudr = models.BooleanField(default=False)
    image = models.ImageField(upload_to="base/product_kind", blank=True, null=True)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    ordering = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Product Kind')
        verbose_name_plural = _('Product Kinds')
        ordering = ['ordering']


class MarketProductSizeStandard(models.Model):
    name = models.CharField(max_length=255, unique=True)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    ordering = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

    def clean(self):
        if self.name:
            self.name = self.name.strip().upper()

    class Meta:
        verbose_name = _('Market Product Size Standard')
        verbose_name_plural = _('Market Product Size Standards')
        ordering = ['ordering']


class MarketProductSizeStandardUnit(models.Model):
    standard = models.ForeignKey(MarketProductSizeStandard, on_delete=models.CASCADE)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    ordering = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = _('Market Product Size Standard Unit')
        verbose_name_plural = _('Market Product Size Standard Units')
        ordering = ['ordering']


class MarketProductSizeStandardUnitSize(models.Model):
    standard_unit = models.ForeignKey(MarketProductSizeStandardUnit, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    alias = models.CharField(max_length=10)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    ordering = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = _('Market Product Size Standard Unit')
        verbose_name_plural = _('Market Product Size Standard Units')
        ordering = ['ordering']

class LegalEntityCategory(models.Model):
    code = models.CharField(max_length=30, verbose_name=_('Code'))
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    country = models.ForeignKey(Country, verbose_name=_('Country'), default=158, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Legal Entity Category')
        verbose_name_plural = _('Legal Entity Categories')
        ordering = ['country', 'code', 'name']
        constraints = [
            models.UniqueConstraint(fields=['code', 'name', 'country'], name='legalentitycategory_unique_code_name_country')
        ]


class Incoterm(models.Model):
    code = models.CharField(max_length=4, verbose_name=_('Code'))
    name = models.CharField(max_length=255)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    ordering = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.code} -- {self.name}"

    class Meta:
        verbose_name = _('Incoterm')
        verbose_name_plural = _('Incoterms')
        ordering = ['ordering']
        constraints = [
            models.UniqueConstraint(fields=['id', 'name'], name='incoterm_unique_id_name')
        ]


class LocalDelivery(models.Model):
    name = models.CharField(max_length=255, unique=True)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    ordering = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Local Delivery')
        verbose_name_plural = _('Local Deliveries')
        ordering = ['ordering']
