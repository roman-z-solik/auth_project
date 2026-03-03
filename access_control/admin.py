from django.contrib import admin
from .models import Role, Permission, RolePermission, UserRole

class RolePermissionInline(admin.TabularInline):
    model = RolePermission
    extra = 1
    autocomplete_fields = ['permission']

class UserRoleInline(admin.TabularInline):
    model = UserRole
    extra = 1
    autocomplete_fields = ['role']

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']
    inlines = [RolePermissionInline]

@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ['codename', 'created_at']
    search_fields = ['codename', 'description']

@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = ['role', 'permission', 'created_at']
    list_filter = ['role', 'permission']
    autocomplete_fields = ['role', 'permission']

@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'created_at']
    list_filter = ['role']
    autocomplete_fields = ['user', 'role']
    search_fields = ['user__email']
