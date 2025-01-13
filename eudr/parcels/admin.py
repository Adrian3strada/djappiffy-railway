from django.contrib import admin
from .models import Parcel
from django.contrib.gis.db import models as geomodels
# from django.contrib.gis.forms import OSMWidget
from .forms import OLGoogleMapsSatelliteWidget

# Register your models here.


# descomentar en desarrollo
# @admin.register(Parcel)
class ParcelAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'uuid', 'ooid', 'producer_name', 'country', 'state', 'city', 'created_at',)
    search_fields = ('name', 'code', 'producer__name')
    list_filter = ('country', 'state', 'city', 'producer',)
    readonly_fields = ('uuid', 'ooid', 'created_at', 'geom_extent', 'buffer_extent')
    fields = ('uuid', 'ooid', 'created_at', 'name', 'code', 'country', 'state', 'city', 'file', 'geom', 'geom_extent', 'buffer_extent', 'producer')

    def producer_name(self, obj):
        return obj.producer.name

    producer_name.short_description = 'Producer Name'

    def has_module_permission(self, request):
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser

    def formfield_for_dbfield(self, db_field, **kwargs):
        if isinstance(db_field, geomodels.GeometryField):
            kwargs['widget'] = OLGoogleMapsSatelliteWidget()
        return super().formfield_for_dbfield(db_field, **kwargs)

    class Media:
        js = ('js/admin/forms/parcels/center_map.js',)
