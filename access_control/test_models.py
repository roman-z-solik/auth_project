from django.test import TestCase
from django.contrib.auth import get_user_model
from access_control.models import Role, Permission, RolePermission, UserRole
from django.db import IntegrityError

User = get_user_model()


class RoleModelTests(TestCase):
    def setUp(self):
        self.role = Role.objects.create(
            name='Test Role',
            description='Test Description'
        )

    def test_role_creation(self):
        self.assertEqual(self.role.name, 'Test Role')
        self.assertEqual(self.role.description, 'Test Description')
        self.assertIsNotNone(self.role.created_at)
        self.assertIsNotNone(self.role.updated_at)

    def test_role_str_method(self):
        self.assertEqual(str(self.role), 'Test Role')

    def test_role_unique_name(self):
        with self.assertRaises(IntegrityError):
            Role.objects.create(name='Test Role')

    def test_role_verbose_names(self):
        self.assertEqual(Role._meta.verbose_name, 'Роль')
        self.assertEqual(Role._meta.verbose_name_plural, 'Роли')


class PermissionModelTests(TestCase):
    def setUp(self):
        self.permission = Permission.objects.create(
            codename='test_permission',
            description='Test Permission Description'
        )

    def test_permission_creation(self):
        self.assertEqual(self.permission.codename, 'test_permission')
        self.assertEqual(self.permission.description, 'Test Permission Description')
        self.assertIsNotNone(self.permission.created_at)
        self.assertIsNotNone(self.permission.updated_at)

    def test_permission_str_method(self):
        self.assertEqual(str(self.permission), 'test_permission')

    def test_permission_unique_codename(self):
        with self.assertRaises(IntegrityError):
            Permission.objects.create(codename='test_permission')

    def test_permission_verbose_names(self):
        self.assertEqual(Permission._meta.verbose_name, 'Разрешение')
        self.assertEqual(Permission._meta.verbose_name_plural, 'Разрешения')


class RolePermissionModelTests(TestCase):
    def setUp(self):
        self.role = Role.objects.create(name='Test Role')
        self.permission = Permission.objects.create(codename='test_perm')
        self.role_permission = RolePermission.objects.create(
            role=self.role,
            permission=self.permission
        )

    def test_role_permission_creation(self):
        self.assertEqual(self.role_permission.role, self.role)
        self.assertEqual(self.role_permission.permission, self.permission)
        self.assertIsNotNone(self.role_permission.created_at)

    def test_role_permission_str_method(self):
        expected = f'{self.role.name} - {self.permission.codename}'
        self.assertEqual(str(self.role_permission), expected)

    def test_role_permission_unique_together(self):
        with self.assertRaises(IntegrityError):
            RolePermission.objects.create(
                role=self.role,
                permission=self.permission
            )

    def test_role_permission_cascade_delete_role(self):
        permission_id = self.permission.id
        self.role.delete()
        self.assertTrue(Permission.objects.filter(id=permission_id).exists())
        self.assertEqual(RolePermission.objects.count(), 0)

    def test_role_permission_cascade_delete_permission(self):
        role_id = self.role.id
        self.permission.delete()
        self.assertTrue(Role.objects.filter(id=role_id).exists())
        self.assertEqual(RolePermission.objects.count(), 0)

    def test_role_permission_verbose_names(self):
        self.assertEqual(RolePermission._meta.verbose_name, 'Разрешение роли')
        self.assertEqual(RolePermission._meta.verbose_name_plural, 'Разрешения ролей')


class UserRoleModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.role = Role.objects.create(name='Test Role')
        self.user_role = UserRole.objects.create(
            user=self.user,
            role=self.role
        )

    def test_user_role_creation(self):
        self.assertEqual(self.user_role.user, self.user)
        self.assertEqual(self.user_role.role, self.role)
        self.assertIsNotNone(self.user_role.created_at)

    def test_user_role_str_method(self):
        expected = f'{self.user.email} - {self.role.name}'
        self.assertEqual(str(self.user_role), expected)

    def test_user_role_unique_together(self):
        with self.assertRaises(IntegrityError):
            UserRole.objects.create(
                user=self.user,
                role=self.role
            )

    def test_user_role_cascade_delete_user(self):
        role_id = self.role.id
        self.user.delete()
        self.assertTrue(Role.objects.filter(id=role_id).exists())
        self.assertEqual(UserRole.objects.count(), 0)

    def test_user_role_cascade_delete_role(self):
        user_id = self.user.id
        self.role.delete()
        self.assertTrue(User.objects.filter(id=user_id).exists())
        self.assertEqual(UserRole.objects.count(), 0)

    def test_user_role_verbose_names(self):
        self.assertEqual(UserRole._meta.verbose_name, 'Роль пользователя')
        self.assertEqual(UserRole._meta.verbose_name_plural, 'Роли пользователей')

    def test_user_can_have_multiple_roles(self):
        role2 = Role.objects.create(name='Second Role')
        user_role2 = UserRole.objects.create(user=self.user, role=role2)
        self.assertEqual(self.user.user_roles.count(), 2)
        self.assertIn(self.user_role, self.user.user_roles.all())
        self.assertIn(user_role2, self.user.user_roles.all())
