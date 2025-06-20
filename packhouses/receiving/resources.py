from common.base.utils import ExportResource, DehydrationResource, default_excluded_fields, render_html_list
from import_export.fields import Field
from import_export import fields, resources
from django.utils.translation import gettext_lazy as _
from .models import IncomingProduct, Batch
from django.utils.encoding import force_str

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
    harvest_ooid = Field(column_name=_("Harvest Number"), readonly=True)
    harvest_date = Field(column_name=_("Harvest Date"), readonly=True)
    orchard = Field(column_name=_("Orchard"), readonly=True)
    orchard_code = Field(column_name=_("Orchard Registery Code"), readonly=True)
    product_producer = Field(column_name=_("Product Producer"), readonly=True)
    gatherer = Field(column_name=_("Gatherer"), readonly=True)
    maquiladora = Field(column_name=_("Maquiladora"), readonly=True)
    product_provider = Field(column_name=_("Product Provider"), readonly=True)
    product_phenology = Field(column_name=_("Product Phenology"), readonly=True)
    harvesting_category = Field(column_name=_("Harvesting Category"), readonly=True)

    def __init__(self, export_format=None, **kwargs):
        super().__init__(**kwargs)
        self.export_format = export_format
    
    def dehydrate_harvest_ooid(self, obj):
        harvest_ooid = hasattr(obj, 'scheduleharvest') and obj.scheduleharvest is not None
        if harvest_ooid:
            ooid = obj.scheduleharvest.ooid
            return ooid or ""
        else:
            return ""
        
    def dehydrate_harvest_date(self, obj):
        harvest_date = hasattr(obj, 'scheduleharvest') and obj.scheduleharvest is not None
        if harvest_date:
            harvest_date = obj.scheduleharvest.harvest_date
            return harvest_date or ""
        else:
            return ""
    
    def dehydrate_orchard(self, obj):
        if hasattr(obj, 'scheduleharvest') and obj.scheduleharvest is not None:
            return obj.scheduleharvest.orchard.name or ""
        return ""
    
    def dehydrate_orchard_code(self, obj):
        if hasattr(obj, 'scheduleharvest') and obj.scheduleharvest is not None:
            return obj.scheduleharvest.orchard.code or ""
        return ""
    
    def dehydrate_product_producer(self, obj):
        if hasattr(obj, 'scheduleharvest') and obj.scheduleharvest is not None:
            return obj.scheduleharvest.orchard.producer.name or ""
        return ""
    
    def dehydrate_gatherer(self, obj):
        sched = getattr(obj, 'scheduleharvest', None)
        if sched and sched.gatherer:
            return sched.gatherer.name or ""
        return ""

    def dehydrate_maquiladora(self, obj):
        sched = getattr(obj, 'scheduleharvest', None)
        if sched and sched.maquiladora:
            return sched.maquiladora.name or ""
        return ""
    
    def dehydrate_product_provider(self, obj):
        sched = getattr(obj, 'scheduleharvest', None)
        if sched and sched.product_provider:
            return sched.product_provider.name or ""
        return ""

    def dehydrate_product_phenology(self, obj):
        sched = getattr(obj, 'scheduleharvest', None)
        if sched and sched.product_phenology:
            return sched.product_phenology.name or ""
        return ""

    def dehydrate_harvesting_category(self, obj):
        sched = getattr(obj, 'scheduleharvest', None)
        if sched and sched.category:
            return sched.get_category_display() or ""
        return ""

    # properties
    containers_count = fields.Field(column_name=_('Total Containers'), attribute="containers_count",readonly=True)
    total_net_weight = fields.Field(column_name=_('Total Net Weight'), attribute="total_net_weight",readonly=True)
     
    class Meta:
        model = IncomingProduct
        exclude = tuple(default_excluded_fields + ('batch', 'id', 'weighing_record_number', 'public_weight_result', 'mrl', 'is_quarantined',
                                                   'public_weighing_scale', 'total_weighed_sets' ))
        export_order = ('harvest_ooid', 'harvest_date', 'created_at', 'phytosanitary_certificate', 'orchard', 'orchard_code',
                        'product_producer', 'gatherer', 'maquiladora', 'product_provider', 'product_phenology', 'harvesting_category',
                        'comments', 'total_net_weight', 'kg_sample', 'containers_count', 'status',)

class BatchResource(DehydrationResource, ExportResource):
    harvest_ooid = Field(column_name=_("Harvest Number"), readonly=True)
    pytosanitary_cetificate = Field(column_name=_("Phytosanitary Certificate"), readonly=True)
    orchard = Field(column_name=_("Orchard"), readonly=True)
    orchard_code = Field(column_name=_("Orchard Registery Code"), readonly=True)
    product_producer = Field(column_name=_("Product Producer"), readonly=True)
    gatherer = Field(column_name=_("Gatherer"), readonly=True)
    maquiladora = Field(column_name=_("Maquiladora"), readonly=True)
    product_provider = Field(column_name=_("Product Provider"), readonly=True)
    product_phenology = Field(column_name=_("Product Phenology"), readonly=True)
    harvesting_category = Field(column_name=_("Harvesting Category"), readonly=True)
    batch_relationship = Field(column_name=_("Batch Relationship"), readonly=True)
    weight_received = Field(column_name=_("Weight Received"), readonly=True)
    full_containers = Field(column_name=_("Full Containments"), readonly=True)
    kg_sample = Field(column_name=_("Kg Sample"), readonly=True)

    def __init__(self, export_format=None, **kwargs):
        super().__init__(**kwargs)
        self.export_format = export_format


    def dehydrate_harvest_ooid(self, obj):
        harvest_ooid = hasattr(obj, 'incomingproduct') and obj.incomingproduct.scheduleharvest is not None
        if harvest_ooid:
            ooid = obj.incomingproduct.scheduleharvest.ooid
            return ooid or ""
        else:
            return ""
        
    def dehydrate_pytosanitary_cetificate(self, obj):
        pytosanitary_cetificate =  hasattr(obj, 'incomingproduct') and obj.incomingproduct.scheduleharvest is not None
        if pytosanitary_cetificate:
            certifiacte = obj.incomingproduct.phytosanitary_certificate
            return certifiacte or ""
        else:
            return ""

    def dehydrate_orchard(self, obj):
        if hasattr(obj, 'incomingproduct') and obj.incomingproduct.scheduleharvest is not None:
            return obj.incomingproduct.scheduleharvest.orchard.name or ""
        return ""

    def dehydrate_orchard_code(self, obj):
        if hasattr(obj, 'incomingproduct') and obj.incomingproduct.scheduleharvest is not None:
            return obj.incomingproduct.scheduleharvest.orchard.code or ""
        return ""

    def dehydrate_product_producer(self, obj):
        if hasattr(obj, 'incomingproduct') and obj.incomingproduct.scheduleharvest is not None:
            return obj.incomingproduct.scheduleharvest.orchard.producer.name or ""
        return ""
    
    def dehydrate_gatherer(self, obj):
        incoming = getattr(obj, 'incomingproduct', None)
        if incoming and incoming.scheduleharvest and incoming.scheduleharvest.gatherer:
            return incoming.scheduleharvest.gatherer.name or ""
        return ""
    
    def dehydrate_maquiladora(self, obj):
        incoming = getattr(obj, 'incomingproduct', None)
        if incoming and incoming.scheduleharvest and incoming.scheduleharvest.maquiladora:
            return incoming.scheduleharvest.maquiladora.name or ""
        return ""

    def dehydrate_product_provider(self, obj):
        incoming = getattr(obj, 'incomingproduct', None)
        if incoming and incoming.scheduleharvest and incoming.scheduleharvest.product_provider:
            return incoming.scheduleharvest.product_provider.name or ""
        return ""

    def dehydrate_product_phenology(self, obj):
        incoming = getattr(obj, 'incomingproduct', None)
        if incoming and incoming.scheduleharvest and incoming.scheduleharvest.product_phenology:
            return incoming.scheduleharvest.product_phenology.name or ""
        return ""

    def dehydrate_harvesting_category(self, obj):
        incoming = getattr(obj, 'incomingproduct', None)
        if incoming and incoming.scheduleharvest and incoming.scheduleharvest.category:
            return incoming.scheduleharvest.get_category_display() or ""
        return ""
    
    def dehydrate_weight_received(self, obj):
        weight_received =  hasattr(obj, 'incomingproduct') and obj.incomingproduct is not None
        if weight_received:
            net_weight = obj.incomingproduct.total_net_weight
            return net_weight or ""
        else:
            return ""
        
    def dehydrate_kg_sample(self, obj):
        sample =  hasattr(obj, 'incomingproduct') and obj.incomingproduct is not None
        if sample:
            kg_sample = obj.incomingproduct.kg_sample
            return kg_sample or ""
        else:
            return ""
    
    def dehydrate_full_containers(self, obj):
        full_containers =  hasattr(obj, 'incomingproduct') and obj.incomingproduct is not None
        if full_containers:
            containers_count = obj.incomingproduct.containers_count
            return containers_count or ""
        else:
            return ""

    def dehydrate_is_available_for_processing(self, obj):
        return "✅" if obj.is_available_for_processing else "❌"
    
    def dehydrate_batch_relationship(self, obj):
        if obj.is_parent:
            hijos = obj.children_ooids or _("None")
            return str(_("Parent")) + f" ({_('Children')}: {hijos})"
        elif obj.is_child:
            padre = obj.parent_batch_ooid or _("Unknown")
            return str(_("Child")) + f" ({_('Parent')}: {padre})"
        else:
            return str(_("Independent"))
            

    class Meta: 
        model = Batch
        exclude = tuple(default_excluded_fields + ('id', 'parent'))
        export_order = ('ooid', 'harvest_ooid', 'created_at', 'pytosanitary_cetificate', 'orchard', 'orchard_code', 'product_producer',
                        'gatherer', 'maquiladora', 'product_provider', 'product_phenology', 'harvesting_category', 'weight_received',
                        'kg_sample', 'full_containers', 'is_available_for_processing', 'batch_relationship', 'status' )