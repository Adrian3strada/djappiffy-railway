from django.contrib import admin
from organizations.admin import OrganizationAdmin, OrganizationUserAdmin
from organizations.models import Organization, OrganizationUser
from .models import (ProductKind, ProductKindCountryStandard, CountryProductStandardSize, LegalEntityCategory, CapitalFramework,
                     CountryProductStandardPackaging, SupplyKind,
                     Incoterm, LocalDelivery, Currency)
from .filters import (ByProductKindForPackagingFilter, ByCountryForMarketProductSizeStandardFilter,
                      ByCountryForCapitalFrameworkFilter)
from wagtail.documents.models import Document
from wagtail.images.models import Image
from taggit.models import Tag
from adminsortable2.admin import SortableAdminMixin
from .decorators import uppercase_form_charfield
from django.utils.translation import gettext_lazy as _

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

# TODO: Remover este cuando todo packaging esté completo
@admin.register(CountryProductStandardPackaging)
class CountryProductStandardPackagingAdmin(admin.ModelAdmin):
    pass


class CountryProductStandardPackagingInline(admin.TabularInline):
    model = CountryProductStandardPackaging
    extra = 0
    verbose_name = 'Standard packaging'
    verbose_name_plural = 'Standard packaging'

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        if 'supply_kind' in formset.form.base_fields:
            formset.form.base_fields['supply_kind'].widget.can_add_related = False
            formset.form.base_fields['supply_kind'].widget.can_change_related = False
            formset.form.base_fields['supply_kind'].widget.can_delete_related = False
            formset.form.base_fields['supply_kind'].widget.can_view_related = False
        return formset

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'supply_kind':
            kwargs['queryset'] = SupplyKind.objects.filter(category='packaging_containment', is_enabled=True)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(ProductKindCountryStandard)
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


@admin.register(CapitalFramework)
class CapitalFrameworkAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'country']
    search_fields = ['name',]
    list_filter = [ByCountryForCapitalFrameworkFilter]


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

@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_enabled')
    list_filter = ['is_enabled']

    @uppercase_form_charfield('code')
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return form


@admin.register(SupplyKind)
class SupplyKindAdmin(admin.ModelAdmin):
    list_display = ('name', 'usage_unit_kind', 'category', 'is_enabled')
    list_filter = ('category', 'usage_unit_kind', 'is_enabled',)

    @uppercase_form_charfield('name')
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return form
