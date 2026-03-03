from rest_framework.permissions import BasePermission
from .utils import has_permission, get_user_permissions


class HasPermission(BasePermission):
    def __init__(self, permission_codename):
        self.permission_codename = permission_codename

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if not request.user.is_active:
            return False

        return has_permission(request.user, self.permission_codename)

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class HasAnyPermission(BasePermission):
    def __init__(self, *permission_codenames):
        self.permission_codenames = permission_codenames

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if not request.user.is_active:
            return False

        for permission in self.permission_codenames:
            if has_permission(request.user, permission):
                return True

        return False

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsAdminOrSuperuser(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if not request.user.is_active:
            return False

        return request.user.is_superuser or has_permission(request.user, 'admin_access')

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)
    