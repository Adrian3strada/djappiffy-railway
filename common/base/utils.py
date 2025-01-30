from django.contrib import admin
from import_export.admin import ExportMixin
from import_export.formats.base_formats import JSON, XLSX
from import_export import resources
from django.core.exceptions import PermissionDenied
from django.core.exceptions import FieldDoesNotExist

# Para exportar solo a PDF
class ReportExportAdmin(ExportMixin):
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

# Para exportar a excel
class SheetExportAdmin(ExportMixin):
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
class SheetReportExportAdmin(ExportMixin):
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
        return " ".join(country.name for country in obj.countries.all())
    def dehydrate_organization(self, obj):
        return obj.organization.name
    def dehydrate_is_foreign(self, obj):
        return "✅" if obj.is_foreign else "❌"
    def dehydrate_is_enabled(self, obj):
        return "✅" if obj.is_enabled else "❌"
    def dehydrate_is_mixable(self, obj):
        return "✅" if obj.is_mixable else "❌"
    def dehydrate_kind(self, obj):
        return obj.kind.name
        
default_excluded_fields = ('label_language', 'organization')