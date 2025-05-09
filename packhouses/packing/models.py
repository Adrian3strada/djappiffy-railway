from django.db import models
from ..hrm.models import Employee
from django.utils.translation import gettext_lazy as _
import uuid

# Create your models here.

class PackerLabel(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    employee = models.ForeignKey(Employee, verbose_name=_('Employee'), on_delete=models.PROTECT)
    scanned_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _('Packer label')
        verbose_name_plural = _('Packer labels')

    def __str__(self):
        scanned_status = "Scanned" if self.scanned_at else "Not Scanned"
        return f"{self.employee.id}-{self.uuid} | {scanned_status}"


class PackerEmployeeManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(
            employeejobposition__job_position__category="packer"
        )


class PackerEmployee(Employee):
    objects = PackerEmployeeManager()

    class Meta:
        proxy = True
        verbose_name = _("Packer Employee")
        verbose_name_plural = _("Packer Employees")

    def position(self):
        job_position = self.employeejobposition
        return job_position.job_position.name if job_position else "N/A"

    def full_name_column(self, obj):
        return obj.full_name

    full_name_column.short_description = _("Full name")


class Package(models.Model):

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    packer = models.ForeignKey(PackerEmployee, verbose_name=_('Packer'), on_delete=models.PROTECT)
    scanned_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _('Package')
        verbose_name_plural = _('Packages')

    def __str__(self):
        scanned_status = "Scanned" if self.scanned_at else "Not Scanned"
        return f"{self.packer.id}-{self.uuid} | {scanned_status}"
