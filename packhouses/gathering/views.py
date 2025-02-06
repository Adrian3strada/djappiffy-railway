from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.utils.translation import gettext as _
from .models import (ScheduleHarvest, ScheduleHarvestHarvestingCrew, ScheduleHarvestVehicle, ScheduleHarvestContainerVehicle, Country, Region, SubRegion, City)
from packhouses.catalogs.models import HarvestingCrew
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseForbidden
from weasyprint import HTML, CSS
from io import BytesIO
from datetime import datetime
from django.db.models import Prefetch
from django.utils.text import capfirst
from django.db.models import Sum
from django.urls import reverse
from django.http import HttpResponseForbidden
from django.http import JsonResponse

from django.contrib.auth.decorators import login_required

def harvest_order_pdf(request, harvest_id):
    # Redirige al login del admin usando 'reverse' si el usuario no está autenticado.
    if not request.user.is_authenticated:
        login_url = reverse('admin:login') 
        return redirect(login_url)
    
    # Obtener el registro
    harvest = get_object_or_404(ScheduleHarvest, pk=harvest_id)

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
    pdf_title = capfirst(ScheduleHarvest._meta.verbose_name)
    packhouse_name = organization
    company_address = f"{add}, {district_name}, {city_name}, {state_name}, {country_name}"
    date = datetime.now()
    year = date.year

    # Obtener los inlines relacionados
    scheduleharvestharvestingcrewinline = ScheduleHarvestHarvestingCrew.objects.filter(harvest_cutting=harvest)
    scheduleharvestvehicleinline = ScheduleHarvestVehicle.objects.filter(harvest_cutting=harvest).prefetch_related(
        Prefetch('scheduleharvestcontainervehicle_set',queryset=ScheduleHarvestContainerVehicle.objects.all(),)
    )
    total_box = ScheduleHarvestContainerVehicle.objects.filter(harvest_cutting__in=scheduleharvestvehicleinline).aggregate(total=Sum('quantity'))['total'] or 0

    # CSS
    base_url = request.build_absolute_uri('/')
    css = CSS(string='''
        @page {
            size: letter portrait;
        }''')

    # Renderizar el template HTML
    html_string = render_to_string('admin/packhouses/on-site-sales-report.html', {
        'packhouse_name': packhouse_name,
        'company_address': company_address,
        'pdf_title': pdf_title,
        'logo_url': logo_url,
        'harvest': harvest,
        'scheduleharvestharvestingcrewinline': scheduleharvestharvestingcrewinline,
        'scheduleharvestvehicleinline': scheduleharvestvehicleinline,
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
    # Redirige al login del admin usando 'reverse' si el usuario no está autenticado.
    if not request.user.is_authenticated:
        login_url = reverse('admin:login') 
        return redirect(login_url)
    
    # Obtener el registro
    harvest = get_object_or_404(ScheduleHarvest, pk=harvest_id)

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
    pdf_title = _("REGISTRO DE VERIFICACIÓN DE LAS BUENAS PRÁCTICAS DE HIGIENE Y SEGURIDAD DURANTE LAS OPERACIONES DE COSECHA (BIT-BPHS-01)")
    packhouse_name = organization
    company_address = f"{add}, {district_name}, {city_name}, {state_name}, {country_name}"
    date = datetime.now()
    year = date.year

    # Obtener los inlines relacionados
    # Filtrar los ScheduleHarvestHarvestingCrew relacionados con el harvest específico
    scheduleharvestharvestingcrewinline = ScheduleHarvestHarvestingCrew.objects.filter(harvest_cutting=harvest).select_related('harvesting_crew')
    # Obtener los IDs de los HarvestingCrew asociados
    harvestingcrew_ids = scheduleharvestharvestingcrewinline.values_list('harvesting_crew', flat=True)

    # Filtrar los HarvestingCrew usando los IDs obtenidos
    harvestingcrew = HarvestingCrew.objects.filter(pk__in=harvestingcrew_ids)

    # Filtrar vehiculos por cuadrillas
    crew_vehicles = []
    for crew in scheduleharvestharvestingcrewinline:
        vehicles = ScheduleHarvestVehicle.objects.filter(harvest_cutting=harvest,provider=crew.provider)
        crew_vehicles.extend(vehicles)


    # CSS
    base_url = request.build_absolute_uri('/')
    css = CSS(string='''
        @page {
            size: legal portrait;
        }''')


    # Renderizar el template HTML
    html_string = render_to_string('admin/packhouses/safety-guidelines-report.html', {
        'packhouse_name': packhouse_name,
        'company_address': company_address,
        'pdf_title': pdf_title,
        'logo_url': logo_url,
        'harvest': harvest,
        'harvesting_crew': harvestingcrew,
        'crew_vehicles': crew_vehicles,
        'scheduleharvestharvestingcrewinline': scheduleharvestharvestingcrewinline,
        'year': year,
        'date': date,
    })

    # Convertir el HTML a PDF
    html = HTML(string=html_string, base_url=base_url)
    pdf_buffer = BytesIO()
    html.write_pdf(pdf_buffer, stylesheets=[css],)

    # Traducir el nombre del archivo manualmente
    filename = f"{_('good_harvest_practices')}_{harvest.ooid}.pdf"

    # Devolver el PDF como respuesta
    pdf_buffer.seek(0)
    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    return response

def cancel_schedule_harvest(request, pk):
    schedule_harvest = get_object_or_404(ScheduleHarvest, pk=pk)
    if schedule_harvest.status not in ['open', 'ready']:
        return JsonResponse({
            'success': False,
            'message': 'You cannot cancel this harvest.'
        }, status=403)  # 403: Forbidden

    schedule_harvest.status = 'canceled'
    schedule_harvest.save()
    success_message = _('Harvest canceled successfully.')

    return JsonResponse({
        'success': True,
        'message': success_message
    })
