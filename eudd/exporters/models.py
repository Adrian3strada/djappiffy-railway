from django.db import models
from profiles.models import OrganizationProfile

# Create your models here.


class ExportRequestStatus(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class ExportRequestAnalysisResult(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class ExportRequest(models.Model):
    importer = models.ForeignKey(OrganizationProfile, on_delete=models.PROTECT, related_name='importer_export_requests')
    exporter = models.ForeignKey(OrganizationProfile, on_delete=models.PROTECT, related_name='exporter_export_requests')
    date_request = models.DateField(auto_now_add=True)
    date_release = models.DateField(null=True, blank=True)
    status = models.ForeignKey(ExportRequestStatus, on_delete=models.PROTECT)
    analysis_result = models.ForeignKey(ExportRequestAnalysisResult, on_delete=models.PROTECT)
    is_verified = models.BooleanField(default=False)

    @property
    def po(self):
        return f"{self.exporter.id}/{self.importer.id}"

    def __str__(self):
        return


class ExportRequestProducer(models.Model):
    export_request = models.ForeignKey(ExportRequest, on_delete=models.CASCADE, related_name='producers')
    box_name = models.CharField(max_length=100)
    box_kg = models.FloatField()
    box_quantity = models.IntegerField()

    def __str__(self):
        return


class ExportRequestPayment(models.Model):
    export_request = models.ForeignKey(ExportRequest, on_delete=models.CASCADE, related_name='payments')
    amount = models.FloatField()
    payment_date = models.DateField()

    def __str__(self):
        return
