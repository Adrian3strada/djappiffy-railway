# admin_mixins.py
from django.contrib import admin
from common.profiles.models import UserProfile
from django.contrib.auth import get_user_model
User = get_user_model()


class ByOrganizationAdminMixin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if hasattr(request, 'organization'):
            return qs.filter(organization=request.organization)
        return qs

    def get_fields(self, request, obj=None):
        fields = list(super().get_fields(request, obj))
        if 'organization' in fields:
            fields.remove('organization')
        return fields

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
    """
    Mixin para eliminar todos los botones de "agregar", "editar", "ver" y "eliminar"
    relacionados en los formularios inlines del admin.
    """
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        form = formset.form

        for field in form.base_fields.values():
            widget = field.widget
            # Solo afecta widgets que soportan relaciones (como ForeignKeyRawIdWidget, RelatedFieldWidgetWrapper, etc.)
            for attr in ['can_add_related', 'can_change_related', 'can_delete_related', 'can_view_related']:
                if hasattr(widget, attr):
                    setattr(widget, attr, False)

        return formset

class ByUserAdminMixin(admin.ModelAdmin):
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if hasattr(request, 'user'):
            user_profile = User.objects.get(username=request.user)
            return queryset.filter(user=user_profile)
        return queryset

    def save_model(self, request, obj, form, change):
        user_profile = User.objects.get(username=request.user)
        obj.user = user_profile
        super().save_model(request, obj, form, change)

class DisableLinksAdminMixin:
    """
    Mixin para desactivar los botones de agregar, editar, ver y eliminar
    relacionados en campos ForeignKey y ManyToManyField del admin principal (no inlines).
    """
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        for field in form.base_fields.values():
            widget = field.widget
            for attr in ['can_add_related', 'can_change_related', 'can_delete_related', 'can_view_related']:
                if hasattr(widget, attr):
                    setattr(widget, attr, False)

        return form
