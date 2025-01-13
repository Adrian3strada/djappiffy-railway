from django.contrib import admin
from cities_light.models import Country, Region, SubRegion, City
from common.profiles.models import UserProfile, OrganizationProfile, PackhouseExporterSetting, PackhouseExporterProfile
from .models import Order
from ..catalogs.models import Client, Maquiladora
from common.base.models import ProductKind
from django.utils.translation import gettext_lazy as _


class ByMaquiladoraForOrganizationFilter(admin.SimpleListFilter):
    title = _('Maquiladora')
    parameter_name = 'maquiladora'

    def lookups(self, request, model_admin):
        organization = getattr(request, 'organization', None)
        maquiladoras = Maquiladora.objects.filter(organization=organization, is_enabled=True)
        return [(maquiladora.id, maquiladora.name) for maquiladora in maquiladoras]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(maquiladora=self.value())
        return queryset


class ByClientForOrganizationFilter(admin.SimpleListFilter):
    title = _('Cliente')
    parameter_name = 'client'

    def lookups(self, request, model_admin):
        organization = getattr(request, 'organization', None)
        clients = Client.objects.filter(organization=organization, is_enabled=True)
        return [(client.id, client.name) for client in clients]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(client=self.value())
        return queryset
