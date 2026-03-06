from django.test import TestCase
from rest_framework.test import APIRequestFactory
from django.contrib.auth import get_user_model
from accounts.serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    UserUpdateSerializer
)

User = get_user_model()


class UserRegistrationSerializerTests(TestCase):
    def test_registration_serializer_valid_data(self):
        data = {
            'email': 'new@example.com',
            'first_name': 'Новый',
            'last_name': 'Пользователь',
            'patronymic': 'Тестович',
            'password': 'StrongPass123',
            'password2': 'StrongPass123'
        }
        serializer = UserRegistrationSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.email, 'new@example.com')
        self.assertEqual(user.first_name, 'Новый')

    def test_registration_serializer_passwords_mismatch(self):
        data = {
            'email': 'new@example.com',
            'first_name': 'Новый',
            'last_name': 'Пользователь',
            'password': 'StrongPass123',
            'password2': 'DifferentPass456'
        }
        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)

    def test_registration_serializer_password_too_short(self):
        data = {
            'email': 'new@example.com',
            'first_name': 'Новый',
            'last_name': 'Пользователь',
            'password': 'short',
            'password2': 'short'
        }
        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)

    def test_registration_serializer_missing_email(self):
        data = {
            'first_name': 'Новый',
            'last_name': 'Пользователь',
            'password': 'StrongPass123',
            'password2': 'StrongPass123'
        }
        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)


class UserLoginSerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='login@example.com',
            password='ValidPass123',
            first_name='Login',
            last_name='User'
        )
        self.factory = APIRequestFactory()
        self.request = self.factory.post('/api/auth/login/')

    def test_login_serializer_valid_credentials(self):
        data = {
            'email': 'login@example.com',
            'password': 'ValidPass123'
        }
        serializer = UserLoginSerializer(data=data, context={'request': self.request})
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['user'], self.user)

    def test_login_serializer_invalid_password(self):
        data = {
            'email': 'login@example.com',
            'password': 'WrongPass123'
        }
        serializer = UserLoginSerializer(data=data, context={'request': self.request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)

    def test_login_serializer_nonexistent_email(self):
        data = {
            'email': 'nonexistent@example.com',
            'password': 'ValidPass123'
        }
        serializer = UserLoginSerializer(data=data, context={'request': self.request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)

    def test_login_serializer_inactive_user(self):
        self.user.is_active = False
        self.user.save()
        data = {
            'email': 'login@example.com',
            'password': 'ValidPass123'
        }
        serializer = UserLoginSerializer(data=data, context={'request': self.request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)

    def test_login_serializer_missing_email(self):
        data = {'password': 'ValidPass123'}
        serializer = UserLoginSerializer(data=data, context={'request': self.request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)


class UserProfileSerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='profile@example.com',
            password='testpass123',
            first_name='Profile',
            last_name='User',
            patronymic='Тестович'
        )

    def test_profile_serializer_contains_correct_fields(self):
        serializer = UserProfileSerializer(self.user)
        data = serializer.data
        self.assertIn('id', data)
        self.assertIn('email', data)
        self.assertIn('first_name', data)
        self.assertIn('last_name', data)
        self.assertIn('patronymic', data)
        self.assertIn('is_active', data)
        self.assertIn('created_at', data)

    def test_profile_serializer_read_only_fields(self):
        serializer = UserProfileSerializer(self.user, data={'email': 'new@example.com'}, partial=True)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'profile@example.com')


class UserUpdateSerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='update@example.com',
            password='testpass123',
            first_name='Old',
            last_name='Name'
        )

    def test_update_serializer_updates_fields(self):
        data = {
            'first_name': 'New',
            'last_name': 'Updated',
            'patronymic': 'Patronymic'
        }
        serializer = UserUpdateSerializer(self.user, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_user = serializer.save()
        self.assertEqual(updated_user.first_name, 'New')
        self.assertEqual(updated_user.last_name, 'Updated')
        self.assertEqual(updated_user.patronymic, 'Patronymic')

    def test_update_serializer_cannot_update_email(self):
        data = {'email': 'hack@example.com'}
        serializer = UserUpdateSerializer(self.user, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'update@example.com')


class UserRegistrationSerializerAdditionalTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.request = self.factory.post('/api/auth/login/')
    def test_registration_serializer_without_first_name(self):
        data = {
            'email': 'new@example.com',
            'last_name': 'Пользователь',
            'password': 'StrongPass123',
            'password2': 'StrongPass123'
        }
        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('first_name', serializer.errors)

    def test_registration_serializer_without_last_name(self):
        data = {
            'email': 'new@example.com',
            'first_name': 'Новый',
            'password': 'StrongPass123',
            'password2': 'StrongPass123'
        }
        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('last_name', serializer.errors)

    def test_login_serializer_missing_password(self):
        data = {'email': 'login@example.com'}
        serializer = UserLoginSerializer(data=data, context={'request': self.request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)
