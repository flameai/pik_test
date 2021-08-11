from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import CreateModelMixin, UpdateModelMixin, DestroyModelMixin
from rest_framework.decorators import action
from rest_framework.permissions import BasePermission, AllowAny, IsAuthenticated
from main.models import Provider, Zone, Service
from main.serializers import ZoneSerializerRead, ZoneSerializerWrite, ProviderSerializer, ServiceSerializerRead, ServiceSerializerWrite
from django_filters import rest_framework as filters
from django.contrib.gis.geos import Point
from django.utils.translation import gettext_lazy as _

class SVIsProviderManager(BasePermission):
    """
    SV (Service View) Права для вью ServiceView
    Пользователь является менеджером для поставщика зоны услуги
    """
    def has_permission(self, request, view):
        return view.get_object().zone.provider.manager == request.user

class ZVIsProviderManager(BasePermission):
    """
    ZV (Zone View) Права для вью ZoneView
    Пользователь является менеджером для поставщика зоны
    """
    def has_permission(self, request, view):
        return view.get_object().provider.manager == request.user


class PVIsProviderManager(BasePermission):
    """
    PV (Provider View) Права для вью ProviderView
    Пользователь является менеджером поставщика
    """
    def has_permission(self, request, view):
        return view.get_object().manager == request.user


class UserHasAtLeastOneProvider(BaseException):
    """
    Пользователь является менеджером хотябы у одного поставщика
    """
    message = _('You should create your first provider before')
    def has_permission(self, request, view):
        return request.user.providers.exists()


class ZoneViewSet(ModelViewSet):
    """
    Вьюсет для работы с зонами обслуживания
    """
    serializer_class = ZoneSerializerRead
    queryset = Zone.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('services__service_type', 'provider', )

    def get_serializer_class(self):        
        if self.action in ['destroy', 'partial_update', 'update', 'create']:
            return ZoneSerializerWrite
        else:
            return ZoneSerializerRead

    def get_permissions(self):
        if self.action in ['destroy', 'partial_update', 'update']:
            permission_classes = [ZVIsProviderManager,]
        elif self.action == 'create':
            permission_classes = [UserHasAtLeastOneProvider,]
        else:
            permission_classes = [IsAuthenticated,]
        return [permission() for permission in permission_classes]

    @action(methods=['get',], detail=False, permission_classes=[AllowAny,])
    def point(self, request, *args, **kwargs):
        """
        АПИ для получения всех зон, поставщиков и услуг, находящихся в данной точке
        Для получения необходимо добавить в GET-запрос параметры:
        longitude - долгота в градусах
        latitude - широта в градусах
        Пример ...zones/point?longitude=62&latitude=58
        Если широта и долгота не указаны, то выведет зоны на северном полюсе
        """
        longitude = float(request.GET.get('longitude', '0'))
        latitude = float(request.GET.get('latitude', '90'))
        print(longitude)
        point = Point(longitude, latitude)
        self.queryset = self.queryset.filter(mpoly__contains=point)
        return super().list(request, *args, **kwargs)
    
    def get_serializer(self, *args, **kwargs):        
        serializer = super().get_serializer(*args, **kwargs)

        # При создании зоны пошлем пользователя в контекст сериалайзера для проверки 
        # является ли он менеджером поставщика для вновь создаваемой зоны
        
        if self.action == 'create':
            serializer.context['manager'] = self.request.user
        return serializer
    

class ProviderViewSet(GenericViewSet, CreateModelMixin, UpdateModelMixin, DestroyModelMixin):
    """
    Вьюсет для работы с поставщиками    
    """
    serializer_class = ProviderSerializer
    queryset = Provider.objects.all()

    def get_permissions(self):
        if self.action in ['create', ]:
            permission_classes = [IsAuthenticated,]
        elif self.action in ['update', 'partial_update','destroy']:
            permission_classes = [PVIsProviderManager,]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_serializer(self, *args, **kwargs):        
        serializer = super().get_serializer(*args, **kwargs)
        # При создании поставщика пошлем пользователя в контекст сериалайзера
        if self.action == 'create':
            serializer.context['manager'] = self.request.user
        return serializer

class ServiceViewSet(ModelViewSet):
    """
    Вьюсет для работы с Услугами
    """
    serializer_class = ServiceSerializerRead
    queryset = Service.objects.all()

    def get_permissions(self):
        pass