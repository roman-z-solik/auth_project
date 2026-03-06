from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()


class UserModelTests(TestCase):
    def test_create_user_successful(self):
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Иван',
            last_name='Иванов'
        )
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertEqual(user.first_name, 'Иван')
        self.assertEqual(user.last_name, 'Иванов')

    def test_create_user_without_email_raises_error(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email='', password='testpass123')

    def test_create_user_with_duplicate_email_raises_error(self):
        User.objects.create_user(
            email='duplicate@example.com',
            password='testpass123'
        )
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                email='duplicate@example.com',
                password='testpass123'
            )

    def test_create_superuser_successful(self):
        admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123',
            first_name='Admin',
            last_name='User'
        )
        self.assertTrue(admin_user.is_superuser)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_active)

    def test_create_superuser_without_is_staff_raises_error(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email='admin@example.com',
                password='adminpass123',
                is_staff=False
            )

    def test_user_str_method(self):
        user = User.objects.create_user(
            email='str@example.com',
            password='testpass123'
        )
        self.assertEqual(str(user), 'str@example.com')

    def test_get_full_name_with_patronymic(self):
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Иван',
            last_name='Иванов',
            patronymic='Иванович'
        )
        self.assertEqual(user.get_full_name(), 'Иванов Иван Иванович')

    def test_get_full_name_without_patronymic(self):
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Петр',
            last_name='Петров'
        )
        self.assertEqual(user.get_full_name(), 'Петров Петр')

    def test_user_can_be_deactivated(self):
        user = User.objects.create_user(
            email='active@example.com',
            password='testpass123'
        )
        self.assertTrue(user.is_active)
        user.is_active = False
        user.save()
        user.refresh_from_db()
        self.assertFalse(user.is_active)


class UserManagerTests(TestCase):
    def test_create_user_normalizes_email(self):
        email = 'test@EXAMPLE.com'
        user = User.objects.create_user(email, 'password')
        self.assertEqual(user.email, email.lower())
