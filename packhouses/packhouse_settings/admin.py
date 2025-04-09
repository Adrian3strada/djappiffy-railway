from django.contrib import admin
from .models import (Status, Bank, VehicleOwnershipKind, VehicleKind, VehicleFuelKind,
                     PaymentKind, VehicleBrand, AuthorityPackagingKind,
                     OrchardCertificationVerifier,
                     OrchardCertificationKind, PaymentKindAdditionalInput)
from common.widgets import UppercaseTextInputWidget, UppercaseAlphanumericTextInputWidget
from organizations.models import Organization
from common.utils import is_instance_used
from common.base.mixins import ByOrganizationAdminMixin
from common.base.decorators import uppercase_formset_charfield, uppercase_alphanumeric_formset_charfield
from common.base.decorators import uppercase_form_charfield, uppercase_alphanumeric_form_charfield

# Register your models here.


@admin.register(Status)
class StatusAdmin(ByOrganizationAdminMixin):
    list_display = ('name', 'is_enabled')
    list_filter = ('is_enabled',)
    fields = ('name', 'is_enabled', 'order')

    @uppercase_form_charfield('name')
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return form

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj and is_instance_used(obj, exclude=[Organization]):
            readonly_fields.extend(['name', 'has_performance', 'organization'])
        return readonly_fields


@admin.register(Bank)
class BankAdmin(ByOrganizationAdminMixin):
    list_display = ('name', 'is_enabled')
    list_filter = ('is_enabled',)
    fields = ('name', 'is_enabled')

    @uppercase_form_charfield('name')
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return form

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj and is_instance_used(obj, exclude=[Organization]):
            readonly_fields.extend(['name', 'organization'])
        return readonly_fields


@admin.register(VehicleOwnershipKind)
class VehicleOwnershipAdmin(ByOrganizationAdminMixin):
    list_display = ('name', 'is_enabled')
    list_filter = ('is_enabled',)
    fields = ('name', 'is_enabled')

    @uppercase_form_charfield('name')
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return form

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj and is_instance_used(obj, exclude=[Organization]):
            readonly_fields.extend(['name', 'organization'])
        return readonly_fields


@admin.register(VehicleKind)
class VehicleKindAdmin(ByOrganizationAdminMixin):
    list_display = ('name', 'is_enabled')
    list_filter = ('is_enabled',)
    fields = ('name', 'is_enabled')

    @uppercase_form_charfield('name')
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return form

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj and is_instance_used(obj, exclude=[Organization]):
            readonly_fields.extend(['name', 'organization'])
        return readonly_fields


@admin.register(VehicleFuelKind)
class VehicleFuelAdmin(ByOrganizationAdminMixin):
    list_display = ('name', 'is_enabled')
    list_filter = ('is_enabled',)
    fields = ('name', 'is_enabled')

    @uppercase_form_charfield('name')
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return form

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj and is_instance_used(obj, exclude=[Organization]):
            readonly_fields.extend(['name', 'organization'])
        return readonly_fields


class PaymentKindAdditionalInputInlineAdmin(admin.TabularInline):
    model = PaymentKindAdditionalInput
    extra = 0
    fields = ('name','data_type', 'is_required', 'is_enabled',)

    @uppercase_formset_charfield('name')
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        return formset


@admin.register(PaymentKind)
class PaymentKindAdmin(ByOrganizationAdminMixin):
    list_display = ('name', 'is_enabled')
    list_filter = ('is_enabled',)
    fields = ('name', 'is_enabled')
    inlines = [PaymentKindAdditionalInputInlineAdmin, ]

    @uppercase_form_charfield('name')
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return form

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj and is_instance_used(obj, exclude=[Organization]):
            readonly_fields.extend(['name', 'organization'])
        return readonly_fields


@admin.register(VehicleBrand)
class VehicleBrandAdmin(ByOrganizationAdminMixin):
    list_display = ('name', 'is_enabled')
    list_filter = ('is_enabled',)
    fields = ('name', 'is_enabled')

    @uppercase_form_charfield('name')
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return form

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj and is_instance_used(obj, exclude=[Organization]):
            readonly_fields.extend(['name', 'organization'])
        return readonly_fields


@admin.register(AuthorityPackagingKind)
class AuthorityPackagingKindAdmin(ByOrganizationAdminMixin):
    list_display = ('name', 'is_enabled')
    list_filter = ('is_enabled',)
    search_fields = ('name',)
    fields = ('name', 'is_enabled')

    @uppercase_form_charfield('name')
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return form


@admin.register(OrchardCertificationVerifier)
class OrchardCertificationVerifierAdmin(ByOrganizationAdminMixin):
    list_display = ('name', 'is_enabled')
    list_filter = ('is_enabled',)
    fields = ('name', 'is_enabled')

    @uppercase_form_charfield('name')
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return form

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj and is_instance_used(obj, exclude=[Organization]):
            readonly_fields.extend(['name', 'organization'])
        return readonly_fields


@admin.register(OrchardCertificationKind)
class OrchardCertificationKindAdmin(ByOrganizationAdminMixin):
    list_display = ('name', 'is_enabled')
    list_filter = ('is_enabled',)
    fields = ('name', 'verifiers', 'extra_code_name', 'is_enabled')

    @uppercase_form_charfield('name')
    @uppercase_alphanumeric_form_charfield('extra_code_name')
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return form

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj and is_instance_used(obj, exclude=[Organization]):
            readonly_fields.extend(['name', 'organization'])
        return readonly_fields

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'verifiers':
            kwargs['queryset'] = OrchardCertificationVerifier.objects.filter(organization=request.organization, is_enabled=True)

        return super().formfield_for_manytomany(db_field, request, **kwargs)
