from rest_framework import serializers
from main.models import Partner, Zone, Service, ServiceType
from django.core.exceptions import ValidationError


class ServiceTypeSerializer(serializer.ModelSerializer):
    class Meta:
        models = ServiceType
        fields = '__all__'

class ServiceSerializer(serializers.ModelSerializer):
    service_type = ServiceTypeSerializer(many=True)
    class Meta:
        model = Service
        fields = '__all__'

class PartnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Partner
        fields = '__all__'

class ZoneSerializer(serializers.ModelSerializer):
    services = ServiceSerializer(many=True)
    partner = PartnerSerializer()

    class Meta:
        model = Zone
        fields = '__all__'

    def validate(self, data):
        tmp_obj = Zone(**data)
        try:
            tmp_obj.clean()
        except ValidationError as e:
            raise serializers.ValidationError(e)
