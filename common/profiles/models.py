from django.db import models
from organizations.models import Organization, OrganizationOwner
from django_countries.fields import CountryField
from base.models import Product
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
    country = CountryField(null=True)

    def __str__(self):
        full_name = ' '.join(filter(None, [self.first_name.strip(), self.last_name.strip()]))
        return full_name if full_name else self.user.email

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            UserProfile.objects.create(user=instance)


class OrganizationProfile(models.Model):
    kind = models.CharField(max_length=20, choices=ORGANIZATION_TYPES)
    name = models.CharField(max_length=255)
    idf = models.CharField(max_length=100)  # TODO: determinar si el id fiscal debe ser único, es decir, si solo puede haber un solo registro con el mismo idf
    address = models.TextField()
    phone_number = models.CharField(max_length=20)
    url = models.URLField(blank=True, null=True)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    country = CountryField()
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.name} ({self.kind}: {self.idf}, {self.country})"
