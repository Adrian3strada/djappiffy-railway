from import_export.fields import Field
from django.http import HttpResponse
from common.base.utils import ExportResource, DehydrationResource, default_excluded_fields
from django.utils.translation import gettext_lazy as _
from .models import IncomingProduct, PreLot

from django.core.exceptions import FieldDoesNotExist

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
