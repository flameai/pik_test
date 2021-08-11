from django.test import TestCase
from main.models import *
from django.contrib.auth.models import User
from main.views import ProviderViewSet

from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate
from main import serializers


# Create your tests here.

class CreateProvider(TestCase):
    def setUp(self):
        self.vasya = User.objects.create(username='vasya', email='vasya@mail.com', password='password')
        self.petya = User.objects.create(username='petya', email='petya@mail.com', password='password')

    def test_users_can_create_only_own_provider(self):
        """Пользователь может сделать поставщика и автоматически стать там менеджером"""        
        factory = APIRequestFactory()
        view = ProviderViewSet.as_view({'post':'create'})
        data = {'name': 'Васин новый поставщик', 'email': self.vasya.email, 'address':'Ленина 129', 'phone': '323233422'}
        request = factory.post('/providers/', data, format='json')
        force_authenticate(request, user=self.vasya)
        response = view(request)        
        self.assertEqual(response.status_code, 201)
        vasya_provider = Provider.objects.get(pk=1)
        self.assertEqual(vasya_provider.manager, self.vasya)        
    
    def test_users_can_update_provider_through_serializer(self):
        """Пользователь может изменить поля поставщика через сериалайзер"""        
        factory = APIRequestFactory()
        # Создадим поставщика
        view = ProviderViewSet.as_view({'post':'create'})
        data = {'name': 'Васин новый поставщик', 'email': self.vasya.email, 'address':'Ленина 129', 'phone': '323233422'}
        request = factory.post('/providers/', data, format='json')
        force_authenticate(request, user=self.vasya)
        view(request)
        # Изменим поставщика
        view = ProviderViewSet.as_view({'patch':'partial_update'})
        new_data = {'name': '(Обновлено) Васин новый поставщик', 'email': 'new_valid@email.com', 'address':'(Обновлено)Ленина 129', 'phone': '123'}
        request = factory.patch('/providers/1/', new_data, format='json')
        force_authenticate(request, user=self.vasya)
        provider = Provider.objects.get(pk=2)
        serializer = serializers.ProviderSerializer(
            provider, data=new_data)        
        self.assertEqual(serializer.is_valid(), True)