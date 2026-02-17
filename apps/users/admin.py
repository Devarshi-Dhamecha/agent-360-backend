from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Profile, UserRole, Users


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'created_date', 'last_modified_date']
    search_fields = ['name']
    list_filter = ['created_date']


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'parent_role', 'created_date']
    search_fields = ['name']
    list_filter = ['created_date']
    raw_id_fields = ['parent_role']


@admin.register(Users)
class UsersAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'name', 'is_active', 'is_staff', 'profile']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'name']
    list_filter = ['is_active', 'is_staff', 'profile']
    
    fieldsets = (
        (None, {'fields': ('id', 'username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Organization', {'fields': ('profile', 'user_role', 'manager')}),
        ('Audit', {'fields': ('last_modified_by', 'created_date', 'last_modified_date')}),
    )
    
    readonly_fields = ['created_date', 'last_modified_date']
    raw_id_fields = ['profile', 'user_role', 'manager', 'last_modified_by']
