from django.apps import apps


def is_instance_used(instance, exclude=None):
    if exclude is None:
        exclude_classes = []

    related_classes = set()

    for model in apps.get_models():
        for field in model._meta.get_fields():
            if field.is_relation and field.related_model == instance.__class__ and not field.many_to_many:
                if model.objects.filter(**{field.name: instance}).exists():
                    related_classes.add(model)

    related_classes.difference_update(exclude_classes)

    return len(related_classes) > 0
