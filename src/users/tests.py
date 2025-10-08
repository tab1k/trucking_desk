from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch
from rest_framework import status
from rest_framework.test import APIClient

from .models import User


class UserPermissionTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.password = 'StrongPass123!'
        self.regular_user = User.objects.create_user(
            username='+70000000001',
            password=self.password,
            email='regular@example.com',
            phone_number='+70000000001'
        )
        self.other_user = User.objects.create_user(
            username='+70000000002',
            password=self.password,
            email='other@example.com',
            phone_number='+70000000002'
        )
        self.admin_user = User.objects.create_user(
            username='+70000000003',
            password=self.password,
            email='admin@example.com',
            role=User.Role.ADMIN,
            phone_number='+70000000003'
        )
        self.admin_user.is_staff = True
        self.admin_user.is_superuser = True
        self.admin_user.save(update_fields=['is_staff', 'is_superuser'])

    def test_regular_user_cannot_list_users(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(reverse('users:user-list'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_list_users(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(reverse('users:user-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 3)

    def test_regular_user_can_retrieve_self(self):
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('users:user-detail', args=[self.regular_user.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.regular_user.pk)

    def test_regular_user_cannot_retrieve_other_user(self):
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('users:user-detail', args=[self.other_user.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_admin_can_retrieve_other_user(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('users:user-detail', args=[self.other_user.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.other_user.pk)


class UserModelTests(TestCase):
    def test_referral_code_regenerates_until_unique(self):
        existing = User.objects.create_user(
            username='+70000000010',
            password='StrongPass123!',
            email='existing@example.com',
            phone_number='+70000000010'
        )
        existing.referral_code = 'DUPLICAT'
        existing.save(update_fields=['referral_code'])

        with patch('users.models.get_random_string', side_effect=['duplicat', 'uniquecd']):
            new_user = User.objects.create_user(
                username='+70000000011',
                password='StrongPass123!',
                email='newuser@example.com',
                phone_number='+70000000011'
            )

        self.assertEqual(new_user.referral_code, 'UNIQUECD')
