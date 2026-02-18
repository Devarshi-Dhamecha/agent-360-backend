from django.db import models


class AiChatThread(models.Model):
    """AI Chat Thread - conversation threads between users and AI assistant"""
    act_id = models.AutoField(
        primary_key=True,
        db_column='act_id',
        verbose_name='ID'
    )
    act_user_sf_id = models.ForeignKey(
        'users.User',
        to_field='usr_sf_id',
        on_delete=models.CASCADE,
        db_column='act_user_sf_id',
        verbose_name='User'
    )
    act_account_sf_id = models.ForeignKey(
        'accounts.Account',
        to_field='acc_sf_id',
        on_delete=models.CASCADE,
        db_column='act_account_sf_id',
        verbose_name='Account'
    )
    act_title = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_column='act_title',
        verbose_name='Title'
    )
    act_message_count = models.IntegerField(
        default=0,
        db_column='act_message_count',
        verbose_name='Message Count'
    )
    act_last_message_at = models.DateTimeField(
        null=True,
        blank=True,
        db_column='act_last_message_at',
        verbose_name='Last Message At'
    )
    act_sf_synced = models.BooleanField(
        default=False,
        db_column='act_sf_synced',
        verbose_name='SF Synced'
    )
    act_sf_synced_at = models.DateTimeField(
        null=True,
        blank=True,
        db_column='act_sf_synced_at',
        verbose_name='SF Synced At'
    )
    act_created_at = models.DateTimeField(
        auto_now_add=True,
        db_column='act_created_at',
        verbose_name='Created At'
    )
    act_updated_at = models.DateTimeField(
        auto_now=True,
        db_column='act_updated_at',
        verbose_name='Updated At'
    )

    class Meta:
        db_table = 'ai_chat_threads'
        verbose_name = 'AI Chat Thread'
        verbose_name_plural = 'AI Chat Threads'
        constraints = [
            models.UniqueConstraint(
                fields=['act_user_sf_id', 'act_account_sf_id'],
                name='uq_ai_chat_thread_pair'
            ),
        ]

    def __str__(self):
        return f"Thread {self.act_id}: {self.act_title or 'Untitled'}"


class AiChatMessage(models.Model):
    """AI Chat Message - individual messages in chat threads"""
    
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    ]
    
    acm_id = models.AutoField(
        primary_key=True,
        db_column='acm_id',
        verbose_name='ID'
    )
    acm_thread_id = models.ForeignKey(
        'ai_assistant.AiChatThread',
        to_field='act_id',
        on_delete=models.CASCADE,
        db_column='acm_thread_id',
        verbose_name='Thread'
    )
    acm_role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        db_column='acm_role',
        verbose_name='Role'
    )
    acm_content = models.TextField(
        db_column='acm_content',
        verbose_name='Content'
    )
    acm_generated_sql = models.TextField(
        null=True,
        blank=True,
        db_column='acm_generated_sql',
        verbose_name='Generated SQL'
    )
    acm_sql_result_summary = models.TextField(
        null=True,
        blank=True,
        db_column='acm_sql_result_summary',
        verbose_name='SQL Result Summary'
    )
    acm_model_used = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        db_column='acm_model_used',
        verbose_name='Model Used'
    )
    acm_tokens_in = models.IntegerField(
        null=True,
        blank=True,
        db_column='acm_tokens_in',
        verbose_name='Tokens In'
    )
    acm_tokens_out = models.IntegerField(
        null=True,
        blank=True,
        db_column='acm_tokens_out',
        verbose_name='Tokens Out'
    )
    acm_latency_ms = models.IntegerField(
        null=True,
        blank=True,
        db_column='acm_latency_ms',
        verbose_name='Latency (ms)'
    )
    acm_error = models.TextField(
        null=True,
        blank=True,
        db_column='acm_error',
        verbose_name='Error'
    )
    acm_sf_synced = models.BooleanField(
        default=False,
        db_column='acm_sf_synced',
        verbose_name='SF Synced'
    )
    acm_created_at = models.DateTimeField(
        auto_now_add=True,
        db_column='acm_created_at',
        verbose_name='Created At'
    )

    class Meta:
        db_table = 'ai_chat_messages'
        verbose_name = 'AI Chat Message'
        verbose_name_plural = 'AI Chat Messages'
        indexes = [
            models.Index(fields=['acm_thread_id'], name='idx_ai_chat_messages_thread'),
            models.Index(fields=['acm_created_at'], name='idx_ai_chat_messages_created'),
            models.Index(fields=['acm_sf_synced'], name='idx_ai_chat_messages_synced'),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(acm_role__in=['user', 'assistant', 'system']),
                name='chk_ai_chat_message_role'
            ),
        ]

    def __str__(self):
        return f"{self.acm_role}: {self.acm_content[:50]}"


class AiBusinessRule(models.Model):
    """AI Business Rule - business rules and constraints for AI assistant"""
    abr_id = models.AutoField(
        primary_key=True,
        db_column='abr_id',
        verbose_name='ID'
    )
    abr_rule_key = models.CharField(
        max_length=100,
        unique=True,
        db_column='abr_rule_key',
        verbose_name='Rule Key'
    )
    abr_category = models.CharField(
        max_length=50,
        db_column='abr_category',
        verbose_name='Category'
    )
    abr_rule_text = models.TextField(
        db_column='abr_rule_text',
        verbose_name='Rule Text'
    )
    abr_is_active = models.BooleanField(
        default=True,
        db_column='abr_is_active',
        verbose_name='Is Active'
    )
    abr_sort_order = models.IntegerField(
        default=0,
        db_column='abr_sort_order',
        verbose_name='Sort Order'
    )
    abr_created_at = models.DateTimeField(
        auto_now_add=True,
        db_column='abr_created_at',
        verbose_name='Created At'
    )
    abr_updated_at = models.DateTimeField(
        auto_now=True,
        db_column='abr_updated_at',
        verbose_name='Updated At'
    )
    abr_updated_by = models.ForeignKey(
        'users.User',
        to_field='usr_sf_id',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        db_column='abr_updated_by',
        verbose_name='Updated By'
    )

    class Meta:
        db_table = 'ai_business_rules'
        verbose_name = 'AI Business Rule'
        verbose_name_plural = 'AI Business Rules'

    def __str__(self):
        return f"{self.abr_rule_key} ({self.abr_category})"


class AiQueryExample(models.Model):
    """AI Query Example - example queries for training AI assistant"""
    aqe_id = models.AutoField(
        primary_key=True,
        db_column='aqe_id',
        verbose_name='ID'
    )
    aqe_question = models.TextField(
        db_column='aqe_question',
        verbose_name='Question'
    )
    aqe_sql = models.TextField(
        db_column='aqe_sql',
        verbose_name='SQL'
    )
    aqe_explanation = models.TextField(
        null=True,
        blank=True,
        db_column='aqe_explanation',
        verbose_name='Explanation'
    )
    aqe_category = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        db_column='aqe_category',
        verbose_name='Category'
    )
    aqe_is_active = models.BooleanField(
        default=True,
        db_column='aqe_is_active',
        verbose_name='Is Active'
    )
    aqe_created_at = models.DateTimeField(
        auto_now_add=True,
        db_column='aqe_created_at',
        verbose_name='Created At'
    )
    aqe_updated_at = models.DateTimeField(
        auto_now=True,
        db_column='aqe_updated_at',
        verbose_name='Updated At'
    )

    class Meta:
        db_table = 'ai_query_examples'
        verbose_name = 'AI Query Example'
        verbose_name_plural = 'AI Query Examples'

    def __str__(self):
        return f"{self.aqe_question[:50]}..."


class AiSchemaConfig(models.Model):
    """AI Schema Config - schema configuration for AI assistant"""
    asc_id = models.AutoField(
        primary_key=True,
        db_column='asc_id',
        verbose_name='ID'
    )
    asc_config_key = models.CharField(
        max_length=100,
        unique=True,
        db_column='asc_config_key',
        verbose_name='Config Key'
    )
    asc_config_value = models.TextField(
        db_column='asc_config_value',
        verbose_name='Config Value'
    )
    asc_version = models.IntegerField(
        default=1,
        db_column='asc_version',
        verbose_name='Version'
    )
    asc_generated_at = models.DateTimeField(
        auto_now_add=True,
        db_column='asc_generated_at',
        verbose_name='Generated At'
    )
    asc_updated_at = models.DateTimeField(
        auto_now=True,
        db_column='asc_updated_at',
        verbose_name='Updated At'
    )

    class Meta:
        db_table = 'ai_schema_config'
        verbose_name = 'AI Schema Config'
        verbose_name_plural = 'AI Schema Configs'

    def __str__(self):
        return f"{self.asc_config_key} (v{self.asc_version})"
