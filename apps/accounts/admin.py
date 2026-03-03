from django.contrib import admin
from .models import Account, FrameAgreement, Target


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('acc_sf_id', 'acc_name', 'acc_owner_id', 'acc_active', 'acc_created_at')
    list_filter = ('acc_active',)
    search_fields = ('acc_name', 'acc_account_number', 'acc_sf_id')


@admin.register(FrameAgreement)
class FrameAgreementAdmin(admin.ModelAdmin):
    list_display = ('fa_sf_id', 'fa_account_id', 'fa_status', 'fa_start_date', 'fa_end_date', 'fa_is_active')
    list_filter = ('fa_status', 'fa_is_active', 'fa_start_year')
    search_fields = ('fa_sf_id',)


@admin.register(Target)
class TargetAdmin(admin.ModelAdmin):
    list_display = ('tgt_sf_id', 'tgt_account_id', 'tgt_quarter', 'tgt_net_turnover_target', 'tgt_active')
    list_filter = ('tgt_quarter', 'tgt_active')
    search_fields = ('tgt_sf_id',)
