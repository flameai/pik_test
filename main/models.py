from django.contrib.gis.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

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

    def __str__(self):
        return self.name

    def clean(self):
        """
        Метод проверки того, что для данной услуги зоны нет пересечений с другими зонами,
        Например, для района Южное Бутово не должно быть пересечения с другим участком.
        А если пересечение есть, то для этих друх участков не должно быть одинаковых типов услуг,
        т.к. это противоречит здравому смыслу        
        """

        # qs зон данного поставщика, которые имеют пересечения
        self_intersected_zones_qs = Zone.objects.filter(mpoly__intersects=self.zone, provider=self.zone.provider)
        if not self_intersected_zones_qs.exists():
            return

        # qs услуг того же типа данного поставщика в зонах пересечения
        self_intersected_serv_qs = Service.objects.filter(zone__in=self_intersected_zones_qs, service_type=self.service_type)
        if not self_intersected_serv_qs.exists():
            return
        
        # Если в базу руками не лазить, то на данном этапе qs должен содержать одну запись
        zone_name = self_intersected_serv_qs.first().zone.name
        raise ValidationError({
            'service_type': f"{_('Service type intersects with other one in zone with name:')} {zone_name}"
        })

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args,**kwargs)