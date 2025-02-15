from django.contrib import admin
from import_export.admin import ExportMixin
from import_export.formats.base_formats import JSON, XLSX
from import_export import resources
from django.core.exceptions import PermissionDenied
from django.core.exceptions import FieldDoesNotExist
from django.utils.translation import gettext_lazy as _

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

        if self.report_function is None:
            raise NotImplementedError("A report for this model is not available at the moment.")

        response = self.report_function(request, export_data, model_name)
        return response

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

# Para exportar a excel y PDF
class SheetReportExportAdminMixin(ExportMixin):
    import_export_change_list_template = "admin/export/export_pdf_sheet/change_list_export.html"
    report_function = None

    def export_action(self, request):
        if not self.has_export_permission(request):
            raise PermissionDenied

        action = request.GET.get("export_type", "export-sheet")

        query_params = request.GET.copy()
        if 'export_type' in query_params:
            del query_params['export_type']
        request.GET = query_params

        queryset = self.get_export_queryset(request)
        model_name = self.model._meta.verbose_name

        if action == "export-sheet":
            formats = [XLSX]
            export_data = self.get_export_data(formats[0](), request, queryset)
            return self._do_file_export(formats[0](), request, queryset)

        elif action == "export-pdf":
            formats = [JSON]
            export_data = self.get_export_data(formats[0](), request, queryset)
            if self.report_function is None:
                raise NotImplementedError("A report for this model is not available at the moment.")

            response = self.report_function(request, export_data, model_name)
            return response
        else:
            raise ValueError("The action is not recognized.")


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

class DehydrationResource():
    def dehydrate_countries(self, obj):
        return " ".join(country.name for country in obj.countries.all()) if obj.countries.exists() else ""

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

    def dehydrate_market_class(self, obj):
        return obj.product_market_class.name if obj.product_market_class else ""

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

    def dehydrate_product_size(self, obj):
        return obj.product_size.name if obj.product_size else ""

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
        return obj.main_supply_kind.name if obj.main_supply_kind else ""

    def dehydrate_main_supply(self, obj):
        return obj.main_supply.name if obj.main_supply else ""

    def dehydrate_kind(self, obj):
        return obj.kind.name if obj.kind else ""

    def dehydrate_packaging_kind(self, obj):
        return obj.packaging_kind.name if obj.packaging_kind else ""

    def dehydrate_authority(self, obj):
        return obj.authority.name if obj.authority else ""

    def dehydrate_crew_chief(self, obj):
        return obj.crew_chief.name if obj.crew_chief else ""

    def dehydrate_service_provider(self, obj):
        return obj.service_provider.name if obj.service_provider else ""

    def dehydrate_is_foreign(self, obj):
        return "✅" if obj.is_foreign else "❌"

    def dehydrate_is_enabled(self, obj):
        return "✅" if obj.is_enabled else "❌"

    def dehydrate_is_mixable(self, obj):
        return "✅" if obj.is_mixable else "❌"

    def dehydrate_is_ripe(self, obj):
        return "✅" if obj.is_ripe else "❌"


default_excluded_fields = ('label_language', 'internal_number', 'comments' ,'organization', 'description')
