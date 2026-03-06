from django.urls import path
from . import mock_views

urlpatterns = [
    path('documents/', mock_views.get_documents, name='documents-list'),
    path('documents/create/', mock_views.create_document, name='document-create'),
    path('documents/<int:doc_id>/update/', mock_views.update_document, name='document-update'),
    path('documents/<int:doc_id>/delete/', mock_views.delete_document, name='document-delete'),
    path('projects/', mock_views.get_projects, name='projects-list'),
    path('users/', mock_views.get_users_list, name='users-list'),
    path('assign-role/', mock_views.assign_role, name='assign-role'),
    path('check-permissions/', mock_views.check_permissions, name='check-permissions'),
]
