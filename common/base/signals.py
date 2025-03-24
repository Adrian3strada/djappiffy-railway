from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import CertificationFormat
from packhouses.certifications.models import Format, Certification

@receiver(post_save, sender=CertificationFormat)
def add_requirement_to_certification(sender, **kwargs):
    print("Funciona")
    instance = kwargs.get('instance')
    id_requeriment = instance.id
    id_certification_entity = instance.certification_entity.id

    ids = Certification.objects.filter(certification_entity_id=id_certification_entity).values_list('id', flat=True)

    certications = [Format(certification_format_id=id_requeriment, certification_id=id_cert) for id_cert in ids]
    Format.objects.bulk_create(certications)