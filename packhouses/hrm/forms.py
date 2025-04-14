from django import forms
from .models import WorkShiftSchedule

class WorkShiftScheduleForm(forms.ModelForm):
    # Campo "day" oculto para nuevos registros
    day = forms.CharField(widget=forms.HiddenInput(), required=True)

    class Meta:
        model = WorkShiftSchedule
        fields = ('day', 'entry_time', 'exit_time', 'is_enabled')