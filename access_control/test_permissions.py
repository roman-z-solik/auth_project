from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView
from access_control.models import Role, Permission, RolePermission, UserRole
from access_control.permissions import HasPermission, HasAnyPermission, IsAdminOrSuperuser
from access_control.decorators import require_permission

User = get_user_model()


class PermissionsAdditionalTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(email='user@example.com', password='pass')
        self.role = Role.objects.create(name='Test Role')
        self.permission = Permission.objects.create(codename='test_perm')

        class DummyView(APIView):
            pass

        self.view = DummyView()

    def test_has_permission_object_permission(self):
        request = self.factory.get('/')
        request.user = self.user
        permission = HasPermission('test_perm')
        result = permission.has_object_permission(request, self.view, None)
        self.assertFalse(result)

    def test_has_any_permission_object_permission(self):
        request = self.factory.get('/')
        request.user = self.user
        permission = HasAnyPermission('test_perm')
        result = permission.has_object_permission(request, self.view, None)
        self.assertFalse(result)

    def test_is_admin_or_superuser_object_permission(self):
        request = self.factory.get('/')
        request.user = self.user
        permission = IsAdminOrSuperuser()
        result = permission.has_object_permission(request, self.view, None)
        self.assertFalse(result)

    def test_require_permission_decorator(self):
        @require_permission('test_perm')
        def dummy_view():
            return True
        self.assertTrue(hasattr(dummy_view, '__wrapped__'))
