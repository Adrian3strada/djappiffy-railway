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


class CountryProductStandardSizeManager(Manager):
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
class CountryProductStandardSize(models.Model):
    name = models.CharField(max_length=255)
    standard = models.ForeignKey(ProductKindCountryStandard, on_delete=models.CASCADE)
    description = models.CharField(max_length=255, null=True, blank=True)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))

    def __str__(self):
        return self.name

    objects = CountryProductStandardSizeManager()

    class Meta:
        verbose_name = _('Product standard, Size')
        verbose_name_plural = _('Product standard, Sizes')
        constraints = [
            models.UniqueConstraint(fields=['name', 'standard'], name='countryproductstandardsize_unique_name_standard')
        ]


class ProductStandardPackaging(models.Model):
    supply_kind = models.ForeignKey(SupplyKind, on_delete=models.PROTECT)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=10, verbose_name=_('Code'))
    max_product_amount = models.FloatField(verbose_name=_('Max product amount'), validators=[MinValueValidator(0.01)])
    description = models.CharField(max_length=255, null=True, blank=True)
    standard = models.ForeignKey(ProductKindCountryStandard, on_delete=models.CASCADE)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Product packaging standard')
        verbose_name_plural = _('Product packaging standard')
        constraints = [
            models.UniqueConstraint(fields=['name', 'code', 'standard'], name='productpackagingstandard_unique_name_code_standard')
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
    entity = models.CharField(max_length=255)
    certification = models.CharField(max_length=255)
    product_kind = models.ForeignKey(ProductKind, verbose_name=_('Product Kind'), on_delete=models.PROTECT)
    country = models.ForeignKey(Country, verbose_name=_('Country'), null=True, blank=True, on_delete=models.PROTECT)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))

    def __str__(self):
        return f"{self.entity} -- {self.certification} -- {self.product_kind}"

    class Meta:
        verbose_name = _('Certification Entity')
        verbose_name_plural = _('Certification Entities')
        constraints = [
            models.UniqueConstraint(
                fields=['entity', 'certification'], 
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

class RequirementCertification(CleanDocumentsMixin, models.Model):
    name = models.CharField(max_length=255)
    route = models.FileField(
        upload_to=certification_file_path, 
        validators=[FileExtensionValidator(allowed_extensions=['docx'])],
        verbose_name=_('Document')
        )
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    certification_entity = models.ForeignKey(CertificationEntity, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} -- {self.is_enabled} -- {self.certification_entity}"

    class Meta:
        verbose_name = _('Requirement Certification')
        verbose_name_plural = _('Requirement Certification')
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'certification_entity'], 
                name='requirementCertification_unique_certification_entity_name'
            )
        ]