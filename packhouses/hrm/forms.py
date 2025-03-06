from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import (EmployeeEvent, EmployeeJobPosition, Employee, EmployeeTaxAndMedicalInformation, 
                     EmployeeAcademicAndWorkInformation, EmployeeStatus)
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

class EmployeeStatusForm(forms.ModelForm):
    class Meta:
        model = EmployeeStatus
        fields = '__all__'
    
    def clean(self):
        cleaned_data = super().clean()
        is_paid = cleaned_data.get('is_paid')
        payment_percentage = cleaned_data.get('payment_percentage')

        if is_paid and not payment_percentage:
            self.add_error('payment_percentage', _("This field is required when 'Is Paid' is checked."))
        
        return cleaned_data
    

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        is_staff = cleaned_data.get('is_staff')
        staff_username = cleaned_data.get('staff_username')

        if is_staff and not staff_username:
            self.add_error('staff_username', _("This field is required when 'Is Staff' is checked."))
        
        return cleaned_data

class JobPositionInlineForm(forms.ModelForm):
    class Meta:
        model = EmployeeJobPosition
        fields = '__all__'
    
    def clean(self):
        cleaned_data = super().clean()
        payment_kind = cleaned_data.get('payment_kind')
        bank = cleaned_data.get('bank')
        bank_account_number = cleaned_data.get('bank_account_number')
        clabe = cleaned_data.get('clabe')
        swift = cleaned_data.get('swift')

        # Verifica si la categoría requiere validación de banco
        if payment_kind in ['bank_transfer', 'cheque']:
            if not bank:
                self.add_error('bank', _('This field is required when Payment Kind is not cash.'))
            if not bank_account_number:
                self.add_error('bank_account_number', _('This field is required when Payment Kind is not cash.'))
            if not clabe:
                self.add_error('clabe', _('This field is required when Payment Kind is not cash.'))
            if not swift:
                self.add_error('swift', _('This field is required when Payment Kind is not cash.'))
        return cleaned_data
    
class TaxAndMedicalInlineForm(forms.ModelForm):
    class Meta:
        model = EmployeeTaxAndMedicalInformation
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        has_disability = cleaned_data.get('has_disability')
        disability_details = cleaned_data.get('disability_details')

        has_chronic_illness  = cleaned_data.get('has_chronic_illness')
        chronic_illness_details = cleaned_data.get('chronic_illness_details')

        has_private_insurance  = cleaned_data.get('has_private_insurance', False)
        medical_insurance_provider = cleaned_data.get('medical_insurance_provider')
        medical_insurance_number = cleaned_data.get('medical_insurance_number')
        medical_insurance_start_date = cleaned_data.get('medical_insurance_start_date')

        private_insurance_details = cleaned_data.get('private_insurance_details')

        if has_disability and not disability_details:
            self.add_error('disability_details', _('This field is required when disability is checked.'))
        
        if has_chronic_illness and not chronic_illness_details:
            self.add_error('chronic_illness_details', _('This field is required when Chronic Illness is checked.'))
        
        if not has_private_insurance: 
            if not medical_insurance_provider:
                self.add_error('medical_insurance_provider', _('This field is required.'))
            if not medical_insurance_start_date:
                self.add_error('medical_insurance_start_date', _('This field is required.'))
            if not medical_insurance_number:
                self.add_error('medical_insurance_number', _('This field is required.'))
        
        if has_private_insurance and not private_insurance_details:
            self.add_error('private_insurance_details', _('This field is requiered when Private Insurance us checked'))
        return cleaned_data
       

class  AcademicAndWorkInlineForm(forms.ModelForm):
    class Meta:
        model = EmployeeAcademicAndWorkInformation
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        academic_status = cleaned_data.get('academic_status')
        graduation_year = cleaned_data.get('graduation_year')
        degree = cleaned_data.get('degree')
        institution = cleaned_data.get('institution')

        if academic_status == 'upper_secondary_education' and not graduation_year:
            self.add_error('graduation_year', _('This field is requiered when academic formation is "Upper Secondary Education"'))
        if academic_status == 'higher_education':
            if not degree:
                self.add_error('degree', _('This field is requiered when academic formation is "Higher Education"'))
            if not institution:
                self.add_error('institution', _('This field is requiered when academic formation is "Higher Education"'))
        return cleaned_data
        