from django import forms
from django.utils.translation import gettext_lazy as _
from packhouses.gathering.models import ScheduleHarvestVehicle, ScheduleHarvestContainerVehicle
from .models import IncomingProduct, Batch, SamplePest, SampleDisease, SamplePhysicalDamage, SampleResidue, FoodSafety
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet
from django.utils.safestring import mark_safe

class ContainerInlineFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.forms:
            if form.instance.pk and form.instance.created_at_model == 'gathering':
                if 'DELETE' in form.fields:
                    form.fields['DELETE'].widget = forms.HiddenInput()
                    form.fields['DELETE'].initial = False

    def _construct_form(self, i, **kwargs):
        form = super()._construct_form(i, **kwargs)
        if form.instance.pk and form.instance.created_at_model == 'gathering':
            if "DELETE" in form.fields:
                form.fields["DELETE"].widget = forms.HiddenInput()
                form.fields["DELETE"].initial = False
                form.fields["DELETE"].disabled = True
        return form

    def clean(self):
        cleaned_data = super().clean()
        for form in self.forms:
            if form.instance.pk and form.instance.created_at_model == 'gathering':
                form.cleaned_data['DELETE'] = False
        return cleaned_data

class ContainerInlineForm(forms.ModelForm):
    class Meta:
        model = ScheduleHarvestContainerVehicle
        exclude = ("created_at_model",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')

        if instance and instance.pk and instance.created_at_model == 'gathering':
            for field_name in self.fields:
                if field_name not in ['full_containers', 'empty_containers', 'missing_containers']:
                    self.fields[field_name].disabled = True
                    self.fields[field_name].widget.attrs.update({
                        "style": (
                            "pointer-events: none; "
                            "background-color: #e9ecef; "
                            "border: none; "
                            "color: #555;"
                        )
                    })

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.created_at_model:  
            instance.created_at_model = 'incoming_product'  
        if commit:
            instance.save()
        return instance
    

class BaseScheduleHarvestVehicleFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()

        incoming_status = None
        if hasattr(self.instance, 'incoming_product'):
            incoming_status = self.instance.incoming_product.status
        else:
            incoming_status = self.data.get('status')

        if incoming_status == "accepted":
            valid_forms = [
                form.cleaned_data
                for form in self.forms
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False)
            ]
            
            has_arrived_flags = [data.get('has_arrived', False) for data in valid_forms]
            
            if not any(has_arrived_flags):
                error_msg = mark_safe('<span style="color: red;">You must register at least one vehicle as having arrived for the Incoming Product.</span>')
                raise ValidationError(error_msg)
        

class ScheduleHarvestVehicleForm(forms.ModelForm):
    stamp_vehicle_number = forms.CharField(label=_('Stamp Number'), required=True,)

    class Meta:
        model = ScheduleHarvestVehicle
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        has_arrived_init = self.instance.has_arrived
        if has_arrived_init:
            self.fields['stamp_vehicle_number'].initial = self.instance.stamp_number
        else:
            self.fields['stamp_vehicle_number'].initial = ""

        if request:
            if request.POST:
                has_arrived_str = request.POST.get('has_arrived')
                has_arrived = has_arrived_str == 'on'
                self.fields['stamp_vehicle_number'].required = has_arrived
            else:
                self.fields['stamp_vehicle_number'].required = True

    def clean(self):
        cleaned_data = super().clean()
        stamp_vehicle_number = cleaned_data.get('stamp_vehicle_number')
        guide_number = cleaned_data.get('guide_number') 

        instance = self.instance
        has_arrived_initial = instance.has_arrived if instance and instance.pk else False
        has_arrived_final = cleaned_data.get('has_arrived', has_arrived_initial)

        errors = {} 
        # Validación cuando cambia de False → True
        if not has_arrived_initial and has_arrived_final:
            if stamp_vehicle_number and instance and instance.stamp_number != stamp_vehicle_number:
                errors['stamp_vehicle_number'] = _('The provided Stamp does not match the original.')
            
            if not stamp_vehicle_number:
                self.fields['stamp_vehicle_number'].required = True
                errors['stamp_vehicle_number'] = _('Stamp Vehicle Number is required when the vehicle has arrived.')

            if not guide_number:
                self.fields['guide_number'].required = True
                errors['guide_number'] = _('Guide Number is required when the vehicle has arrived.')
        if errors:
            raise forms.ValidationError(errors)

        return cleaned_data


class IncomingProductForm(forms.ModelForm):
    class Meta:
        model = IncomingProduct
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean() or {}

        # Status guardado en la base de datos
        initial_status = self.instance.status if self.instance and self.instance.pk else None
        # Obtener el status final (del form)
        final_status = cleaned_data.get('status', initial_status)

        # Si ya está aceptado, se impide cambiar el status a otro valor.
        if self.instance.pk and initial_status == 'accepted' and final_status != 'accepted':
            raise ValidationError(_("Once accepted, the status cannot be changed."))

        # VALIDACIÓN PARA WEIGHING SETS:
        total_weighing_sets = int(self.data.get('weighingset_set-TOTAL_FORMS', 0))
        remaining_weighing_sets = 0
        
        # Contar los weighing sets que NO se marcaron para borrar.
        for i in range(total_weighing_sets):
            delete_key = f'weighingset_set-{i}-DELETE'
            if self.data.get(delete_key, 'off') != 'on':
                remaining_weighing_sets += 1

        if remaining_weighing_sets < 1 and final_status == "accepted":
            raise ValidationError(_("At least one Weighing Set must be registered for the Incoming Product."))

        # Validar cada weighing set
        for i in range(remaining_weighing_sets):
            weighingset_prefix = f'weighingset_set-{i}-'
            provider = self.data.get(weighingset_prefix + 'provider')
            harvesting_crew = self.data.get(weighingset_prefix + 'harvesting_crew')

            if not provider or not provider.strip():
                raise ValidationError(_(f'Weighing Set {i + 1} is missing a provider.'))
            if not harvesting_crew or not harvesting_crew.strip():
                raise ValidationError(_(f'Weighing Set {i + 1} is missing a harvesting crew.'))
        
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
    
        if instance.status == 'accepted' and not instance.batch:
            instance.create_batch()

        if commit:
            instance.save()
        return instance


class BatchForm(forms.ModelForm):
    class Meta:
        model = Batch
        fields = '__all__'

    def clean(self):
        cleaned = super().clean()

        # Recorre cada IncomingProduct y comprueba que tenga al menos un WeighingSet no marcado para borrar
        for i in range(int(self.data.get('incomingproduct_set-TOTAL_FORMS', 0))):
            ws_prefix = f'incomingproduct_set-{i}-weighingset_set'
            total_ws = int(self.data.get(f'{ws_prefix}-TOTAL_FORMS', 0))

            # Cuenta los que NO tienen DELETE = 'on'
            remaining = sum(
                1
                for j in range(total_ws)
                if self.data.get(f'{ws_prefix}-{j}-DELETE', 'off') != 'on'
            )

            if remaining < 1:
                raise ValidationError(
                    _('At least one Weighing Set must be registered.')
                )

        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
    
        if instance.status == 'accepted' and not instance.batch:
            instance.create_batch()

        if commit:
            instance.save()
        return instance


class BatchForm(forms.ModelForm):
    class Meta:
        model = Batch
        fields = '__all__'

    def clean(self):
        cleaned = super().clean()

        # Recorre cada IncomingProduct y comprueba que tenga al menos un WeighingSet no marcado para borrar
        for i in range(int(self.data.get('incomingproduct_set-TOTAL_FORMS', 0))):
            ws_prefix = f'incomingproduct_set-{i}-weighingset_set'
            total_ws = int(self.data.get(f'{ws_prefix}-TOTAL_FORMS', 0))

            # Cuenta los que NO tienen DELETE = 'on'
            remaining = sum(
                1
                for j in range(total_ws)
                if self.data.get(f'{ws_prefix}-{j}-DELETE', 'off') != 'on'
            )

            if remaining < 1:
                raise ValidationError(
                    _('At least one Weighing Set must be registered.')
                )

        return cleaned

class SamplePestForm(forms.ModelForm):
    class Meta:
        model = SamplePest
        fields = ['product_pest', 'sample_pest', 'percentage']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['percentage'].widget.attrs['readonly'] = 'readonly'

class SampleDiseaseForm(forms.ModelForm):
    class Meta:
        model = SampleDisease
        fields = ['product_disease', 'sample_disease', 'percentage']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['percentage'].widget.attrs['readonly'] = 'readonly'

class SamplePhysicalDamageForm(forms.ModelForm):
    class Meta:
        model = SamplePhysicalDamage
        fields = ['product_physical_damage', 'sample_physical_damage', 'percentage']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['percentage'].widget.attrs['readonly'] = 'readonly'

class SampleResidueForm(forms.ModelForm):
    class Meta:
        model = SampleResidue
        fields = ['product_residue', 'sample_residue', 'percentage']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['percentage'].widget.attrs['readonly'] = 'readonly'

class FoodSafetyFormInline(forms.ModelForm):
    class Meta:
        model = FoodSafety
        fields = ['batch']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['batch'].widget.can_add_related = False
        self.fields['batch'].widget.can_change_related = False
        self.fields['batch'].widget.can_delete_related = False
        self.fields['batch'].widget.can_view_related = False