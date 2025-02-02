from django.utils.translation import gettext_lazy as _
from django.db import models
from wagtail.models import Orderable
from organizations.models import Organization
from cities_light.models import City, Country, Region
from django.db.models import Manager, QuerySet
from django.db.models import Case, When, IntegerField, Value
from django.db.models.functions import Cast

# Create your models here.


class ProductKind(models.Model):
    name = models.CharField(max_length=255, unique=True)
    for_packaging = models.BooleanField(default=False)
    for_orchard = models.BooleanField(default=False)
    for_eudr = models.BooleanField(default=False)
    image = models.ImageField(upload_to="base/product_kind", blank=True, null=True)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    sort_order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Product Kind')
        verbose_name_plural = _('Product Kinds')
        ordering = ['sort_order']


# Ejemplo:
#   - Estándar del APEAM para AGUACATE en MÉXICO
#   - Estándar del APEAM para AGUACATE en ESTADOS UNIDOS
#   - Estándar de X para LIMÓN-MEXICANO en MÉXICO
#   - Estándar de X para LIMÓN-PERSA en ESTADOS UNIDOS
class MarketProductStandard(models.Model):
    name = models.CharField(max_length=255, unique=True)
    product_kind = models.ForeignKey(ProductKind, verbose_name=_('Product Kind'), on_delete=models.PROTECT)
    country = models.ForeignKey(Country, verbose_name=_('Country'), on_delete=models.PROTECT)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    sort_order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Market Product Size Standard')
        verbose_name_plural = _('Market Product Size Standards')
        ordering = ['sort_order']
        constraints = [
            models.UniqueConstraint(fields=['product_kind', 'country'], name='marketproductsizestandard_unique_productkind_country')
            # TODO: Revisar este constraint. Valorar que para un mismo país se puede tener MÁS DE UN ESTÁNDAR
            #       para el mismo PRODUCT_KIND. Siendo el ESTÁNDAR aplicable por VARIEDAD.
        ]


class MarketProductStandardSizeManager(Manager):
    def get_queryset(self):
        return super().get_queryset().annotate(
            name_as_int=Case(
                When(name__regex=r'^\d+$', then=Cast('name', output_field=IntegerField())),
                default=Value(None),
                output_field=IntegerField(),
            )
        ).order_by('name_as_int', 'name')

# Ejemplo:
#   - Comercial, Extra, Mediano, Primera, Super, ... (de APEAM para AGUACATES en MÉXICO)
#   - 32, 36, 40, 48, 60, 70, ... (de APEAM para AGUACATES en ESTADOS UNIDOS)
#   - 300, 400, 500, 600, ... (de APEAM para LIMÓN-MEXICANO en MÉXICO)
#   - 110, 150, 175, 200, 230, 250, ... (de "ALGUNA ASOCIACIÓN" para LIMÓN-PERSA en ESTADOS UNIDOS)
class MarketProductStandardSize(models.Model):
    name = models.CharField(max_length=255)
    standard = models.ForeignKey(MarketProductStandard, on_delete=models.CASCADE)
    description = models.CharField(max_length=255, null=True, blank=True)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))

    def __str__(self):
        return self.name

    objects = MarketProductStandardSizeManager()

    class Meta:
        verbose_name = _('Market product standard, Size')
        verbose_name_plural = _('Market product standard, Sizes')
        constraints = [
            models.UniqueConstraint(fields=['name', 'standard'], name='marketproductstandardsize_unique_name_standard')
        ]


class MarketProductStandardPackaging(models.Model):
    name = models.CharField(max_length=255, unique=True)
    standard = models.ForeignKey(MarketProductStandard, on_delete=models.CASCADE)
    description = models.CharField(max_length=255, null=True, blank=True)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Market product standard, Packaging')
        verbose_name_plural = _('Market product standard, Packaging')
        constraints = [
            models.UniqueConstraint(fields=['name', 'standard'], name='marketproductstandardpackaging_unique_name_standard')
        ]


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
    sort_order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.code} -- {self.name}"

    class Meta:
        verbose_name = _('Incoterm')
        verbose_name_plural = _('Incoterms')
        ordering = ['sort_order']
        constraints = [
            models.UniqueConstraint(fields=['id', 'name'], name='incoterm_unique_id_name')
        ]


class LocalDelivery(models.Model):
    name = models.CharField(max_length=255, unique=True)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    sort_order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Local Delivery')
        verbose_name_plural = _('Local Deliveries')
        ordering = ['sort_order']
