from django.utils.translation import gettext_lazy as _
from django.db import models

# Create your models here.


class Product(models.Model):
    name = models.CharField(max_length=255)
    in_due_diligence = models.BooleanField(default=False)
    for_packaging = models.BooleanField(default=False)
    for_orchad = models.BooleanField(default=False)
    for_eudd = models.BooleanField(default=False)
    for_export = models.BooleanField(default=False)
    image = models.ImageField(upload_to="products", blank=True, null=True)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))

    def __str__(self):
        return self.name
