from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from .utils import has_permission


def require_permission(permission_codename):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user or not request.user.is_authenticated:
                return Response(
                    {'error': 'Authentication required'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            if not request.user.is_active:
                return Response(
                    {'error': 'Account is deactivated'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            if not has_permission(request.user, permission_codename):
                return Response(
                    {'error': 'You do not have permission to perform this action'},
                    status=status.HTTP_403_FORBIDDEN
                )

            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator
