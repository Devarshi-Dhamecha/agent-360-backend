from django.db import models


class Case(models.Model):
    """Salesforce Case - customer support cases"""
    cs_sf_id = models.CharField(
        max_length=18,
        primary_key=True,
        db_column='cs_sf_id',
        verbose_name='Salesforce ID'
    )
    cs_case_number = models.CharField(
        max_length=80,
        db_column='cs_case_number',
        verbose_name='Case Number'
    )
    cs_subject = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_column='cs_subject',
        verbose_name='Subject'
    )
    cs_description = models.TextField(
        null=True,
        blank=True,
        db_column='cs_description',
        verbose_name='Description'
    )
    cs_status = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        db_column='cs_status',
        verbose_name='Status'
    )
    cs_account_id = models.ForeignKey(
        'accounts.Account',
        to_field='acc_sf_id',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        db_column='cs_account_id',
        verbose_name='Account'
    )
    cs_owner_id = models.ForeignKey(
        'users.User',
        to_field='usr_sf_id',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        db_column='cs_owner_id',
        verbose_name='Owner'
    )
    cs_priority = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        db_column='cs_priority',
        verbose_name='Priority'
    )
    cs_sf_created_date = models.DateTimeField(
        db_column='cs_sf_created_date',
        verbose_name='SF Created Date'
    )
    cs_last_modified_date = models.DateTimeField(
        db_column='cs_last_modified_date',
        verbose_name='Last Modified Date'
    )
    cs_last_modified_by_id = models.CharField(
        max_length=18,
        db_column='cs_last_modified_by_id',
        verbose_name='Last Modified By ID'
    )
    cs_active = models.SmallIntegerField(
        default=1,
        db_column='cs_active',
        verbose_name='Active Flag'
    )
    cs_created_at = models.DateTimeField(
        auto_now_add=True,
        db_column='cs_created_at',
        verbose_name='Created At'
    )
    cs_updated_at = models.DateTimeField(
        auto_now=True,
        db_column='cs_updated_at',
        verbose_name='Updated At'
    )

    class Meta:
        db_table = 'cases'
        verbose_name = 'Case'
        verbose_name_plural = 'Cases'
        indexes = [
            models.Index(fields=['cs_account_id'], name='idx_cases_account'),
            models.Index(fields=['cs_owner_id'], name='idx_cases_owner'),
            models.Index(fields=['cs_status'], name='idx_cases_status'),
        ]

    def __str__(self):
        return f"{self.cs_case_number} - {self.cs_subject}"


class CaseHistory(models.Model):
    """Case History - tracks field changes on cases"""
    ch_sf_id = models.CharField(
        max_length=18,
        primary_key=True,
        db_column='ch_sf_id',
        verbose_name='Salesforce ID'
    )
    ch_case_id = models.ForeignKey(
        'cases.Case',
        to_field='cs_sf_id',
        on_delete=models.CASCADE,
        db_column='ch_case_id',
        verbose_name='Case'
    )
    ch_field = models.CharField(
        max_length=255,
        db_column='ch_field',
        verbose_name='Field'
    )
    ch_old_value = models.TextField(
        null=True,
        blank=True,
        db_column='ch_old_value',
        verbose_name='Old Value'
    )
    ch_new_value = models.TextField(
        null=True,
        blank=True,
        db_column='ch_new_value',
        verbose_name='New Value'
    )
    ch_created_date = models.DateTimeField(
        db_column='ch_created_date',
        verbose_name='Created Date'
    )
    ch_created_by_id = models.ForeignKey(
        'users.User',
        to_field='usr_sf_id',
        on_delete=models.RESTRICT,
        db_column='ch_created_by_id',
        verbose_name='Created By'
    )
    ch_active = models.SmallIntegerField(
        default=1,
        db_column='ch_active',
        verbose_name='Active Flag'
    )
    ch_created_at = models.DateTimeField(
        auto_now_add=True,
        db_column='ch_created_at',
        verbose_name='Created At'
    )
    ch_updated_at = models.DateTimeField(
        auto_now=True,
        db_column='ch_updated_at',
        verbose_name='Updated At'
    )

    class Meta:
        db_table = 'case_history'
        verbose_name = 'Case History'
        verbose_name_plural = 'Case Histories'
        indexes = [
            models.Index(fields=['ch_case_id'], name='idx_case_history_case'),
        ]

    def __str__(self):
        return f"{self.ch_case_id} - {self.ch_field}"


class CaseComment(models.Model):
    """Case Comment - comments on cases, can be created by Agent360"""
    cc_id = models.AutoField(
        primary_key=True,
        db_column='cc_id',
        verbose_name='ID'
    )
    cc_sf_id = models.CharField(
        max_length=18,
        null=True,
        blank=True,
        unique=True,
        db_column='cc_sf_id',
        verbose_name='Salesforce ID'
    )
    cc_case_id = models.ForeignKey(
        'cases.Case',
        to_field='cs_sf_id',
        on_delete=models.CASCADE,
        db_column='cc_case_id',
        verbose_name='Case'
    )
    cc_comment_body = models.TextField(
        null=True,
        blank=True,
        db_column='cc_comment_body',
        verbose_name='Comment Body'
    )
    cc_is_published = models.BooleanField(
        null=True,
        blank=True,
        db_column='cc_is_published',
        verbose_name='Is Published'
    )
    # Salesforce audit fields
    cc_sf_created_date = models.DateTimeField(
        null=True,
        blank=True,
        db_column='cc_sf_created_date',
        verbose_name='SF Created Date'
    )
    cc_sf_created_by_id = models.ForeignKey(
        'users.User',
        to_field='usr_sf_id',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='cc_sf_created',
        db_column='cc_sf_created_by_id',
        verbose_name='SF Created By'
    )
    cc_last_modified_date = models.DateTimeField(
        null=True,
        blank=True,
        db_column='cc_last_modified_date',
        verbose_name='Last Modified Date'
    )
    cc_last_modified_by_id = models.CharField(
        max_length=18,
        null=True,
        blank=True,
        db_column='cc_last_modified_by_id',
        verbose_name='Last Modified By ID'
    )
    # Agent360 audit fields
    cc_agent_modified_by = models.ForeignKey(
        'users.User',
        to_field='usr_sf_id',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='cc_agent_modified',
        db_column='cc_agent_modified_by',
        verbose_name='Agent Modified By'
    )
    cc_agent_modified_date = models.DateTimeField(
        null=True,
        blank=True,
        db_column='cc_agent_modified_date',
        verbose_name='Agent Modified Date'
    )
    cc_agent_created_by = models.ForeignKey(
        'users.User',
        to_field='usr_sf_id',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='cc_agent_created',
        db_column='cc_agent_created_by',
        verbose_name='Agent Created By'
    )
    cc_agent_created_date = models.DateTimeField(
        null=True,
        blank=True,
        db_column='cc_agent_created_date',
        verbose_name='Agent Created Date'
    )
    cc_agent360_source = models.BooleanField(
        null=True,
        blank=True,
        db_column='cc_agent360_source',
        verbose_name='Agent360 Source'
    )
    # Sync control fields
    cc_sync_status = models.SmallIntegerField(
        default=1,
        db_column='cc_sync_status',
        verbose_name='Sync Status'
    )
    cc_version = models.IntegerField(
        default=1,
        db_column='cc_version',
        verbose_name='Version'
    )
    cc_retry_count = models.IntegerField(
        default=0,
        db_column='cc_retry_count',
        verbose_name='Retry Count'
    )
    cc_last_sync_error = models.TextField(
        null=True,
        blank=True,
        db_column='cc_last_sync_error',
        verbose_name='Last Sync Error'
    )
    cc_active = models.SmallIntegerField(
        default=1,
        db_column='cc_active',
        verbose_name='Active Flag'
    )
    cc_created_at = models.DateTimeField(
        auto_now_add=True,
        db_column='cc_created_at',
        verbose_name='Created At'
    )
    cc_updated_at = models.DateTimeField(
        auto_now=True,
        db_column='cc_updated_at',
        verbose_name='Updated At'
    )

    class Meta:
        db_table = 'case_comments'
        verbose_name = 'Case Comment'
        verbose_name_plural = 'Case Comments'
        indexes = [
            models.Index(fields=['cc_case_id'], name='idx_case_comments_case'),
            models.Index(fields=['cc_sync_status'], name='idx_case_comments_sync_status'),
            models.Index(fields=['cc_retry_count'], name='idx_case_comments_retry_count'),
        ]

    def __str__(self):
        return f"Comment on {self.cc_case_id}"
