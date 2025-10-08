from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User
from locations.models import Location
from .models import Order, CargoType


class CargoRequestViewSetTests(APITestCase):
    def setUp(self):
        self.password = 'StrongPass123!'
        self.sender = User.objects.create_user(
            username='+70000000001',
            phone_number='+70000000001',
            password=self.password,
            role=User.Role.SENDER,
            email='sender@example.com'
        )
        self.driver = User.objects.create_user(
            username='+70000000002',
            phone_number='+70000000002',
            password=self.password,
            role=User.Role.DRIVER,
            email='driver@example.com'
        )
        self.admin = User.objects.create_user(
            username='+70000000003',
            phone_number='+70000000003',
            password=self.password,
            role=User.Role.ADMIN,
            email='admin@example.com',
            is_staff=True,
            is_superuser=True
        )
        self.cargo_type = CargoType.objects.create(name='Документы', description='Небольшие посылки')
        self.departure = Location.objects.create(city_name='Алматы')
        self.destination = Location.objects.create(city_name='Астана')
        self.list_url = reverse('cargo:cargo-request-list')

    def _create_order(self, sender=None, **kwargs):
        defaults = dict(
            sender=sender or self.sender,
            departure_point=self.departure,
            destination_point=self.destination,
            cargo_type=self.cargo_type,
            weight=100,
            description='Грузы'
        )
        defaults.update(kwargs)
        return Order.objects.create(**defaults)

    def test_sender_can_create_order(self):
        self.client.force_authenticate(self.sender)
        payload = {
            'departure_point': self.departure.id,
            'destination_point': self.destination.id,
            'cargo_type': self.cargo_type.id,
            'weight': 150,
            'description': 'Посылка',
        }
        response = self.client.post(self.list_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        order = Order.objects.get()
        self.assertEqual(order.sender, self.sender)
        self.assertEqual(order.weight, 150)

    def test_sender_sees_only_own_orders(self):
        own_order = self._create_order(sender=self.sender)
        other_sender = User.objects.create_user(
            username='+70000000004',
            phone_number='+70000000004',
            password=self.password,
            role=User.Role.SENDER,
            email='another@example.com'
        )
        other_order = self._create_order(sender=other_sender)

        self.client.force_authenticate(self.sender)
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [item['id'] for item in response.data['results']]
        self.assertIn(own_order.id, ids)
        self.assertNotIn(other_order.id, ids)

    def test_driver_sees_assigned_orders(self):
        assigned_order = self._create_order(sender=self.sender, driver=self.driver)
        self._create_order(sender=self.sender)  # не назначено водителю

        self.client.force_authenticate(self.driver)
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['id'], assigned_order.id)

    def test_admin_sees_all_orders(self):
        first = self._create_order(sender=self.sender)
        second_sender = User.objects.create_user(
            username='+70000000005',
            phone_number='+70000000005',
            password=self.password,
            role=User.Role.SENDER,
            email='second@example.com'
        )
        second = self._create_order(sender=second_sender)

        self.client.force_authenticate(self.admin)
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = sorted(item['id'] for item in response.data['results'])
        self.assertEqual(ids, sorted([first.id, second.id]))

    def test_sender_can_update_own_order(self):
        order = self._create_order(sender=self.sender)
        url = reverse('cargo:cargo-request-detail', args=[order.id])
        self.client.force_authenticate(self.sender)
        response = self.client.patch(url, {'description': 'Обновлено'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertEqual(order.description, 'Обновлено')

    def test_sender_cannot_update_other_order(self):
        other_sender = User.objects.create_user(
            username='+70000000006',
            phone_number='+70000000006',
            password=self.password,
            role=User.Role.SENDER,
            email='cantedit@example.com'
        )
        order = self._create_order(sender=other_sender)
        url = reverse('cargo:cargo-request-detail', args=[order.id])

        self.client.force_authenticate(self.sender)
        response = self.client.patch(url, {'description': 'Попытка'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_driver_can_mark_order_delivered(self):
        order = self._create_order(sender=self.sender, driver=self.driver, status=Order.Status.IN_PROGRESS)
        url = reverse('cargo:cargo-request-detail', args=[order.id])

        self.client.force_authenticate(self.driver)
        response = self.client.patch(
            url,
            {
                'status': Order.Status.DELIVERED,
                'delivered_at': timezone.now().isoformat()
            },
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertEqual(order.status, Order.Status.DELIVERED)

    def test_driver_cannot_create_order(self):
        self.client.force_authenticate(self.driver)
        payload = {
            'departure_point': self.departure.id,
            'destination_point': self.destination.id,
            'weight': 50,
        }
        response = self.client.post(self.list_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
