from django.apps import apps
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def is_instance_used(instance, exclude=None):
    if exclude is None:
        exclude = []

    related_classes = set()

    for model in apps.get_models():
        for field in model._meta.get_fields():
            if field.is_relation and field.related_model == instance.__class__ and not field.many_to_many:
                if model.objects.filter(**{field.name: instance}).exists():
                    related_classes.add(model)

    related_classes.difference_update(exclude)
    print("is_instance_used() related_classes: ", related_classes)

    return len(related_classes) > 0


def validate_file_extension(value, allowed_extensions=None):
    """
    Validador para asegurar que un archivo tenga una extensión permitida.

    Args:
        value (FileField): El archivo a validar.
        allowed_extensions (list, opcional): Lista de extensiones permitidas.
                                             Si no se especifica, se usan las predeterminadas.

    Ejemplo de uso especificando extensiones:
    from common.utils import validate_file_extension
    class AnotherModel(models.Model):
        document = models.FileField(
            upload_to='documents/',
            validators=[lambda x: validate_file_extension(x, allowed_extensions=['.docx', '.xlsx'])]
        )
    """
    if allowed_extensions is None:
        allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.heic']

    ext = value.name.split('.')[-1].lower()
    if f'.{ext}' not in allowed_extensions:
        raise ValidationError(
            _(f'Unsupported file extension. Allowed extensions are: {", ".join(allowed_extensions)}.'))

