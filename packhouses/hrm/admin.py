from django.contrib import admin
from .models import (Employee, JobPosition, EmployeeJobPosition, EmployeeTaxAndMedicalInformation, EmployeeContactInformation,
                     EmployeeAcademicAndWorkInfomation, WorkShiftSchedule, EmployeeStatus, EmployeeCertificationInformation, EmployeeWorkExperience)
from django.utils.translation import gettext_lazy as _
from common.base.decorators import uppercase_form_charfield, uppercase_alphanumeric_form_charfield
from cities_light.models import Country, Region, SubRegion, City
from common.base.mixins import (ByOrganizationAdminMixin, DisableInlineRelatedLinksMixin)
import nested_admin
from common.base.utils import ReportExportAdminMixin, SheetExportAdminMixin, SheetReportExportAdminMixin
from .views import basic_report
from .resources import EmployeeResource
from .forms import EmployeeContactInformationForm

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
    fields = ('name', 'description', 'is_enabled', 'category')
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

class EmployeeContactInformationInline(DisableInlineRelatedLinksMixin, nested_admin.NestedStackedInline):
    model = EmployeeContactInformation
    form = EmployeeContactInformationForm
    min_num = 1

    @uppercase_form_charfield('neighborhood')
    @uppercase_form_charfield('address')
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return form

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        post_data = request.POST

        if db_field.name == "country":
            kwargs["queryset"] = Country.objects.all()

        elif db_field.name == "state":
            country_id = self._extract_value_from_post(post_data, 'country')
            if country_id:
                kwargs["queryset"] = Region.objects.filter(country_id=country_id)
            else:
                kwargs["queryset"] = Region.objects.none()

        elif db_field.name == "city":
            state_id = self._extract_value_from_post(post_data, 'state')
            if state_id:
                kwargs["queryset"] = SubRegion.objects.filter(region_id=state_id)
            else:
                kwargs["queryset"] = SubRegion.objects.none()

        elif db_field.name == "district":
            city_id = self._extract_value_from_post(post_data, 'city')
            if city_id:
                kwargs["queryset"] = City.objects.filter(subregion_id=city_id)
            else:
                kwargs["queryset"] = City.objects.none()

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def _extract_value_from_post(self, post_data, field_suffix):
        for key in post_data:
            if key.endswith(f'-{field_suffix}'):
                return post_data.get(key)
        return None

    class Media:
        js = ('js/admin/forms/common/country-state-city-district.js',)



class EmployeeTaxAndMedicalInformationInline(DisableInlineRelatedLinksMixin, nested_admin.NestedStackedInline):
    model = EmployeeTaxAndMedicalInformation


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
    list_display = ('full_name', 'get_job_position', 'gender', 'hire_date','status')
    list_filter = ('status',)
    fields = ('status', 'name', 'middle_name', 'last_name', 'population_registry_code', 'gender',
              'marital_status', 'hire_date', 'termination_date')
    search_fields = ('full_name', )
    inlines = [EmployeeJobPositionInline, EmployeeContactInformationInline,
               EmployeeTaxAndMedicalInformationInline, EmployeeAcademicAndWorkInfomationInline,]

    @uppercase_form_charfield('name')
    @uppercase_form_charfield('middle_name')
    @uppercase_form_charfield('last_name')
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

