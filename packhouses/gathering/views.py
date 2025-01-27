from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils.translation import gettext as _
from .models import (ScheduleHarvest, ScheduleHarvestHarvestingCrew, ScheduleHarvestVehicle, ScheduleHarvestContainerVehicle)
from packhouses.catalogs.models import HarvestingCrew
from django.template.loader import render_to_string
from django.http import HttpResponse
from weasyprint import HTML, CSS
from io import BytesIO
from datetime import datetime
from django.db.models import Prefetch
from django.utils.text import capfirst
from django.db.models import Sum

def generate_pdf(request, harvest_id):
    base_url = request.build_absolute_uri('/')
    if hasattr(request, 'organization'):
        organization = request.organization.organizationprofile.name
        add =  request.organization.organizationprofile.address
        organization_profile = request.organization.organizationprofile
        def get_name(model, obj_id, default):
            if obj_id:
                try:
                    return model.objects.get(id=obj_id).name
                except model.DoesNotExist:
                    return f"{default} no encontrada"
            return f"{default} no especificada"

        # Obtener los nombres de las regiones
        city_name = get_name(SubRegion, organization_profile.city_id, "Ciudad")
        country_name = get_name(Country, organization_profile.country_id, "Country")
        state_name = get_name(Region, organization_profile.state_id, "State")
        district_name = get_name(City, organization_profile.district_id, "District")
        if organization_profile.logo:  
            logo_url = organization_profile.logo.url  
    
    packhouse_name = organization
    company_address = f"{add}, {district_name}, {city_name}, {state_name}, {country_name}"
    date = datetime.now()
    year = date.year
    
def harvest_order_pdf(request, harvest_id):
    # Obtener el registro
    harvest = get_object_or_404(ScheduleHarvest, pk=harvest_id)
    pdf_title = capfirst(ScheduleHarvest._meta.verbose_name)

    # Obtener los inlines relacionados
    scheduleharvestharvestingcrewinline = ScheduleHarvestHarvestingCrew.objects.filter(harvest_cutting=harvest)
    scheduleharvestvehicleinline = ScheduleHarvestVehicle.objects.filter(harvest_cutting=harvest).prefetch_related(
        Prefetch(
            'scheduleharvestcontainervehicle_set',
            queryset=ScheduleHarvestContainerVehicle.objects.all(),
        )
    )
    
    total_box = ScheduleHarvestContainerVehicle.objects.filter(harvest_cutting__in=scheduleharvestvehicleinline).aggregate(total=Sum('quantity'))['total'] or 0


    css = CSS(string='''
        @page {
            size: letter portrait;
        }''')

    # Renderizar el template HTML
    html_string = render_to_string('admin/packhouses/schedule-harvest.html', {
        'packhouse_name': packhouse_name,
        'company_address': company_address,
        'pdf_title': pdf_title,
        'logo_url': logo_url,
        'harvest': harvest,
        'scheduleharvestharvestingcrewinline': scheduleharvestharvestingcrewinline,
        'scheduleharvestvehicleinline': scheduleharvestvehicleinline,
        'packhouse_name': packhouse_name,
        'total_box': total_box,
        'year': year,
        'date': date, 
    })

    # Convertir el HTML a PDF
    html = HTML(string=html_string, base_url=base_url)
    pdf_buffer = BytesIO()
    html.write_pdf(pdf_buffer, stylesheets=[css],)

    # Traducir el nombre del archivo manualmente
    filename = f"{_('harvest_order')}_{harvest.ooid}.pdf"

    # Devolver el PDF como respuesta
    pdf_buffer.seek(0)
    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    return response

def good_harvest_practices_format(request, harvest_id):
    # Obtener el registro
    harvest = get_object_or_404(ScheduleHarvest, pk=harvest_id)

    # Obtener los inlines relacionados
    # Filtrar los ScheduleHarvestHarvestingCrew relacionados con el harvest específico
    scheduleharvestharvestingcrewinline = ScheduleHarvestHarvestingCrew.objects.filter(harvest_cutting=harvest).select_related('harvesting_crew')
    # Obtener los IDs de los HarvestingCrew asociados
    harvestingcrew_ids = scheduleharvestharvestingcrewinline.values_list('harvesting_crew', flat=True)

    # Filtrar los HarvestingCrew usando los IDs obtenidos
    harvestingcrew = HarvestingCrew.objects.filter(pk__in=harvestingcrew_ids)


    # Renderizar el template HTML
    html_string = render_to_string('admin/packhouses/safety_guidelines_report.html', {
        'harvest': harvest,
        'harvesting_crew': harvestingcrew,
        'scheduleharvestharvestingcrewinline': scheduleharvestharvestingcrewinline,
    })
    # Convertir el HTML a PDF
    html = HTML(string=html_string)
    pdf_buffer = BytesIO()
    html.write_pdf(pdf_buffer)

    # Traducir el nombre del archivo manualmente
    filename = f"{_('good_harvest_practices')}_{harvest.ooid}.pdf"

    # Devolver el PDF como respuesta
    pdf_buffer.seek(0)
    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    return response
