from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse
from packhouses.gathering.models import ScheduleHarvestVehicle
from .forms import ScheduleHarvestVehicleForm
from django.utils.translation import gettext_lazy as _

def edit_schedule_harvest_vehicle(request, vehicle_id):
    vehicle = get_object_or_404(ScheduleHarvestVehicle, id=vehicle_id)
    
    if request.method == 'POST':
        form = ScheduleHarvestVehicleForm(request.POST, instance=vehicle)
        
        if form.is_valid():
            form.save()
            return redirect('success_url')  
        else:
            errors = form.errors.as_text()
            error_message = _('Error in the vehicle stamp: ') + errors
            return HttpResponse(error_message, status=400)
    else:
        form = ScheduleHarvestVehicleForm(instance=vehicle)
        return redirect('edit_schedule_harvest_vehicle', vehicle_id=vehicle.id)