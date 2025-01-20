from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils.translation import gettext as _
from .models import *
from django.template.loader import render_to_string
from django.http import HttpResponse
from weasyprint import HTML, CSS
from io import BytesIO

def generate_pdf(request, harvest_id):
    # Obtener el registro
    harvest = get_object_or_404(ScheduleHarvest, pk=harvest_id)

    # Obtener los inlines relacionados
    scheduleharvestharvestingcrewinline = ScheduleHarvestHarvestingCrew.objects.filter(harvest_cutting=harvest)
    scheduleharvestvehicleinline = ScheduleHarvestVehicle.objects.filter(harvest_cutting=harvest)
    scheduleharvestcontainervehicleinline = ScheduleHarvestContainerVehicle.objects.filter(harvest_cutting__in=scheduleharvestvehicleinline)

    # Renderizar el template HTML
    html_string = render_to_string('admin/scheduleharvest_pdf.html', {
        'harvest': harvest,
        'scheduleharvestharvestingcrewinline': scheduleharvestharvestingcrewinline,
        'scheduleharvestvehicleinline': scheduleharvestvehicleinline,
        'scheduleharvestcontainervehicleinline': scheduleharvestcontainervehicleinline,
    })
    # Convertir el HTML a PDF
    html = HTML(string=html_string)
    pdf_buffer = BytesIO()
    html.write_pdf(pdf_buffer)

    # Traducir el nombre del archivo manualmente
    filename = f"{_('harvest_order')}_{harvest.ooid}.pdf"

    # Devolver el PDF como respuesta
    pdf_buffer.seek(0)
    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    return response
