from django.contrib import admin
from .models import UserRole, User, RecordType, UserLoginLog


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ('ur_sf_id', 'ur_name', 'ur_active', 'ur_created_at')
    list_filter = ('ur_active',)
    search_fields = ('ur_name', 'ur_sf_id')


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('usr_sf_id', 'usr_name', 'usr_email', 'usr_is_active', 'usr_user_role_id')
    list_filter = ('usr_is_active', 'usr_active')
    search_fields = ('usr_name', 'usr_email', 'usr_username', 'usr_sf_id')


@admin.register(RecordType)
class RecordTypeAdmin(admin.ModelAdmin):
    list_display = ('rt_sf_id', 'rt_name', 'rt_developer_name', 'rt_sobject_type', 'rt_is_active')
    list_filter = ('rt_is_active', 'rt_sobject_type')
    search_fields = ('rt_name', 'rt_developer_name', 'rt_sf_id')


@admin.register(UserLoginLog)
class UserLoginLogAdmin(admin.ModelAdmin):
    list_display = ('ull_id', 'ull_user_sf_id', 'ull_login_at', 'ull_ip_address')
    list_filter = ('ull_login_at',)
    search_fields = ('ull_ip_address',)
    readonly_fields = ('ull_login_at',)
