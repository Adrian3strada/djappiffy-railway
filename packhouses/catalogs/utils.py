from django.core.exceptions import ValidationError
import datetime


# Función para generar el rango de años desde 1888 hasta el año actual
def vehicle_year_choices():
    current_year = datetime.date.today().year
    return [(str(year), str(year)) for year in range(1888, current_year)]


# Validador para asegurarse de que el año esté dentro del rango
def vehicle_validate_year(value):
    current_year = datetime.date.today().year
    if int(value) < 1888 or int(value) > current_year + 1:
        raise ValidationError(f'{value} no está dentro del rango permitido (1888 - {current_year}).')
