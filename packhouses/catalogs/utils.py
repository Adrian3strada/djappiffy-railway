from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import datetime


# Función para generar el rango de años desde 1888 hasta el año actual
def vehicle_year_choices():
    current_year = datetime.date.today().year
    return [(str(year), str(year)) for year in range(1888, current_year + 2)]


# Validador para asegurarse de que el año esté dentro del rango
def vehicle_validate_year(value):
    current_year = datetime.date.today().year
    if int(value) < 1888 or int(value) > current_year + 1:
        raise ValidationError(f'{value} no está dentro del rango permitido (1980 - {current_year}).')

# Función para generar tipo región dinámicamente
def get_type_choices():
    return [
        ('local', _('Local')),
        ('exportacion', _('Export')),
    ]

# Función para generar tipos de pago dinámicamente
def get_payment_choices():
    return [
        ('percentage', _('Percentage')),
        ('fixed_amount', _('Fixed amount')),
    ]

def vehicle_scope_choices():
    return [
        ('packhouse', _('Packhouse')),
        ('harvesting_crew', _('Harvesting crew')),
    ]

def get_provider_categories_choices():
    return [
        ('product_provider', _('Product provider')),
        ('service_provider', _('Service provider')),
        ('supply_provider', _('Supply provider')),
        ('harvesting_provider', _('Harvesting provider')),
        ('product_producer', _('Product producer')),
    ]
