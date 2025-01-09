from django.db import models
from organizations.models import Organization
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from common.mixins import (CleanNameAndOrganizationMixin, CleanNameAndMarketMixin, CleanUniqueNameForOrganizationMixin,
                           CleanNameAndCodeAndOrganizationMixin)

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


class SupplyKind(CleanNameAndOrganizationMixin, models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    is_packaging = models.BooleanField(default=False, verbose_name=_('Is packaging'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    class Meta:
        verbose_name = _('Supply kind')
        verbose_name_plural = _('Supply kinds')
        ordering = ('organization', 'name',)
        constraints = [
            models.UniqueConstraint(fields=['name', 'organization'], name='supplykind_unique_name_organization'),
        ]


class SupplyUnitKind(CleanNameAndCodeAndOrganizationMixin, models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    code = models.CharField(max_length=20, verbose_name=_('Code'), null=True, blank=True, help_text=_('Abbreviation or code for the presentation kind, Preferably in SI if applies.'))
    sub_units = models.ManyToManyField('self', verbose_name=_('Sub units'), through='SupplySubUnitRelation', symmetrical=False, blank=True)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def clean(self):
        # Esta es una triquiñuela para que el código no se cambie por mayúsculas al limpiar el modelo y no tener que hacer un mixin nuevo
        code = self.code
        super().clean()
        self.code = code

    class Meta:
        verbose_name = _('Supply unit kind')
        verbose_name_plural = _('Supply unit kinds')
        ordering = ('organization', 'name',)
        constraints = [
            models.UniqueConstraint(fields=['name', 'code', 'organization'], name='supplypresentationkind_unique_name_code_organization'),
        ]


class SupplySubUnitRelation(models.Model):
    parent_unit = models.ForeignKey(SupplyUnitKind, related_name='parent_units', on_delete=models.CASCADE)
    child_unit = models.ForeignKey(SupplyUnitKind, related_name='child_units', on_delete=models.CASCADE)
    conversion_factor = models.FloatField(verbose_name=_('Conversion factor'))

    class Meta:
        unique_together = ('parent_unit', 'child_unit')

    def __str__(self):
        return f"{self.parent_unit} -> {self.child_unit} ({self.conversion_factor})"
