from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group as OriginalGroup
from django.utils.translation import gettext_lazy as _
from organizations.models import OrganizationUser
from common.base.mixins import (ByOrganizationAdminMixin)

from .models import User, Group, Permission

class OrganizationUserInline(admin.TabularInline):
    model = OrganizationUser
    max_num = 1
    fields = ["is_admin", "organization"]

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)

        if not request.user.is_superuser:
            fields = ["is_admin"]
        
            return fields
        
        return fields


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Override Django's default UserAdmin to use the email address
    as the identifier, instead of username.
    """

    list_display = ["username", "email",
                    "first_name", "last_name",
                    "is_superuser", "is_staff", "is_active",
                    "date_joined", "last_login"]
    search_fields = ["email", "first_name", "last_name"]
    ordering = ["email"]
    filter_horizontal = ["groups", "user_permissions"]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "email",
                    "password",
                ),
            },
        ),
        (
            _("Personal info"),
            {
                "fields": (
                    "first_name",
                    "last_name",
                )
            },
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (
            _("Important dates"),
            {
                "fields": (
                    "last_login",
                    "date_joined",
                ),
            },
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2",),
            },
        ),
    )
    inlines = [OrganizationUserInline]

    def get_inline_instances(self, request, obj=None):
        if obj is None:
            return []
        return super().get_inline_instances(request, obj)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs


admin.site.unregister(OriginalGroup)
admin.site.register(Group)
# admin.site.register(Permission)
