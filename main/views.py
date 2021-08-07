from rest_framework.viewsets import ModelViewSet
from main.models import WorldBorder
from main.serializers import WorldBorderSerializer

# Create your views here.

class WorldBorderViewSet(ModelViewSet):
    serializer_class = WorldBorderSerializer
    queryset = WorldBorder.objects.all()