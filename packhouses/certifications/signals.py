from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import Certification, Format
from common.base.models import CertificationFormat

@receiver(post_save, sender=Certification)
def add_requirement(sender, **kwargs):
    instance = kwargs.get('instance')
    id_certification = instance.id
    id_certification_entity = instance.certification_entity.id

    ids = CertificationFormat.objects.filter(certification_entity_id=id_certification_entity).values_list('id', flat=True)

    formants = [Format(certification_format_id=id_formant, certification_id=id_certification) for id_formant in ids]
    Format.objects.bulk_create(formants)
