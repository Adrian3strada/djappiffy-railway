from import_export.fields import Field
from .models import Employee
from django.http import HttpResponse
from common.base.utils import ExportResource, DehydrationResource, default_excluded_fields
from import_export import resources, fields
from django.utils.translation import gettext_lazy as _
from .utils import EMPLOYEE_GENDER_CHOICES, MARITAL_STATUS_CHOICES

class EmployeeResource(DehydrationResource, ExportResource):
    def dehydrate_gender(self, obj):
        choices_dict = dict(EMPLOYEE_GENDER_CHOICES)
        gender_value = obj.gender
        category_display = choices_dict.get(gender_value, "")
        
        return f"{category_display}"
    
    def dehydrate_marital_status(self, obj):
        choices_dict = dict(MARITAL_STATUS_CHOICES)
        marital_status_value = obj.marital_status
        category_display = choices_dict.get(marital_status_value, "")
        
        return f"{category_display}"
    
    class Meta:
        model = Employee
        exclude = default_excluded_fields + ('name', 'middle_name', 'last_name', 'population_registry_code',)
        export_order = ('id', 'full_name', 'gender', 'marital_status', 'hire_date', 'termination_date','status')