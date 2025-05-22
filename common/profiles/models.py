from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from cities_light.models import Country, Region, SubRegion, City
from organizations.models import Organization, OrganizationUser
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
    organization = models.OneToOneField(
        Organization,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_('Organization'),
        help_text=_('Linked Organization to this profile.'),
    )

    ### Referenced fields about localization
    country = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        verbose_name=_('Country'),
    )
    state = models.ForeignKey(
        Region,
        on_delete=models.PROTECT,
        verbose_name=_('State'),
    )
    city = models.ForeignKey(
        SubRegion,
        on_delete=models.PROTECT,
        verbose_name=_('City'),
    )
    district = models.ForeignKey(
        City,
        on_delete=models.PROTECT,
        verbose_name=_('District'),
        blank=True,
        null=True
    )
    postal_code = models.CharField(
        max_length=10,
        verbose_name=_('Postal code'),
    )
    neighborhood = models.CharField(
        max_length=255,
        verbose_name=_('Neighborhood'),
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
    product_kinds = models.ManyToManyField(
        ProductKind,
        blank=True,
        verbose_name=_('Product kinds'),
    )

    def __str__(self):
        return f"{self.name} ({self.country.name} {self.tax_id})"

    class Meta:
        verbose_name = _('Organization profile')
        verbose_name_plural = _('Organization profiles')
        constraints = [
            models.UniqueConstraint(fields=['name', 'tax_id'],
                                    name='organizationprofile_unique_name_tax_id'),
        ]

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

    def save(self, *args, **kwargs):
        if not self.organization:
            organization = Organization.objects.create(name=self.name)
            self.organization = organization
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _('Packhouse exporter profile')
        verbose_name_plural = _('Packhouse exporter profiles')

class PackhouseExporterSetting(models.Model):
    profile = models.OneToOneField(PackhouseExporterProfile, on_delete=models.CASCADE, verbose_name=_('Packhouse exporter profile'))
    product_kinds = models.ManyToManyField(ProductKind, blank=True, verbose_name=_('Product kinds'))
    hostname = models.CharField(max_length=255, blank=False, null=False, verbose_name=_('Hostname'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    user_organization = models.OneToOneField(OrganizationUser, on_delete=models.PROTECT, null=True, blank=True, verbose_name=_('User owner'))

    def clean(self):
        """
        Override the clean method to ensure uniqueness only if hostname is set.
        """
        if self.hostname:
            if PackhouseExporterSetting.objects.filter(hostname=self.hostname).exclude(id=self.id).exists():
                raise ValidationError(f"The hostname '{self.hostname}' is already taken.")
        super().clean()

    def __str__(self):
        return f"{self.profile}"

    class Meta:
        verbose_name = _('Packhouse exporter settings')
        verbose_name_plural = _('Packhouse exporter settings')


class TradeExporterProfile(OrganizationProfile):

    class Meta:
        verbose_name = _('Trade exporter profile')
        verbose_name_plural = _('Trade exporter profiles')


class EudrOperatorProfile(OrganizationProfile):

    eori_number = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        verbose_name=_("EORI number"),
        help_text=_("Required for importers"),
    )

    class Meta: 
        verbose_name = _('EUDR operator profile')
        verbose_name_plural = _('EUDR operator profiles')
