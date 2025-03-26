from django.contrib import admin
from cities_light.models import Country, Region, SubRegion, City
from common.profiles.models import UserProfile, OrganizationProfile, PackhouseExporterSetting, PackhouseExporterProfile
from .models import Order
from ..catalogs.models import Client, Maquiladora
from common.base.models import ProductKind
from django.utils.translation import gettext_lazy as _


class ByMaquiladoraForOrganizationOrderFilter(admin.SimpleListFilter):
    title = _('Maquiladora')
    parameter_name = 'maquiladora'

    def lookups(self, request, model_admin):
        maquiladoras = Maquiladora.objects.none()
        if hasattr(request, 'organization'):
            maquiladora_ids = list(Order.objects.filter(organization=request.organization).values_list('maquiladora', flat=True).distinct())
            maquiladoras = Maquiladora.objects.filter(id__in=maquiladora_ids).order_by('name')
        return [(maquiladora.id, maquiladora.name) for maquiladora in maquiladoras]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(maquiladora=self.value())
        return queryset


class ByClientForOrganizationOrderFilter(admin.SimpleListFilter):
    title = _('Client')
    parameter_name = 'client'

    def lookups(self, request, model_admin):
        clients = Client.objects.none()
        if hasattr(request, 'organization'):
            client_ids = list(Order.objects.filter(organization=request.organization).values_list('client', flat=True).distinct())
            clients = Client.objects.filter(id__in=client_ids).order_by('name')
        return [(client.id, client.name) for client in clients]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(client=self.value())
        return queryset
