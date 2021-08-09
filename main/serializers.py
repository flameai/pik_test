from rest_framework import serializers
from main.models import Provider, Zone, Service, ServiceType
from django.core.exceptions import ValidationError


class ServiceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceType
        fields = '__all__'

class ServiceSerializer(serializers.ModelSerializer):
    service_type = ServiceTypeSerializer()
    class Meta:
        model = Service
        fields = '__all__'

class ProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provider
        fields = '__all__'

class ZoneSerializer(serializers.ModelSerializer):
    services = ServiceSerializer(many=True)
    provider = ProviderSerializer()

    class Meta:
        model = Zone
        fields = '__all__'

    def validate(self, data):
        tmp_obj = Zone(**data)
        try:
            tmp_obj.clean()
        except ValidationError as e:
            raise serializers.ValidationError(e)
