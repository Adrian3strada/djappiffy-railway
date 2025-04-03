from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse
from packhouses.gathering.models import ScheduleHarvestVehicle, ScheduleHarvest

from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from .models import IncomingProduct, PalletReceived
from cities_light.models import City, Country, Region, SubRegion
from django.utils.text import capfirst
from datetime import datetime
from weasyprint import HTML, CSS
from django.template.loader import render_to_string
from io import BytesIO
from django.core import serializers
from django.http import JsonResponse
import json
from .resources import get_model_fields_verbose_names, transform_data

    
def weighing_report(request, pk):
    # Redirige al login del admin usando 'reverse' si el usuario no está autenticado.
    if not request.user.is_authenticated:
        login_url = reverse('admin:login')
        return redirect(login_url)
    incomingProduct = get_object_or_404(IncomingProduct, pk=pk)
    
    # Obtener Datos de la Organización
    if hasattr(request, 'organization'):
        organization = request.organization.organizationprofile.name
        add =  request.organization.organizationprofile.address
        organization_profile = request.organization.organizationprofile
        def get_name(model, obj_id, default):
            if obj_id:
                try:
                    return model.objects.get(id=obj_id).name
                except model.DoesNotExist:
                    return f"{default} does not exist"
            return f"{default} not specified"

        # Obtener los nombres de las regiones
        city_name = get_name(SubRegion, organization_profile.city_id, "Ciudad")
        country_name = get_name(Country, organization_profile.country_id, "Country")
        state_name = get_name(Region, organization_profile.state_id, "State")
        district_name = get_name(City, organization_profile.district_id, "District")
        if organization_profile.logo:
            logo_url = organization_profile.logo.url
        else:
            logo_url = None

    pdf_title = _('Weighing')
    packhouse_name = organization
    company_address = f"{add}, {district_name}, {city_name}, {state_name}, {country_name}"
    date = datetime.now()
    year = date.year

    # Obtener Corte relacionado con IncomingProduct
    harvest = ScheduleHarvest.objects.filter(incoming_product=incomingProduct).first()
    print(harvest)
    # Obtener pallets de IncomingProduct y transformar datos
    pallet_received_records = incomingProduct.palletreceived_set.all()
    pallet_received_json = serializers.serialize('json', pallet_received_records)
    
    json_data = json.loads(pallet_received_json)
    if json_data: 
       headers = list(json_data[0]['fields'].keys())
    else: 
        headers = [] 
    
    # Excluir los campos no deseados
    excluded_fields = ['id', 'incoming_product']
    headers = get_model_fields_verbose_names(PalletReceived, excluded_fields=excluded_fields)

        
    data = [[item['fields'].get(header) for header in headers] for item in json_data]
    # Transformar los datos del queryset
    data = transform_data(pallet_received_records, excluded_fields=excluded_fields)

    # Calcular los totales
    total_gross_weight = sum(item.gross_weight for item in pallet_received_records)
    total_net_weight = sum(item.net_weight for item in pallet_received_records)

    # Crear un diccionario con los totales usando gettext_lazy para traducción
    totals = {
        _('Total Gross Weight (Kg)'): total_gross_weight,
        _('Total Net Weight (Kg)'): total_net_weight,
    }

    # CSS
    base_url = request.build_absolute_uri('/')
    css = CSS(string='''
        @page {
            size: letter portrait;
        }''')

    # Renderizar el template HTML
    html_string = render_to_string('admin/packhouses/receiving/weighing-report.html', {
        'packhouse_name': packhouse_name,
        'company_address': company_address,
        'pdf_title': pdf_title,
        'logo_url': logo_url,
        'harvest': harvest,
        'headers': headers,
        'data': data,
        "totals": totals,
        'year': year,
        'date': date,
    })

    # Convertir el HTML a PDF
    html = HTML(string=html_string, base_url=base_url)
    pdf_buffer = BytesIO()
    html.write_pdf(pdf_buffer, stylesheets=[css],)

    # Traducir el nombre del archivo manualmente
    filename = f"{_('good_harvest_practices')}_{incomingProduct.id}.pdf"

    # Devolver el PDF como respuesta
    pdf_buffer.seek(0)
    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    return response