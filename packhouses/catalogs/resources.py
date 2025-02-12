from import_export.fields import Field
from .models import (Market, Product, MarketProductSize, Provider, Client, Vehicle, Gatherer, Maquiladora, Orchard, HarvestingCrew,
                     Supply, Packaging, Service, WeighingScale, ColdChamber, PalletConfiguration, ProductPackaging,
                     ExportingCompany, Transfer, LocalTransporter, BorderToDestinationTransporter, CustomsBroker,
                     Vessel, Airline, InsuranceCompany, HarvestContainer)
from django.http import HttpResponse
from common.base.utils import ExportResource, DehydrationResource, default_excluded_fields
from import_export import resources, fields
from django.utils.translation import gettext_lazy as _
from .utils import get_vehicle_category_choices, get_provider_categories_choices
from .settings import ORCHARD_PRODUCT_CLASSIFICATION_CHOICES
from packhouses.packhouse_settings.settings import SUPPLY_UNIT_KIND_CHOICES
from django.utils.safestring import mark_safe

class MarketResource(DehydrationResource, ExportResource):
    class Meta:
        model = Market
        exclude = tuple(default_excluded_fields + ("address_label",))
        export_order = ('id', 'name', 'alias', 'countries', 'management_cost_per_kg', 'is_mixable' ,'is_enabled')

        
class ProductResource(DehydrationResource, ExportResource): 
    product_managment_cost = Field(column_name=_("Managment Cost"), readonly=True)
    product_class = Field(column_name=_("Class"), readonly=True)
    product_variety = Field(column_name=_("Variety"), readonly=True)
    product_phenology = Field(column_name=_("Phenology Kind"), readonly=True)
    product_harvest_size = Field(column_name=_("Harvest Size"), readonly=True)
    product_mass_volume = Field(column_name=_("Mass Volume"), readonly=True)
    product_ripeness = Field(column_name=_("Ripeness"), readonly=True)

    def dehydrate_product_managment_cost(self, product):
        product_managment_costs = product.productmarketmeasureunitmanagementcost_set.filter(is_enabled=True)
        if product_managment_costs:
            return "<ul>" + "".join([f"<li>{pmc.measure_unit_management_cost} ({pmc.market})</li>" for pmc in product_managment_costs]) + "</ul>"
        return ''
    
    def dehydrate_product_class(self, product):
        product_classes = product.productmarketclass_set.filter(is_enabled=True)
        if product_classes:
            return "<ul>" + "".join([f"<li>{pc.class_name} ({pc.market})</li>" for pc in product_classes]) + "</ul>"
        return ''

    def dehydrate_product_variety(self, product):
        product_varieties = product.productvariety_set.filter(is_enabled=True)
        if product_varieties:
            return "<ul>" + "".join([f"<li>{pv.name} ({pv.alias})</li>" for pv in product_varieties]) + "</ul>"
        return ''
    
    def dehydrate_product_phenology(self, product):
        product_phenologies = product.productphenologykind_set.filter(is_enabled=True)
        if product_phenologies:
            return "<ul>" + "".join([f"<li>{pph.name}</li>" for pph in product_phenologies]) + "</ul>"
        return ''
    
    def dehydrate_product_harvest_size(self, product):
        product_harvest_sizes = product.productharvestsizekind_set.filter(is_enabled=True)
        if product_harvest_sizes:
            return "<ul>" + "".join([f"<li>{phk.name}</li>" for phk in product_harvest_sizes]) + "</ul>"
        return ''
    
    def dehydrate_product_mass_volume(self, product):
        product_mass_volumes = product.productmassvolumekind_set.filter(is_enabled=True)
        if product_mass_volumes:
            return "<ul>" + "".join([f"<li>{pmv.name}</li>" for pmv in product_mass_volumes]) + "</ul>"
        return ''
    
    def dehydrate_product_ripeness(self, product):
        product_ripeness = product.productripeness_set.filter(is_enabled=True)
        if product_ripeness:
            return "<ul>" + "".join([f"<li>{pr.name}</li>" for pr in product_ripeness]) + "</ul>"
        return ''
    
    class Meta:
        model = Product
        exclude = default_excluded_fields 
        export_order = ('id', 'kind', 'name', 'price_measure_unit_category', 'product_managment_cost', 'product_class',  'product_variety', 
                        'product_phenology', 'product_harvest_size', 'product_mass_volume', 'product_ripeness', 'is_enabled')


class MarketProductSizeResource(DehydrationResource, ExportResource):
    class Meta:
        model = MarketProductSize
        exclude = tuple(default_excluded_fields + ("sort_order",))
    
class ProviderResource(DehydrationResource, ExportResource):
    crew_chief = Field(column_name=_("Crew Chief"), readonly=True)

    def dehydrate_crew_chief(self, provider):
        crew_chiefs = provider.crewchief_set.filter(is_enabled=True)
        if crew_chiefs:
            return "<ul>" + "".join([f"<li>{s.name}</li>" for s in crew_chiefs]) + "</ul>"
        return ''
        
    def dehydrate_category(self, obj):
        choices_dict = dict(get_provider_categories_choices())
        category_value = obj.category
        category_display = choices_dict.get(category_value, None)
        
        return f"{category_display}"
    class Meta:
        model = Provider
        exclude = tuple(default_excluded_fields + ("provider_provider", "vehicle_provider", "neighborhood", "address", "internal_number"))
    
class ClientResource(DehydrationResource, ExportResource):
    class Meta:
        model = Client
        exclude = tuple(default_excluded_fields + ("shipping_address", "payment_kind", "max_money_credit_limit", "max_days_credit_limit", "fda", "swift", "aba", "clabe", "bank", "contact_name"))
        
class VehicleResource(DehydrationResource, ExportResource):
    def dehydrate_category(self, obj):
        choices_dict = dict(get_vehicle_category_choices())
        category_value = obj.category
        category_display = choices_dict.get(category_value, None)
        
        return f"{category_display}"
    class Meta:
        model = Vehicle
        exclude = default_excluded_fields 
        
class GathererResource(DehydrationResource, ExportResource):
    class Meta:
        model = Gatherer
        exclude = tuple(default_excluded_fields + ("population_registry_code", "social_number_code"))
       
class MaquiladoraResource(DehydrationResource, ExportResource):
    class Meta:
        model = Maquiladora
        exclude = default_excluded_fields 

class OrchardResource(DehydrationResource, ExportResource):
    def dehydrate_category(self, obj):
        choices_dict = dict(ORCHARD_PRODUCT_CLASSIFICATION_CHOICES)
        category_value = obj.category
        category_display = choices_dict.get(category_value, "No category")
        
        return f"{category_display}"
    
    certification_kind = Field(column_name=_("Orchard Certification Kind"), readonly=True) 
    def dehydrate_certification_kind(self, orchard):
        certification_kinds = orchard.orchardcertification_set.filter(is_enabled=True) 
        if certification_kinds:
            return "<ul>" + "".join([f"<li>{oc.certification_kind.name}" for oc in certification_kinds]) + "</ul>"   
        return ''
    
    class Meta:
        model = Orchard
        exclude = default_excluded_fields 
        export_order = ('id', 'name', 'code', 'category', 'product', 'producer', 'safety_authority_registration_date', 
                        'state', 'city', 'district', 'ha', 'sanitary_certificate', 'certification_kind', 'is_enabled')
      
class HarvestingCrewResource(DehydrationResource, ExportResource):
    class Meta:
        model = HarvestingCrew
        exclude = default_excluded_fields 

class SupplyResource(DehydrationResource, ExportResource):
    class Meta:
        model = Supply
        exclude = default_excluded_fields 

class PackagingResource(DehydrationResource, ExportResource):
    packaging_kind = Field(column_name=_("Complementary Supplies"))
    inside = Field(column_name=_("Relation Packaging"))

    def dehydrate_packaging_kind(self, packaging):
        complementary_supplies = packaging.packagingsupply_set.all()
        if complementary_supplies:
            return "<ul>" + "".join([f"<li>{cs.packaging_kind.name}" for cs in complementary_supplies]) + "</ul>"   
        return ''
    
    def dehydrate_inside(self, packaging):
        containers = packaging.outside.all()
        if containers:
            return "<ul>" + "".join([f"<li>{i.inside.name}" for i in containers]) + "</ul>"   
        return ''

    class Meta:
        model = Packaging
        exclude = default_excluded_fields 

class ServiceResource(DehydrationResource, ExportResource):
    class Meta:
        model = Service
        exclude = default_excluded_fields 

class WeighingScaleResource(DehydrationResource, ExportResource):
    class Meta:
        model = WeighingScale
        exclude = default_excluded_fields 

class ColdChamberResource(DehydrationResource, ExportResource):
    class Meta:
        model = ColdChamber
        exclude = default_excluded_fields 

class PalletConfigurationResource(DehydrationResource, ExportResource):
    class Meta:
        model = PalletConfiguration
        exclude = default_excluded_fields 

class ProductPackagingResource(DehydrationResource, ExportResource):
    class Meta:
        model = ProductPackaging
        exclude = default_excluded_fields 

class ExportingCompanyResource(DehydrationResource, ExportResource):
    class Meta:
        model = ExportingCompany
        exclude = default_excluded_fields 

class TransferResource(DehydrationResource, ExportResource):
    class Meta:
        model = Transfer
        exclude = default_excluded_fields 

class LocalTransporterResource(DehydrationResource, ExportResource):
    class Meta:
        model = LocalTransporter
        exclude = default_excluded_fields 

class BorderToDestinationTransporterResource(DehydrationResource, ExportResource):
    class Meta:
        model = BorderToDestinationTransporter
        exclude = default_excluded_fields 

class CustomsBrokerResource(DehydrationResource, ExportResource):
    class Meta:
        model = CustomsBroker
        exclude = default_excluded_fields 

class VesselResource(DehydrationResource, ExportResource):
    class Meta:
        model = Vessel
        exclude = default_excluded_fields

class AirlineResource(DehydrationResource, ExportResource):
    class Meta:
        model = Airline
        exclude = default_excluded_fields 

class InsuranceCompanyResource(DehydrationResource, ExportResource):
    class Meta:
        model = InsuranceCompany
        exclude = default_excluded_fields 

class HarvestContainerResource(DehydrationResource, ExportResource):
    def dehydrate_unit_kind(self, obj):
        choices_dict = dict(SUPPLY_UNIT_KIND_CHOICES)
        category_value = obj.unit_kind
        category_display = choices_dict.get(category_value, "")
        
        return f"{category_display}"
    class Meta:
        model = HarvestContainer
        exclude = default_excluded_fields 