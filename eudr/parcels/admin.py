from django.contrib import admin
from .models import Parcel
from django.contrib.gis.db import models as geomodels
# from django.contrib.gis.forms import OSMWidget
from .forms import OLGoogleMapsSatelliteWidget

# Register your models here.


@admin.register(Parcel)
class ParcelAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'uuid', 'created_at', 'producer_name')
    search_fields = ('name', 'code', 'producer__name')
    list_filter = ('producer', )
    readonly_fields = ('uuid', 'created_at', 'geom_extent', 'buffer_extent')
    fields = ('uuid', 'created_at', 'name', 'code', 'file', 'geom', 'geom_extent', 'buffer_extent', 'producer')

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
