from django.db import models
from organizations.models import Organization
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from common.mixins import CleanNameAndOrganizationMixin, CleanNameAndMarketMixin

# Create your models here.


class Status(CleanNameAndOrganizationMixin, models.Model):
    name = models.CharField(max_length=255, verbose_name=_('name'))
    description = models.TextField(verbose_name=_('description'), null=True, blank=True)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    order = models.PositiveIntegerField(default=0, verbose_name=_('Order'))
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT, verbose_name=_('Organization'))

    class Meta:
        verbose_name = _('Status')
        verbose_name_plural = _('Statuses')
        ordering = ['order']


class ProductQualityKind(CleanNameAndOrganizationMixin, models.Model):
    # Normal, roña, etc
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)
    order = models.PositiveIntegerField(default=0, verbose_name=_('Order'))  # TODO: implementar ordenamiento con drag and drop

    class Meta:
        verbose_name = _('Product quality kind')
        verbose_name_plural = _('Product quality kinds')
        unique_together = ('name', 'organization')
        ordering = ('order',)
        constraints = [
            models.UniqueConstraint(fields=['name', 'organization'], name='productqualitykind_unique_name_organization'),
        ]


class ProductKind(CleanNameAndOrganizationMixin, models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    description = models.TextField(blank=True, null=True, verbose_name=_('Description'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    class Meta:
        verbose_name = _('Product kind')
        verbose_name_plural = _('Product kinds')
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(fields=['name', 'organization'], name='productkind_unique_name_organization'),
        ]
