from django.contrib import admin
from organizations.admin import OrganizationAdmin, OrganizationUserAdmin
from organizations.models import Organization, OrganizationUser
from .models import (ProductKind, CountryProductStandard, CountryProductStandardSize, LegalEntityCategory,
                     CountryProductStandardPackaging,
                     Incoterm, LocalDelivery)
from .filters import ByProductKindForPackagingFilter, ByCountryForMarketProductSizeStandardFilter
from wagtail.documents.models import Document
from wagtail.images.models import Image
from taggit.models import Tag
from adminsortable2.admin import SortableAdminMixin

#


@admin.register(ProductKind)
class ProductKindAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'for_packaging', 'for_orchard', 'for_eudr', 'is_enabled', 'sort_order')
    list_filter = ['for_packaging', 'for_orchard', 'for_eudr', 'is_enabled']


class CountryProductStandardSizeInline(admin.TabularInline):
    model = CountryProductStandardSize
    extra = 0
    verbose_name = 'Size'
    verbose_name_plural = 'Sizes'


class CountryProductStandardPackagingInline(admin.TabularInline):
    model = CountryProductStandardPackaging
    extra = 0
    verbose_name = 'Packaging'
    verbose_name_plural = 'Packaging'


@admin.register(CountryProductStandard)
class CountryProductStandardAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'product_kind', 'country', 'is_enabled', 'sort_order')
    list_filter = [ByProductKindForPackagingFilter, ByCountryForMarketProductSizeStandardFilter, 'is_enabled']
    search_fields = ['name']
    ordering = ['sort_order']
    inlines = [CountryProductStandardSizeInline, CountryProductStandardPackagingInline]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'product_kind':
            kwargs['queryset'] = ProductKind.objects.filter(for_packaging=True, is_enabled=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


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

