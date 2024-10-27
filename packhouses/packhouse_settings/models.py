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
