from django.contrib.gis.db import models
from django.contrib.auth.models import User

# Create your models here.

class ServiceType(models.Model):
    """
    Модель типа услуги
    """
    name = models.CharField(max_length=250, verbose_name="наименование типа услуги")


class Provider(models.Model):
    """
    Модель поставщика услуги
    """
    name = models.CharField(max_length=250, verbose_name="наименование организации-поставщика")
    email = models.EmailField(verbose_name="электронная почта")
    phone = models.CharField(max_length=10, verbose_name="телефон")
    address = models.CharField(max_length=250, verbose_name="адрес центрального офиса")
    manager = models.OneToOneField(User, on_delete=models.DO_NOTHING, verbose_name="менеджер организации", null=False, blank=False, related_name="provider")

    def __str__(self):
        return self.name


class Zone(models.Model):
    """
    Модель зоны обслуживания
    """
    name = models.CharField(max_length=250, verbose_name="наименование зоны")
    mpoly = models.MultiPolygonField()
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, verbose_name="поставщик услуги", null=False, blank=False, related_name="zones")

    def __str__(self):
        return self.name

class Service(models.Model):
    """
    Модель услуги, оказываемой в рамках одной зоны
    """
    name = models.CharField(max_length=250, verbose_name="наименование услуги")
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, verbose_name="зона обслуживания", null=False, blank=False, related_name="services")
    service_type = models.ForeignKey(ServiceType, on_delete=models.CASCADE, verbose_name="тип услуги", null=False, blank=False, related_name="services")
    cost = models.DecimalField(max_digits=2, decimal_places=2, verbose_name="стоимость услуги", null=False, blank=False)