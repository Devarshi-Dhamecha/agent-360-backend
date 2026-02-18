from django.contrib import admin
from .models import Case, CaseHistory, CaseComment


@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = ('cs_sf_id', 'cs_case_number', 'cs_subject', 'cs_status', 'cs_priority', 'cs_owner_id')
    list_filter = ('cs_status', 'cs_priority', 'cs_active')
    search_fields = ('cs_case_number', 'cs_subject', 'cs_sf_id')


@admin.register(CaseHistory)
class CaseHistoryAdmin(admin.ModelAdmin):
    list_display = ('ch_sf_id', 'ch_case_id', 'ch_field', 'ch_created_date', 'ch_created_by_id')
    list_filter = ('ch_field', 'ch_active')
    search_fields = ('ch_sf_id',)
    date_hierarchy = 'ch_created_date'


@admin.register(CaseComment)
class CaseCommentAdmin(admin.ModelAdmin):
    list_display = ('cc_id', 'cc_case_id', 'cc_is_published', 'cc_sync_status', 'cc_agent360_source')
    list_filter = ('cc_is_published', 'cc_sync_status', 'cc_agent360_source', 'cc_active')
    search_fields = ('cc_sf_id', 'cc_comment_body')
