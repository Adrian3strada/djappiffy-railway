from django.db import models
from organizations.models import Organization, OrganizationOwner
# from django_countries.fields import CountryField
from cities_light.models import Country
from common.base.models import Product
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

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


class OrganizationKind(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Name'))

    def __str__(self):
        return self.name


class OrganizationProfile(models.Model):
    # kind = models.CharField(max_length=20, choices=ORGANIZATION_TYPES)
    kind = models.ForeignKey(OrganizationKind, on_delete=models.PROTECT)
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    tax_id = models.CharField(max_length=50)
    address = models.TextField()
    phone_number = models.CharField(max_length=20)
    url = models.URLField(blank=True, null=True)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    country = models.ForeignKey(Country, verbose_name=_('Country'), default=158, on_delete=models.PROTECT,
                                related_name='organization_profiles')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.name} ({self.kind}: {self.tax_id}, {self.country})"
