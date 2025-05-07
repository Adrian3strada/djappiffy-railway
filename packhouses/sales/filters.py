from django.contrib import admin
from cities_light.models import Country, Region, SubRegion, City
from common.profiles.models import UserProfile, OrganizationProfile, PackhouseExporterSetting, PackhouseExporterProfile
from .models import Order
from .utils import incoterms_choices
from ..catalogs.models import Client, Maquiladora, Product, ProductVariety
from common.base.models import ProductKind, LocalDelivery, Incoterm
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


class ByLocalDeliveryForOrganizationOrderFilter(admin.SimpleListFilter):
    title = _('Local delivery')
    parameter_name = 'local_delivery'

    def lookups(self, request, model_admin):
        local_deliveries = LocalDelivery.objects.none()
        if hasattr(request, 'organization'):
            local_delivery_related = list(Order.objects.filter(organization=request.organization).values_list('local_delivery', flat=True).distinct())
            local_deliveries = LocalDelivery.objects.filter(id__in=local_delivery_related).order_by('name')
        return [(local_delivery.id, local_delivery.name) for local_delivery in local_deliveries]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(local_delivery=self.value())
        return queryset


class ByIncotermsForOrganizationOrderFilter(admin.SimpleListFilter):
    title = _('Incoterms')
    parameter_name = 'incoterms'

    def lookups(self, request, model_admin):
        incoterms = LocalDelivery.objects.none()
        if hasattr(request, 'organization'):
            incoterms_related = list(Order.objects.filter(organization=request.organization).values_list('incoterms', flat=True).distinct())
            incoterms = Incoterm.objects.filter(id__in=incoterms_related).order_by('name')
        return [(incoterm.id, incoterm.name) for incoterm in incoterms]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(incoterms=self.value())
        return queryset


class ByProductForOrganizationOrderFilter(admin.SimpleListFilter):
    title = _('Product')
    parameter_name = 'product'

    def lookups(self, request, model_admin):
        products = LocalDelivery.objects.none()
        if hasattr(request, 'organization'):
            product_related = list(Order.objects.filter(organization=request.organization).values_list('product', flat=True).distinct())
            products = Product.objects.filter(id__in=product_related).order_by('name')
        return [(product.id, product.name) for product in products]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(product=self.value())
        return queryset


class ByProductVarietyForOrganizationOrderFilter(admin.SimpleListFilter):
    title = _('Product variety')
    parameter_name = 'product_variety'

    def lookups(self, request, model_admin):
        product_varieties = LocalDelivery.objects.none()
        if hasattr(request, 'organization'):
            product_variety_related = list(Order.objects.filter(organization=request.organization).values_list('product_variety', flat=True).distinct())
            product_varieties = ProductVariety.objects.filter(id__in=product_variety_related).order_by('name')
        return [(product_variety.id, product_variety.name) for product_variety in product_varieties]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(product_variety=self.value())
        return queryset
