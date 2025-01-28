from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils.translation import gettext as _
from .models import (ScheduleHarvest, ScheduleHarvestHarvestingCrew, ScheduleHarvestVehicle, ScheduleHarvestContainerVehicle)
from packhouses.catalogs.models import HarvestingCrew
from django.template.loader import render_to_string
from django.http import HttpResponse
from weasyprint import HTML, CSS
from io import BytesIO
from django.urls import reverse
from django.http import HttpResponseForbidden

def harvest_order_pdf(request, harvest_id):
    # Obtener el registro
    harvest = get_object_or_404(ScheduleHarvest, pk=harvest_id)

    # Obtener los inlines relacionados
    scheduleharvestharvestingcrewinline = ScheduleHarvestHarvestingCrew.objects.filter(harvest_cutting=harvest)
    scheduleharvestvehicleinline = ScheduleHarvestVehicle.objects.filter(harvest_cutting=harvest)
    scheduleharvestcontainervehicleinline = ScheduleHarvestContainerVehicle.objects.filter(harvest_cutting__in=scheduleharvestvehicleinline)

    # Renderizar el template HTML
    html_string = render_to_string('admin/packhouses/scheduleharvest_pdf.html', {
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

def cancel_schedule_harvest(request, pk):
    schedule_harvest = get_object_or_404(ScheduleHarvest, pk=pk)
    if schedule_harvest.status not in ['open']:
        return HttpResponseForbidden("You cannot cancel this harvest.")
    schedule_harvest.status = 'canceled'
    schedule_harvest.save()
    return redirect(reverse('admin:gathering_scheduleharvest_changelist'))
