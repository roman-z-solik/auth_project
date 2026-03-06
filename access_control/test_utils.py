from django.test import TestCase
from django.contrib.auth import get_user_model
from access_control.models import Role, Permission, RolePermission, UserRole
from access_control.utils import get_user_permissions, has_permission

User = get_user_model()


class UtilsTests(TestCase):
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
        self.permission1 = Permission.objects.create(codename='test_perm1')
        self.permission2 = Permission.objects.create(codename='test_perm2')

        RolePermission.objects.create(role=self.role, permission=self.permission1)
        RolePermission.objects.create(role=self.role, permission=self.permission2)

    def test_get_user_permissions_for_superuser(self):
        permissions = get_user_permissions(self.superuser)
        self.assertEqual(permissions, ['*'])

    def test_get_user_permissions_for_user_without_roles(self):
        permissions = get_user_permissions(self.user)
        self.assertEqual(permissions, [])

    def test_get_user_permissions_for_user_with_roles(self):
        UserRole.objects.create(user=self.user, role=self.role)
        permissions = get_user_permissions(self.user)
        self.assertIn('test_perm1', permissions)
        self.assertIn('test_perm2', permissions)
        self.assertEqual(len(permissions), 2)

    def test_get_user_permissions_for_unauthenticated_user(self):
        anonymous = type('Anonymous', (), {'is_authenticated': False, 'is_active': True, 'is_superuser': False})()
        permissions = get_user_permissions(anonymous)
        self.assertEqual(permissions, [])

    def test_get_user_permissions_for_inactive_user(self):
        self.user.is_active = False
        permissions = get_user_permissions(self.user)
        self.assertEqual(permissions, [])

    def test_has_permission_for_superuser(self):
        result = has_permission(self.superuser, 'any_permission')
        self.assertTrue(result)

    def test_has_permission_for_user_without_role(self):
        result = has_permission(self.user, 'test_perm1')
        self.assertFalse(result)

    def test_has_permission_for_user_with_role_but_wrong_permission(self):
        UserRole.objects.create(user=self.user, role=self.role)
        result = has_permission(self.user, 'nonexistent_perm')
        self.assertFalse(result)

    def test_has_permission_for_user_with_role_and_correct_permission(self):
        UserRole.objects.create(user=self.user, role=self.role)
        result = has_permission(self.user, 'test_perm1')
        self.assertTrue(result)

    def test_has_permission_for_inactive_user(self):
        UserRole.objects.create(user=self.user, role=self.role)
        self.user.is_active = False
        result = has_permission(self.user, 'test_perm1')
        self.assertFalse(result)

    def test_has_permission_for_unauthenticated(self):
        anonymous = type('Anonymous', (), {'is_authenticated': False, 'is_active': True, 'is_superuser': False})()
        result = has_permission(anonymous, 'test_perm1')
        self.assertFalse(result)


class PermissionClassesTests(TestCase):
    def setUp(self):
        from access_control.permissions import HasPermission, HasAnyPermission, IsAdminOrSuperuser
        from rest_framework.test import APIRequestFactory
        from rest_framework.views import APIView

        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(email='user@example.com', password='pass')
        self.superuser = User.objects.create_superuser(email='admin@example.com', password='pass')

        self.role = Role.objects.create(name='Test Role')
        self.permission = Permission.objects.create(codename='test_perm')
        RolePermission.objects.create(role=self.role, permission=self.permission)

        class DummyView(APIView):
            pass

        self.view = DummyView()

    def test_has_permission_class_with_correct_permission(self):
        from access_control.permissions import HasPermission

        UserRole.objects.create(user=self.user, role=self.role)
        request = self.factory.get('/')
        request.user = self.user

        permission = HasPermission('test_perm')
        result = permission.has_permission(request, self.view)
        self.assertTrue(result)

    def test_has_permission_class_without_permission(self):
        from access_control.permissions import HasPermission

        request = self.factory.get('/')
        request.user = self.user

        permission = HasPermission('test_perm')
        result = permission.has_permission(request, self.view)
        self.assertFalse(result)

    def test_has_permission_class_unauthenticated(self):
        from access_control.permissions import HasPermission

        request = self.factory.get('/')
        request.user = type('Anonymous', (), {'is_authenticated': False, 'is_active': True})()

        permission = HasPermission('test_perm')
        result = permission.has_permission(request, self.view)
        self.assertFalse(result)

    def test_has_any_permission_class_with_one_correct(self):
        from access_control.permissions import HasAnyPermission

        UserRole.objects.create(user=self.user, role=self.role)
        request = self.factory.get('/')
        request.user = self.user

        permission = HasAnyPermission('wrong_perm', 'test_perm', 'another_wrong')
        result = permission.has_permission(request, self.view)
        self.assertTrue(result)

    def test_has_any_permission_class_with_none_correct(self):
        from access_control.permissions import HasAnyPermission

        request = self.factory.get('/')
        request.user = self.user

        permission = HasAnyPermission('wrong_perm1', 'wrong_perm2')
        result = permission.has_permission(request, self.view)
        self.assertFalse(result)

    def test_is_admin_or_superuser_with_superuser(self):
        from access_control.permissions import IsAdminOrSuperuser

        request = self.factory.get('/')
        request.user = self.superuser

        permission = IsAdminOrSuperuser()
        result = permission.has_permission(request, self.view)
        self.assertTrue(result)

    def test_is_admin_or_superuser_with_admin_permission(self):
        from access_control.permissions import IsAdminOrSuperuser

        admin_perm = Permission.objects.create(codename='admin_access')
        admin_role = Role.objects.create(name='Admin Role')
        RolePermission.objects.create(role=admin_role, permission=admin_perm)
        UserRole.objects.create(user=self.user, role=admin_role)

        request = self.factory.get('/')
        request.user = self.user

        permission = IsAdminOrSuperuser()
        result = permission.has_permission(request, self.view)
        self.assertTrue(result)

    def test_is_admin_or_superuser_without_rights(self):
        from access_control.permissions import IsAdminOrSuperuser

        request = self.factory.get('/')
        request.user = self.user

        permission = IsAdminOrSuperuser()
        result = permission.has_permission(request, self.view)
        self.assertFalse(result)
