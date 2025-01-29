# admin_mixins.py
from django.contrib import admin
from common.profiles.models import UserProfile


class ByOrganizationAdminMixin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if hasattr(request, 'organization'):
            return qs.filter(organization=request.organization)
        return qs

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            if hasattr(request, 'organization'):
                obj.organization = request.organization
        super().save_model(request, obj, form, change)


class ByProductForOrganizationAdminMixin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if hasattr(request, 'organization'):
            return qs.filter(product__organization=request.organization)
        return qs

class DisableInlineRelatedLinksMixin:
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        form = formset.form
        for field in form.base_fields.values():
            field.widget.can_add_related = False
            field.widget.can_change_related = False
            field.widget.can_delete_related = False
            field.widget.can_view_related = False
        return formset

class ByUserAdminMixin(admin.ModelAdmin):
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if hasattr(request, 'user'):
            user_profile = UserProfile.objects.get(user=request.user)
            return queryset.filter(user=user_profile)
        return queryset

    def save_model(self, request, obj, form, change):
        user_profile = UserProfile.objects.get(user=request.user)
        obj.user = user_profile
        super().save_model(request, obj, form, change)

