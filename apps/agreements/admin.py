from django.contrib import admin
from .models import FrameAgreement, Target


@admin.register(FrameAgreement)
class FrameAgreementAdmin(admin.ModelAdmin):
    list_display = ['id', 'account', 'agreement_type', 'start_date', 'end_date', 'status', 'is_active']
    search_fields = ['account__name']
    list_filter = ['status', 'is_active', 'agreement_type', 'start_year']
    raw_id_fields = ['account', 'created_by', 'last_modified_by']
    readonly_fields = ['start_year', 'created_date', 'last_modified_date']


@admin.register(Target)
class TargetAdmin(admin.ModelAdmin):
    list_display = ['id', 'account', 'frame_agreement', 'quarter', 'net_turnover_target', 'rebate_rate']
    search_fields = ['account__name']
    list_filter = ['quarter']
    raw_id_fields = ['account', 'frame_agreement', 'created_by', 'last_modified_by']
    readonly_fields = ['created_date', 'last_modified_date']
