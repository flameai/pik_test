from rest_framework import serializers
from main.models import *

class WorldBorderSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorldBorder
        fields = '__all__'

