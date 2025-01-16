from django.contrib import admin
from organizations.admin import OrganizationAdmin, OrganizationUserAdmin
from organizations.models import Organization, OrganizationUser
from .models import ProductKind, LegalEntityCategory, Incoterm, LocalDelivery
from wagtail.documents.models import Document
from wagtail.images.models import Image
from taggit.models import Tag
from adminsortable2.admin import SortableAdminMixin

#


@admin.register(ProductKind)
class ProductKindAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'for_packaging', 'for_orchard', 'for_eudr', 'is_enabled', 'sort_order')


@admin.register(Incoterm)
class IncotermAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('get_name', 'is_enabled', 'sort_order')

    def get_name(self, obj):
        return f"{obj.id} -- {obj.name}"
    get_name.short_description = 'Name'


@admin.register(LocalDelivery)
class LocalDeliveryAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'is_enabled', 'sort_order')


@admin.register(LegalEntityCategory)
class LegalEntityCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'country']
    search_fields = ['name',]
    list_filter = ['country']


class CustomOrganizationAdmin(OrganizationAdmin):
    pass


class CustomOrganizationUserAdmin(OrganizationUserAdmin):
    pass


admin.site.unregister(Organization)
admin.site.register(Organization, CustomOrganizationAdmin)
admin.site.unregister(OrganizationUser)
admin.site.register(OrganizationUser, CustomOrganizationUserAdmin)

admin.site.unregister(Document)
admin.site.unregister(Image)
admin.site.unregister(Tag)



# descomentar los siguientes solo para demo o producción, no para desarrollo
# admin.site.unregister(ProductKind)

