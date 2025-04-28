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
    fields = ["is_admin"]
    can_delete = False

    def get_readonly_fields(self, request, obj=None):
        if obj:
            if not request.user.is_superuser:
                if obj != request.user:
                    user_request = OrganizationUser.objects.filter(organization = request.organization, user=request.user).first()
                    if user_request:
                        user_request_is_owner = OrganizationOwner.objects.filter(organization = request.organization, organization_user_id=user_request).exists()

                        if not user_request_is_owner:
                            user_obj = OrganizationUser.objects.filter(organization = request.organization, user=obj).first()
                            
                            if user_obj:
                                user_obj_is_owner = OrganizationOwner.objects.filter(organization = request.organization, organization_user_id=user_obj).exists()

                                if user_obj.is_admin or user_obj_is_owner:
                                    return ["is_admin"]

        return super().get_readonly_fields(request, obj)

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
            creator_user = OrganizationUser.objects.filter(organization = request.organization, user=request.user).first()
            
            if creator_user:
                creator_is_owner = OrganizationOwner.objects.filter(organization = request.organization, organization_user_id=creator_user).exists()
                
                if not request.user.is_superuser and not creator_user.is_admin and not creator_is_owner:
                    return []

        return super().get_inline_instances(request, obj)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            if not request.user.is_superuser:
                if obj != request.user:
                    user_request = OrganizationUser.objects.filter(organization = request.organization, user=request.user).first()
                    if user_request:
                        user_request_is_owner = OrganizationOwner.objects.filter(organization = request.organization, organization_user_id=user_request).exists()

                        if not user_request_is_owner:
                            user_obj = OrganizationUser.objects.filter(organization = request.organization, user=obj).first()
                            
                            if user_obj:
                                user_obj_is_owner = OrganizationOwner.objects.filter(organization = request.organization, organization_user_id=user_obj).exists()

                                if user_obj.is_admin or user_obj_is_owner:
                                    readonly_fields = [field.name for field in obj._meta.fields]
                                    readonly_fields += ['groups', 'user_permissions']
                                    return readonly_fields

        return super().get_readonly_fields(request, obj)

    def has_change_permission(self, request, obj=None):
        if obj:
            if not request.user.is_superuser:
                if obj != request.user:
                    user_request = OrganizationUser.objects.filter(organization = request.organization, user=request.user).first()
                    if user_request:
                        user_request_is_owner = OrganizationOwner.objects.filter(organization = request.organization, organization_user_id=user_request).exists()

                        if not user_request_is_owner:
                            user_obj = OrganizationUser.objects.filter(organization = request.organization, user=obj).first()
                            
                            if user_obj:
                                user_obj_is_owner = OrganizationOwner.objects.filter(organization = request.organization, organization_user_id=user_obj).exists()

                                if user_obj.is_admin or user_obj_is_owner:
                                    return request.method in ["GET", "HEAD"]

        return super().has_change_permission(request, obj)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        obj = self.get_object(request, object_id)

        if obj:
            if not request.user.is_superuser:
                if obj != request.user:
                    user_request = OrganizationUser.objects.filter(organization = request.organization, user=request.user).first()
                    if user_request:
                        user_request_is_owner = OrganizationOwner.objects.filter(organization = request.organization, organization_user_id=user_request).exists()

                        if not user_request_is_owner:
                            user_obj = OrganizationUser.objects.filter(organization = request.organization, user=obj).first()
                            
                            if user_obj:
                                user_obj_is_owner = OrganizationOwner.objects.filter(organization = request.organization, organization_user_id=user_obj).exists()

                                if user_obj_is_owner or user_obj.is_admin:
                                    extra_context['show_save'] = False
                                    extra_context['show_save_and_continue'] = False
                                    extra_context['show_save_and_add_another'] = False

        return super().change_view(request, object_id, form_url, extra_context=extra_context)

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
        updated_fieldsets = []
        fields_to_hide = []

        if obj and obj == request.user:
            fields_to_hide.append("is_active")

            if not request.user.is_superuser:
                fields_to_hide += ["is_superuser", "is_staff", "user_permissions"]

        else:
            if not request.user.is_superuser:
                fields_to_hide += ["is_superuser", "is_staff", "user_permissions"]

        for name, options in fieldsets:
            if name == _("Permissions"):
                fields = tuple(
                    f for f in options["fields"]
                    if f not in fields_to_hide
                )
                updated_fieldsets.append((name, {"fields": fields}))
            else:
                updated_fieldsets.append((name, options))

        return updated_fieldsets

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        users_organization = OrganizationUser.objects.filter(organization=request.organization).values_list('user_id', flat=True)
        
        if users_organization:
            queryset = queryset.filter(username__in=users_organization)
        
        else:
            return queryset.none()    
        
        return queryset
    
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "groups":
            if not request.user.is_superuser:
                creator_user = OrganizationUser.objects.filter(organization = request.organization, user=request.user).first()
                
                if creator_user:
                    creator_is_owner = OrganizationOwner.objects.filter(organization = request.organization, organization_user_id=creator_user).exists()
                    
                    if not request.user.is_superuser and not creator_user.is_admin and not creator_is_owner:
                        manage_users = Permission.objects.filter(codename__in=["add_user", "change_user", "view_user", "delete_user"]).values_list('id', flat=True)
                        kwargs["queryset"] = Group.objects.exclude(permissions__in=manage_users)
                    
                    else:
                        kwargs["queryset"] = Group.objects.all()

        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if not obj.is_staff:
            obj.is_staff = True
            super().save_model(request, obj, form, change)

            user_new = OrganizationUser.objects.filter(user_id=obj).exists()
            if not user_new:
                OrganizationUser.objects.create(
                    organization_id = request.organization.id,
                    user_id = obj.username
                )
        obj.save()

admin.site.unregister(OriginalGroup)
admin.site.register(Group)
# admin.site.register(Permission)
