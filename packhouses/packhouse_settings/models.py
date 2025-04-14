from django.db import models
from organizations.models import Organization
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from common.mixins import (CleanNameAndOrganizationMixin, CleanNameAndMarketMixin, CleanUniqueNameForOrganizationMixin,
                           CleanNameAndCodeAndOrganizationMixin)
<<<<<<< HEAD

=======
from common.settings import DATA_TYPE_CHOICES
>>>>>>> dev-certiffy
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


class Bank(CleanNameAndOrganizationMixin, models.Model):
    name = models.CharField(max_length=120, verbose_name=_('Name'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    class Meta:
        verbose_name = _('Bank')
        verbose_name_plural = _('Banks')
        ordering = ('organization', 'name',)
        constraints = [
            models.UniqueConstraint(fields=['name', 'organization'], name='bank_unique_name_organization'),
        ]


class VehicleOwnershipKind(CleanNameAndOrganizationMixin, models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    class Meta:
        verbose_name = _('Vehicle ownership kind')
        verbose_name_plural = _('Vehicle ownership kinds')
        ordering = ('organization', 'name',)
        constraints = [
            models.UniqueConstraint(fields=['name', 'organization'], name='vehicleownershipkind_unique_name_organization'),
        ]


class VehicleKind(CleanNameAndOrganizationMixin, models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    class Meta:
        verbose_name = _('Vehicle kind')
        verbose_name_plural = _('Vehicle kinds')
        ordering = ('organization', 'name',)
        constraints = [
            models.UniqueConstraint(fields=['name', 'organization'], name='vehiclekind_unique_name_organization'),
        ]


class VehicleFuelKind(CleanNameAndOrganizationMixin, models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    class Meta:
        verbose_name = _('Vehicle fuel kind')
        verbose_name_plural = _('Vehicle fuel kinds')
        ordering = ('organization', 'name',)
        constraints = [
            models.UniqueConstraint(fields=['name', 'organization'], name='vehiclefuelkind_unique_name_organization'),
        ]


class PaymentKind(CleanNameAndOrganizationMixin, models.Model):
    name = models.CharField(max_length=120, verbose_name=_('Name'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    class Meta:
        verbose_name = _('Payment kind')
        verbose_name_plural = _('Payment kinds')
        ordering = ('organization', 'name',)
        constraints = [
            models.UniqueConstraint(fields=['name', 'organization'], name='paymentkind_unique_name_organization'),
        ]

class PaymentKindAdditionalInput(models.Model):
    payment_kind = models.ForeignKey(PaymentKind, verbose_name=_('Payment Kind'), on_delete=models.CASCADE)
    name = models.CharField(max_length=120, verbose_name=_('Name'))
    data_type = models.CharField(max_length=20, verbose_name=_('Data type'), choices=DATA_TYPE_CHOICES)
    is_required = models.BooleanField(default=False, verbose_name=_('Is required'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))

    class Meta:
        verbose_name = _('Additional Input')
        verbose_name_plural = _('Additional Inputs')
        constraints = [
            models.UniqueConstraint(fields=['name', 'payment_kind'], name='paymentkindadditionalinput_unique_name_payment_kind'),
        ]


class VehicleBrand(CleanNameAndOrganizationMixin, models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    class Meta:
        verbose_name = _('Vehicle brand')
        verbose_name_plural = _('Vehicle brands')
        ordering = ('organization', 'name',)
        constraints = [
            models.UniqueConstraint(fields=['name', 'organization'], name='vehiclebrand_unique_name_organization'),
        ]


class AuthorityPackagingKind(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Packaging Kind Authority')
        verbose_name_plural = _('Packaging Kind Authorities')
        ordering = ('name', )
        constraints = [
            models.UniqueConstraint(fields=('name', 'organization'),
                                    name='authoritypackagingkind_unique_name_organization'),
        ]


class OrchardCertificationVerifier(CleanNameAndOrganizationMixin, models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    class Meta:
        verbose_name = _('Orchard certification verifier')
        verbose_name_plural = _('Orchard certification verifiers')
        ordering = ('organization', 'name',)
        constraints = [
            models.UniqueConstraint(fields=['name', 'organization'], name='orchardcertificationverifier_unique_name_organization'),
        ]


class OrchardCertificationKind(CleanNameAndOrganizationMixin, models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    verifiers = models.ManyToManyField(OrchardCertificationVerifier, verbose_name=_('Verifiers'), blank=False)
    extra_code_name = models.CharField(max_length=20, verbose_name=_('Extra code name'), null=True, blank=True)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    class Meta:
        verbose_name = _('Orchard certification kind')
        verbose_name_plural = _('Orchard certification kinds')
        ordering = ('organization', 'name',)
        constraints = [
            models.UniqueConstraint(fields=['name', 'organization'], name='orchardcertificationkind_unique_name_organization'),
        ]

