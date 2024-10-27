from django.db import models
from organizations.models import Organization
from django.utils.translation import gettext_lazy as _

# Create your models here.


class Status(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('name'))
    description = models.TextField(verbose_name=_('description'), null=True, blank=True)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    order = models.PositiveIntegerField(default=0, verbose_name=_('Order'))
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT, verbose_name=_('Organization'))

    class Meta:
        verbose_name = _('Status')
        verbose_name_plural = _('Statuses')
        ordering = ['order']

    def __str__(self):
        return self.name


class ProductKind(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    description = models.TextField(blank=True, null=True, verbose_name=_('Description'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Product kind')
        verbose_name_plural = _('Product kinds')
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(fields=['name', 'organization'], name='productkind_unique_name_organization'),
        ]


class ProductStandardSize(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Product standard size')
        verbose_name_plural = _('Product standard sizes')
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'organization'],
                name='productstandardsize_unique_name_organization'
            ),
        ]
