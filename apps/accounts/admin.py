from django.contrib import admin
from .models import Account, AccountPlan


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'owner', 'account_number', 'credit_limit', 'created_date']
    search_fields = ['name', 'account_number']
    list_filter = ['created_date', 'currency_iso_code']
    raw_id_fields = ['owner', 'last_modified_by']
    readonly_fields = ['created_date', 'last_modified_date']


@admin.register(AccountPlan)
class AccountPlanAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'account', 'status', 'start_date', 'end_date']
    search_fields = ['name', 'account__name']
    list_filter = ['status', 'start_date']
    raw_id_fields = ['account', 'created_by', 'last_modified_by']
    readonly_fields = ['created_date', 'last_modified_date']
