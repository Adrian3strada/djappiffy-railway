from django.contrib import admin, messages
from .models import (Employee, JobPosition, EmployeeJobPosition, EmployeeTaxAndMedicalInformation, EmployeeAcademicAndWorkInformation,
                     EmployeeStatus, EmployeeCertificationInformation, EmployeeWorkExperience, EmployeeStatusChange,
                     EmployeeEvent, WorkSchedule, EmployeeWorkSchedule)
from django.forms.models import BaseInlineFormSet
from django.utils.translation import gettext_lazy as _
from common.base.decorators import uppercase_form_charfield, uppercase_alphanumeric_form_charfield
from cities_light.models import Country, Region, SubRegion, City
from common.base.mixins import (ByOrganizationAdminMixin, DisableInlineRelatedLinksMixin)
import nested_admin
from common.base.utils import ReportExportAdminMixin, SheetExportAdminMixin, SheetReportExportAdminMixin
from .views import basic_report
from .resources import EmployeeResource
from common.users.models import User
from django.utils.html import format_html, format_html_join
from django.urls import reverse, path
from .forms import (EmployeeEventForm, EmployeeForm, JobPositionInlineForm, TaxAndMedicalInlineForm, AcademicAndWorkInlineForm,
                    EmployeeStatusForm)
from django.shortcuts import redirect
from django.core.exceptions import ValidationError
from django import forms


@admin.register(WorkSchedule)
class WorkScheduleAdmin(ByOrganizationAdminMixin):
    list_display = ('name', 'start_time', 'end_time', 'is_enabled')
    fields = ('name', 'start_time', 'end_time', 'is_enabled')
    list_filter = ('is_enabled',)
    search_fields = ('name',)

    @uppercase_form_charfield('name')
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return form

class EmployeeWorkScheduleInlineFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        if 'instance' in kwargs and not kwargs['instance'].pk:
            kwargs.setdefault('initial', [
                {'day': 'Monday'},
                {'day': 'Tuesday'},
                {'day': 'Wednesday'},
                {'day': 'Thursday'},
                {'day': 'Friday'},
                {'day': 'Saturday'},
                {'day': 'Sunday'},
            ])
        super().__init__(*args, **kwargs)

    def clean(self):
        super().clean()
        days = []

        valid_forms = [form for form in self.forms if form.cleaned_data and not self._should_delete_form(form)]

        # Verificar que no se agreguen más de 7 formularios
        if len(valid_forms) > 7:
            raise forms.ValidationError(_('You cannot have more than 7 days.'))

        # Verificar que no se repitan los días
        for form in valid_forms:
            if 'day' in form.cleaned_data:
                day = form.cleaned_data['day']
                if day in days:
                    form.add_error('day', _('This day is already selected.'))
                else:
                    days.append(day)


class WorkScheduleInline(admin.TabularInline):
    model = EmployeeWorkSchedule
    fields = ('day', 'schedule')
    formset = EmployeeWorkScheduleInlineFormSet
    fk_name = "employee"
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        organization = request.organization if hasattr(request, 'organization') else None
        organization_queryfilter = {'organization': organization, 'is_enabled': True}

        if db_field.name == "schedule":
            kwargs["queryset"] = WorkSchedule.objects.filter(**organization_queryfilter)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_extra(self, request, obj=None, **kwargs):
        if obj is None or not obj.employeeworkschedule_set.exists():
            return 7
        return 0

class ScheduleInline(admin.TabularInline):
    model = EmployeeWorkSchedule
    fields = ('day', 'schedule')
    formset = EmployeeWorkScheduleInlineFormSet
    fk_name = "job_position"

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        organization = request.organization if hasattr(request, 'organization') else None
        organization_queryfilter = {'organization': organization, 'is_enabled': True}

        if db_field.name == "schedule":
            kwargs["queryset"] = WorkSchedule.objects.filter(**organization_queryfilter)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_extra(self, request, obj=None, **kwargs):
        if obj is None or not obj.employeeworkschedule_set.exists():
            return 7
        return 0

@admin.register(JobPosition)
class JobPositionAdmin(ByOrganizationAdminMixin):
    list_display = ('name', 'is_enabled')
    fields = ('name', 'description', 'is_enabled', 'category')
    inlines = [ScheduleInline,]
    @uppercase_form_charfield('name')
    def get_form(self, request, obj=None, **kwargs):
        return super().get_form(request, obj, **kwargs)

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

class EmployeeWorkScheduleInline(admin.TabularInline, nested_admin.NestedStackedInline):
    model = EmployeeWorkSchedule
    fields = ('day', 'schedule')
    formset = EmployeeWorkScheduleInlineFormSet

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        organization = request.organization if hasattr(request, 'organization') else None
        organization_queryfilter = {'organization': organization, 'is_enabled': True}

        if db_field.name == "schedule":
            kwargs["queryset"] = WorkSchedule.objects.filter(**organization_queryfilter)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_extra(self, request, obj=None, **kwargs):
        if obj is None or not obj.employeeworkschedule_set.exists():
            return 7
        return 0


class EmployeeJobPositionInline(DisableInlineRelatedLinksMixin, nested_admin.NestedStackedInline):
    model = EmployeeJobPosition
    form = JobPositionInlineForm

    class Media:
        js = ('js/admin/forms/packhouses/hrm/job-position-inline.js',)


class EmployeeTaxAndMedicalInformationInline(DisableInlineRelatedLinksMixin, nested_admin.NestedStackedInline):
    model = EmployeeTaxAndMedicalInformation
    fields = ('country', 'tax_id', 'legal_category', 'has_private_insurance', 'medical_insurance_provider', 'medical_insurance_number',
              'medical_insurance_start_date', 'medical_insurance_end_date', 'private_insurance_details','blood_type', 'has_disability',
              'disability_details', 'has_chronic_illness', 'chronic_illness_details', 'emergency_contact_name', 'emergency_contact_phone',
              'emergency_contact_relationship')
    form = TaxAndMedicalInlineForm
    class Media:
        js = ('js/admin/forms/packhouses/hrm/tax-medical-inline.js',)

class EmployeeCertificationInformationInline(nested_admin.NestedTabularInline):
    model = EmployeeCertificationInformation
    extra = 0

class EmployeeWorkExperienceInline(nested_admin.NestedTabularInline):
    model = EmployeeWorkExperience
    extra = 0

class EmployeeAcademicAndWorkInformationInline(DisableInlineRelatedLinksMixin, nested_admin.NestedStackedInline):
    model = EmployeeAcademicAndWorkInformation
    inlines = [EmployeeCertificationInformationInline, EmployeeWorkExperienceInline]
    form = AcademicAndWorkInlineForm

    class Media:
        css = {'all': ('css/admin_tabular.css',) }
        js = ('js/admin/forms/packhouses/hrm/employee-academic-inline.js',)

@admin.register(Employee)
class EmployeeAdmin(SheetReportExportAdminMixin, ByOrganizationAdminMixin, nested_admin.NestedModelAdmin):
    report_function = staticmethod(basic_report)
    resource_classes = [EmployeeResource]
    list_display = ('full_name', 'get_job_position', 'gender', 'hire_date', 'status')
    list_filter = ('status',)
    fields = ('status', 'name', 'middle_name', 'last_name', 'population_registry_code', 'gender',
              'marital_status', 'hire_date', 'termination_date',)
    search_fields = ('full_name', )
    inlines = [EmployeeJobPositionInline, EmployeeWorkScheduleInline, EmployeeTaxAndMedicalInformationInline, EmployeeAcademicAndWorkInformationInline,]
    form = EmployeeForm

    @uppercase_form_charfield('name')
    @uppercase_form_charfield('middle_name')
    @uppercase_form_charfield('last_name')
    @uppercase_form_charfield('neighborhood')
    @uppercase_form_charfield('address')
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
        js = ('js/admin/forms/common/country-state-city-district.js',
              'js/admin/forms/packhouses/hrm/employee-staff.js',)


@admin.register(EmployeeStatus)
class EmployeeStatusAdmin(ByOrganizationAdminMixin):
    form = EmployeeStatusForm
    list_display = ('name', 'payment_percentage', 'is_paid', 'is_enabled')
    fields = ('name','is_paid', 'payment_percentage', 'description', 'is_enabled')
    @uppercase_form_charfield('name')
    @uppercase_form_charfield('description')
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return form
    class Media:
        js = ('js/admin/forms/packhouses/hrm/employee-status.js',)

@admin.register(EmployeeStatusChange)
class EmployeeStatusChangeAdmin(ByOrganizationAdminMixin):
    pass

@admin.register(EmployeeEvent)
class EmployeeEventAdmin(ByOrganizationAdminMixin):
    form = EmployeeEventForm
    list_display = ('employee', 'event_type', 'start_date', 'end_date', 'approval_status', 'generate_actions_buttons')
    list_filter = ('event_type__name',)
    search_fields = ('employee__name', 'event_type__name')
    fields = ('employee', 'event_type', 'start_date', 'end_date', 'description', 'parent_event')

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'event_type' in form.base_fields:
            form.base_fields['event_type'].queryset = EmployeeStatus.objects.filter(
                organization=request.organization,
                is_enabled=True
            )
        return form

    def generate_actions_buttons(self, obj):
        if obj.approval_status == 'pending':
            approve_url = reverse('admin:approve_event', args=[obj.pk])
            reject_url = reverse('admin:reject_event', args=[obj.pk])

            def create_button(url, color, icon, title):
                return format_html(
                    '''
                    <a class="button" href="{}" style="color:{};" title="{}">
                        <i class="fa-solid {}"></i>
                    </a>
                    ''',
                    url, color, _(title), icon
                )

            approve_button = create_button(approve_url, '#4daf50', 'fa-check', _('Approve'))
            reject_button = create_button(reject_url, '#f44336', 'fa-times', _('Reject'))

            return format_html('{}&nbsp;{}', approve_button, reject_button)
        return _('No actions')

    generate_actions_buttons.short_description = _('Actions')
    generate_actions_buttons.allow_tags = True

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:pk>/approve/',
                self.admin_site.admin_view(self.process_event),
                {'action': 'approve'},
                name='approve_event'
            ),
            path(
                '<int:pk>/reject/',
                self.admin_site.admin_view(self.process_event),
                {'action': 'reject'},
                name='reject_event'
            ),
        ]
        return custom_urls + urls

    def process_event(self, request, pk, action):
        event = EmployeeEvent.objects.get(pk=pk)
        if action == 'approve':
            event.approval_status = _('APPROVED')
            message = f"Evento {event} aprobado."
            message_type = messages.SUCCESS
        elif action == 'reject':
            event.approval_status = _('REJECTED')
            message = f"Evento {event} rechazado."
            message_type = messages.WARNING
        event.approved_by = request.user
        event.save()
        self.message_user(request, message, message_type)
        return redirect('admin:hrm_employeeevent_changelist')
