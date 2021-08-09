from rest_framework.viewsets import ModelViewSet
from main.models import Zone
from main.serializers import ZoneSerializer
from django_filters import rest_framework as filters

# Create your views here.

class ZoneViewSet(ModelViewSet):
    serializer_class = ZoneSerializer
    queryset = Zone.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    # filterset_fields = ('category', 'in_stock')
    def get_queryset(self):
        return super().get_queryset().filter(provider__manager=self.request.user)