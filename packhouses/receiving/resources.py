from common.base.utils import ExportResource, DehydrationResource, default_excluded_fields, render_html_list
from import_export.fields import Field
from import_export import fields, resources
from django.utils.translation import gettext_lazy as _
from .models import IncomingProduct

def get_model_fields_verbose_names(model, excluded_fields=None):
    excluded_fields = excluded_fields or []
    fields = []
    for field in model._meta.fields:
        if field.name not in excluded_fields:
            fields.append(field.verbose_name or field.name)
    return fields

def transform_data(queryset, excluded_fields=None):
    excluded_fields = excluded_fields or []
    transformed_data = []

    for obj in queryset:
        row = []
        for field in obj._meta.fields:
            if field.name not in excluded_fields:
                value = getattr(obj, field.name)
                if field.name == "gross_weight" or field.name == "net_weight":
                    value = f"{value} Kg" if value else "N/A"
                row.append(value)
        transformed_data.append(row)
    
    return transformed_data

class IncomingProductResource(DehydrationResource, ExportResource):
    public_weighing_scale = Field(column_name=_("Public Weighing Scale"), readonly=True)
    harvest_ooid = Field(column_name=_("Harvest Number"), readonly=True)

    def __init__(self, export_format=None, **kwargs):
        super().__init__(**kwargs)
        self.export_format = export_format

    def dehydrate_public_weighing_scale(self, obj):
        return obj.public_weighing_scale.name if obj.public_weighing_scale else ""

    def dehydrate_is_quarantined(self, obj):
        return str(_('Yes')) if obj.is_quarantined else str(_('No'))
    
    def dehydrate_harvest_ooid(self, obj):
        harvest_ooid = hasattr(obj, 'scheduleharvest') and obj.scheduleharvest is not None
        if harvest_ooid:
            ooid = obj.scheduleharvest.ooid
            return ooid or ""
        else:
            return ""

    # properties
    weighed_sets_count = fields.Field(column_name=_('Total Weighed Sets'), attribute="weighed_sets_count",readonly=True)
    containers_count = fields.Field(column_name=_('Total Containers'), attribute="containers_count",readonly=True)
    total_net_weight = fields.Field(column_name=_('Total Net Weight'), attribute="total_net_weight",readonly=True)
    average_weight_per_container = fields.Field(column_name=_('Average Weight per Container'), attribute="average_weight_per_container",readonly=True)
    assigned_container_total = fields.Field(column_name=_('Assigned Containers'), attribute="assigned_container_total",readonly=True)
    full_container_total = fields.Field(column_name=_('Full Containers per Harvest'), attribute="full_container_total",readonly=True)
    empty_container_total = fields.Field(column_name=_('Empty Containers'), attribute="empty_container_total",readonly=True)
    missing_container_total = fields.Field(column_name=_('Missing Containers '), attribute="missing_container_total",readonly=True)
    
    class Meta:
        model = IncomingProduct
        exclude = tuple(default_excluded_fields + ('batch', 'id' ))
        export_order = ('harvest_ooid','public_weighing_scale', 'weighing_record_number', 'public_weight_result', 'kg_sample', 'weighed_sets_count', 
                        'containers_count', 'total_net_weight', 'average_weight_per_container', 'assigned_container_total', 
                        'full_container_total', 'empty_container_total', 'missing_container_total', 'phytosanitary_certificate',
                        'mrl', 'is_quarantined', 'status',)
        

