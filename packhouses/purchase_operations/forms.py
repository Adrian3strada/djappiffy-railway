from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import Requisition

class RequisitionForm(forms.ModelForm):
    class Meta:
        model = Requisition
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        requisition_supplies = self.data.getlist('requisitionsupply_set-TOTAL_FORMS', [])
        if not requisition_supplies or int(requisition_supplies[0]) < 1:
            raise ValidationError(_("You must add at least one supply to the requisition."))

        return cleaned_data

