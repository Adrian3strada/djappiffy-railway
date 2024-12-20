from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from cities_light.models import City, Country, Region
from organizations.models import Organization, OrganizationOwner
from polymorphic.models import PolymorphicModel

from common.base.models import ProductKind
from common.billing.models import LegalEntityCategory


ORGANIZATION_TYPES = (
    ('', 'Organization type'),
    ("producer", "Producer"),
    ("marketer", "Marketer"),
    ("exporter", "Exporter"),
    ("importer", "Importer"),
    ("government", "Government")
)
User = get_user_model()


class UserProfile(models.Model):
    ### Related User model
    user = models.OneToOneField(
        User,
        primary_key=True,
        on_delete=models.PROTECT,
        verbose_name=_('User profile'),
        related_name='user_profile',
    )

    ### User's Name
    first_name = models.CharField(
        max_length=255,
        default="",
        verbose_name=_('First name'),
    )
    last_name = models.CharField(
        max_length=255,
        default="",
        verbose_name=_('Last name'),
    )

    ### User's Country
    country = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        default=158,    # Mexico's ID from 'cities_light'
        blank=True,
        null=True,
        verbose_name=_('Country'),
        related_name='user_profiles',
    )

    ### Contact info
    phone_number = models.CharField(
        max_length=20,
        default="",
        verbose_name=_('Phone number'),
        )

    def __str__(self):
        full_name = ' '.join(filter(None, [self.first_name.strip(), self.last_name.strip()]))
        return full_name if full_name else self.user.email

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            UserProfile.objects.create(user=instance)


class OrganizationProfile(PolymorphicModel):
    ### Identification Fields
    name = models.CharField(
        max_length=255,
        verbose_name=_('Name'),
        help_text=_('Name of the Organization.'),
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        null=True,
        verbose_name=_('Organization'),
        help_text=_('Linked Organization to this profile.'),
    )

    ### Legals
    legal_category = models.ForeignKey(
        LegalEntityCategory,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        verbose_name=_('Legal entity category'),
        help_text=_('Legal category, must have a country selected to show that country legal categories.'),
    )
    tax_id = models.CharField(
        max_length=50,
    )

    ### Referenced fields about localization
    country = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        verbose_name=_('Country'),
        help_text=_('Country'),
    )
    state = models.ForeignKey(
        Region,
        on_delete=models.PROTECT,
        verbose_name=_('State'),
        help_text=_('State'),
    )
    city = models.ForeignKey(
        City,
        on_delete=models.PROTECT,
        verbose_name=_('City'),
        help_text=_('City'),
    )

    ### Non-referenced fields about localization
    district = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_('District'),
    )
    neighborhood = models.CharField(
        max_length=255,
        verbose_name=_('Neighborhood'),
    )
    postal_code = models.CharField(
        max_length=10,
        verbose_name=_('Postal code'),
    )
    address = models.CharField(
        max_length=255,
        verbose_name=_('Address'),
    )
    external_number = models.CharField(
        max_length=10,
        verbose_name=_('External number'),
    )
    internal_number = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name=_('Internal number'),
    )

    ### Contact fields
    email = models.EmailField(
        # TO-DO?: Check non-duplication with other Organization
        #           and other Users
        verbose_name=_('Email address'),
    )
    phone_number = models.CharField(
        max_length=20,
        verbose_name=_('Phone number'),
    )
    url = models.URLField(
        blank=True,
        null=True,
        verbose_name=_('URL'),
    )

    ### Logo
    logo = models.ImageField(
        blank=True,
        null=True,
        upload_to='organization_logos/',
    )

    ### Products
    products = models.ManyToManyField(
        ProductKind,
        blank=False,
    )

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
    packhouse_number = models.CharField(max_length=50, verbose_name=_('Packhouse number'))
    registry_number = models.CharField(max_length=50, verbose_name=_('Registry number'))
    sanitary_registry = models.CharField(max_length=50, verbose_name=_('Sanitary registry'))
    chain_of_custody = models.CharField(max_length=150, verbose_name=_('Chain of custody'))
    hostname = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        unique=True,
        verbose_name=_('Hostname'),
    )

    def clean(self):
        """
        Override the clean method to ensure uniqueness only if hostname is set.
        """
        if self.hostname:
            if PackhouseExporterProfile.objects.filter(hostname=self.hostname).exclude(id=self.id).exists():
                raise ValidationError(f"The hostname '{self.hostname}' is already taken.")
        super().clean()

    class Meta:
        verbose_name = _('Packhouse exporter profile')
        verbose_name_plural = _('Packhouse exporter profiles')


class TradeExporterProfile(OrganizationProfile):

    class Meta:
        verbose_name = _('Trade exporter profile')
        verbose_name_plural = _('Trade exporter profiles')
