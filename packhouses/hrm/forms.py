from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import EmployeeEvent

class EmployeeEventForm(forms.ModelForm):
    class Meta:
        model = EmployeeEvent
        fields = '__all__'

    question_button_text = _("How would you like to proceed?")
    confirm_button_text = _("Save and approved")
    deny_button_text = _("Only save")
    cancel_button_text = _("Cancel")

    save_and_send = forms.BooleanField(
        label=_("Save and send to Purchase Operations Department"),
        required=False,
        widget=forms.HiddenInput(attrs={
            'data-question': question_button_text,
            'data-confirm': confirm_button_text,
            'data-deny': deny_button_text,
            'data-cancel': cancel_button_text
        })
    )

