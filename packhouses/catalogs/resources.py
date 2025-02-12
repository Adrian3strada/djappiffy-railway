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
    market_class_name = Field(column_name=_("Market Class"), attribute="marketclass_set", readonly=True)

    def dehydrate_market_class_name(self, market):
        # Filtrar solo las clases activas
        active_market_classes = market.marketclass_set.filter(is_enabled=True)  
        
        # Retornar en formato de lista HTML
        if active_market_classes:
            return "<ul>" + "".join([f"<li>{mc.name}</li>" for mc in active_market_classes]) + "</ul>"
        return ''

    class Meta:
        model = Market
        exclude = tuple(default_excluded_fields + ("address_label",))
        export_order = ('id', 'name', 'alias', 'countries', 'management_cost_per_kg', 'market_class_name', 'is_mixable' ,'is_enabled')

        
class ProductResource(DehydrationResource, ExportResource): 
    product_season = Field(column_name=_("Season"), readonly=True) 
    product_variety = Field(column_name=_("Variety"), readonly=True) 
    mass_volume_kind = Field(column_name=_("Mass Volume Kind"), readonly=True) 
    harvest_size_kind = Field(column_name=_("Harvest Size Kinds"), readonly=True) 

    def dehydrate_product_season(self, product):
        product_seasons = product.productseasonkind_set.filter(is_enabled=True) 
        if product_seasons:
            return "<ul>" + "".join([f"<li>{s.name}</li>" for s in product_seasons]) + "</ul>"
        return ''
    
    def dehydrate_product_variety(self, product):
        product_varieties = product.productvariety_set.filter(is_enabled=True) 
        if product_varieties:
            return "<ul>" + "".join([f"<li>{pv.name} ({pv.alias})</li>" for pv in product_varieties]) + "</ul>"
        return ''
    
    def dehydrate_mass_volume_kind(self, product):
        mass_volume = product.productmassvolumekind_set.filter(is_enabled=True)
        if mass_volume:
            return "<ul>" + "".join([f"<li>{mvk.name}</li>" for mvk in mass_volume]) + "</ul>"
        return ''
    
    def dehydrate_harvest_size_kind(self, product):
        harvest_size = product.productharvestsizekind_set.filter(is_enabled=True)
        if harvest_size:
            return "<ul>" + "".join([f"<li>{phk.name}</li>" for phk in harvest_size]) + "</ul>"
        return ''

    class Meta:
        model = Product
        exclude = default_excluded_fields 
        export_order = ('id', 'kind', 'name', 'product_season', 'mass_volume_kind', 'product_variety',  'harvest_size_kind', 'is_enabled')


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