from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils.translation import gettext as _
from .models import (Requisition, RequisitionSupply, Country, Region, SubRegion, City)
from packhouses.catalogs.models import HarvestingCrew
from django.template.loader import render_to_string
from django.http import HttpResponse
from weasyprint import HTML, CSS
from io import BytesIO
from datetime import datetime
from django.db.models import Prefetch
from django.utils.text import capfirst
from django.db.models import Sum
from django.urls import reverse
from django.http import HttpResponseForbidden
from django.http import JsonResponse

def requisition_pdf(request, requisition_id):
    # Obtener el registro
    requisition = get_object_or_404(Requisition, pk=requisition_id)

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
    pdf_title = f"{capfirst(Requisition._meta.verbose_name)}"
    packhouse_name = organization
    company_address = f"{add}, {district_name}, {city_name}, {state_name}, {country_name}"
    date = datetime.now()
    year = date.year

    # Obtener los inlines relacionados
    requisitionsupplyinline = RequisitionSupply.objects.filter(requisition=requisition)

    # CSS
    base_url = request.build_absolute_uri('/')
    css = CSS(string='''
        @page {
            size: letter portrait;
        }''')

    request_text = _("We hereby request the Purchasing Operations Department to acquire the necessary supplies as detailed in this document.")

    applicant_name = f"{requisition.user.first_name or ''} {requisition.user.last_name or ''}".strip()
    applicant_email = requisition.user.email or ""

    # Renderizar el template HTML
    html_string = render_to_string('admin/packhouses/sales-order-requisition-report.html', {
        'packhouse_name': packhouse_name,
        'company_address': company_address,
        'pdf_title': pdf_title,
        'logo_url': logo_url,
        'requisition': requisition,
        'requisitionsupplyinline': requisitionsupplyinline,
        'year': year,
        'date': date,
        'request_text': request_text,
        'applicant_name': applicant_name,
        'applicant_email': applicant_email,
    })

    # Convertir el HTML a PDF
    html = HTML(string=html_string, base_url=base_url)
    pdf_buffer = BytesIO()
    html.write_pdf(pdf_buffer, stylesheets=[css],)

    # Traducir el nombre del archivo manualmente
    filename = f"{_('requisition')}_{requisition.ooid}.pdf"

    # Devolver el PDF como respuesta
    pdf_buffer.seek(0)
    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    return response


def set_requisition_ready(request, requisition_id):
    requisition = get_object_or_404(Requisition, pk=requisition_id)
    if requisition.status not in ['open']:
        return JsonResponse({
            'success': False,
            'message': 'You cannot send this requisition.'
        }, status=403)

    requisition.status = 'ready'
    requisition.save()
    success_message = _('Requisition sent to Purchase Operations Department successfully.')

    return JsonResponse({
        'success': True,
        'message': success_message
    })
