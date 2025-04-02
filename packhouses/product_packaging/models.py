from django.db import models
from ..hrm.models import Employee
from django.utils.translation import gettext_lazy as _
import uuid
from .settings import STATUS_CHOICES

# Create your models here.

class PackerLabel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False) 
    id_employee = models.ForeignKey(Employee, verbose_name=_('Employee'), on_delete=models.PROTECT)
    creation_date = models.DateTimeField(auto_now_add=True)
    scanned_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')  

    class Meta:
        verbose_name = _('Packer label')
        verbose_name_plural = _('Packer labels')

    def __str__(self):
        return f"{self.id_employee.id}-{self.id} | Created: {self.creation_date.strftime('%Y-%m-%d %H:%M:%S')} | Status: {self.status}"



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
    
    @property
    def ticket_r(self):
        return f"Ticket #{self.pk}"
