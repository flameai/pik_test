from rest_framework import serializers
from main.models import *
from django.core.exceptions import ValidationError


class ZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zone
        fields = '__all__'

    def validate(self, data):
        tmp_obj = Zone(**data)
        try:
            tmp_obj.clean()
        except ValidationError as e:
            raise serializers.ValidationError(e)
