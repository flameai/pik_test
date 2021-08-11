from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.mixins import CreateModelMixin, UpdateModelMixin, DestroyModelMixin
from rest_framework.decorators import action
from rest_framework.permissions import BasePermission, AllowAny, IsAuthenticated
from main.models import Provider, Zone, Service
from main.serializers import ZoneSerializerRead, ZoneSerializerWrite, ProviderSerializer, ServiceSerializerRead, ServiceSerializerWrite
from django_filters import rest_framework as filters
from django.contrib.gis.geos import Point
from django.utils.translation import gettext_lazy as _



class IsManagerForNew(BasePermission):
    """
    Пользователь является менеджером поставщика для новой сущности
    (Зона, Услуга)
    """
    message = _("You dont have access for requested provider")
    def has_permission(self, request, view):
        model = view.queryset.model
        return model.can_create(request.user, request.data)

class IsObjectManager(BasePermission):
    """    
    Пользователь является менеджером поставщика сущности
    (Зона, Поставщик, Услуга)
    """
    message = _("You dont have access for this object")
    def has_object_permission(self, request, view, obj):        
        return obj.is_manager(request.user)

class CanUpdate(BasePermission):
    """
    Пользователь может делать изменения либо передвигать сущность.    
    """
    message = _("You can not update entity with new data")
    def has_object_permission(self, request, view, obj):
        return obj.can_update(request.user, request.data)

class ZoneViewSet(ModelViewSet):
    """
    Вьюсет для работы с зонами обслуживания. 
    Для получения всех зон с услугами и поставщиками для конкретной точки
    необходимо добавить в GET-запрос параметры:
    longitude - долгота в градусах
    latitude - широта в градусах
    Пример ...zones/point?longitude=62.012122323&latitude=58.021312413
    Если широта и долгота не указаны, то выведет зоны на северном полюсе
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
        action = self.action
        if action == 'destroy':
            permission_classes = [IsObjectManager,]
        elif action == 'create':
            permission_classes = [IsManagerForNew,]
        elif action in ['partial_update', 'update']:
            permission_classes = [CanUpdate,]        
        else:
            permission_classes = [IsAuthenticated,]
        return [permission() for permission in permission_classes]

    @action(methods=['get',], detail=False, permission_classes=[AllowAny,])
    def point(self, request, *args, **kwargs):
        """
        АПИ для получения всех зон, поставщиков и услуг, находящихся в запрашиваемой точке.
        Для получения необходимо добавить в GET-запрос параметры:
        longitude - долгота в градусах
        latitude - широта в градусах
        Пример ...zones/point?longitude=62.012122323&latitude=58.021312413
        Если широта и долгота не указаны, то выведет зоны на северном полюсе
        """
        longitude = float(request.GET.get('longitude', '0'))
        latitude = float(request.GET.get('latitude', '90'))
        print(longitude)
        point = Point(longitude, latitude)
        self.queryset = self.queryset.filter(mpoly__contains=point)
        return super().list(request, *args, **kwargs)


class ProviderViewSet(ModelViewSet):
    """
    Вьюсет для работы с поставщиками.
    При создании и обновлении поставщика полю manager автоматически присваивается пользователь
    Для пользователя отображаются только те поставщики, менеджером в которых он является
    """
    serializer_class = ProviderSerializer
    queryset = Provider.objects.all()

    def get_queryset(self):
        if self.action in ['list', 'retrieve']:
            self.queryset = self.queryset.filter(manager=self.request.user)
        return super().get_queryset()

    def get_permissions(self):
        action = self.action
        if action == 'create':
            permission_classes = [IsAuthenticated,]
        elif action in ['update', 'partial_update','destroy']:
            permission_classes = [IsObjectManager,]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_serializer(self, *args, **kwargs):        
        serializer = super().get_serializer(*args, **kwargs)
        # При создании поставщика пошлем пользователя в контекст сериалайзера
        if self.action == 'create':
            serializer.context['manager'] = self.request.user
        return serializer

class ServiceViewSet(ReadOnlyModelViewSet, DestroyModelMixin, CreateModelMixin, UpdateModelMixin):
    """
    Вьюсет для работы с Услугами. Возможно просмотреть, создать и удалить  услугу
    """
    serializer_class = ServiceSerializerRead
    queryset = Service.objects.all()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return ServiceSerializerRead
        else:
            return ServiceSerializerWrite

    def get_permissions(self):
        action = self.action
        if action == 'create':
            permission_classes = [IsManagerForNew,]
        elif action =='destroy':
            permission_classes = [IsObjectManager,]
        elif action in ['update', 'partial_update']:
            permission_classes = [CanUpdate,]
        else:
            permission_classes = [IsAuthenticated,]
        return [permission() for permission in permission_classes]
