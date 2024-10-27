from django.db import models
from organizations.models import Organization
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

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


class ProductQualityKind(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)
    order = models.PositiveIntegerField(default=0, verbose_name=_('Order'))  # TODO: implementar ordenamiento con drag and drop

    def __str__(self):
        return f"{self.name}"

    def clean(self):
        self.name = self.name.upper()

        errors = {}

        try:
            super().clean()
        except ValidationError as e:
            errors = e.message_dict

        if self.organization_id:
            if ProductQualityKind.objects.filter(name=self.name, organization=self.organization).exclude(pk=self.pk).exists():
                errors['name'] = _('Name must be unique, it already exists.')

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _('Product quality kind')
        verbose_name_plural = _('Product quality kinds')
        unique_together = ('name', 'organization')
        ordering = ('order',)
        constraints = [
            models.UniqueConstraint(fields=['name', 'organization'], name='productqualitykind_unique_name_organization'),
        ]


class ProductKind(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    description = models.TextField(blank=True, null=True, verbose_name=_('Description'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    def clean(self):
        self.name = self.name.upper()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

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
