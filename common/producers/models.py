from django.contrib.gis.db import models
from common.profiles.models import OrganizationProfile

# Create your models here.


class Producer(models.Model):
    organization = models.ForeignKey(OrganizationProfile, on_delete=models.PROTECT, related_name='producers')
    name = models.CharField(max_length=200)
    registry_number = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    ha = models.FloatField()
    anual_production_ha = models.FloatField()
    phytosanitary_certificate = models.CharField(max_length=100)
    registry_date = models.DateField()
    geom_file = models.FileField()  # TODO implementar la logica de procesamiento en el archivo
    geom = models.MultiPolygonField(srid=4326)

    def __str__(self):
        return


class Certification(models.Model):
    producer = models.ForeignKey(Producer, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    verifier = models.CharField(max_length=200)
    issue_date = models.DateField()
    expiration_date = models.DateField()

    def __str__(self):
        return
