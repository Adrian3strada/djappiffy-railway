from django.utils.translation import gettext_lazy as _
from django.db import models
from wagtail.models import Orderable
from organizations.models import Organization
from cities_light.models import City, Country, Region
from django.db.models import Manager, QuerySet
from django.db.models import Case, When, IntegerField, Value
from django.db.models.functions import Cast
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.validators import FileExtensionValidator
from common.mixins import CleanDocumentsMixin
from django.utils.text import slugify
from .utils import get_filtered_models
from django.utils.functional import lazy
import os


# Create your models here.

from .settings import (SUPPLY_MEASURE_UNIT_CATEGORY_CHOICES, SUPPLY_CATEGORY_CHOICES,
                       PRODUCT_MEASURE_UNIT_CATEGORY_CHOICES)

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


class SupplyKind(models.Model):
    category = models.CharField(max_length=40, verbose_name=_('Category'), choices=SUPPLY_CATEGORY_CHOICES)
    name = models.CharField(max_length=100, verbose_name=_('Name'), unique=True)
    capacity_unit_category = models.CharField(max_length=30, verbose_name=_('Capacity unit category'),
                                              null=True, blank=False,
                                              help_text=_('Capacity unit to group supply kinds by his capacity'),
                                              choices=PRODUCT_MEASURE_UNIT_CATEGORY_CHOICES)
    usage_discount_unit_category = models.CharField(max_length=30, verbose_name=_('Usage discount unit category'),
                                                    help_text=_(
                                                        'Usage unit kind to measure when supplies are consumed'),
                                                    choices=SUPPLY_MEASURE_UNIT_CATEGORY_CHOICES)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Supply kind')
        verbose_name_plural = _('Supply kinds')
        ordering = ('name',)


# Ejemplo:
#   - Estándar del APEAM para AGUACATE en MÉXICO
#   - Estándar del APEAM para AGUACATE en ESTADOS UNIDOS
#   - Estándar de X para LIMÓN-MEXICANO en MÉXICO
#   - Estándar de X para LIMÓN-PERSA en ESTADOS UNIDOS
class ProductKindCountryStandard(models.Model):
    name = models.CharField(max_length=255, unique=True)
    country = models.ForeignKey(Country, verbose_name=_('Country'), on_delete=models.PROTECT)
    product_kind = models.ForeignKey(ProductKind, verbose_name=_('Product Kind'), on_delete=models.PROTECT)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    sort_order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Product kind country standard')
        verbose_name_plural = _('Product kind country standards')
        ordering = ['sort_order']
        constraints = [
            models.UniqueConstraint(fields=['product_kind', 'country'], name='countryproductsizestandard_unique_productkind_country')
            # TODO: Revisar este constraint. Valorar que para un mismo país se puede tener MÁS DE UN ESTÁNDAR
            #       para el mismo PRODUCT_KIND. Siendo el ESTÁNDAR aplicable por VARIEDAD.
        ]


# Ejemplo:
#   - Comercial, Extra, Mediano, Primera, Super, ... (de APEAM para AGUACATES en MÉXICO)
#   - 32, 36, 40, 48, 60, 70, ... (de APEAM para AGUACATES en ESTADOS UNIDOS)
#   - 300, 400, 500, 600, ... (de APEAM para LIMÓN-MEXICANO en MÉXICO)
#   - 110, 150, 175, 200, 230, 250, ... (de "ALGUNA ASOCIACIÓN" para LIMÓN-PERSA en ESTADOS UNIDOS)
class ProductKindCountryStandardSize(models.Model):
    standard = models.ForeignKey(ProductKindCountryStandard, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=10, verbose_name=_('Code'))
    description = models.CharField(max_length=255, null=True, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Product kind country standard, Size')
        verbose_name_plural = _('Product kind country standard, Sizes')
        ordering = ['sort_order']
        constraints = [
            models.UniqueConstraint(fields=['name', 'code', 'standard'], name='productkindcountrystandardsize_unique_standard_name_code')
        ]


class ProductKindCountryStandardPackaging(models.Model):
    standard = models.ForeignKey(ProductKindCountryStandard, on_delete=models.CASCADE)
    supply_kind = models.ForeignKey(SupplyKind, on_delete=models.PROTECT)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=10, verbose_name=_('Code'))
    max_product_amount = models.FloatField(verbose_name=_('Max product amount'), validators=[MinValueValidator(0.01)])
    description = models.CharField(max_length=255, null=True, blank=True)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Product kind country standard, Packaging')
        verbose_name_plural = _('Product kind country standard, Packaging')
        constraints = [
            models.UniqueConstraint(fields=['name', 'code', 'standard'], name='productkindcountrystandardpackaging_unique_name_code_standard')
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


class CapitalFramework(Orderable):
    code = models.CharField(max_length=30, verbose_name=_('Code'))
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    country = models.ForeignKey(Country, verbose_name=_('Country'), default=158, on_delete=models.PROTECT, related_name='tax_regimes')

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Capital framework')
        verbose_name_plural = _('Capital frameworks')
        ordering = ['country', 'code', 'name']
        constraints = [
            models.UniqueConstraint(fields=['code', 'name', 'country'], name='taxregime_unique_code_name_country')
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


class Currency(models.Model):
    code = models.CharField(max_length=3, verbose_name=_('Code'))
    name = models.CharField(max_length=255)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))

    def __str__(self):
        return f"{self.code} -- {self.name}"

    class Meta:
        verbose_name = _('Currency')
        verbose_name_plural = _('Currencies')
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(fields=['id', 'name'], name='currency_unique_id_name')
        ]

class CertificationEntity(models.Model):
    product_kind = models.ForeignKey(ProductKind, verbose_name=_('Product'), on_delete=models.PROTECT)
    country = models.ForeignKey(Country, verbose_name=_('Country'), null=True, blank=True, on_delete=models.PROTECT)
    entity = models.CharField(max_length=255, verbose_name=_('Certification Entity'))
    name_certification = models.CharField(max_length=255, verbose_name=_('Certification'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))

    def __str__(self):
        return f"{self.entity} -- {self.name_certification} -- {self.product_kind}"

    class Meta:
        verbose_name = _('Certification Entity')
        verbose_name_plural = _('Certification Entities')
        constraints = [
            models.UniqueConstraint(
                fields=['entity', 'name_certification'],
                name='certificationEntity_unique_certification_entity'
            )
        ]

def certification_file_path(instance, filename):

    certification_id = instance.certification_entity.id
    certification_entity = slugify(instance.certification_entity.entity.replace(" ", ""))
    certification_product_kind = slugify(instance.certification_entity.product_kind).replace(" ", "")

    file_extension = os.path.splitext(filename)[1]
    file_name = slugify(instance.name.replace(" ", ""))

    return f'certifications/requirements/{certification_id}_{certification_product_kind}_{certification_entity}_{file_name}{file_extension}'

class CertificationFormat(CleanDocumentsMixin, models.Model):
    name = models.CharField(max_length=255)
    route = models.FileField(
        upload_to=certification_file_path,
        validators=[FileExtensionValidator(allowed_extensions=['docx'])],
        verbose_name=_('Document')
        )
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    certification_entity = models.ForeignKey(CertificationEntity, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Certification Format')
        verbose_name_plural = _('Certification Formats')
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'certification_entity'],
                name='certificationFormat_unique_certification_entity_name'
            )
        ]

class Pest(models.Model):
    name = models.CharField(max_length=255, unique=True)
    inside = models.BooleanField(verbose_name=_('Inside'))
    outside = models.BooleanField(verbose_name=_('Outside'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))

    class Meta:
        verbose_name = _('Pest')
        verbose_name_plural = _('Pests')

    def __str__(self):
        return f"{self.name}"

class Disease(models.Model):
    name = models.CharField(max_length=255, unique=True)
    inside = models.BooleanField(verbose_name=_('Inside'))
    outside = models.BooleanField(verbose_name=_('Outside'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))

    class Meta:
        verbose_name = _('Disease')
        verbose_name_plural = _('Diseases')

    def __str__(self):
        return f"{self.name}"

class PestProductKind(models.Model):
    product_kind = models.ForeignKey(ProductKind, verbose_name=_('Product'), on_delete=models.PROTECT)
    pest = models.ForeignKey(Pest, verbose_name=_('Pest'), on_delete=models.PROTECT)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))

    class Meta:
        verbose_name = _('Pest Product Kind')
        verbose_name_plural = _('Pests Product Kind')

    def __str__(self):
        return f"{self.product_kind} - {self.pest}"

class DiseaseProductKind(models.Model):
    product_kind = models.ForeignKey(ProductKind, verbose_name=_('Product'), on_delete=models.PROTECT)
    disease = models.ForeignKey(Disease, verbose_name=_('Disease'), on_delete=models.PROTECT)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))

    class Meta:
        verbose_name = _('Disease Product Kind')
        verbose_name_plural = _('Diseases Product Kind')

    def __str__(self):
        return f"{self.product_kind} - {self.disease}"

def get_model_choices():
    return [(model, model) for model in get_filtered_models()]

MODEL_CHOICES = lazy(get_model_choices, list)

class FoodSafetyProcedure(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True, blank=True)
    model = models.CharField(max_length=255, unique=True, choices=MODEL_CHOICES)

    class Meta:
        verbose_name = _('Food Safety Procedure')
        verbose_name_plural = _('Food Safety Procedures')

    def __str__(self):
        return f"{self.name}"