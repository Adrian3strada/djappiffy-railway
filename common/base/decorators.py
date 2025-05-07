# decorators.py

from functools import wraps
from common.widgets import UppercaseTextInputWidget, UppercaseAlphanumericTextInputWidget


# formsets

def uppercase_formset_charfield(field_name):
    def decorator(get_formset_method):
        @wraps(get_formset_method)
        def wrapper(self, request, obj=None, **kwargs):
            formset = get_formset_method(self, request, obj, **kwargs)
            if field_name in formset.form.base_fields:
                formset.form.base_fields[field_name].widget = UppercaseTextInputWidget()
            return formset
        return wrapper
    return decorator

def uppercase_alphanumeric_formset_charfield(field_name):
    def decorator(get_formset_method):
        @wraps(get_formset_method)
        def wrapper(self, request, obj=None, **kwargs):
            formset = get_formset_method(self, request, obj, **kwargs)
            if field_name in formset.form.base_fields:
                formset.form.base_fields[field_name].widget = UppercaseAlphanumericTextInputWidget()
            return formset
        return wrapper
    return decorator


# forms

def uppercase_form_charfield(field_name):
    def decorator(get_form_method):
        @wraps(get_form_method)
        def wrapper(self, request, obj=None, **kwargs):
            form = get_form_method(self, request, obj, **kwargs)
            if field_name in form.base_fields:
                form.base_fields[field_name].widget = UppercaseTextInputWidget()
            return form
        return wrapper
    return decorator

def uppercase_alphanumeric_form_charfield(field_name):
    def decorator(get_form_method):
        @wraps(get_form_method)
        def wrapper(self, request, obj=None, **kwargs):
            form = get_form_method(self, request, obj, **kwargs)
            if field_name in form.base_fields:
                form.base_fields[field_name].widget = UppercaseAlphanumericTextInputWidget()
            return form
        return wrapper
    return decorator
