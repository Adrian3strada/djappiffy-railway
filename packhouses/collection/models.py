from django.db import models
from organizations.models import Organization
from cities_light.models import City, Country, Region
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django_ckeditor_5.fields import CKEditor5Field
from django.conf import settings
from common.billing.models import TaxRegime, LegalEntityCategory
from packhouses.packhouse_settings.models import Status
from packhouses.catalogs.models import ProductProvider, ProductVariety, ProductVarietySize, ProductProviderBenefactor, ProductProducerBenefactor, ServiceProviderBenefactor


# Create your models here.

class Collection(models.Model):
    status = models.ForeignKey(Status, verbose_name=_('Status'), on_delete=models.PROTECT)
    provider = models.ForeignKey(ProductProvider, verbose_name=_('Provider'), on_delete=models.PROTECT)

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='collections', verbose_name=_('organization'))
    name = models.CharField(max_length=255, verbose_name=_('name'))
    description = CKEditor5Field(verbose_name=_('description'))
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='collections', verbose_name=_('city'))
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='collections', verbose_name=_('country'))
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='collections', verbose_name=_('region'))
    address = models.CharField(max_length=255, verbose_name=_('address'))
    postal_code = models.CharField(max_length=10, verbose_name=_('postal code'))
    latitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name=_('latitude'))
    longitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name=_('longitude'))
    phone = models.CharField(max_length=20, verbose_name=_('phone'))
    email = models.EmailField(verbose_name=_('email'))
    website = models.URLField(verbose_name=_('website'))
    tax_regime = models.ForeignKey(TaxRegime, on_delete=models.CASCADE, related_name='collections', verbose_name=_('tax regime'))
    legal_entity_category = models.ForeignKey(LegalEntityCategory, on_delete=models.CASCADE, related_name='collections', verbose_name=_('legal entity category'))
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='collections', verbose_name=_('created by'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('updated at'))

    class Meta:
        verbose_name = _('collection')
        verbose_name_plural = _('collections')
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('packhouses:collection_detail', args=[self.pk])
