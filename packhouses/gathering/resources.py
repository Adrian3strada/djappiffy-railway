from import_export.fields import Field
from django.utils.formats import date_format
from common.base.utils import ExportResource, DehydrationResource, default_excluded_fields, render_html_list
from .models import ScheduleHarvest
from django.utils.translation import gettext_lazy as _
from packhouses.catalogs.utils import get_harvest_cutting_categories_choices
from django.utils.formats import localize
from django.utils.timezone import localtime

class ScheduleHarvestResource(DehydrationResource, ExportResource):
    crew = Field(column_name=_("Harvesting Crews"), readonly=True)
    orchard_certification = Field(column_name=_("Orchard Certifications"), readonly=True)
    product_producer = Field(column_name=_("Product Producer"), readonly=True)
    product_category = Field(column_name=_("Product Category"), readonly=True)
    is_scheduled = Field(column_name=_("Scheduling Type"), readonly=True)
    category = Field(column_name=_("Harvesting Category"), readonly=True)
    orchard_registry_code = Field(column_name=_("Orchard Registry Code"), readonly=True)
   
    def __init__(self, export_format=None, **kwargs):
        super().__init__(**kwargs)
        self.export_format = export_format

    
    def dehydrate_crew(self, obj):
        crews = obj.scheduleharvestharvestingcrew_set.select_related('harvesting_crew').all()
        if not crews.exists():
            return ' '
        crew_names = [c.harvesting_crew.name for c in crews if c.harvesting_crew]
        return render_html_list(crew_names) if self.export_format == 'pdf' else ", ".join(crew_names)

    def dehydrate_orchard_certification(self, obj):
        certifications = obj.orchard.orchardcertification_set.select_related('certification_kind').all()
        if not certifications.exists():
            return ' '
        cert_names = [cert.certification_kind.name if cert.certification_kind else cert.certification_kind_name for cert in certifications]
        return render_html_list(cert_names) if self.export_format == 'pdf' else ", ".join(cert_names)
    
    def dehydrate_product_producer(self, obj):
        producer = obj.orchard.producer
        if not producer:
            return ' '
        return producer.name
    
    def dehydrate_product_category(self, obj):
        category = obj.orchard.category
        if not category:
            return ' '
        return obj.orchard.get_category_display()
    
    def dehydrate_orchard_registry_code(self, obj):
        code = obj.orchard.code
        if not code:
            return ' '
        return code

    def dehydrate_is_scheduled(self, obj):
        return str(_('Scheduled Harvest')) if obj.is_scheduled else str(_('Unscheduled Harvest'))
    
    def dehydrate_category(self, obj):
        return obj.get_category_display() if obj.category else ""
    
    class Meta:
        model = ScheduleHarvest
        exclude = tuple(
            f for f in default_excluded_fields
            if f != 'comments'
        ) + (
            'id', 'meeting_point', 'incoming_product', 'created_at',
            'product', 'product_variety', 'weighing_scale',
            'product_ripeness', 'product_harvest_size_kind',
        )
        export_order = ('ooid', 'harvest_date', 'orchard', 'orchard_registry_code', 
                        'product_producer', 'gatherer', 'maquiladora', 'product_provider', 'crew', 'orchard_certification', 
                        'product_category', 'market', 'weight_expected', 'product_phenology', 'is_scheduled', 'category', 'comments', 'status')