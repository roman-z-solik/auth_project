from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Role(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='Название роли')
    description = models.TextField(blank=True, verbose_name='Описание')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Роль'
        verbose_name_plural = 'Роли'

    def __str__(self):
        return self.name


class Permission(models.Model):
    codename = models.CharField(max_length=100, unique=True, verbose_name='Кодовое имя')
    description = models.TextField(blank=True, verbose_name='Описание')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Разрешение'
        verbose_name_plural = 'Разрешения'

    def __str__(self):
        return self.codename


class RolePermission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='role_permissions')
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, related_name='permission_roles')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Разрешение роли'
        verbose_name_plural = 'Разрешения ролей'
        unique_together = ['role', 'permission']

    def __str__(self):
        return f'{self.role.name} - {self.permission.codename}'


class UserRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_roles')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='role_users')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Роль пользователя'
        verbose_name_plural = 'Роли пользователей'
        unique_together = ['user', 'role']

    def __str__(self):
        return f'{self.user.email} - {self.role.name}'
