from django.contrib import admin
from .models import Campaign, Task


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('cmp_sf_id', 'cmp_name', 'cmp_status', 'cmp_owner_id', 'cmp_start_date', 'cmp_end_date')
    list_filter = ('cmp_status', 'cmp_is_active', 'cmp_active')
    search_fields = ('cmp_name', 'cmp_sf_id')
    date_hierarchy = 'cmp_start_date'


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('tsk_sf_id', 'tsk_subject', 'tsk_status', 'tsk_priority', 'tsk_owner_id', 'tsk_activity_date')
    list_filter = ('tsk_status', 'tsk_priority', 'tsk_active')
    search_fields = ('tsk_subject', 'tsk_description', 'tsk_sf_id')
    date_hierarchy = 'tsk_activity_date'
