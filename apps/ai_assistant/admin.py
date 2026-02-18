from django.contrib import admin
from .models import AiChatThread, AiChatMessage, AiBusinessRule, AiQueryExample, AiSchemaConfig


@admin.register(AiChatThread)
class AiChatThreadAdmin(admin.ModelAdmin):
    list_display = ('act_id', 'act_user_sf_id', 'act_account_sf_id', 'act_title', 'act_message_count', 'act_last_message_at')
    list_filter = ('act_sf_synced',)
    search_fields = ('act_title',)
    date_hierarchy = 'act_created_at'


@admin.register(AiChatMessage)
class AiChatMessageAdmin(admin.ModelAdmin):
    list_display = ('acm_id', 'acm_thread_id', 'acm_role', 'acm_created_at', 'acm_sf_synced')
    list_filter = ('acm_role', 'acm_sf_synced')
    search_fields = ('acm_content',)
    date_hierarchy = 'acm_created_at'


@admin.register(AiBusinessRule)
class AiBusinessRuleAdmin(admin.ModelAdmin):
    list_display = ('abr_id', 'abr_rule_key', 'abr_category', 'abr_is_active', 'abr_sort_order')
    list_filter = ('abr_category', 'abr_is_active')
    search_fields = ('abr_rule_key', 'abr_rule_text')


@admin.register(AiQueryExample)
class AiQueryExampleAdmin(admin.ModelAdmin):
    list_display = ('aqe_id', 'aqe_category', 'aqe_is_active', 'aqe_created_at')
    list_filter = ('aqe_category', 'aqe_is_active')
    search_fields = ('aqe_question', 'aqe_sql')


@admin.register(AiSchemaConfig)
class AiSchemaConfigAdmin(admin.ModelAdmin):
    list_display = ('asc_id', 'asc_config_key', 'asc_version', 'asc_generated_at')
    search_fields = ('asc_config_key',)
