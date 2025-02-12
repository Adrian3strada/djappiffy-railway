from django.http import JsonResponse
from django.http import HttpResponse
from .models import (Country, Region, SubRegion, City)
from django.template.loader import render_to_string
from weasyprint import HTML, CSS
from datetime import datetime
from import_export.admin import BaseExportMixin, ExportMixin
import json 
import os


# Create your views here.

def basic_report(request, json_data, model_name):
    # prepare data
    json_data = json.loads(json_data)
    base_url = request.build_absolute_uri('/')

    if json_data: 
        headers = list(json_data[0].keys()) 
    else: 
        headers = [] 
     
    data = [[item.get(header) for header in headers] for item in json_data]

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
    pdf_title = model_name
    packhouse_name = organization
    company_address = f"{add}, {district_name}, {city_name}, {state_name}, {country_name}"
    columns_total = len(headers)
    date = datetime.now()
    year = date.year
    
    # orientation page
    if len(headers) < 12:
        css = CSS(string='''
        @page {
            size: letter portrait;
        }''')
    elif len(headers) < 18: 
        css = CSS(string='''
        @page {
            size: letter landscape;
        }''')
    else:
        css = CSS(string='''
        @page {
            size: legal landscape;
        }''')

    # send data to create pdf
    html_string = render_to_string('admin/packhouses/base-table-report.html',{
        'company_info': 'Certiffy',
        'pdf_title': pdf_title,
        'headers': headers,
        'packhouse_name': packhouse_name,
        'company_address': company_address,
        'data': data,
        'columns_total': columns_total,
        'year': year,
        'date': date, 
    })

    html = HTML(string=html_string, base_url=base_url)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{model_name}.pdf"'
    html.write_pdf(response, stylesheets=[css], )

    return response


