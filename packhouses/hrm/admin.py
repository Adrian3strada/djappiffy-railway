from django.contrib import admin
from .models import (Employee, JobPosition, EmployeeJobPosition, 
                     EmployeeTaxAndMedicalInformation, EmployeeContactInformation, 
                     EmployeeAcademicAndWorkInfomation, WorkShiftSchedule)
from django.utils.translation import gettext_lazy as _
from common.base.decorators import uppercase_form_charfield, uppercase_alphanumeric_form_charfield
from django.db.models import Case, When 
from cities_light.models import Country, Region, SubRegion, City


class WorkShiftScheduleInline(admin.TabularInline):
    model = WorkShiftSchedule
    fields = ('day', 'entry_time', 'exit_time', 'is_enabled')  
    extra = 0 

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
    

@admin.register(JobPosition)
class JobPositionAdmin(admin.ModelAdmin):
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
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('first_name','full_name', 'get_job_position', 'status')
    inlines = [EmployeeJobPositionInline,  
               EmployeeTaxAndMedicalInformationInline, EmployeeAcademicAndWorkInfomationInline]

    @uppercase_form_charfield('first_name')
    @uppercase_form_charfield('middle_name')
    @uppercase_form_charfield('paternal_last_name')
    @uppercase_form_charfield('maternal_last_name')
    @uppercase_form_charfield('full_name')
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return form

    def get_job_position(self, obj):
        if hasattr(obj, 'employeejobposition') and obj.employeejobposition.job_position:
            return obj.employeejobposition.job_position
    get_job_position.short_description = 'Job Position'