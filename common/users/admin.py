from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group as OriginalGroup
from django.utils.translation import gettext_lazy as _
from organizations.models import OrganizationUser, OrganizationOwner
from .models import User, Group, Permission

class OrganizationUserInline(admin.TabularInline):
    model = OrganizationUser
    max_num = 1
    max_num = 1
    verbose_name = _('Is admin')
    verbose_name_plural = _('Is admin')
    fields = ["is_admin", "organization"]
    can_delete = False

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if not request.user.is_superuser:
            fields = ["is_admin"]
            return fields
        
        return fields

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        if 'organization' in formset.form.base_fields:
            formset.form.base_fields['organization'].widget.can_add_related = False
            formset.form.base_fields['organization'].widget.can_change_related = False
            formset.form.base_fields['organization'].widget.can_delete_related = False
            formset.form.base_fields['organization'].widget.can_view_related = False

        return formset

    class Media:
        js = ('js/admin/forms/common/eye_admin.js',)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Override Django's default UserAdmin to use the email address
    as the identifier, instead of username.
    """

    # list_display = ["username", "email",
    #                 "first_name", "last_name",
    #                 "is_superuser", "is_staff", "is_active",
    #                 "date_joined", "last_login"]
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
        else:
            creator_user = OrganizationUser.objects.filter(user=request.user).first()
            if creator_user:
                creator_is_owner = OrganizationOwner.objects.filter(organization = request.organization, organization_user_id=creator_user).exists()
                if creator_user.is_admin and not creator_is_owner:
                    return []

        return super().get_inline_instances(request, obj)

    def has_delete_permission(self, request, obj=None):
        # Retorna False para desactivar la opción de eliminar
        return False

    def get_list_display(self, request):
        list = []
        if request.user.is_superuser:
            list = ["username", "email",
                    "first_name", "last_name",
                    "is_superuser", "is_staff", "is_active",
                    "date_joined", "last_login"]
        else:
            list =["username", "email",
                    "first_name", "last_name",
                    "is_active", "date_joined", "last_login"]
        return list

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)

        if not request.user.is_superuser:
            # Modificar la sección de permisos eliminando algunos campos
            updated_fieldsets = []
            for name, options in fieldsets:
                if name == _("Permissions"):
                    fields = tuple(
                        f for f in options["fields"]
                        if f not in ("is_superuser", "is_staff", "user_permissions")
                    )
                    updated_fieldsets.append((name, {"fields": fields}))
                else:
                    updated_fieldsets.append((name, options))
            return updated_fieldsets
        return fieldsets

    def get_queryset(self, request):
        queryset = super().get_queryset(request)

        # users_organization = OrganizationUser.objects.filter(organization=request.organization).values_list('user_id', flat=True)
        # if users_organization:
        #     print(users_organization)
        #     # queryset = queryset.filter(username__in=users_organization)
        # else:
        #     return queryset.none()    
        
        if not request.user.is_superuser:
            users = OrganizationUser.objects.filter(organization=request.organization).values_list('user_id', flat=True)
            user = OrganizationUser.objects.filter(user=request.user).first()
            if user:
                owner = OrganizationOwner.objects.filter(organization = request.organization).first()
                if owner.organization_user_id == user.id:
                    queryset = queryset.filter(username__in=users)
                elif user.is_admin:
                    queryset = queryset.filter(username__in=users).exclude(username=owner.organization_user.user)
        
        return queryset

    def save_model(self, request, obj, form, change):
        if not obj.is_staff:
            creator_user = OrganizationUser.objects.filter(user=request.user).first()
            if creator_user:
                creator_is_owner = OrganizationOwner.objects.filter(organization = request.organization, organization_user_id=creator_user).exists()
                if creator_user.is_admin or creator_is_owner:
                    obj.is_staff = True
                    super().save_model(request, obj, form, change)

                    user_new = OrganizationUser.objects.filter(user_id=obj).exists()
                    if not user_new:
                        OrganizationUser.objects.create(
                            organization_id = creator_user.organization_id,
                            user_id = obj.username
                        )
        obj.save()

admin.site.unregister(OriginalGroup)
admin.site.register(Group)
# admin.site.register(Permission)
