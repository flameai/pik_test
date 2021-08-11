from django.contrib.gis.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

# Create your models here.


class ManagebleByUserMixin:
    """
    Миксин для определения интерфейсов того, что у сущности есть менеджер
    """
    def is_manager(self, user):
        return False


class CreatableByUserMixin:
    """
    Миксин сущности, которая может быть создана пользователем
    """
    @classmethod
    def can_create(cls, user, data):
        """
        Возвращает истину, если из данных data пользователю разрешено создать сущность
        """
        return False


class UpdatebleByUserMixin:
    """
    Миксин сущности, которая может быть обновлена пользователем
    """    
    def can_update(self, user, data):
        """
        Возвращает истину, если с новыми данными data пользователю разрешено сохранить сущность
        """
        return False


class ServiceType(models.Model):
    """
    Модель типа услуги
    """
    name = models.CharField(max_length=250, verbose_name="наименование типа услуги")

    def __str__(self):
        return self.name


class Provider(models.Model, ManagebleByUserMixin, CreatableByUserMixin, UpdatebleByUserMixin):
    """
    Модель поставщика услуги
    """
    name = models.CharField(max_length=250, verbose_name="наименование организации-поставщика")
    email = models.EmailField(verbose_name="электронная почта")
    phone = models.CharField(max_length=10, verbose_name="телефон")
    address = models.CharField(max_length=250, verbose_name="адрес центрального офиса")
    manager = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="менеджер организации", null=False, blank=False, related_name="providers")

    def __str__(self):
        return self.name

    def is_manager(self, user):
        return self.manager == user

    @classmethod
    def can_create(self, user, data):
        # Пользователь может создать поставщика и сразу же станет его менеджером
        return True

    def can_update(self, user, data):
        # Пользователь всегда сможет обновить Поставщика
        return True


class Zone(models.Model, ManagebleByUserMixin, CreatableByUserMixin, UpdatebleByUserMixin):
    """
    Модель зоны обслуживания
    """
    name = models.CharField(max_length=250, verbose_name="наименование зоны")
    mpoly = models.MultiPolygonField()
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, verbose_name="поставщик услуги", null=False, blank=False, related_name="zones")

    def __str__(self):
        return self.name

    def is_manager(self, user):
        return self.provider.manager == user

    @classmethod
    def can_create(cls, user, data):
        return data['provider'] in user.providers.all().values_list('pk', flat=True)

    def can_update(self, user, data):
        """
        Возвращает True, если пользователь является менеджером поставщика зоны
        и не пытается передать зону чужому провайдеру
        """
        if self.provider.manager != user:
            return False
        if 'provider' in data and self.provider != data['provider']:
            # Попытка смены поставщика
            return Zone.can_create(user, data)
        return True
    

class Service(models.Model, ManagebleByUserMixin, CreatableByUserMixin, UpdatebleByUserMixin):
    """
    Модель услуги, оказываемой в рамках одной зоны
    """
    name = models.CharField(max_length=250, verbose_name="наименование услуги")
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, verbose_name="зона обслуживания", null=False, blank=False, related_name="services")
    service_type = models.ForeignKey(ServiceType, on_delete=models.CASCADE, verbose_name="тип услуги", null=False, blank=False, related_name="services")
    cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="стоимость услуги", null=False, blank=False)

    def __str__(self):
        return self.name
    
    def is_manager(self, user):
        return self.zone.provider.manager == user

    @classmethod
    def can_create(cls, user, data):
        # Пользователь может создать услугу только в своих зонах        
        return data['zone'] in Zone.objects.filter(provider__manager=user).values_list('pk', flat=True)
    
    def can_update(self, user, data):
        """
        Возвращает True, если пользователь является менеджером поставщика зоны
        и не пытается передать услугу в чужую зону
        """
        if self.zone.provider.manager != user:
            return False        
        if 'zone' in data and data['zone'] != self.zone.pk:
            return Service.can_create(user,data)
        return True

    def clean(self):
        """
        Проверка того, что для данной услуги зоны нет пересечений с другими зонами,
        Например, для района Южное Бутово не должно быть пересечения с другим участком 
        одного и того же поставщика с одинаковым типом услуг,
        т.к. это противоречит здравому смыслу
        """

        # qs зон данного поставщика, которые имеют пересечения
        self_intersected_zones_qs = Zone.objects.filter(mpoly__intersects=self.zone.mpoly, provider=self.zone.provider)
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