from django.contrib import admin
from .models import (Status, ProductSizeKind, ProductMassVolumeKind, Bank, VehicleOwnershipKind, VehicleKind, VehicleFuelKind,
                     PaymentKind, VehicleBrand, OrchardProductClassificationKind, OrchardCertificationVerifier,
                     OrchardCertificationKind, SupplyKind, SupplyPresentationKind)
from common.widgets import UppercaseTextInputWidget, UppercaseAlphanumericTextInputWidget
from organizations.models import Organization
from common.utils import is_instance_used
from common.base.mixins import ByOrganizationAdminMixin


# Register your models here.


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_enabled')
    list_filter = ('is_enabled',)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['name'].widget = UppercaseTextInputWidget()
        return form

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj and is_instance_used(obj, exclude=[Organization]):
            readonly_fields.extend(['name', 'has_performance', 'organization'])
        return readonly_fields


@admin.register(ProductSizeKind)
class ProductSizeKindAdmin(admin.ModelAdmin):
    list_display = ('name', 'has_performance', 'is_enabled')
    list_filter = ('has_performance', 'is_enabled',)
    fields = ('name', 'has_performance', 'is_enabled', 'organization', 'order')

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'name' in form.base_fields:
            form.base_fields['name'].widget = UppercaseTextInputWidget()
        return form

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj and is_instance_used(obj, exclude=[Organization]):
            readonly_fields.extend(['name', 'has_performance', 'organization'])
        return readonly_fields


@admin.register(ProductMassVolumeKind)
class MassVolumeKindAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_enabled')
    list_filter = ('is_enabled',)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'name' in form.base_fields:
            form.base_fields['name'].widget = UppercaseTextInputWidget()
        return form

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj and is_instance_used(obj, exclude=[Organization]):
            readonly_fields.extend(['name', 'organization'])
        return readonly_fields


@admin.register(Bank)
class BankAdmin(ByOrganizationAdminMixin):
    list_display = ('name', 'is_enabled')
    list_filter = ('is_enabled',)
    fields = ('name', 'is_enabled')

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'name' in form.base_fields:
            form.base_fields['name'].widget = UppercaseTextInputWidget()
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

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'name' in form.base_fields:
            form.base_fields['name'].widget = UppercaseTextInputWidget()
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

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'name' in form.base_fields:
            form.base_fields['name'].widget = UppercaseTextInputWidget()
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

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'name' in form.base_fields:
            form.base_fields['name'].widget = UppercaseTextInputWidget()
        return form

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj and is_instance_used(obj, exclude=[Organization]):
            readonly_fields.extend(['name', 'organization'])
        return readonly_fields


@admin.register(PaymentKind)
class PaymentKindAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_enabled')
    list_filter = ('is_enabled',)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'name' in form.base_fields:
            form.base_fields['name'].widget = UppercaseTextInputWidget()
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

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'name' in form.base_fields:
            form.base_fields['name'].widget = UppercaseTextInputWidget()
        return form

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj and is_instance_used(obj, exclude=[Organization]):
            readonly_fields.extend(['name', 'organization'])
        return readonly_fields


@admin.register(OrchardProductClassificationKind)
class OrchardProductClassificationKindAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_enabled')
    list_filter = ('is_enabled',)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'name' in form.base_fields:
            form.base_fields['name'].widget = UppercaseTextInputWidget()
        return form

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj and is_instance_used(obj, exclude=[Organization]):
            readonly_fields.extend(['name', 'organization'])
        return readonly_fields


@admin.register(OrchardCertificationVerifier)
class OrchardCertificationVerifierAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_enabled')
    list_filter = ('is_enabled',)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'name' in form.base_fields:
            form.base_fields['name'].widget = UppercaseTextInputWidget()
        return form

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj and is_instance_used(obj, exclude=[Organization]):
            readonly_fields.extend(['name', 'organization'])
        return readonly_fields


@admin.register(OrchardCertificationKind)
class OrchardCertificationKindAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_enabled')
    list_filter = ('is_enabled',)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'name' in form.base_fields:
            form.base_fields['name'].widget = UppercaseTextInputWidget()
        if 'extra_code_name' in form.base_fields:
            form.base_fields['extra_code_name'].widget = UppercaseAlphanumericTextInputWidget()
        return form

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj and is_instance_used(obj, exclude=[Organization]):
            readonly_fields.extend(['name', 'organization'])
        return readonly_fields


@admin.register(SupplyKind)
class SupplyKindAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_container', 'is_enabled')
    list_filter = ('is_enabled',)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'name' in form.base_fields:
            form.base_fields['name'].widget = UppercaseTextInputWidget()
        return form

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj and is_instance_used(obj, exclude=[Organization]):
            readonly_fields.extend(['name', 'is_container', 'organization'])
        return readonly_fields


@admin.register(SupplyPresentationKind)
class SupplyPresentationKindAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_enabled')
    list_filter = ('is_enabled',)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'name' in form.base_fields:
            form.base_fields['name'].widget = UppercaseTextInputWidget()
        return form

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj and is_instance_used(obj, exclude=[Organization]):
            readonly_fields.extend(['name', 'organization'])
        return readonly_fields
