from django.contrib import admin
from .models import OperatorParcel, ProductionInterval, LegalCompliance
from django.contrib.gis.db import models as geomodels
# from django.contrib.gis.forms import OSMWidget
from .forms import OLGoogleMapsSatelliteWidget

# Register your models here.


# descomentar en desarrollo
@admin.register(OperatorParcel)
class OperatorParcelAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'uuid', 'ooid', 'eudr_operator_name', 'country', 'state', 'city', 'created_at',)
    search_fields = ('name', 'code', 'eudr_operator__name')
    list_filter = ('country', 'state', 'city', 'eudr_operator',)
    readonly_fields = ('uuid', 'ooid', 'created_at', 'geom_extent', 'buffer_extent')
    fields = ('uuid', 'ooid', 'created_at', 'name', 'code', 'country', 'state', 'city', 'file', 'geom', 'geom_extent', 'buffer_extent', 'eudr_operator')

    def eudr_operator_name(self, obj):
        return obj.eudr_operator.name

    eudr_operator_name.short_description = 'EUDR Operator Name'

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


@admin.register(ProductionInterval) # This is just for dev
class ProductionIntervalAdmin(admin.ModelAdmin):
    list_display = ('start_date', 'end_date', 'operator_parcel')
    # search_fields = ('operator_parcel')
    # list_filter = ('operator_parcel')
    # readonly_fields = ('operator_parcel')
    fields = ('operator_parcel', 'start_date', 'end_date')


    def has_module_permission(self, request):
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser
    
@admin.register(LegalCompliance) # This is just for dev
class LegalComplianceAdmin(admin.ModelAdmin):
    list_display = ('land_use_right', 'operator_parcel')
    
    fields = (
        'operator_parcel', 
        'land_use_right', 
        'third_party_rights', 
        'environmental_protection', 
        'free_prior_informed_consent', 
        'labor_and_human_rights' 
    )

    def has_module_permission(self, request):
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser



