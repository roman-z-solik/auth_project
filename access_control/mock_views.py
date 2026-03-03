from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .permissions import HasPermission, IsAdminOrSuperuser
from .decorators import require_permission

# Mock данные для демонстрации
MOCK_DOCUMENTS = [
    {'id': 1, 'title': 'Договор поставки №1', 'type': 'contract', 'created_by': 'user1@example.com'},
    {'id': 2, 'title': 'Счет-фактура №45', 'type': 'invoice', 'created_by': 'user2@example.com'},
    {'id': 3, 'title': 'Отчет за январь', 'type': 'report', 'created_by': 'user1@example.com'},
]

MOCK_PROJECTS = [
    {'id': 1, 'name': 'Разработка API', 'status': 'active', 'budget': 100000},
    {'id': 2, 'name': 'Внедрение CRM', 'status': 'completed', 'budget': 50000},
    {'id': 3, 'name': 'Миграция данных', 'status': 'pending', 'budget': 75000},
]


@api_view(['GET'])
@permission_classes([IsAuthenticated, HasPermission('document_view')])
def get_documents(request):
    return Response({
        'documents': MOCK_DOCUMENTS,
        'user_permissions': get_user_permissions(request.user)
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated, HasPermission('document_create')])
def create_document(request):
    return Response({
        'message': 'Document created successfully',
        'document': {'id': 4, 'title': 'New Document', 'type': 'draft'}
    }, status=status.HTTP_201_CREATED)


@api_view(['PUT'])
@permission_classes([IsAuthenticated, HasPermission('document_update')])
def update_document(request, doc_id):
    return Response({
        'message': f'Document {doc_id} updated successfully'
    })


@api_view(['DELETE'])
@permission_classes([IsAuthenticated, HasPermission('document_delete')])
def delete_document(request, doc_id):
    return Response({
        'message': f'Document {doc_id} deleted successfully'
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@require_permission('project_view')
def get_projects(request):
    return Response({
        'projects': MOCK_PROJECTS
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, HasPermission('user_view')])
def get_users_list(request):
    from accounts.models import CustomUser
    users = CustomUser.objects.filter(is_active=True).values('id', 'email', 'first_name', 'last_name')
    return Response({'users': list(users)})


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminOrSuperuser])
def assign_role(request):
    return Response({
        'message': 'Role assigned successfully'
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_permissions(request):
    user = request.user
    permissions = get_user_permissions(user)

    return Response({
        'user': user.email,
        'is_superuser': user.is_superuser,
        'is_active': user.is_active,
        'permissions': permissions
    })
