from rest_framework import permissions


class IsOrganizationMember(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.organization.organizationuser_set.filter(user=request.user).exists()
