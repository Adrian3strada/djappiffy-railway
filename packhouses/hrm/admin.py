from django.contrib import admin
from .models import (Employee, JobPosition, EmployeeJobPosition, 
                     EmployeeTaxAndMedicalInformation, EmployeeContactInformation, 
                     EmployeeAcademicAndWorkInfomation, WorkShiftSchedule, EmployeeStatus)
from django.utils.translation import gettext_lazy as _
from common.base.decorators import uppercase_form_charfield, uppercase_alphanumeric_form_charfield
from django.db.models import Case, When 
from cities_light.models import Country, Region, SubRegion, City
from common.base.mixins import ByOrganizationAdminMixin

@admin.register(EmployeeStatus)
class EmployeeStatusAdmin(ByOrganizationAdminMixin):
    list_display = ('name', 'payment_type', 'is_enabled')
    fields = ('name', 'description', 'payment_type', 'is_enabled')
    @uppercase_form_charfield('name')
    @uppercase_form_charfield('description')
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return form


class WorkShiftScheduleInline(admin.TabularInline):
    model = WorkShiftSchedule
    fields = ('day', 'entry_time', 'exit_time', 'is_enabled')  
    extra = 0 

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
    

@admin.register(JobPosition)
class JobPositionAdmin(ByOrganizationAdminMixin):
    list_display = ('name', 'is_enabled')
    fields = ('name', 'description', 'is_enabled')
    inlines = [WorkShiftScheduleInline]


    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change) 
        if not change:  
            days_of_week = [
                _("Monday"), _("Tuesday"), _("Wednesday"), _("Thursday"),
                _("Friday"), _("Saturday"), _("Sunday")
            ]
            for day in days_of_week:
                WorkShiftSchedule.objects.create(
                    day=day,
                    job_position=obj,  
                )


class EmployeeJobPositionInline(admin.StackedInline):
    model = EmployeeJobPosition

class EmployeeContactInformationInline(admin.StackedInline):
    model = EmployeeContactInformation
    min_num = 1
    @uppercase_form_charfield('neighborhood')
    @uppercase_form_charfield('address')
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return form

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        object_id = request.resolver_match.kwargs.get("object_id")
        obj = EmployeeContactInformation.objects.get(id=object_id) if object_id else None

        if db_field.name == "country":
            kwargs["queryset"] = Country.objects.all()
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda item: item.name
            return formfield
        
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    class Media:
        js = ('js/admin/forms/packhouses/hrm/country-state-city-district.js',)

    
class EmployeeTaxAndMedicalInformationInline(admin.StackedInline):
    model = EmployeeTaxAndMedicalInformation

class EmployeeAcademicAndWorkInfomationInline(admin.StackedInline):
    model = EmployeeAcademicAndWorkInfomation

@admin.register(Employee)
class EmployeeAdmin(ByOrganizationAdminMixin):
    list_display = ('full_name', 'get_job_position', 'status')
    list_filter = ('status',)
    fields = ('status', 'first_name', 'middle_name', 'last_name', 'second_last_name', 'population_registry_code', 'gender', 
              'marital_status', 'hire_date', 'termination_date')
    inlines = [EmployeeJobPositionInline,  
               EmployeeTaxAndMedicalInformationInline, EmployeeAcademicAndWorkInfomationInline]

    @uppercase_form_charfield('first_name')
    @uppercase_form_charfield('middle_name')
    @uppercase_form_charfield('last_name')
    @uppercase_form_charfield('second_last_name')
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return form
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "status":
            if hasattr(request, 'organization'):
                kwargs["queryset"] = EmployeeStatus.objects.filter(organization=request.organization, is_enabled=True)
            else:
                kwargs["queryset"] = EmployeeStatus.objects.none()
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            return formfield
        
    def get_job_position(self, obj):
        if hasattr(obj, 'employeejobposition') and obj.employeejobposition.job_position:
            return obj.employeejobposition.job_position
    get_job_position.short_description = 'Job Position'