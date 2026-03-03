from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from access_control.models import Role, Permission, RolePermission, UserRole

User = get_user_model()


class MockViewsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.superuser = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123'
        )

        self.role = Role.objects.create(name='Test Role')
        self.doc_view_perm = Permission.objects.create(codename='document_view')
        self.doc_create_perm = Permission.objects.create(codename='document_create')
        self.doc_update_perm = Permission.objects.create(codename='document_update')
        self.doc_delete_perm = Permission.objects.create(codename='document_delete')
        self.project_view_perm = Permission.objects.create(codename='project_view')
        self.user_view_perm = Permission.objects.create(codename='user_view')

        self.documents_url = reverse('documents-list')
        self.document_create_url = reverse('document-create')
        self.projects_url = reverse('projects-list')
        self.users_list_url = reverse('users-list')
        self.check_permissions_url = reverse('check-permissions')
        self.assign_role_url = reverse('assign-role')

    def test_documents_list_without_permission(self):
        self.client.force_login(self.user)
        response = self.client.get(self.documents_url)
        self.assertEqual(response.status_code, 403)

    def test_documents_list_with_permission(self):
        RolePermission.objects.create(role=self.role, permission=self.doc_view_perm)
        UserRole.objects.create(user=self.user, role=self.role)
        self.client.force_login(self.user)
        response = self.client.get(self.documents_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('documents', response.data)
        self.assertEqual(len(response.data['documents']), 3)

    def test_documents_list_unauthenticated(self):
        response = self.client.get(self.documents_url)
        self.assertEqual(response.status_code, 403)

    def test_document_create_without_permission(self):
        self.client.force_login(self.user)
        response = self.client.post(self.document_create_url)
        self.assertEqual(response.status_code, 403)

    def test_document_create_with_permission(self):
        RolePermission.objects.create(role=self.role, permission=self.doc_create_perm)
        UserRole.objects.create(user=self.user, role=self.role)
        self.client.force_login(self.user)
        response = self.client.post(self.document_create_url)
        self.assertEqual(response.status_code, 201)
        self.assertIn('message', response.data)

    def test_projects_list_without_permission(self):
        self.client.force_login(self.user)
        response = self.client.get(self.projects_url)
        self.assertEqual(response.status_code, 403)

    def test_projects_list_with_permission(self):
        RolePermission.objects.create(role=self.role, permission=self.project_view_perm)
        UserRole.objects.create(user=self.user, role=self.role)
        self.client.force_login(self.user)
        response = self.client.get(self.projects_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('projects', response.data)
        self.assertEqual(len(response.data['projects']), 3)

    def test_users_list_without_permission(self):
        self.client.force_login(self.user)
        response = self.client.get(self.users_list_url)
        self.assertEqual(response.status_code, 403)

    def test_users_list_with_permission(self):
        RolePermission.objects.create(role=self.role, permission=self.user_view_perm)
        UserRole.objects.create(user=self.user, role=self.role)
        self.client.force_login(self.user)
        response = self.client.get(self.users_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('users', response.data)

    def test_check_permissions_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get(self.check_permissions_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('user', response.data)
        self.assertIn('permissions', response.data)
        self.assertEqual(response.data['user'], self.user.email)

    def test_check_permissions_unauthenticated(self):
        response = self.client.get(self.check_permissions_url)
        self.assertEqual(response.status_code, 403)

    def test_check_permissions_with_roles(self):
        RolePermission.objects.create(role=self.role, permission=self.doc_view_perm)
        RolePermission.objects.create(role=self.role, permission=self.user_view_perm)
        UserRole.objects.create(user=self.user, role=self.role)
        self.client.force_login(self.user)
        response = self.client.get(self.check_permissions_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('document_view', response.data['permissions'])
        self.assertIn('user_view', response.data['permissions'])

    def test_assign_role_as_superuser(self):
        self.client.force_login(self.superuser)
        response = self.client.post(self.assign_role_url)
        self.assertEqual(response.status_code, 200)

    def test_assign_role_as_regular_user(self):
        self.client.force_login(self.user)
        response = self.client.post(self.assign_role_url)
        self.assertEqual(response.status_code, 403)

    def test_assign_role_unauthenticated(self):
        response = self.client.post(self.assign_role_url)
        self.assertEqual(response.status_code, 403)
