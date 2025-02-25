from django.db import models

from organizations.models import Organization
from cities_light.models import City, Country, Region, SubRegion
from django.utils.translation import gettext_lazy as _
from common.mixins import CleanNameAndOrganizationMixin, CleanEmployeeAndOrganizationMixin
from common.base.mixins import ByOrganizationAdminMixin
from packhouses.packhouse_settings.models import PaymentKind 
from common.billing.models import LegalEntityCategory
from packhouses.packhouse_settings.models import Bank
from .utils import (EMPLOYEE_GENDER_CHOICES, EMPLOYEE_BLOOD_TYPE_CHOICES, EMPLOYEE_ACADEMIC_CHOICES, EMPLOYEE_PAYMENT_CHOICES, 
                    EMERGENCY_CONTACT_RELATIONSHIP_CHOICES, MARITAL_STATUS_CHOICES, EMPLOYEE_PAYMENT_METHOD_CHOICES, )
from django.core.exceptions import ValidationError
from datetime import datetime
from common.users.models import User
from django.db.models.signals import pre_save
from django.dispatch import receiver
# Create your models here.

class EmployeeStatus(CleanNameAndOrganizationMixin, models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Status'))
    description = models.CharField(max_length=255, verbose_name=_('Description'), blank=True, null=True)
    payment_percentage = models.PositiveIntegerField(default=100, verbose_name=_("Payment Percentage"), help_text=_("Enter the payment percentage (e.g., 100 for 100%, 60 for 60%, etc.)"))

    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Employee Status")
        verbose_name_plural = _("Employee Status")

class JobPosition(CleanNameAndOrganizationMixin, models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Job Title'))
    description = models.CharField(max_length=255, verbose_name=_('Description'), blank=True, null=True)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"
    
    class Meta: 
        verbose_name = _('Job Position')
        verbose_name_plural = _('Job Positions')
        ordering = ('name', )
        constraints = [
            models.UniqueConstraint(fields=('name', 'organization'),
                                    name='jobposition_unique_name_organization'),
        ]

class WorkShiftSchedule(models.Model):
    day = models.CharField(max_length=50, verbose_name=_("Day"))
    entry_time = models.TimeField(verbose_name=_('Entry Time'), blank=True, null=True, default="08:00:00" )
    exit_time = models.TimeField(verbose_name=_('Exit Time'), blank=True, null=True, default="18:00:00" )
    is_enabled = models.BooleanField(default=True, verbose_name=_("Is Enabled"))
    job_position = models.ForeignKey(JobPosition, on_delete=models.CASCADE, verbose_name=_('Job Position'))
    
    def __str__(self):
        return self.day

    class Meta:
        verbose_name = _('Work Shift Schedule')
        verbose_name_plural = _('Work Shift Schedules')

class Employee(CleanNameAndOrganizationMixin, models.Model):
    status = models.ForeignKey(EmployeeStatus, on_delete=models.CASCADE, verbose_name=_('Status'))
    name = models.CharField(max_length=100, verbose_name=_('First Name'))
    middle_name = models.CharField(max_length=100, verbose_name=_('Middle Name'), blank=True, null=True)
    last_name = models.CharField(max_length=100, verbose_name=_('Last Name'),)
    full_name = models.CharField(max_length=300, verbose_name=_('Full Name'), blank=True)
    population_registry_code = models.CharField(max_length=20, verbose_name=_('Population registry code'), null=True,)
    gender = models.CharField(max_length=20, choices=EMPLOYEE_GENDER_CHOICES, verbose_name=_('Gender'))
    marital_status = models.CharField(max_length=20, choices=MARITAL_STATUS_CHOICES, verbose_name=_('Marital Status'))
    hire_date = models.DateField(verbose_name=_('Hire Date'), blank=False, null=False)
    termination_date = models.DateField(verbose_name=_('Termination Date'), blank=True, null=True)
    country = models.ForeignKey(Country, verbose_name=_('Country'), on_delete=models.PROTECT)  
    state = models.ForeignKey(Region, verbose_name=_('State'), on_delete=models.PROTECT)
    city = models.ForeignKey(SubRegion, verbose_name=_('City'), on_delete=models.PROTECT)
    district = models.ForeignKey(City, verbose_name=_('District'), on_delete=models.PROTECT, null=True, blank=True)
    postal_code = models.CharField(max_length=10, verbose_name=_('Postal code'))
    neighborhood = models.CharField(max_length=255, verbose_name=_('Neighborhood'))
    address = models.CharField(max_length=255, verbose_name=_('Address'))
    external_number = models.CharField(max_length=10, verbose_name=_('External number'))
    internal_number = models.CharField(max_length=10, verbose_name=_('Internal number'), null=True, blank=True)
    phone_number = models.CharField(max_length=20, verbose_name=_('Phone number'))
    email = models.EmailField(max_length=255, verbose_name=_('Email'))
    is_staff = models.BooleanField(default=False, verbose_name=_('Is Staff'))
    staff_username = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name=_('Staff Username'), null=True, blank=True)
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def get_full_name(self):
        parts = [self.name]
        if self.middle_name:
            parts.append(self.middle_name)
        parts.append(self.last_name)
        return ' '.join(parts)
    
    def get_antiguedad(self):
        today = datetime.now().date()
        if self.termination_date:  
            end_date = self.termination_date  
        else:
            end_date = today  
        
        difference = end_date - self.hire_date
        years = difference.days // 365
        months = (difference.days % 365) // 30
        days = (difference.days % 365) % 30

        return _("%(years)d years, %(months)d months, %(days)d days") % {
            "years": years, "months": months, "days": days
        }
    get_antiguedad.short_description = "Antigüedad"
    
    def save(self, *args, **kwargs):
        self.full_name = self.get_full_name()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.full_name}"

    class Meta: 
        verbose_name = _('Employee')
        verbose_name_plural = _('Employees')
        ordering = ('full_name',)


class EmployeeJobPosition(models.Model):
    job_position = models.ForeignKey(JobPosition, on_delete=models.CASCADE, verbose_name=_('Job Position'))
    payment_per_hour = models.DecimalField(default=0.0, max_digits=10, decimal_places=2, verbose_name=_("Payment per Hour"))
    work_hours_per_day = models.IntegerField(default=0, verbose_name=_("Work Hours per Day"))
    payment_per_day = models.DecimalField(default=0.0, max_digits=10, decimal_places=2, verbose_name=_("Payment per Day"))
    payment_frequency = models.CharField(max_length=20, choices=EMPLOYEE_PAYMENT_CHOICES, verbose_name=_('Payment Frecuency'))
    payment_kind = models.CharField(max_length=30, choices=EMPLOYEE_PAYMENT_METHOD_CHOICES, verbose_name=_('Payment Kind'))
    bank = models.ForeignKey(Bank, on_delete=models.PROTECT, verbose_name=_("Bank"), null=True, blank=True)
    bank_account_number = models.CharField(max_length=25, verbose_name=_("Bank Account Number"), null=True, blank=True)
    clabe = models.CharField(max_length=18, verbose_name=_('CLABE'), null=True, blank=True)
    swift = models.CharField(max_length=20, verbose_name=_('SWIFT'), null=True, blank=True)
    overtime = models.BooleanField(default=False, verbose_name=_('Overtime'), help_text=_('Employee is allowed for overtime'))
    license = models.BooleanField(default=False, verbose_name=_('License'), help_text=_('Employee requires drivers license'))
    equipment = models.BooleanField(default=True, verbose_name=_('Equipment'), help_text=_('Employee requires uniform and/or equipment'))
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, verbose_name=_('Employee'))
    
    def __str__(self):
        return f"{self.employee} - {self.job_position}"

    class Meta:
        verbose_name = _('Job Position and Payment')
        verbose_name_plural = _('Job Position and Payment')


class EmployeeTaxAndMedicalInformation(models.Model):
    country = models.ForeignKey(Country, verbose_name=_('Country'), on_delete=models.PROTECT)
    tax_id = models.CharField(max_length=100, verbose_name=_('Tax ID'))
    legal_category = models.ForeignKey(LegalEntityCategory, verbose_name=_('Legal entity category'), null=True, blank=True, on_delete=models.PROTECT, help_text=_(
            'Legal category of the client, must have a country selected to show that country legal categories.'))
    blood_type = models.CharField(max_length=20, choices=EMPLOYEE_BLOOD_TYPE_CHOICES, verbose_name=_('Blood Type'))
    has_disability = models.BooleanField(default=False, verbose_name=_('Has Disability'))
    disability_details = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('Disability Details'))
    has_chronic_illness = models.BooleanField(default=False, verbose_name=_('Has Chronic Illness'))
    chronic_illness_details = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('Chronic Illness Details'))
    medical_insurance_provider = models.CharField(max_length=100, verbose_name=_('Medical Insurance Provider'), blank=True, null=True)
    medical_insurance_number = models.CharField(max_length=100, verbose_name=_('Medical Insurance Number'), blank=True, null=True)
    medical_insurance_start_date = models.DateField(verbose_name=_('Medical Insurance Start Date'), blank=True, null=True)
    medical_insurance_end_date = models.DateField(verbose_name=_('Medical Insurance End Date'), blank=True, null=True)
    has_private_insurance = models.BooleanField(default=False, verbose_name=_('Has Private Insurance'))
    private_insurance_details = models.TextField(blank=True, null=True, verbose_name=_('Private Insurance Details'))
    emergency_contact_name = models.CharField(max_length=100, verbose_name=_('Emergency Contact Name'), blank=False, null=False, help_text=_('Name of the emergency contact'))
    emergency_contact_phone = models.CharField(max_length=20, verbose_name=_('Emergency Contact Phone'), blank=False, null=False, help_text=_('Phone number of the emergency contact'))
    emergency_contact_relationship = models.CharField(max_length=20, choices=EMERGENCY_CONTACT_RELATIONSHIP_CHOICES, verbose_name=_('Emergency Contact Relationship'), blank=False, null=False)
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, verbose_name=_('Employee'))
    
    class Meta:
        verbose_name = _('Tax and Medical Record')
        verbose_name_plural = _('Tax and Medical Records')

class EmployeeAcademicAndWorkInformation(models.Model):
    academic_status = models.CharField(default='none', max_length=30, choices=EMPLOYEE_ACADEMIC_CHOICES, verbose_name=_('Academic Formation'))
    degree = models.CharField(max_length=255, verbose_name=_('Degree'), null=True, blank=True)
    professional_license = models.CharField(max_length=255, verbose_name=_('Professional License'), null=True, blank=True)
    institution = models.CharField(max_length=100, verbose_name=_('Institution'), blank=True, null=True)
    graduation_year = models.DateField(verbose_name=_('Graduation Year'), blank=True, null=True)
    field_of_study = models.CharField(max_length=100, verbose_name=_('Field of Study'), blank=True, null=True)
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, verbose_name=_('Employee'))
    
    class Meta:
        verbose_name = _('Academic and Work Record')
        verbose_name_plural = _('Academic and Work Records')

class EmployeeWorkExperience(models.Model):
    work_record = models.ForeignKey(EmployeeAcademicAndWorkInformation, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, verbose_name=_('Previous Role'))
    company_name = models.CharField(max_length=255, verbose_name=_("Company Name"))
    time_in_position = models.CharField(max_length=20, verbose_name="Time in Position", help_text=_("Example: '2 years 3 months'"))
    
    def __str__(self):
        return f"{self.title} at {self.company_name}" if self.company_name else self.title

class EmployeeCertificationInformation(models.Model):
    academic_record = models.ForeignKey(EmployeeAcademicAndWorkInformation, on_delete=models.CASCADE)
    certification_name = models.CharField(max_length=200)
    issuing_organization = models.CharField(max_length=200)
    issue_date = models.DateField()
    expiration_date = models.DateField(null=True, blank=True)  
    
    def __str__(self):
        return f"{self.certification_name}"
    
class EmployeeStatusChange(CleanEmployeeAndOrganizationMixin, models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name=_("Employee"))
    old_status = models.ForeignKey(EmployeeStatus, on_delete=models.SET_NULL, null=True, related_name='old_status_changes', verbose_name=_("Previous Status"))
    new_status = models.ForeignKey(EmployeeStatus, on_delete=models.SET_NULL, null=True, related_name='new_status_changes', verbose_name=_("New Status"))
    changed_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Changed at"))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.employee.name} changed from {self.old_status} to {self.new_status} at {self.changed_at}"


@receiver(pre_save, sender=Employee)
def log_status_change(sender, instance, **kwargs):
    if not instance.pk:
        return

    try:
        old_instance = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return

    if old_instance.status != instance.status:
        EmployeeStatusChange.objects.create(
            employee=instance,  
            old_status=old_instance.status,
            new_status=instance.status,
            organization=instance.organization
        )