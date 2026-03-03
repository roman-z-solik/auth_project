from django.contrib.auth import get_user_model

User = get_user_model()


def get_user_permissions(user):
    if user.is_superuser:
        return ['*']

    if not user.is_authenticated or not user.is_active:
        return []

    permissions = set()
    user_roles = user.user_roles.select_related('role').prefetch_related('role__role_permissions__permission')

    for user_role in user_roles:
        for role_permission in user_role.role.role_permissions.all():
            permissions.add(role_permission.permission.codename)

    return list(permissions)


def has_permission(user, permission_codename):
    if user.is_superuser:
        return True

    if not user.is_authenticated or not user.is_active:
        return False

    user_roles = user.user_roles.select_related('role').prefetch_related('role__role_permissions__permission')

    for user_role in user_roles:
        for role_permission in user_role.role.role_permissions.all():
            if role_permission.permission.codename == permission_codename:
                return True

    return False
