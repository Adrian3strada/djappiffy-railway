from django.contrib import admin
from .models import (Employee, JobPosition, EmployeeJobPosition, EmployeeTaxAndMedicalInformation, EmployeeAcademicAndWorkInfomation, 
                     WorkShiftSchedule, EmployeeStatus, EmployeeCertificationInformation, EmployeeWorkExperience, EmployeeStatusChange)
from django.utils.translation import gettext_lazy as _
from common.base.decorators import uppercase_form_charfield, uppercase_alphanumeric_form_charfield
from cities_light.models import Country, Region, SubRegion, City
from common.base.mixins import (ByOrganizationAdminMixin, DisableInlineRelatedLinksMixin)
import nested_admin
from common.base.utils import ReportExportAdminMixin, SheetExportAdminMixin, SheetReportExportAdminMixin
from .views import basic_report
from .resources import EmployeeResource
from common.users.models import User

@admin.register(EmployeeStatus)
class EmployeeStatusAdmin(ByOrganizationAdminMixin):
    list_display = ('name', 'payment_type', 'description', 'is_enabled')
    fields = ('name', 'payment_type', 'payment_percentage', 'description', 'is_enabled')
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
    @uppercase_form_charfield('name')
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return form

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


class EmployeeJobPositionInline(DisableInlineRelatedLinksMixin, nested_admin.NestedStackedInline):
    model = EmployeeJobPosition

    
    
    class Media:
        js = ('js/admin/forms/packhouses/hrm/job-position-inline.js',)


class EmployeeTaxAndMedicalInformationInline(DisableInlineRelatedLinksMixin, nested_admin.NestedStackedInline):
    model = EmployeeTaxAndMedicalInformation
    fields = ('country', 'tax_id', 'legal_category', 'has_private_insurance', 'medical_insurance_provider', 'medical_insurance_number', 
              'medical_insurance_start_date', 'medical_insurance_end_date', 'private_insurance_details','blood_type', 'has_disability', 
              'disability_details', 'has_chronic_illness', 'chronic_illness_details', 'emergency_contact_name', 'emergency_contact_phone',
              'emergency_contact_relationship')

    class Media:
        js = ('js/admin/forms/packhouses/hrm/tax-medical-inline.js',)

class EmployeeCertificationInformationInline(nested_admin.NestedTabularInline):
    model = EmployeeCertificationInformation
    extra = 0

class EmployeeWorkExperienceInline(nested_admin.NestedTabularInline):
    model = EmployeeWorkExperience
    extra = 0

class EmployeeAcademicAndWorkInfomationInline(DisableInlineRelatedLinksMixin, nested_admin.NestedStackedInline):
    model = EmployeeAcademicAndWorkInfomation
    inlines = [EmployeeCertificationInformationInline, EmployeeWorkExperienceInline]

@admin.register(Employee)
class EmployeeAdmin(SheetReportExportAdminMixin, ByOrganizationAdminMixin, nested_admin.NestedModelAdmin):
    report_function = staticmethod(basic_report)
    resource_classes = [EmployeeResource]
    list_display = ('full_name', 'get_job_position', 'gender', 'hire_date', 'get_antiguedad', 'status', 'is_staff')
    list_filter = ('status', 'is_staff')
    fields = ('status', 'name', 'middle_name', 'last_name', 'population_registry_code', 'gender', 
              'marital_status', 'country', 'state', 'city', 'district', 'postal_code', 
              'neighborhood', 'address', 'external_number', 'internal_number', 'phone_number', 
              'email', 'hire_date', 'termination_date', 'is_staff', 'staff_username')
    search_fields = ('full_name', )
    inlines = [EmployeeJobPositionInline, EmployeeTaxAndMedicalInformationInline, EmployeeAcademicAndWorkInfomationInline,]

    @uppercase_form_charfield('name')
    @uppercase_form_charfield('middle_name')
    @uppercase_form_charfield('last_name')
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['staff_username'].widget.can_add_related = False
        form.base_fields['staff_username'].widget.can_change_related = False
        form.base_fields['staff_username'].widget.can_view_related = False
        return form
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        object_id = request.resolver_match.kwargs.get("object_id")
        obj = Employee.objects.get(id=object_id) if object_id else None

        if db_field.name == "staff_username":
            if hasattr(request, 'organization'):
                kwargs["queryset"] = User.objects.filter(is_staff=True)
            else:
                kwargs["queryset"] = User.objects.none()
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            return formfield
        
        if db_field.name == "status":
            if hasattr(request, 'organization'):
                kwargs["queryset"] = EmployeeStatus.objects.filter(organization=request.organization, is_enabled=True)
            else:
                kwargs["queryset"] = EmployeeStatus.objects.none()
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            return formfield

        if db_field.name == "country":
            kwargs["queryset"] = Country.objects.all()
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda item: item.name
            return formfield

        if db_field.name == "state":
            if request.POST:
                country_id = request.POST.get('country')
            else:
                country_id = obj.country_id if obj else None
            if country_id:
                kwargs["queryset"] = Region.objects.filter(country_id=country_id)
            else:
                kwargs["queryset"] = Region.objects.none()
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda item: item.name
            return formfield

        if db_field.name == "city":
            if request.POST:
                state_id = request.POST.get('state')
            else:
                state_id = obj.state_id if obj else None
            if state_id:
                kwargs["queryset"] = SubRegion.objects.filter(region_id=state_id)
            else:
                kwargs["queryset"] = SubRegion.objects.none()
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda item: item.name
            return formfield

        if db_field.name == "district":
            if request.POST:
                city_id = request.POST.get('city')
            else:
                city_id = obj.city_id if obj else None
            if city_id:
                kwargs["queryset"] = City.objects.filter(subregion_id=city_id)
            else:
                kwargs["queryset"] = City.objects.none()
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda item: item.name
            return formfield

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

        
    def get_job_position(self, obj):
        if hasattr(obj, 'employeejobposition') and obj.employeejobposition.job_position:
            return obj.employeejobposition.job_position
    get_job_position.short_description = 'Job Position'

    class Media:
        js = ('js/admin/forms/common/country-state-city-district.js',)


@admin.register(EmployeeStatusChange)
class EmployeeStatusChangeAdmin(admin.ModelAdmin):
    pass