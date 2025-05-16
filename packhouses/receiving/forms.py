from django import forms
from django.utils.translation import gettext_lazy as _
from packhouses.gathering.models import ScheduleHarvestVehicle, ScheduleHarvestContainerVehicle
from .models import IncomingProduct, Batch, WeighingSet, WeighingSetContainer
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet
from django.utils.safestring import mark_safe
from django.db import transaction
from common.settings import STATUS_CHOICES

# Forms
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

        if incoming_status == "ready":
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        status = self.initial.get('status') or self.instance.status
        # Oculta los estados no seleccionables para el usuario
        if 'status' in self.fields:
            self.fields['status'].choices = [
                (value, label) for value, label in self.fields['status'].choices
                if value != 'closed' or value == status
            ]

    def clean(self):
        cleaned_data = super().clean() or {}

        # Status guardado en base de datos
        initial_status = self.instance.status if self.instance and self.instance.pk else None
        # Status final enviado por el form
        final_status = cleaned_data.get('status', initial_status)

        if initial_status == 'ready' and final_status != 'ready':
            raise ValidationError(_("Once it is ready, the status cannot be changed."))

        # Validación de los WeighingSets (igual que antes)…
        total = int(self.data.get('weighingset_set-TOTAL_FORMS', 0))
        remaining = sum(
            1 for i in range(total)
            if self.data.get(f'weighingset_set-{i}-DELETE', 'off') != 'on'
        )
        if remaining < 1 and final_status == "ready":
            raise ValidationError(_("At least one Weighing Set must be registered for the Incoming Product."))

        for i in range(remaining):
            prefix = f'weighingset_set-{i}-'
            if not self.data.get(prefix + 'provider', '').strip():
                raise ValidationError(_(f'Weighing Set {i + 1} is missing a provider.'))
            if not self.data.get(prefix + 'harvesting_crew', '').strip():
                raise ValidationError(_(f'Weighing Set {i + 1} is missing a harvesting crew.'))

        return cleaned_data



class BatchForm(forms.ModelForm):
    class Meta:
        model = Batch
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        status = self.initial.get('status') or self.instance.status
        # Oculta los estados no seleccionables para el usuario
        self.fields['status'].choices = [
            (value, label) for value, label in self.fields['status'].choices
            if value != 'closed' or value == status
        ]

    def clean(self):
        cleaned = super().clean()

        status = cleaned.get('status')
        quarantine = cleaned.get('is_quarantined')
        available = cleaned.get('is_available_for_processing')

        # No permitir cambiar de estado una vez cerrado el lote
        if self.instance.pk and self.instance.status == 'closed' and status != 'closed':
            self.add_error('status', _('Cannot change status once closed.'))
            cleaned['status'] = 'closed'  # restaurar el valor real

        # No permitir cambiar valores de campos booleanos cuando este cancelado o rechazado el lote
        if status in ['closed', 'canceled'] and self.instance.pk:
            if quarantine != self.instance.is_quarantined:
                self.add_error('is_quarantined', _('Cannot change this field when status is closed or canceled.'))
            if available != self.instance.is_available_for_processing:
                self.add_error('is_available_for_processing', _('Cannot change this field when status is closed or canceled.'))

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


class WeighingSetForm(forms.ModelForm):
    class Meta:
        model = WeighingSet
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()

        if self.instance.pk and self.instance.protected:
            # Solo revisamos si hay cambios reales
            for field in self.fields:
                if field in self.changed_data:
                    raise ValidationError(_("No se puede modificar una pesada protegida."))

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)

        if instance.pk and instance.protected:
            try:
                from_db = type(instance).objects.get(pk=instance.pk)
            except Exception:
                raise ValidationError(_("No se pudo recuperar la pesada desde base de datos para validar."))

            for field in self.fields:
                if field in self.changed_data:
                    old = getattr(from_db, field)
                    new = getattr(instance, field)
                    if old != new:
                        raise ValidationError(
                            _(f"No se puede modificar la pesada protegida (campo modificado: {field}).")
                        )

        if commit:
            instance.save()
        return instance

class WeighingSetInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        for form in self.forms:
            if not form.cleaned_data:
                continue

            instance = form.instance
            if form.cleaned_data.get('DELETE', False) and instance.protected:
                raise ValidationError(_("No se puede eliminar una pesada protegida."))

