from django import forms
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _


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

class CustomFileDisplayWidget(forms.ClearableFileInput):
    """
    Widget personalizado para campos FileField en Django.

    Este widget reemplaza el comportamiento estándar del ClearableFileInput para:

    1. Mostrar un botón de "Visualizar Comprobante" en lugar de la ruta del archivo.
    2. Integrar un modal con SweetAlert2 para visualizar el comprobante sin salir de la página.
    3. Soportar archivos de imagen (JPEG, PNG, HEIC) y documentos PDF.

    -> Si el archivo es un PDF, se muestra en un iframe dentro del modal.
    -> Si el archivo es una imagen, se muestra como un elemento `<img>`.
    -> Si el archivo no existe aún (en modo creación), se muestra el campo para subirlo.
    """

    def render(self, name, value, attrs=None, renderer=None):
        """
        Sobrescribe el metodo render para cambiar la vista estándar del FileField.

        - Si existe un valor y tiene URL, muestra un botón de "Visualizar archivo".
        - Caso contrario, muestra el input para subir un archivo.
        """
        # Generar un identificador único para cada botón basado en el nombre del campo
        unique_id = f'{name.replace("-", "_")}_view'

        if value and hasattr(value, 'url'):
            # Definimos el tipo de vista dependiendo de la extensión
            if value.file.name.lower().endswith('.pdf'):
                html_preview = f'<iframe src="{value.url}" width="100%" height="600px" style="border:none;"></iframe>'
            else:
                html_preview = f'<img src="{value.url}" style="max-width:100%; height:auto;" />'

            # Botón para visualizar en un modal de SweetAlert2 con un ID único
            link_text = _("View attached file")
            return mark_safe(f'''
                <a class="button" href="javascript:void(0);" onclick="showAttachedFile_{unique_id}()" style="color:blue;">
                    {link_text}
                </a>

                <script type="text/javascript">
                    function showAttachedFile_{unique_id}() {{
                        Swal.fire({{
                            title: `{link_text}`,
                            html: `{html_preview}`,
                            width: '80%',
                            heightAuto: true,
                            showCloseButton: true,
                            showConfirmButton: false,
                            customClass: {{
                                popup: 'swal-wide'
                            }},
                        }});
                    }}
                </script>
            ''')
        else:
            # Muestra el input estándar para subir archivo si no existe valor
            return super().render(name, value, attrs, renderer)

