from django.contrib import admin
from organizations.admin import OrganizationAdmin, OrganizationUserAdmin
from organizations.models import Organization, OrganizationUser
from .models import ProductKind
from wagtail.documents.models import Document
from wagtail.images.models import Image
from taggit.models import Tag


@admin.register(ProductKind)
class ProductKindAdmin(admin.ModelAdmin):
    pass


class CustomOrganizationAdmin(OrganizationAdmin):
    list_display = ["id", "name", "slug", "created", "modified", "is_active"]
    ordering = ["id"]


class CustomOrganizationUserAdmin(OrganizationUserAdmin):
    list_display = ["id", "created", "modified", "is_admin",
                    "organization", "user"]
    list_display_links = ["id", "organization", "user"]
    ordering = ["id"]


admin.site.unregister(Organization)
admin.site.register(Organization, CustomOrganizationAdmin)
admin.site.unregister(OrganizationUser)
admin.site.register(OrganizationUser, CustomOrganizationUserAdmin)

admin.site.unregister(Document)
admin.site.unregister(Image)
admin.site.unregister(Tag)
