from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.utils.translation import gettext as _
from .models import (ScheduleHarvest, ScheduleHarvestHarvestingCrew, ScheduleHarvestVehicle, ScheduleHarvestContainerVehicle, Country, Region, SubRegion, City)
from packhouses.catalogs.models import HarvestingCrew, OrchardCertification
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
from packhouses.receiving.models import IncomingProduct
from django.contrib.auth.decorators import login_required
from itertools import chain
import json 
import qrcode
import base64
from io import BytesIO
from .utils import FILTER_DISPLAY_CONFIG, apply_filter_config

def generate_qr_base64(data: str) -> str:
    qr = qrcode.make(data)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{img_str}"


def harvest_order_pdf(request, harvest_id):
    """
    # Redirige al login del admin usando 'reverse' si el usuario no está autenticado.
    if not request.user.is_authenticated:
        login_url = reverse('admin:login')
        return redirect(login_url)
    """

    # Obtener el registro
    harvest = get_object_or_404(ScheduleHarvest, pk=harvest_id)

    organization_profile = harvest.orchard.organization.organizationprofile
    organization = organization_profile.name
    add = organization_profile.address

    def get_name(model, obj_id, default):
        if obj_id:
            try:
                return model.objects.get(id=obj_id).name
            except model.DoesNotExist:
                return f"{default} does not exist"
        return f"{default} not specified"

    city_name = get_name(SubRegion, organization_profile.city_id, "City")
    country_name = get_name(Country, organization_profile.country_id, "Country")
    state_name = get_name(Region, organization_profile.state_id, "State")
    district_name = get_name(City, organization_profile.district_id, "District")
    logo_url = organization_profile.logo.url if organization_profile.logo else None

    pdf_title = _("Schedule Harvest Order")
    packhouse_name = organization
    company_address = f"{add}, {district_name}, {city_name}, {state_name}, {country_name}"
    date = datetime.now()
    year = str(date.year)

    # Obtener los inlines relacionados
    scheduleharvestharvestingcrewinline = ScheduleHarvestHarvestingCrew.objects.filter(harvest_cutting=harvest)
    scheduleharvestvehicleinline = ScheduleHarvestVehicle.objects.filter(harvest_cutting=harvest).prefetch_related(
        Prefetch('scheduleharvestcontainervehicle_set',queryset=ScheduleHarvestContainerVehicle.objects.all(),)
    )
    orchard_certifications = OrchardCertification.objects.filter(
        orchard=harvest.orchard,
        created_at__lte=harvest.harvest_date,
        expiration_date__gte=harvest.harvest_date,
        is_enabled=True
        )
    import logging
    logger = logging.getLogger(__name__)
    logger.debug(f"Orchard certifications: {orchard_certifications}")

    # CSS
    base_url = request.build_absolute_uri('/')
    css = CSS(string='''
        @page {
            size: letter portrait;
        }''')

    report_url = request.build_absolute_uri(
        reverse("harvest_order_pdf", args=[harvest.pk])
    )
    qr_data = report_url
    qr_image = generate_qr_base64(qr_data)

    # Renderizar el template HTML
    html_string = render_to_string('admin/packhouses/gathering/schedule-harvest-report.html', {
        'packhouse_name': packhouse_name,
        'company_address': company_address,
        'pdf_title': pdf_title,
        'logo_url': logo_url,
        'harvest': harvest,
        "qr_image": qr_image,
        'orchard_certifications': orchard_certifications,
        'scheduleharvestharvestingcrewinline': scheduleharvestharvestingcrewinline,
        'scheduleharvestvehicleinline': scheduleharvestvehicleinline,
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
        city_name = get_name(SubRegion, organization_profile.city_id, "City")
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
    year = str(date.year)

    # Filtrar los ScheduleHarvestHarvestingCrew relacionados con el harvest específico
    scheduleharvestharvestingcrewinline = ScheduleHarvestHarvestingCrew.objects.filter(harvest_cutting=harvest).select_related('harvesting_crew')
    # Obtener los IDs de los HarvestingCrew asociados
    harvestingcrew_ids = scheduleharvestharvestingcrewinline.values_list('harvesting_crew', flat=True)

    # Filtrar los HarvestingCrew usando los IDs obtenidos
    harvestingcrew = HarvestingCrew.objects.filter(pk__in=harvestingcrew_ids)

    # Filtrar vehiculos por cuadrillas
    vehicles = ScheduleHarvestVehicle.objects.filter(harvest_cutting=harvest)

    # CSS
    base_url = request.build_absolute_uri('/')
    css = CSS(string='''
        @page {
            size: legal portrait;
        }''')

    orchard_certifications = OrchardCertification.objects.filter(
        orchard=harvest.orchard,
        created_at__lte=harvest.harvest_date,
        expiration_date__gte=harvest.harvest_date,
        is_enabled=True
        )
    import logging
    logger = logging.getLogger(__name__)
    logger.debug(f"Orchard certifications: {orchard_certifications}")

    # Renderizar el template HTML
    html_string = render_to_string('admin/packhouses/gathering/safety-guidelines-report.html', {
        'packhouse_name': packhouse_name,
        'company_address': company_address,
        'pdf_title': pdf_title,
        'logo_url': logo_url,
        'harvest': harvest,
        'orchard_certifications': orchard_certifications,
        'harvesting_crew': harvestingcrew,
        'vehicles': vehicles,
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

    if schedule_harvest.incoming_product is not None:
        return JsonResponse({
            'success': False,
            'message': 'Cannot cancel harvest because an incoming product is linked.'
        }, status=403)

    schedule_harvest.status = 'canceled'
    schedule_harvest.save()
    success_message = _('Harvest canceled successfully.')

    return JsonResponse({
        'success': True,
        'message': success_message
    })

def set_scheduleharvest_ready(request, harvest_id):
    scheduleharvest = get_object_or_404(
        ScheduleHarvest,
        pk=harvest_id,
        organization=request.organization
    )
    if scheduleharvest.status not in ['open']:
        return JsonResponse({
            'success': False,
            'message': 'You cannot send this harvest.'
        }, status=403)

    incoming_kwargs = {
        'organization': scheduleharvest.organization,
    }
    if scheduleharvest.weighing_scale:
        incoming_kwargs['public_weighing_scale'] = scheduleharvest.weighing_scale

    incoming_product = IncomingProduct.objects.create(**incoming_kwargs)
    scheduleharvest.incoming_product = incoming_product
    scheduleharvest.status = 'ready'
    scheduleharvest.save()

    success_message = _('Harvest sent to Fruit Receiving Area successfully.')
    return JsonResponse({
        'success': True,
        'message': success_message
    })



def basic_report(request, json_data, model_verbose_name, model_key, pretty_filters):
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
        add = request.organization.organizationprofile.address
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

    pdf_title = model_verbose_name
    packhouse_name = organization
    company_address = f"{add}, {district_name}, {city_name}, {state_name}, {country_name}"
    columns_total = len(headers)
    date = datetime.now()
    year = str(date.year)
    ordered = apply_filter_config(pretty_filters, model_key)

    # 1. Separar “date‐ranges” del resto
    date_ranges = {}
    other_filters = {}
    for label, value in ordered.items():
        # Si el valor contiene " - ", asumimos que es un rango de fechas
        if isinstance(value, str) and " - " in value:
            date_ranges[label] = value
        else:
            other_filters[label] = value

    # orientation page
    if len(headers) < 10:
        css = CSS(string='''
        @page {
            size: letter portrait;
        }''')
    elif len(headers) < 16:
        css = CSS(string='''
        @page {
            size: letter landscape;
        }''')
    else:
        css = CSS(string='''
        @page {
            size: 18in 11in;
        }''')

    # send data to create pdf
    html_string = render_to_string(
        "admin/packhouses/base-table-report.html",
        {
            "company_info":    "Certiffy",
            "pdf_title":       pdf_title,
            "headers":         headers,
            "packhouse_name":  packhouse_name,
            "company_address": company_address,
            "data":            data,
            "columns_total":   columns_total,
            "year":            year,
            "date":            date,
            "date_ranges":     date_ranges,
            "other_filters":   other_filters,
        },
    )

    html = HTML(string=html_string, base_url=base_url)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{model_verbose_name}.pdf"'
    html.write_pdf(response, stylesheets=[css])

    return response

