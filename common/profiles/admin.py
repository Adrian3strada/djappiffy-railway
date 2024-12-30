from django.contrib import admin
from .models import (UserProfile, OrganizationProfile, ProducerProfile,
                     ImporterProfile, PackhouseExporterProfile,
                     TradeExporterProfile, PackhouseExporterSetting)
from django.utils.translation import gettext_lazy as _
from cities_light.models import Country, Region, SubRegion, City
from organizations.models import Organization
from common.billing.models import LegalEntityCategory
from common.base.models import ProductKind


# Register your Admin classes here.


# Admin Mixins

class OrganizationProfileMixin:
    list_display = ("name", "country_name", "state_name", "city_name", "email", "phone_number", "is_enabled")
    list_filter = ("country", "state", "city", "district", "is_enabled")
    search_fields = ("name", "tax_id", "neighborhood", "postal_code", "email", "phone_number")

    def country_name(self, obj):
        return obj.country.name

    country_name.short_description = _("Country")
    country_name.admin_order_field = 'country__name'

    def state_name(self, obj):
        return obj.state.name

    state_name.short_description = _("State")
    state_name.admin_order_field = 'state__name'

    def city_name(self, obj):
        return obj.city.name

    city_name.short_description = _("City")
    city_name.admin_order_field = 'city__name'

    class Media:
        js = [
            'js/admin/forms/common/country-state-city.js',
            'js/admin/forms/common/profiles/packhouseexporterprofile.js',
        ]


# /Admin Mixins


# Admin classes

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "first_name", "last_name", "phone_number", "country")
    ordering = ("user",)


@admin.register(ProducerProfile)
class ProducerProfileAdmin(admin.ModelAdmin, OrganizationProfileMixin):
    pass


@admin.register(ImporterProfile)
class ImporterProfileAdmin(admin.ModelAdmin, OrganizationProfileMixin):
    pass


class PackhouseExporterSettingInline(admin.StackedInline):
    model = PackhouseExporterSetting
    extra = 1
    min_num = 1
    max_num = 1
    can_delete = False
    verbose_name = _("Platform setting")

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'product_kinds':
            kwargs['queryset'] = ProductKind.objects.filter(for_packaging=True, is_enabled=True)
            formfield = super().formfield_for_manytomany(db_field, request, **kwargs)
            formfield.required = True
            return formfield

        return super().formfield_for_manytomany(db_field, request, **kwargs)


@admin.register(PackhouseExporterProfile)
class PackhouseExporterProfileAdmin(admin.ModelAdmin, OrganizationProfileMixin):
    inlines = [PackhouseExporterSettingInline]

    def get_fields(self, request, obj=None):
        fields = list(super().get_fields(request, obj))
        if not request.user.is_superuser:
            fields.remove('product_kinds')
        return fields

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'legal_category' in form.base_fields:
            form.base_fields['legal_category'].required = True
        if 'hostname' in form.base_fields and request.user.is_superuser:
            form.base_fields['hostname'].required = True
        return form

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        object_id = request.resolver_match.kwargs.get("object_id")
        obj = OrganizationProfile.objects.get(id=object_id) if object_id else None

        if db_field.name == "state":
            if request.POST:
                country_id = request.POST.get('country')
            else:
                country_id = obj.country_id if obj else None
            if country_id:
                kwargs["queryset"] = Region.objects.filter(country_id=country_id)
            else:
                kwargs["queryset"] = Region.objects.none()
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda item: item.name
            return formfield

        if db_field.name == "city":
            if request.POST:
                state_id = request.POST.get('state')
            else:
                state_id = obj.state_id if obj else None
            if state_id:
                kwargs["queryset"] = SubRegion.objects.filter(region_id=state_id)
            else:
                kwargs["queryset"] = SubRegion.objects.none()
            print("city", kwargs["queryset"])
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda item: item.name
            return formfield

        if db_field.name == "district":
            if request.POST:
                city_id = request.POST.get('city')
            else:
                city_id = obj.city_id if obj else None
            if city_id:
                kwargs["queryset"] = City.objects.filter(subregion_id=city_id)
            else:
                kwargs["queryset"] = City.objects.none()
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda item: item.name
            return formfield

        if db_field.name == "legal_category":
            if request.POST:
                country_id = request.POST.get('country')
            else:
                country_id = obj.country_id if obj else None
            if country_id:
                kwargs["queryset"] = LegalEntityCategory.objects.filter(country_id=country_id)
            else:
                kwargs["queryset"] = LegalEntityCategory.objects.none()
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda item: f"{item.code}: {item.name}"
            return formfield

        if db_field.name == "organization":
            queryset = Organization.objects.filter(organizationprofile__isnull=True)
            if obj:
                queryset = queryset | Organization.objects.filter(id=obj.organization_id)
            if not request.user.is_superuser:
                queryset = queryset.filter(id=obj.organization_id)
            kwargs["queryset"] = queryset
            return super().formfield_for_foreignkey(db_field, request, **kwargs)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):

        if db_field.name == 'product_kinds':
            kwargs['queryset'] = ProductKind.objects.filter(for_packaging=True, is_enabled=True)
            formfield = super().formfield_for_manytomany(db_field, request, **kwargs)
            formfield.required = True
            return formfield

        return super().formfield_for_manytomany(db_field, request, **kwargs)


@admin.register(TradeExporterProfile)
class TradeExporterProfileAdmin(admin.ModelAdmin, OrganizationProfileMixin):
    pass
