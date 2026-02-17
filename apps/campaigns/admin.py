from django.contrib import admin
from .models import RecordType, Campaign, Task


@admin.register(RecordType)
class RecordTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'developer_name', 'sobject_type', 'is_active']
    search_fields = ['name', 'developer_name']
    list_filter = ['is_active', 'sobject_type']
    readonly_fields = ['created_date']


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'type', 'status', 'owner', 'start_date', 'end_date', 'is_active']
    search_fields = ['name']
    list_filter = ['status', 'type', 'is_active']
    raw_id_fields = ['record_type', 'parent', 'owner', 'created_by', 'last_modified_by']
    readonly_fields = ['created_date', 'last_modified_date']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'subject', 'owner', 'status', 'priority', 'activity_date', 'is_closed']
    search_fields = ['subject']
    list_filter = ['status', 'priority', 'is_closed']
    raw_id_fields = ['owner', 'created_by', 'last_modified_by']
    readonly_fields = ['created_date', 'last_modified_date']
