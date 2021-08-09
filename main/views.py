from rest_framework.viewsets import ModelViewSet
from main.models import Zone
from main.serializers import ZoneSerializer

# Create your views here.

class ZoneViewSet(ModelViewSet):
    serializer_class = ZoneSerializer
    queryset = Zone.objects.all()
    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)