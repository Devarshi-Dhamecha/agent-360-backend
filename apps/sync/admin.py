from django.contrib import admin
from .models import SyncLog, SyncWatermark, SyncConflict


@admin.register(SyncLog)
class SyncLogAdmin(admin.ModelAdmin):
    list_display = ('sl_id', 'sl_job_name', 'sl_object_name', 'sl_status', 'sl_started_at', 'sl_completed_at')
    list_filter = ('sl_status', 'sl_direction', 'sl_object_name')
    search_fields = ('sl_job_name', 'sl_object_name', 'sl_run_id')
    date_hierarchy = 'sl_started_at'
    readonly_fields = ('sl_run_id', 'sl_started_at')


@admin.register(SyncWatermark)
class SyncWatermarkAdmin(admin.ModelAdmin):
    list_display = ('sw_id', 'sw_object_name', 'sw_last_sync_ts', 'sw_sync_frequency', 'sw_sync_enabled')
    list_filter = ('sw_sync_frequency', 'sw_sync_enabled')
    search_fields = ('sw_object_name', 'sw_sf_object_api')


@admin.register(SyncConflict)
class SyncConflictAdmin(admin.ModelAdmin):
    list_display = ('sc_id', 'sc_object_name', 'sc_record_sf_id', 'sc_conflict_type', 'sc_resolution', 'sc_resolved_at')
    list_filter = ('sc_conflict_type', 'sc_resolution', 'sc_object_name')
    search_fields = ('sc_record_sf_id', 'sc_object_name')
