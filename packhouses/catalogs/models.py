from django.db import models
from organizations.models import Organization
from cities_light.models import City, Country, Region
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django_ckeditor_5.fields import CKEditor5Field
from django.conf import settings

# Create your models here.


class Market(models.Model):
    name = models.CharField(max_length=100)
    management_cost_per_kg = models.FloatField(validators=[MinValueValidator(0.01)], help_text=_('Cost generated per Kg for product management and packaging'))
    is_foreign = models.BooleanField(default=False, help_text=_('Conditional for performance reporting to separate foreign and domestic markets; separation in the report of volume by mass and customer addresses'))
    is_mixable = models.BooleanField(default=False, help_text=_('Conditional that does not allow mixing fruit with other markets'))
    label_language = models.CharField(max_length=100, choices=settings.LANGUAGES, default='es')
    address_label = CKEditor5Field(blank=True, null=True, verbose_name=_('Address on label with the packing house address'), help_text=_('Leave blank to use the default address defined in the organization'))
    is_enabled = models.BooleanField(default=True)
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Market')
        verbose_name_plural = _('Markets')
        unique_together = ('name', 'organization')


class KGCostMarket(models.Model):
    name = models.CharField(max_length=100)
    cost_per_kg = models.FloatField(validators=[MinValueValidator(0.01)])
    is_enabled = models.BooleanField(default=False)
    market = models.ForeignKey(Market, verbose_name=_('Market'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('KG Cost Market')
        verbose_name_plural = _('KG Cost Markets')
        unique_together = ('name', 'market')


class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')
        unique_together = ('name', 'organization')


class ProductSizeKind(models.Model):
    pass

class ProductVariety(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    product = models.ForeignKey(Product, verbose_name=_('Product'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.product.name} : {self.name}"

    class Meta:
        verbose_name = _('Product Variety')
        verbose_name_plural = _('Product Varieties')
        unique_together = ('name', 'product')


class ProductVarietyKind(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.product_variety.product.name} : {self.product_variety.name} : {self.name}"

    class Meta:
        verbose_name = _('Product Variety Kind')
        verbose_name_plural = _('Product Variety Kinds')
        unique_together = ('name', 'product_variety')


class ProductVarietySize(models.Model):
    market = models.ForeignKey(Market, verbose_name=_('Market'), on_delete=models.PROTECT)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    product_variety = models.ForeignKey(ProductVariety, verbose_name=_('Product Variety'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.product_variety.product.name} : {self.product_variety.name} : {self.name}"

    class Meta:
        verbose_name = _('Product Variety Size')
        verbose_name_plural = _('Product Variety Sizes')
        unique_together = ('name', 'product_variety')
