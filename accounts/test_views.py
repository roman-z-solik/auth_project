from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()


class AuthViewsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.profile_url = reverse('profile')
        self.update_profile_url = reverse('update-profile')
        self.delete_account_url = reverse('delete-account')

        self.user_data = {
            'email': 'test@example.com',
            'first_name': 'Тест',
            'last_name': 'Тестов',
            'patronymic': 'Тестович',
            'password': 'TestPass123',
            'password2': 'TestPass123'
        }

    def test_register_success(self):
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['email'], 'test@example.com')
        self.assertTrue(User.objects.filter(email='test@example.com').exists())

    def test_register_password_mismatch(self):
        data = self.user_data.copy()
        data['password2'] = 'DifferentPass'
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('non_field_errors', response.data)

    def test_register_duplicate_email(self):
        self.client.post(self.register_url, self.user_data, format='json')
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_login_success(self):
        self.client.post(self.register_url, self.user_data, format='json')
        login_data = {
            'email': 'test@example.com',
            'password': 'TestPass123'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('user', response.data)

    def test_login_invalid_password(self):
        self.client.post(self.register_url, self.user_data, format='json')
        login_data = {
            'email': 'test@example.com',
            'password': 'WrongPass'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_login_inactive_user(self):
        self.client.post(self.register_url, self.user_data, format='json')
        user = User.objects.get(email='test@example.com')
        user.is_active = False
        user.save()
        login_data = {
            'email': 'test@example.com',
            'password': 'TestPass123'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_logout_authenticated(self):
        self.client.post(self.register_url, self.user_data, format='json')
        login_data = {
            'email': 'test@example.com',
            'password': 'TestPass123'
        }
        self.client.post(self.login_url, login_data, format='json')
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, 200)

    def test_logout_unauthenticated(self):
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, 403)

    def test_profile_authenticated(self):
        self.client.post(self.register_url, self.user_data, format='json')
        login_data = {
            'email': 'test@example.com',
            'password': 'TestPass123'
        }
        self.client.post(self.login_url, login_data, format='json')
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['email'], 'test@example.com')

    def test_profile_unauthenticated(self):
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 403)

    def test_update_profile_authenticated(self):
        self.client.post(self.register_url, self.user_data, format='json')
        login_data = {
            'email': 'test@example.com',
            'password': 'TestPass123'
        }
        self.client.post(self.login_url, login_data, format='json')

        update_data = {
            'first_name': 'Обновлен',
            'last_name': 'Пользователь'
        }
        response = self.client.put(self.update_profile_url, update_data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['first_name'], 'Обновлен')

    def test_delete_account_authenticated(self):
        self.client.post(self.register_url, self.user_data, format='json')
        login_data = {
            'email': 'test@example.com',
            'password': 'TestPass123'
        }
        self.client.post(self.login_url, login_data, format='json')

        response = self.client.delete(self.delete_account_url)
        self.assertEqual(response.status_code, 200)

        user = User.objects.get(email='test@example.com')
        self.assertFalse(user.is_active)

        logout_check = self.client.get(self.profile_url)
        self.assertEqual(logout_check.status_code, 403)


class AuthViewsAdditionalTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.profile_url = reverse('profile')

        self.user_data = {
            'email': 'test@example.com',
            'first_name': 'Тест',
            'last_name': 'Тестов',
            'password': 'TestPass123',
            'password2': 'TestPass123'
        }

    def test_register_with_invalid_email(self):
        data = self.user_data.copy()
        data['email'] = 'not-an-email'
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('email', response.data)

    def test_register_with_short_password(self):
        data = self.user_data.copy()
        data['password'] = 'short'
        data['password2'] = 'short'
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('password', response.data)

    def test_login_with_nonexistent_email(self):
        login_data = {
            'email': 'nonexistent@example.com',
            'password': 'TestPass123'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_profile_without_auth(self):
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 403)

    def test_update_profile_without_auth(self):
        response = self.client.put(self.profile_url, {}, format='json')
        self.assertEqual(response.status_code, 403)

    def test_delete_account_without_auth(self):
        response = self.client.delete(reverse('delete-account'))
        self.assertEqual(response.status_code, 403)
    