from django.contrib import admin
from import_export.admin import ExportMixin
from import_export.formats.base_formats import JSON, XLSX
from import_export import resources
from django.core.exceptions import PermissionDenied
from django.core.exceptions import FieldDoesNotExist
from django.utils.translation import gettext_lazy as _
from django.apps import apps
from django.db.models.fields.related import ForeignKey
from packhouses.catalogs.models import Provider, HarvestingCrew, OrchardCertificationKind
from packhouses.catalogs.settings import ORCHARD_PRODUCT_CLASSIFICATION_CHOICES

def resolve_custom_fields(request, model):
    resolved = {}
    if 'is_scheduled' in request.GET:
        resolved['is_scheduled'] = request.GET['is_scheduled']

    if 'orchard_product_category' in request.GET:
        raw = request.GET['orchard_product_category']
        label = dict(ORCHARD_PRODUCT_CLASSIFICATION_CHOICES).get(raw, raw)
        resolved['orchard_product_category'] = label

    if 'scheduleharvest_product_provider' in request.GET:
        provider_id = request.GET['scheduleharvest_product_provider']
        name = Provider.objects.filter(id=provider_id).values_list('name', flat=True).first()
        resolved['scheduleharvest_product_provider'] = name or f"ID {provider_id}"

    if 'scheduleharvest_product_producer' in request.GET:
        producer_id = request.GET['scheduleharvest_product_producer']
        name = Provider.objects.filter(id=producer_id).values_list('name', flat=True).first()
        resolved['scheduleharvest_product_producer'] = name or f"ID {producer_id}"

    if 'harvesting_crew' in request.GET:
        crew_id = request.GET['harvesting_crew']
        name = HarvestingCrew.objects.filter(id=crew_id).values_list('name', flat=True).first()
        resolved['harvesting_crew'] = name or f"ID {crew_id}"

    if 'orchard_certification' in request.GET:
        cert_id = request.GET['orchard_certification']
        name = (
            OrchardCertificationKind.objects
            .filter(id=cert_id)
            .values_list('name', flat=True)
            .first()
        )
        resolved['orchard_certification'] = name or f"ID {cert_id}"
    return resolved


def resolve_field_verbose_and_value(model, key, raw_value):
    try:
        if key.endswith('__range'):
            field_lookup = key.replace('__range', '')
            field = model._meta.get_field(field_lookup)
            label = str(_(field.verbose_name)).title()

            if isinstance(raw_value, (list, tuple)):
                if len(raw_value) >= 2:
                    value = f"{raw_value[0]} - {raw_value[1]}"
                else:
                    value = raw_value[0]
            elif isinstance(raw_value, str):
                if ',' in raw_value:
                    parts = raw_value.split(',', 1)
                    if len(parts) == 2:
                        value = f"{parts[0].strip()} - {parts[1].strip()}"
                    else:
                        value = raw_value
                else:
                    value = raw_value
            else:
                value = raw_value
            return key, value

        parts = key.split('__')
        current_model = model
        field = None
        for part in parts:
            field = current_model._meta.get_field(part)
            if hasattr(field, 'remote_field') and field.remote_field:
                current_model = field.remote_field.model

        label = str(_(field.verbose_name)).title()

        if field.choices:
            value = str(_(dict(field.choices).get(raw_value, raw_value)))
        elif hasattr(field, 'remote_field'):
            obj = field.remote_field.model.objects.filter(pk=raw_value).first()
            value = str(obj) if obj else raw_value
        else:
            value = raw_value
        return key, value

    except Exception as e:
        return key, raw_value



def prettify_filter_names(filters, model, request=None):
    ignored_keys = {'q', 'o', 'export_type'}
    pretty = {}
    range_filters = {}
    custom = resolve_custom_fields(request, model) if request else {}
    pretty.update(custom)

    for key, value in filters.items():
        if key in ignored_keys:
            continue
        if not value:
            continue
        if key in custom:
            continue

        # Si es un filtro de rango
        if key.endswith('__gte') or key.endswith('__lte'):
            if key.endswith('__gte'):
                base_key = key.replace('__gte', '')
                bound = 'gte'
            elif key.endswith('__lte'):
                base_key = key.replace('__lte', '')
                bound = 'lte'
            final_key = f"{base_key}__range"
            if final_key not in range_filters:
                range_filters[final_key] = {}
            range_filters[final_key][bound] = value
        else:
            clean_key = key
            for suffix in ['__id__exact', '__exact', '__gte', '__lte', '__contains', '__icontains', '__range']:
                if clean_key.endswith(suffix):
                    clean_key = clean_key.replace(suffix, '')
                    break
            if clean_key not in pretty:
                label_key, resolved_value = resolve_field_verbose_and_value(model, clean_key, value)
                pretty[clean_key] = resolved_value

    # Combinar los filtros de rango almacenados
    for final_key, bounds in range_filters.items():
        combined = ""
        if 'gte' in bounds and 'lte' in bounds:
            combined = f"{bounds['gte']} - {bounds['lte']}"
        elif 'gte' in bounds:
            combined = bounds['gte']
        elif 'lte' in bounds:
            combined = bounds['lte']
        pretty[final_key] = combined
    return pretty


# Para exportar solo a PDF
class ReportExportAdminMixin(ExportMixin):
    import_export_change_list_template = "admin/export/export_pdf/change_list_export.html"
    report_function = None

    def export_action(self, request):
        if not self.has_export_permission(request):
            raise PermissionDenied
        formats = [JSON]
        queryset = self.get_export_queryset(request)
        export_data = self.get_export_data(formats[0](), request, queryset)
        model_name = self.model._meta.verbose_name
        model_key = self.model.__name__

        if self.report_function is None:
            raise NotImplementedError("A report for this model is not available at the moment.")
        model = self.model
        applied_filters = prettify_filter_names(request.GET.dict(), model)
        response = self.report_function(request, export_data, model_name, model_key, applied_filters)
        return response

    def get_export_resource_kwargs(self, request, *args, **kwargs):
        kwargs = super().get_export_resource_kwargs(request, *args, **kwargs)
        kwargs['export_format'] = 'pdf'
        return kwargs

# Para exportar solo a excel
class SheetExportAdminMixin(ExportMixin):
    import_export_change_list_template = "admin/export/export_sheet/change_list_export.html"

    def export_action(self, request):
        if not self.has_export_permission(request):
            raise PermissionDenied

        formats = [XLSX]
        queryset = self.get_export_queryset(request)
        export_data = self.get_export_data(formats[0](), request, queryset)
        model_name = self.model._meta.verbose_name
        return self._do_file_export(formats[0](), request, queryset)

    def get_export_resource_kwargs(self, request, *args, **kwargs):
        kwargs = super().get_export_resource_kwargs(request, *args, **kwargs)
        kwargs['export_format'] = 'export-sheet'
        return kwargs

# Para exportar a excel y PDF
class SheetReportExportAdminMixin(ExportMixin):
    import_export_change_list_template = "admin/export/export_pdf_sheet/change_list_export.html"
    report_function = None

    def export_action(self, request):
        if not self.has_export_permission(request):
            raise PermissionDenied

        action = request.GET.get("export_type", "export-sheet")
        request.export_action_type = action
        original_get = request.GET.copy()
        clean_get = original_get.copy()
        clean_get.pop('export_type', None)

        request.GET = clean_get

        queryset = self.get_export_queryset(request)
        request.GET = original_get
        model_name = self.model._meta.verbose_name
        model_key = self.model.__name__

        if action == "export-sheet":
            formats = [XLSX]
            export_data = self.get_export_data(formats[0](), request, queryset)
            return self._do_file_export(formats[0](), request, queryset)

        elif action == "export-pdf":
            formats = [JSON]
            export_data = self.get_export_data(formats[0](), request, queryset)
            if self.report_function is None:
                raise NotImplementedError("A report for this model is not available at the moment.")
            model = self.model
            applied_filters = prettify_filter_names(request.GET.dict(), self.model, request)
            response = self.report_function(request, export_data, model_name, model_key, applied_filters)
            return response
        else:
            raise ValueError("The action is not recognized.")

    def get_export_resource_kwargs(self, request, *args, **kwargs):
        kwargs = super().get_export_resource_kwargs(request, *args, **kwargs)
        if hasattr(request, 'export_action_type'):
            export_format = 'pdf' if request.export_action_type == 'export-pdf' else 'excel'
            kwargs['export_format'] = export_format
        return kwargs

# Change headers to it verbose
class ExportResource(resources.ModelResource):
    def get_export_fields(self, instance=None):
        fields = super().get_export_fields(instance)
        model_class = self._meta.model
        for field in fields:
            if hasattr(field, 'attribute'):
                try:
                    field.column_name = model_class._meta.get_field(field.attribute).verbose_name
                except FieldDoesNotExist:
                    pass
        return fields

def render_html_list(items):
        if not items:
            return ''
        ul_style = "margin:0; padding:0; list-style-type: disc; list-style-position: inside; text-align:left;"
        li_style = "margin:0; padding:0;"
        return "<ul style='{}'>{}</ul>".format(
            ul_style,
            "".join([f"<li style='{li_style}'>{item}</li>" for item in items])
        )

class DehydrationResource():
    def dehydrate_countries(self, obj):
        return ", ".join(country.name for country in obj.countries.all()) if obj.countries.exists() else ""

    def dehydrate_country(self, obj):
        return obj.country.name if obj.country else ""

    def dehydrate_state(self, obj):
        return obj.state.name if obj.state else ""

    def dehydrate_city(self, obj):
        return obj.city.name if obj.city else ""

    def dehydrate_district(self, obj):
        return obj.district.name if obj.district else ""

    def dehydrate_market(self, obj):
        return obj.market.name if obj.market else ""

    def dehydrate_markets(self, obj):
        if not obj.markets.exists():
            return ''

        if self.export_format == 'pdf':
            return render_html_list([market.name for market in obj.markets.all()])
        else:
            return ", ".join(market.name for market in obj.markets.all())

        #return obj.market.name if obj.market else ""

    def dehydrate_market_class(self, obj):
        return obj.market_class.name if obj.market_class else ""

    def dehydrate_varieties(self, obj):
        return ", ".join(variety.name for variety in obj.varieties.all()) if obj.varieties.exists() else ""

    def dehydrate_standard_size(self, obj):
        return obj.standard_size.name if obj.standard_size else ""

    def dehydrate_product(self, obj):
        # Si "product" es un ManyToManyField, devolver una lista de nombres
        if hasattr(obj.product, "all"):
            return ", ".join(product.name for product in obj.product.all()) if obj.product.exists() else ""
        # Si "product" es un ForeignKey, devolver directamente el nombre del producto
        return obj.product.name if obj.product else ""

    def dehydrate_product_variety(self, obj):
        return obj.product_variety.name if obj.product_variety else ""

    def dehydrate_product_variety_size(self, obj):
        return obj.product_variety_size.name if obj.product_variety_size else ""

    def dehydrate_product_phenologies(self, obj):
        return obj.product_phenologies.name if obj.product_phenologies else ""

    def dehydrate_product_phenology(self, obj):
        return obj.product_phenology.name if obj.product_phenology else ""

    def dehydrate_product_harvest_size_kind(self, obj):
        return obj.product_harvest_size_kind.name if obj.product_harvest_size_kind else ""

    def dehydrate_product_size(self, obj):
        return obj.product_size.name if obj.product_size else ""

    def dehydrate_product_ripeness(self, obj):
        return obj.product_ripeness.name if obj.product_ripeness else ""

    def dehydrate_product_standard_packaging(self, obj):
        return obj.country_standard_packaging.name if obj.country_standard_packaging else ""

    def dehydrate_organization(self, obj):
        return obj.organization.name if obj.organization else ""

    def dehydrate_producer(self, obj):
        return obj.producer.name if obj.producer else ""

    def dehydrate_brand(self, obj):
        return obj.brand.name if obj.brand else ""

    def dehydrate_legal_category(self, obj):
        return obj.legal_category.name if obj.legal_category else ""

    def dehydrate_ownership(self, obj):
        return obj.ownership.name if obj.ownership else ""

    def dehydrate_fuel(self, obj):
        return obj.fuel.name if obj.fuel else ""

    def dehydrate_vehicle(self, obj):
        return obj.vehicle.name if obj.vehicle else ""

    def dehydrate_maquiladora_clients(self, obj):
        return ", ".join(client.name for client in obj.clients.all()) if obj.clients.exists() else ""

    def dehydrate_provider(self, obj):
        return obj.provider.name if obj.provider else ""

    def dehydrate_main_supply_kind(self, obj):
        return obj.kind.name if obj.kind else ""

    def dehydrate_main_supply(self, obj):
        return obj.presentation_supply.name if obj.presentation_supply else ""

    def dehydrate_kind(self, obj):
        return obj.kind.name if obj.kind else ""

    def dehydrate_packaging_supply_kind(self, obj):
        return obj.packaging_supply_kind.name if obj.packaging_supply_kind else ""

    def dehydrate_packaging_supply(self, obj):
        return obj.packaging_supply.name if obj.packaging_supply else ""

    def dehydrate_authority(self, obj):
        return obj.authority.name if obj.authority else ""

    def dehydrate_crew_chief(self, obj):
        return obj.crew_chief.name if obj.crew_chief else ""

    def dehydrate_service_provider(self, obj):
        return obj.service_provider.name if obj.service_provider else ""

    def dehydrate_capital_framework(self, obj):
        return obj.capital_framework.name if obj.capital_framework else ""

    def dehydrate_status(self, obj):
        return obj.get_status_display() if obj.status else ""

    def dehydrate_is_foreign(self, obj):
        return "✅" if obj.is_foreign else "❌"

    def dehydrate_is_enabled(self, obj):
        return "✅" if obj.is_enabled else "❌"

    def dehydrate_is_mixable(self, obj):
        return "✅" if obj.is_mixable else "❌"

    def dehydrate_label_language(self, obj):
        return obj.get_label_language_display()

    def dehydrate_country_standard_packaging(self, obj):
        return obj.country_standard_packaging.name if obj.country_standard_packaging else ""

    def dehydrate_presentation_supply_kind(self, obj):
        return obj.presentation_supply_kind.name if obj.presentation_supply_kind else ""

    def dehydrate_presentation_supply(self, obj):
        return f"{obj.presentation_supply.name} ({obj.presentation_supply.capacity} {_('pieces')})" if obj.presentation_supply else ""

    def dehydrate_supply(self, obj):
        return obj.supply.name if obj.supply else ""

    def dehydrate_packaging(self, obj):
        return obj.product_packaging.name if obj.product_packaging else ""

    def dehydrate_product_presentation(self, obj):
        return obj.product_presentation.name if obj.product_presentation else ""

    def dehydrate_measure_unit_category(self, obj):
        return obj.get_measure_unit_category_display() if obj.measure_unit_category else ""

    def dehydrate_orchard(self, obj):
        return obj.orchard.name if obj.orchard else ""

    def dehydrate_weighing_scale(self, obj):
        return obj.weighing_scale.name if obj.weighing_scale else ""

    def dehydrate_gatherer(self, obj):
        return obj.gatherer.name if obj.gatherer else ""

    def dehydrate_maquiladora(self, obj):
        return obj.maquiladora.name if obj.maquiladora else ""

    def dehydrate_product_provider(self, obj):
        return obj.product_provider.name if obj.product_provider else ""

default_excluded_fields = ('label_language', 'internal_number', 'comments' ,'organization', 'description')


def filter_models_by_food_safety():
    filtered_models = set()

    for model in apps.get_models():
        if any(field.name == 'food_safety' for field in model._meta.get_fields()):
            filtered_models.add(model.__name__)

        for field in model._meta.get_fields():
            if field.is_relation and field.related_model:
                if any(f.name == 'food_safety' for f in field.related_model._meta.get_fields()):
                    filtered_models.add(field.related_model.__name__)

    return [(model, model) for model in list(filtered_models)]
