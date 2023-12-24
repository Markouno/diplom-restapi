from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from mtv.models import Category, Shop, User
import json


class CategoryViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('category-list')
        self.category1 = Category.objects.create(name='Category 1')
        self.category2 = Category.objects.create(name='Category 2')

    def test_get_categories(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = json.loads(response.content)
        self.assertEqual(len(response_data), 2)
        self.assertEqual(response_data[0]['name'], 'Category 1')
        self.assertEqual(response_data[1]['name'], 'Category 2')


class RegisterAccountTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('register-account')
        self.valid_payload = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'password': 'password123'
        }
        self.invalid_payload = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com'
        }

    def test_register_account_with_valid_payload(self):
        response = self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_register_account_with_invalid_payload(self):
        response = self.client.post(self.url, self.invalid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(response_data['Status'], False)
        self.assertIn('Не указаны все необходимые аргументы', response_data['Errors'])


