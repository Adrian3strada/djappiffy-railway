from django.db import models
from django.utils.translation import gettext_lazy as _


# Create your models here.

class StorageRoom(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Storage Room Name"))
    capacity = models.PositiveIntegerField(verbose_name=_("Capacity (in cubic meters)"))
    location = models.CharField(max_length=255, verbose_name=_("Location"))

    class Meta:
        verbose_name = _("Storage Room")
        verbose_name_plural = _("Storage Rooms")

    def __str__(self):
        return self.name


class Location(models.Model):  # estantería, zona, etc.
    storage_room = models.ForeignKey(StorageRoom, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=50, choices=[('caja', 'Caja'), ('pallet', 'Pallet')])


class Product(models.Model):
    sku = models.CharField(max_length=100, unique=True)
    nombre = models.CharField(max_length=200)
    temperatura_objetivo = models.DecimalField(max_digits=5, decimal_places=2)


class Inventory(models.Model):
    producto = models.ForeignKey(Product, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_entrada = models.DateField()
    fecha_caducidad = models.DateField(null=True, blank=True)
