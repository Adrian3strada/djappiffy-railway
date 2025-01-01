from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group as OriginalGroup
from django.utils.translation import gettext_lazy as _

from .models import User, Group, Permission


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


admin.site.unregister(OriginalGroup)
admin.site.register(Group)
# admin.site.register(Permission)
