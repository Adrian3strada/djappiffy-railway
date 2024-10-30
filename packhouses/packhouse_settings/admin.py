from django.contrib import admin
from .models import Status, ProductSizeKind, MassVolumeKind, Bank
from common.widgets import UppercaseTextInputWidget
from organizations.models import Organization
from common.utils import is_instance_used

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


@admin.register(MassVolumeKind)
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
class BankAdmin(admin.ModelAdmin):
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
