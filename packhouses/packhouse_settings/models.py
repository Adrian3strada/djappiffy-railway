from django.db import models
from organizations.models import Organization
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from common.mixins import CleanNameAndOrganizationMixin, CleanNameAndMarketMixin

# Create your models here.


class Status(CleanNameAndOrganizationMixin, models.Model):
    name = models.CharField(max_length=255, verbose_name=_('name'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT, verbose_name=_('Organization'))
    order = models.PositiveIntegerField(default=0, verbose_name=_('Order'))

    class Meta:
        verbose_name = _('Status')
        verbose_name_plural = _('Statuses')
        ordering = ['organization', 'order']
        constraints = [
            models.UniqueConstraint(fields=['name', 'organization'], name='status_unique_name_organization'),
        ]


class ProductSizeKind(CleanNameAndOrganizationMixin, models.Model):
    # Normal, roña, etc
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    has_performance = models.BooleanField(default=True, verbose_name=_('Take it for performance calculation'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)
    order = models.PositiveIntegerField(default=0, verbose_name=_('Order'))  # TODO: implementar ordenamiento con drag and drop

    class Meta:
        verbose_name = _('Product size kind')
        verbose_name_plural = _('Product size kinds')
        ordering = ('organization', 'order',)
        constraints = [
            models.UniqueConstraint(fields=['name', 'organization'], name='productkind_unique_name_organization'),
        ]


class MassVolumeKind(CleanNameAndOrganizationMixin, models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)
    order = models.PositiveIntegerField(default=0, verbose_name=_('Order'))  # TODO: implementar ordenamiento con drag and drop

    class Meta:
        verbose_name = _('Mass volume kind')
        verbose_name_plural = _('Mass volume kinds')
        ordering = ('organization', 'order',)
        constraints = [
            models.UniqueConstraint(fields=['name', 'organization'], name='massvolumekind_unique_name_organization'),
        ]


class Bank(models.Model):
    name = models.CharField(max_length=120, verbose_name=_('Name'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Bank')
        verbose_name_plural = _('Banks')
        ordering = ('organization', 'name',)
        constraints = [
            models.UniqueConstraint(fields=['name', 'organization'], name='bank_unique_name_organization'),
        ]


class VehicleOwnershipKind(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Vehicle ownership kind')
        verbose_name_plural = _('Vehicle ownership kinds')
        ordering = ('organization', 'name',)
        constraints = [
            models.UniqueConstraint(fields=['name', 'organization'], name='vehicleownershipkind_unique_name_organization'),
        ]


class VehicleKind(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Vehicle kind')
        verbose_name_plural = _('Vehicle kinds')
        ordering = ('organization', 'name',)
        constraints = [
            models.UniqueConstraint(fields=['name', 'organization'], name='vehiclekind_unique_name_organization'),
        ]


class VehicleFuelKind(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Vehicle fuel kind')
        verbose_name_plural = _('Vehicle fuel kinds')
        ordering = ('organization', 'name',)
        constraints = [
            models.UniqueConstraint(fields=['name', 'organization'], name='vehiclefuelkind_unique_name_organization'),
        ]


class PaymentKind(models.Model):
    name = models.CharField(max_length=120, verbose_name=_('Name'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Payment kind')
        verbose_name_plural = _('Payment kinds')
        ordering = ('organization', 'name',)
        constraints = [
            models.UniqueConstraint(fields=['name', 'organization'], name='paymentkind_unique_name_organization'),
        ]


class VehicleBrand(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Vehicle brand')
        verbose_name_plural = _('Vehicle brands')
        ordering = ('organization', 'name',)
        constraints = [
            models.UniqueConstraint(fields=['name', 'organization'], name='vehiclebrand_unique_name_organization'),
        ]


class OrchardProductClassificationKind(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Product Classification')
        verbose_name_plural = _('Product Classifications')
        ordering = ('organization', 'name',)
        constraints = [
            models.UniqueConstraint(fields=['name', 'organization'], name='orchardproductclassificationkind_unique_name_organization'),
        ]


class OrchardCertificationVerifier(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Orchard certification verifier')
        verbose_name_plural = _('Orchard certification verifiers')
        ordering = ('organization', 'name',)
        constraints = [
            models.UniqueConstraint(fields=['name', 'organization'], name='orchardcertificationverifier_unique_name_organization'),
        ]


class OrchardCertificationKind(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    verifiers = models.ManyToManyField(OrchardCertificationVerifier, verbose_name=_('Verifiers'), blank=False)
    extra_code = models.CharField(max_length=20, verbose_name=_('Extra code'), null=True, blank=True)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Orchard certification kind')
        verbose_name_plural = _('Orchard certification kinds')
        ordering = ('organization', 'name',)
        constraints = [
            models.UniqueConstraint(fields=['name', 'organization'], name='orchardcertificationkind_unique_name_organization'),
        ]
