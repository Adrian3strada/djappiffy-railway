from django import forms


class UppercaseTextInputWidget(forms.TextInput):
    def __init__(self, *args, **kwargs):
        kwargs['attrs'] = {
            'oninput': (
                "let start = this.selectionStart, end = this.selectionEnd;"
                "this.value = this.value.toUpperCase();"
                "this.setSelectionRange(start, end);"
            )
        }
        super().__init__(*args, **kwargs)

    def format_value(self, value):
        return value.upper() if value else ''


class UppercaseAlphanumericTextInputWidget(forms.TextInput):
    def __init__(self, *args, **kwargs):
        kwargs['attrs'] = {
            'oninput': (
                "let start = this.selectionStart, end = this.selectionEnd;"
                "this.value = this.value.toUpperCase().replace(/[^A-Z0-9]/g, '');"
                "this.setSelectionRange(start, end);"
            )
        }
        super().__init__(*args, **kwargs)

    def format_value(self, value):
        return value.upper() if value else ''


class AutoGrowingTextareaWidget(forms.Textarea):
    def __init__(self, attrs=None):
        default_attrs = {
            'rows': 1,
            'class': 'vTextField',
            'style': 'width: 100%; max-height: 12em; overflow-y: auto; min-height: calc(2.25rem + 2px);',
            'oninput': 'this.style.height = ""; this.style.height = Math.min(this.scrollHeight, 12 * parseFloat(getComputedStyle(this).lineHeight)) + "px";'
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)

    class Media:
        js = (
            'js/admin/forms/adjust_textarea_height.js',
        )
