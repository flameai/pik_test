from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import BasePermission, AllowAny, IsAuthenticated
from main.models import Zone
from main.serializers import ZoneSerializer
from django_filters import rest_framework as filters
from django.contrib.gis.geos import Point

class IsProviderManager(BasePermission):
    def has_permission(self, request, view):
        return view.get_object().provider.manager == request.user

class ZoneViewSet(ModelViewSet):
    serializer_class = ZoneSerializer
    queryset = Zone.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('services__service_type',)

    def get_permissions(self):
        if self.action in ['destroy', 'partial_update', 'update']:
            permission_classes = [IsProviderManager]
        elif self.action == 'list':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(methods=['get',], detail=False, permission_classes=[AllowAny,])
    def point(self, request, *args, **kwargs):
        longitude = float(request.GET.get('long', '0'))
        latitude = float(request.GET.get('lat', '0'))
        point = Point(longitude, latitude)
        self.queryset = self.queryset.filter(mpoly__contains=point)
        return super().list(request, *args, **kwargs)