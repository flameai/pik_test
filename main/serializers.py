from rest_framework import serializers
from main.models import Provider, Zone, Service, ServiceType
from django.core.exceptions import ValidationError, PermissionDenied
from django.utils.translation import gettext_lazy as _


class ServiceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceType
        fields = '__all__'

class ServiceSerializerRead(serializers.ModelSerializer):
    service_type = ServiceTypeSerializer()
    class Meta:
        model = Service
        fields = '__all__'

class ServiceSerializerWrite(serializers.ModelSerializer):    
    class Meta:
        model = Service
        fields = '__all__'

    def validate(self, data):
        # Проведем валидацию по правилам модели
        tmp_obj = Service(**data)
        try:
            tmp_obj.clean()
        except ValidationError as e:
            raise serializers.ValidationError(e)

        return data
    

class ProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provider
        fields = '__all__'
        read_only_fields = ('manager',)

    def create(self, data):
        data['manager'] = self.context['manager']
        return super().create(data)

class ZoneSerializerRead(serializers.ModelSerializer):
    services = ServiceSerializerRead(many=True)
    provider = ProviderSerializer()

    class Meta:
        model = Zone
        fields = '__all__'
    
class ZoneSerializerWrite(serializers.ModelSerializer):    

    class Meta:
        model = Zone
        fields = '__all__'

