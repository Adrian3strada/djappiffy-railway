from import_export.fields import Field
from .models import (Market, Product, ProductSize, Provider, Client, Vehicle, Gatherer, Maquiladora, Orchard, HarvestingCrew,
                     Supply, ProductPackaging, Service, WeighingScale, ColdChamber, Pallet,
                     ExportingCompany, Transfer, LocalTransporter, BorderToDestinationTransporter, CustomsBroker,
                     Vessel, Airline, InsuranceCompany, ProductPresentation, SizePackaging)
from django.http import HttpResponse
from common.base.utils import ExportResource, DehydrationResource, default_excluded_fields, render_html_list
from import_export import resources, fields
from django.utils.translation import gettext_lazy as _
from .utils import get_vehicle_category_choices, get_provider_categories_choices
from .settings import ORCHARD_PRODUCT_CLASSIFICATION_CHOICES, PRODUCT_PACKAGING_CATEGORY_CHOICES
from common.base.settings import SUPPLY_MEASURE_UNIT_CATEGORY_CHOICES
from django.utils.safestring import mark_safe
from django.utils.formats import date_format

class MarketResource(DehydrationResource, ExportResource):
    class Meta:
        model = Market
        exclude = tuple(
            field for field in default_excluded_fields + ("address_label",)
            if field != "label_language"
        )
        export_order = ('id', 'name', 'alias', 'countries', 'management_cost_per_kg', 'label_language', 'is_mixable' ,'is_enabled')

class ProductResource(DehydrationResource, ExportResource):
    product_managment_cost = Field(column_name=_("Managment Cost"), readonly=True)
    product_class = Field(column_name=_("Class"), readonly=True)
    product_variety = Field(column_name=_("Variety"), readonly=True)
    product_phenology = Field(column_name=_("Phenology Kind"), readonly=True)
    product_harvest_size = Field(column_name=_("Harvest Size"), readonly=True)
    product_ripeness = Field(column_name=_("Ripeness"), readonly=True)
    product_pest = Field(column_name=_("Pest"), readonly=True)
    product_diseases = Field(column_name=_("Deseases"), readonly=True)
    product_physical_damage = Field(column_name=_("Physical Damage"), readonly=True)
    product_residues = Field(column_name=_("Residues"), readonly=True)
    product_food_safety_process = Field(column_name=_("Food Safety Process"), readonly=True)

    def __init__(self, export_format=None, **kwargs):
        super().__init__(**kwargs)
        self.export_format = export_format

    def dehydrate_product_managment_cost(self, product):
        product_managment_costs = product.productmarketmeasureunitmanagementcost_set.filter(is_enabled=True)
        if not product_managment_costs.exists():
            return ' '
        if self.export_format == 'pdf':
            product_managment_costs = [f"{pmc.measure_unit_management_cost} ({pmc.market.alias})" for pmc in product_managment_costs]
            return render_html_list(product_managment_costs)
        else:
            return ", ".join([f"{pmc.measure_unit_management_cost} ({pmc.market.alias})" for pmc in product_managment_costs])

    def dehydrate_product_class(self, product):
        product_classes = product.productmarketclass_set.filter(is_enabled=True)
        if not product_classes.exists():
            return ' '
        if self.export_format == 'pdf':
            product_classes = [f"{pc.name} ({pc.market.alias})" for pc in product_classes]
            return render_html_list(product_classes)
        else:
            return ", ".join([f"{pc.name} ({pc.market.alias})" for pc in product_classes])

    def dehydrate_product_variety(self, product):
        product_varieties = product.productvariety_set.filter(is_enabled=True)
        if not product_varieties.exists():
            return ' '
        if self.export_format == 'pdf':
            product_varieties = [f"{pv.name} ({pv.alias})" for pv in product_varieties]
            return render_html_list(product_varieties)
        else:
            return ", ".join([f"{pv.name} ({pv.alias})" for pv in product_varieties])

    def dehydrate_product_phenology(self, product):
        product_phenologies = product.productphenologykind_set.filter(is_enabled=True)
        if not product_phenologies.exists():
            return ' '
        if self.export_format == 'pdf':
            product_phenologies = [pph.name for pph in product_phenologies]
            return render_html_list(product_phenologies)
        else:
            return ", ".join([pph.name for pph in product_phenologies])

    def dehydrate_product_harvest_size(self, product):
        product_harvest_sizes = product.productharvestsizekind_set.filter(is_enabled=True)
        if not product_harvest_sizes.exists():
            return ' '
        if self.export_format == 'pdf':
            product_harvest_sizes = [phk.name for phk in product_harvest_sizes]
            return render_html_list(product_harvest_sizes)
        else:
            return ", ".join([phk.name for phk in product_harvest_sizes])

    def dehydrate_product_ripeness(self, product):
        product_ripeness = product.productripeness_set.filter(is_enabled=True)
        if not product_ripeness.exists():
            return ''
        if self.export_format == 'pdf':
            product_ripeness = [pr.name for pr in product_ripeness]
            return render_html_list(product_ripeness)
        else:
            return ", ".join([pr.name for pr in product_ripeness])

    def dehydrate_product_pest(self, product):
        product_pests = product.productpest_set.filter(is_enabled=True)
        if not product_pests.exists():
            return ''
        if self.export_format == 'pdf':
            product_pests = [f"{p.pest} ({p.name})" for p in product_pests]
            return render_html_list(product_pests)
        else:
            return ", ".join([f"{p.pest} ({p.name})" for p in product_pests])

    def dehydrate_product_diseases(self, product):
        product_diseases = product.productdisease_set.filter(is_enabled=True)
        if not product_diseases.exists():
            return ''
        if self.export_format == 'pdf':
            product_diseases = [f"{pd.disease} ({pd.name})" for pd in product_diseases]
            return render_html_list(product_diseases)
        else:
            return ", ".join([f"{pd.disease} ({pd.name})" for pd in product_diseases])

    def dehydrate_product_physical_damage(self, product):
        product_physical_damage = product.productphysicaldamage_set.filter(is_enabled=True)
        if not product_physical_damage.exists():
            return ''
        if self.export_format == 'pdf':
            product_physical_damage = [pd.name for pd in product_physical_damage]
            return render_html_list(product_physical_damage)
        else:
            return ", ".join([pd.name for pd in product_physical_damage])

    def dehydrate_product_residues(self, product):
        product_residues = product.productresidue_set.filter(is_enabled=True)
        if not product_residues.exists():
            return ''
        if self.export_format == 'pdf':
            product_residues = [pr.name for pr in product_residues]
            return render_html_list(product_residues)
        else:
            residue_names = ", ".join([pr.name for pr in product_residues])
            return residue_names

    def dehydrate_product_food_safety_process(self, product):
        product_food_safety_process = product.productfoodsafetyprocess_set.filter(is_enabled=True)
        if not product_food_safety_process.exists():
            return ''
        if self.export_format == 'pdf':
            product_food_safety_process = [pr.procedure for pr in product_food_safety_process]
            return render_html_list(product_food_safety_process)
        else:
            product_food_safety_process = ", ".join([str(pr.procedure) for pr in product_food_safety_process])
            return product_food_safety_process

    class Meta:
        model = Product
        exclude = default_excluded_fields
        export_order = ('id', 'kind', 'name', 'measure_unit_category', 'markets', 'product_managment_cost', 'product_class',  'product_variety',
                        'product_phenology', 'product_harvest_size', 'product_ripeness', 'product_pest', 'product_diseases',
                        'product_physical_damage', 'product_residues', 'product_food_safety_process', 'is_enabled')

class ProductSizeResource(DehydrationResource, ExportResource):
    class Meta:
        model = ProductSize
        exclude = tuple(default_excluded_fields + ("sort_order",))

class ProviderResource(DehydrationResource, ExportResource):
    crew_chief = Field(column_name=_("Crew Chief"), readonly=True)

    def __init__(self, export_format=None, **kwargs):
        super().__init__(**kwargs)
        self.export_format = export_format

    def dehydrate_crew_chief(self, provider):
        crew_chiefs = provider.crewchief_set.filter(is_enabled=True)
        if not crew_chiefs:
            return ''
        if self.export_format == 'pdf':
            crew_chiefs = [s.name for s in crew_chiefs]
            return render_html_list(crew_chiefs)
        else:
            return ", ".join([s.name for s in crew_chiefs])
    def dehydrate_category(self, obj):
        choices_dict = dict(get_provider_categories_choices())
        category_value = obj.category
        category_display = choices_dict.get(category_value, None)

        return f"{category_display}"
    class Meta:
        model = Provider
        exclude = tuple(default_excluded_fields + ("provider_provider", "vehicle_provider", "neighborhood", "address", "internal_number"))
        export_order = ('id', 'name', 'category', 'country', 'state', 'city', 'district', 'neighborhood', 'postal_code', 'address', 'external_number', 'tax_id', 'email', 'phone_number', 'crew_chief', 'is_enabled')

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
    clients = Field(column_name="Clients")

    def __init__(self, export_format=None, **kwargs):
        super().__init__(**kwargs)
        self.export_format = export_format

    def dehydrate_clients(self, obj):
        clients = obj.clients.all()
        if self.export_format == "pdf":
            clients = [mc for mc  in clients]
            return render_html_list(clients)
        else:
            return ", ".join([str(mc) for mc in clients])

    class Meta:
        model = Maquiladora
        exclude = default_excluded_fields
        exclude = default_excluded_fields
        export_order = ('id', 'name', 'zone', 'tax_id', 'state', 'city', 'district', 'neighborhood', 'postal_code', 'address', 'external_number', 'email', 'phone_number', 'clients', 'is_enabled')

class OrchardResource(DehydrationResource, ExportResource):
    product = Field(column_name="Product")
    certification_kind = Field(column_name=_("Orchard Certification Kind"))
    certification_number = Field(column_name=_("Orchard Certification Number"))
    expiration_date = Field(column_name=_("Orchard Certification Expiration Date"))
    certification_verifier = Field(column_name=_("Orchard Certification Verifier"), readonly=True)

    def __init__(self, export_format=None, **kwargs):
        super().__init__(**kwargs)
        self.export_format = export_format

    def dehydrate_product(self, obj):
        product = obj.product.all()
        if self.export_format == "pdf":
            product = [p for p in product]
            return render_html_list(product)
        else:
            return ", ".join([str(p) for p in product])

    def dehydrate_category(self, obj):
        choices_dict = dict(ORCHARD_PRODUCT_CLASSIFICATION_CHOICES)
        category_value = obj.category
        category_display = choices_dict.get(category_value, "No category")

        return f"{category_display}"

    def dehydrate_certification_kind(self, orchard):
        certification_kinds = orchard.orchardcertification_set.filter(is_enabled=True)
        if not certification_kinds:
            return ' '
        if self.export_format == 'pdf':
            certification_kinds = [oc.certification_kind.name for oc in certification_kinds]
            return certification_kinds[0]
        else:
            return ", ".join([oc.certification_kind.name for oc in certification_kinds])

    def dehydrate_certification_number(self, orchard):
        certification_number = orchard.orchardcertification_set.filter(is_enabled=True)
        if not certification_number:
            return ' '
        if self.export_format == 'pdf':
            certification_number = [ocn.certification_number for ocn in certification_number]
            return certification_number[0] if certification_number else ""
        else:
            return ",".join([ocn.certification_number for ocn in certification_number])

    def dehydrate_expiration_date(self, orchard):
        certification_qs = orchard.orchardcertification_set.filter(is_enabled=True)
        if not certification_qs.exists():
            return ''
        if self.export_format == 'pdf':
            dates = []
            for ocd in certification_qs:
                formatted = date_format(ocd.expiration_date, use_l10n=True)
                dates.append(formatted)
            return dates[0]
        else:
            formatted_dates = []
            for ocd in certification_qs:
                formatted = date_format(ocd.expiration_date, use_l10n=True)
                formatted_dates.append(formatted)
            result = ", ".join(formatted_dates)
            return result

    def dehydrate_certification_verifier(self, orchard):
        certification_verifier = orchard.orchardcertification_set.filter(is_enabled=True)
        if not certification_verifier.exists():
            return ''
        if self.export_format == 'pdf':
            certification_verifier = [cv.verifier.name for cv in certification_verifier]
            return certification_verifier[0]
        else:
            return ",".join([cv.verifier.name for cv in certification_verifier])

    class Meta:
        model = Orchard
        exclude = default_excluded_fields
        export_order = ('id', 'name', 'code', 'category', 'product', 'producer', 'safety_authority_registration_date',
                        'state', 'city', 'district', 'ha', 'sanitary_certificate', 'certification_kind', 'certification_number',
                        'expiration_date', 'certification_verifier', 'is_enabled')

class HarvestingCrewResource(DehydrationResource, ExportResource):
    class Meta:
        model = HarvestingCrew
        exclude = default_excluded_fields

class SupplyResource(DehydrationResource, ExportResource):
    class Meta:
        model = Supply
        exclude = default_excluded_fields
    def dehydrate_capacity(self, obj):
        if obj.capacity and obj.capacity > 0:
            capacity = str(int(obj.capacity) if obj.capacity.is_integer() else obj.capacity)
            if obj.kind and obj.kind.capacity_unit_category:
                try:
                    units_display = obj.kind.get_capacity_unit_category_display()
                except AttributeError:
                    units_display = obj.kind.capacity_unit_category
                unit = units_display[:-1] if obj.capacity == 1 and units_display[-1].lower() == 's' else units_display
                return f"{capacity} {unit}"
            return capacity
        return "-"

    def dehydrate_usage_discount_quantity(self, obj):
        if obj.usage_discount_quantity:
            if obj.kind and obj.kind.usage_discount_unit_category:
                try:
                    units_display = obj.kind.usage_discount_unit_category.get_unit_category_display()
                except AttributeError:
                    units_display = obj.kind.usage_discount_unit_category.unit_category
                unit = units_display[:-1] if obj.usage_discount_quantity == 1 and units_display[-1].lower() == 's' else units_display
                return f"{obj.usage_discount_quantity} {unit}"
            return str(obj.usage_discount_quantity)
        return "-"

class PackagingResource(DehydrationResource, ExportResource):
    complementary_supplies = Field(column_name=_("Complementary Supplies"))

    def __init__(self, export_format=None, **kwargs):
        super().__init__(**kwargs)
        self.export_format = export_format

    def dehydrate_complementary_supplies(self, packaging):
        complementary_supplies = packaging.packagingcomplementarysupply_set.all()
        if not complementary_supplies.exists():
            return ''
        if self.export_format == 'pdf':
            supply_names = [f"{s.kind.name}: {s.supply.name} ({s.quantity})" for s in complementary_supplies]
            return render_html_list(supply_names)
        else:
            return ", ".join(f"{s.kind.name}: {s.supply.name} ({s.quantity})" for s in complementary_supplies)

    class Meta:
        model = ProductPackaging
        exclude = default_excluded_fields
        export_order = ('id', 'name', 'packaging_supply_kind', 'packaging_supply', 'product', 'market',
                        'country_standard_packaging', 'complementary_supplies', 'is_enabled')

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

class PalletResource(DehydrationResource, ExportResource):
    complementary_supplies = Field(column_name=_("Complementary Supplies"))

    def __init__(self, export_format=None, **kwargs):
        super().__init__(**kwargs)
        self.export_format = export_format

    def dehydrate_complementary_supplies(self, pallet):
        complementary_supplies = pallet.palletcomplementarysupply_set.all()
        if not complementary_supplies.exists():
            return ''
        if self.export_format == 'pdf':
            supply_names = [f"{s.kind.name} [{s.supply.name}]" for s in complementary_supplies]
            return render_html_list(supply_names)
        else:
            return ", ".join(f"{s.kind.name} [{s.supply.name}]" for s in complementary_supplies)

    class Meta:
        model = Pallet
        exclude = default_excluded_fields
        export_order = ('id', 'name', 'alias', 'market', 'product', 'supply', 'complementary_supplies', 'is_enabled')

class ExportingCompanyResource(DehydrationResource, ExportResource):
    company_beneficiary = Field(column_name=_("Exporting Company's Beneficiaries"))

    def __init__(self, export_format=None, **kwargs):
        super().__init__(**kwargs)
        self.export_format = export_format

    def dehydrate_company_beneficiary(self, company):
        company_beneficiary = company.exportingcompanybeneficiary_set.all()
        if not company_beneficiary.exists():
            return ''
        if self.export_format == 'pdf':
            company_beneficiary = [b.name for b in company_beneficiary]
            return render_html_list(company_beneficiary)
        else:
            return ",".join([b.name for b in company_beneficiary])

    class Meta:
        model = ExportingCompany
        exclude = default_excluded_fields
        export_order = ('id', 'name', 'contact_name', 'tax_id', 'country', 'state', 'city', 'district', 'postal_code', 'neighborhood', 'address', 'external_number',
                        'internal_number', 'email', 'phone_number', 'company_beneficiary')

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

class ProductPresentationResource(DehydrationResource, ExportResource):
    complementary_supplies = Field(column_name=_("Complementary Supplies"))

    def __init__(self, export_format=None, **kwargs):
        super().__init__(**kwargs)
        self.export_format = export_format

    def dehydrate_complementary_supplies(self, productpresentation):
        complementary_supplies = productpresentation.productpresentationcomplementarysupply_set.all()
        if not complementary_supplies.exists():
            return ''
        if self.export_format == 'pdf':
            supply_names = [f"{s.kind.name} ({s.supply.name})" for s in complementary_supplies]
            return render_html_list(supply_names)
        else:
            return ", ".join(f"{s.kind.name} ({s.supply.name})" for s in complementary_supplies)

    class Meta:
        model = ProductPresentation
        exclude = default_excluded_fields
        export_order = ('id', 'name', 'product', 'markets', 'presentation_supply_kind', 'presentation_supply', 'complementary_supplies', 'is_enabled')

class SizePackagingResource(DehydrationResource, ExportResource):
    pallets = Field(column_name=_("Pallets"))
    def __init__(self, export_format=None, **kwargs):
        super().__init__(**kwargs)
        self.export_format = export_format

    def dehydrate_category(self, obj):
        choices_dict = dict(PRODUCT_PACKAGING_CATEGORY_CHOICES)
        category_value = obj.category
        category_display = choices_dict.get(category_value, "No category")

        return f"{category_display}"

    def dehydrate_pallets(self, productpackaging):
        pallets = productpackaging.productpackagingpallet_set.all()
        if not pallets.exists():
            return ''
        if self.export_format == 'pdf':
            pallet_names = [f"{ppp.pallet}: {ppp.product_packaging_quantity} ({_('quantity')})" for ppp in pallets.filter(is_enabled=True)]
            return render_html_list(pallet_names)
        else:
            return ", ".join(f"{ppp.pallet}: {ppp.product_packaging_quantity} ({_('quantity')})" for ppp in pallets.filter(is_enabled=True))

    class Meta:
        model = SizePackaging
        exclude = default_excluded_fields
        export_order = ('id', 'name', 'alias', 'category', 'market', 'product', 'product_size', 'packaging', 'product_weight_per_packaging',
                        'product_presentation', 'product_presentations_per_packaging', 'product_pieces_per_presentation', 'pallets', 'is_enabled')
