from django.db import models
from wagtail.models import Orderable
from django_countries.fields import CountryField

# Create your models here.


class TaxRegimeCategory(Orderable):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Categoría de Regimen Fiscal'
        verbose_name_plural = 'Categorías de Regímenes Fiscales'


class TaxRegime(Orderable):
    code = models.CharField(max_length=30)
    name = models.CharField(max_length=255)
    # category = models.ForeignKey(TaxRegimeCategory, on_delete=models.PROTECT)
    country = CountryField(default='MX', editable=False)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = 'Regimen Fiscal'
        verbose_name_plural = 'Regímenes Fiscales'
        unique_together = ('code', 'name', 'country')
        # TODO: poner lazy _ para traducción


class LegalEntityCategory(Orderable):
    name = models.CharField(max_length=255)
    country = CountryField(default='MX', editable=False)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = 'Regimen Capital'
        verbose_name_plural = 'Regímenes Capitales'
        unique_together = ('name', 'country')


class LegalEntity(Orderable):
    tax_regime = models.ForeignKey(TaxRegime, on_delete=models.PROTECT)
    category = models.ForeignKey(LegalEntityCategory, on_delete=models.PROTECT)
    name = models.CharField(max_length=255)
    tax_id = models.CharField(max_length=30)
    country = CountryField(default='MX', editable=False)
    postal_code = models.CharField(max_length=10)
    state = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    district = models.CharField(max_length=255)
    neighborhood = models.CharField(max_length=255)
    street = models.CharField(max_length=255)
    ext_number = models.CharField(max_length=10)
    int_number = models.CharField(max_length=10)
    phone = models.CharField(max_length=15)
    email = models.EmailField()


    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = 'Entidad Legal'
        verbose_name_plural = 'Entidades Legales'
        unique_together = ('code', 'name', 'country')

