from django.contrib import admin
from .models import Case, CaseHistory, CaseComment


class CaseHistoryInline(admin.TabularInline):
    model = CaseHistory
    extra = 0
    readonly_fields = ['field', 'old_value', 'new_value', 'created_date', 'created_by']
    can_delete = False


class CaseCommentInline(admin.StackedInline):
    model = CaseComment
    extra = 0
    raw_id_fields = ['created_by', 'last_modified_by']
    readonly_fields = ['created_date', 'last_modified_date']


@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = ['id', 'case_number', 'subject', 'status', 'priority', 'account', 'owner', 'is_closed']
    search_fields = ['case_number', 'subject', 'account__name']
    list_filter = ['status', 'priority', 'is_closed']
    raw_id_fields = ['account', 'owner', 'created_by', 'last_modified_by']
    readonly_fields = ['created_date', 'last_modified_date']
    inlines = [CaseHistoryInline, CaseCommentInline]


@admin.register(CaseHistory)
class CaseHistoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'case', 'field', 'old_value', 'new_value', 'created_date', 'created_by']
    search_fields = ['case__case_number', 'field']
    list_filter = ['field', 'created_date']
    raw_id_fields = ['case', 'created_by']
    readonly_fields = ['created_date']


@admin.register(CaseComment)
class CaseCommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'case', 'is_published', 'created_date', 'created_by']
    search_fields = ['case__case_number', 'comment_body']
    list_filter = ['is_published', 'created_date']
    raw_id_fields = ['case', 'created_by', 'last_modified_by']
    readonly_fields = ['created_date', 'last_modified_date']
