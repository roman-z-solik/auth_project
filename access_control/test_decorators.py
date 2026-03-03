from django.test import TestCase
from django.contrib.auth import get_user_model
from django.http import HttpRequest
from rest_framework.response import Response
from unittest.mock import Mock, patch
from access_control.decorators import require_permission
from access_control.models import Role, Permission, RolePermission, UserRole

User = get_user_model()


class RequirePermissionDecoratorTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.superuser = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123'
        )

        self.role = Role.objects.create(name='Test Role')
        self.permission = Permission.objects.create(codename='test_perm')
        RolePermission.objects.create(role=self.role, permission=self.permission)

        self.mock_view = Mock(return_value=Response({'success': True}))
        self.request = HttpRequest()

    def test_decorator_with_superuser(self):
        self.request.user = self.superuser
        decorated_view = require_permission('any_perm')(self.mock_view)
        response = decorated_view(self.request)
        self.assertEqual(response.data['success'], True)
        self.mock_view.assert_called_once_with(self.request)

    def test_decorator_with_user_having_permission(self):
        UserRole.objects.create(user=self.user, role=self.role)
        self.request.user = self.user
        decorated_view = require_permission('test_perm')(self.mock_view)
        response = decorated_view(self.request)
        self.assertEqual(response.data['success'], True)
        self.mock_view.assert_called_once_with(self.request)

    def test_decorator_with_user_not_having_permission(self):
        self.request.user = self.user
        decorated_view = require_permission('test_perm')(self.mock_view)
        response = decorated_view(self.request)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data['error'], 'You do not have permission to perform this action')
        self.mock_view.assert_not_called()

    def test_decorator_with_unauthenticated_user(self):
        self.request.user = type('Anonymous', (), {
            'is_authenticated': False,
            'is_active': True
        })()
        decorated_view = require_permission('test_perm')(self.mock_view)
        response = decorated_view(self.request)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['error'], 'Authentication required')
        self.mock_view.assert_not_called()

    def test_decorator_with_inactive_user(self):
        self.user.is_active = False
        self.user.save()
        self.request.user = self.user
        decorated_view = require_permission('test_perm')(self.mock_view)
        response = decorated_view(self.request)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['error'], 'Account is deactivated')
        self.mock_view.assert_not_called()

    def test_decorator_preserves_function_name(self):
        @require_permission('test_perm')
        def test_function():
            pass

        self.assertEqual(test_function.__name__, 'test_function')
