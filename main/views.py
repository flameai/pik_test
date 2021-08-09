from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from main.models import Zone
from main.serializers import ZoneSerializer
from django_filters import rest_framework as filters
from django.contrib.gis.geos import Point

# Create your views here.

class ZoneViewSet(ModelViewSet):
    serializer_class = ZoneSerializer
    queryset = Zone.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('services__service_type',)

    # def get_queryset(self):
    #     return super().get_queryset().filter(provider__manager=self.request.user)

    @action(methods=['get',], detail=False)
    def point(self, request, *args, **kwargs):
        longitude = float(request.GET.get('long', '0'))
        latitude = float(request.GET.get('lat', '0'))
        point = Point(longitude, latitude)
        self.queryset = self.queryset.filter(mpoly__contains=point)
        return super().list(request, *args, **kwargs)