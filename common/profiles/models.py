from django.db import models
from polymorphic.models import PolymorphicModel
from organizations.models import Organization, OrganizationOwner
# from django_countries.fields import CountryField
from cities_light.models import Country
from common.base.models import ProductKind
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from common.billing.models import LegalEntityCategory
from cities_light.models import City, Country, Region

# Create your models here.

ORGANIZATION_TYPES = (('', 'Organization type'), ("producer", "Producer"), ("marketer", "Marketer"), ("exporter", "Exporter"), ("importer", "Importer"), ("government", "Government"))
User = get_user_model()


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT, primary_key=True, related_name='user_profile')
    first_name = models.CharField(max_length=255,default="")
    last_name = models.CharField(max_length=255, default="")
    phone_number = models.CharField(max_length=20, default="")
    country = models.ForeignKey(Country, verbose_name=_('Country'), default=158, on_delete=models.PROTECT,
                                null=True, blank=True, related_name='user_profiles')

    def __str__(self):
        full_name = ' '.join(filter(None, [self.first_name.strip(), self.last_name.strip()]))
        return full_name if full_name else self.user.email

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            UserProfile.objects.create(user=instance)


class OrganizationProfile(PolymorphicModel):
    name = models.CharField(max_length=255)
    legal_category = models.ForeignKey(LegalEntityCategory, verbose_name=_('Legal entity category'),
                                       on_delete=models.PROTECT, help_text=_('Legal category, must have a country selected to show that country legal categories.'))
    tax_id = models.CharField(max_length=50)
    country = models.ForeignKey(Country, verbose_name=_('Country'), on_delete=models.PROTECT, help_text=_('Country'))
    state = models.ForeignKey(Region, verbose_name=_('State'), on_delete=models.PROTECT)
    city = models.ForeignKey(City, verbose_name=_('City'), on_delete=models.PROTECT)
    district = models.CharField(max_length=255, verbose_name=_('District'), null=True, blank=True)
    neighborhood = models.CharField(max_length=255, verbose_name=_('Neighborhood'))
    postal_code = models.CharField(max_length=10, verbose_name=_('Postal code'))
    address = models.CharField(max_length=255, verbose_name=_('Address'))
    external_number = models.CharField(max_length=10, verbose_name=_('External number'))
    internal_number = models.CharField(max_length=10, verbose_name=_('Internal number'), null=True, blank=True)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    url = models.URLField(blank=True, null=True)
    products = models.ManyToManyField(ProductKind)
    logo = models.ImageField(upload_to='organization_logos/', blank=True, null=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.name} ({self.country.name} {self.tax_id})"

    class Meta:
        verbose_name = _('Organization profile')
        verbose_name_plural = _('Organization profiles')


class ProducerProfile(OrganizationProfile):

    class Meta:
        verbose_name = _('Producer profile')
        verbose_name_plural = _('Producer profiles')


class ImporterProfile(OrganizationProfile):

    class Meta:
        verbose_name = _('Importer profile')
        verbose_name_plural = _('Importer profiles')


class PackhouseExporterProfile(OrganizationProfile):

    class Meta:
        verbose_name = _('Packhouse exporter profile')
        verbose_name_plural = _('Packhouse exporter profiles')
