from django.db import models


class Campaign(models.Model):
    """Salesforce Campaign - marketing campaigns and promotions"""
    cmp_sf_id = models.CharField(
        max_length=18,
        primary_key=True,
        db_column='cmp_sf_id',
        verbose_name='Salesforce ID'
    )
    cmp_name = models.CharField(
        max_length=80,
        db_column='cmp_name',
        verbose_name='Campaign Name'
    )
    cmp_record_type_id = models.ForeignKey(
        'users.RecordType',
        to_field='rt_sf_id',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        db_column='cmp_record_type_id',
        verbose_name='Record Type'
    )
    cmp_type = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        db_column='cmp_type',
        verbose_name='Type'
    )
    cmp_parent_id = models.ForeignKey(
        'self',
        to_field='cmp_sf_id',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        db_column='cmp_parent_id',
        verbose_name='Parent Campaign'
    )
    cmp_status = models.CharField(
        max_length=100,
        db_column='cmp_status',
        verbose_name='Status'
    )
    cmp_start_date = models.DateField(
        null=True,
        blank=True,
        db_column='cmp_start_date',
        verbose_name='Start Date'
    )
    cmp_end_date = models.DateField(
        null=True,
        blank=True,
        db_column='cmp_end_date',
        verbose_name='End Date'
    )
    cmp_actual_cost = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
        db_column='cmp_actual_cost',
        verbose_name='Actual Cost'
    )
    cmp_budgeted_cost = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
        db_column='cmp_budgeted_cost',
        verbose_name='Budgeted Cost'
    )
    cmp_currency_iso_code = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        db_column='cmp_currency_iso_code',
        verbose_name='Currency ISO Code'
    )
    cmp_owner_id = models.ForeignKey(
        'users.User',
        to_field='usr_sf_id',
        on_delete=models.RESTRICT,
        db_column='cmp_owner_id',
        verbose_name='Owner'
    )
    cmp_account_id = models.ForeignKey(
        'accounts.Account',
        to_field='acc_sf_id',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        db_column='cmp_account_id',
        verbose_name='Account'
    )
    cmp_initial_quantity = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
        db_column='cmp_initial_quantity',
        verbose_name='Initial Quantity'
    )
    cmp_used_quantity = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
        db_column='cmp_used_quantity',
        verbose_name='Used Quantity'
    )
    cmp_available_budget = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
        db_column='cmp_available_budget',
        verbose_name='Available Budget'
    )
    cmp_is_active = models.BooleanField(
        null=True,
        blank=True,
        db_column='cmp_is_active',
        verbose_name='Is Active'
    )
    cmp_sf_created_date = models.DateTimeField(
        db_column='cmp_sf_created_date',
        verbose_name='SF Created Date'
    )
    cmp_last_modified_date = models.DateTimeField(
        db_column='cmp_last_modified_date',
        verbose_name='Last Modified Date'
    )
    cmp_last_modified_by_id = models.CharField(
        max_length=18,
        db_column='cmp_last_modified_by_id',
        verbose_name='Last Modified By ID'
    )
    cmp_active = models.SmallIntegerField(
        default=1,
        db_column='cmp_active',
        verbose_name='Active Flag'
    )
    cmp_created_at = models.DateTimeField(
        auto_now_add=True,
        db_column='cmp_created_at',
        verbose_name='Created At'
    )
    cmp_updated_at = models.DateTimeField(
        auto_now=True,
        db_column='cmp_updated_at',
        verbose_name='Updated At'
    )

    class Meta:
        db_table = 'campaigns'
        verbose_name = 'Campaign'
        verbose_name_plural = 'Campaigns'
        indexes = [
            models.Index(fields=['cmp_owner_id'], name='idx_campaigns_owner'),
            models.Index(fields=['cmp_account_id'], name='idx_campaigns_account'),
            models.Index(fields=['cmp_parent_id'], name='idx_campaigns_parent'),
            models.Index(fields=['cmp_status'], name='idx_campaigns_status'),
        ]

    def __str__(self):
        return self.cmp_name


class Task(models.Model):
    """Salesforce Task - activities and to-dos"""
    tsk_sf_id = models.CharField(
        max_length=18,
        primary_key=True,
        db_column='tsk_sf_id',
        verbose_name='Salesforce ID'
    )
    # Polymorphic relationship - can relate to various objects
    tsk_what_id = models.CharField(
        max_length=18,
        null=True,
        blank=True,
        db_column='tsk_what_id',
        verbose_name='What ID'
    )
    tsk_what_type = models.CharField(
        max_length=40,
        null=True,
        blank=True,
        db_column='tsk_what_type',
        verbose_name='What Type'
    )
    tsk_what_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_column='tsk_what_name',
        verbose_name='What Name'
    )
    tsk_activity_date = models.DateField(
        null=True,
        blank=True,
        db_column='tsk_activity_date',
        verbose_name='Activity Date'
    )
    tsk_status = models.CharField(
        max_length=100,
        db_column='tsk_status',
        verbose_name='Status'
    )
    tsk_priority = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        db_column='tsk_priority',
        verbose_name='Priority'
    )
    tsk_subject = models.CharField(
        max_length=255,
        db_column='tsk_subject',
        verbose_name='Subject'
    )
    tsk_owner_id = models.ForeignKey(
        'users.User',
        to_field='usr_sf_id',
        on_delete=models.RESTRICT,
        db_column='tsk_owner_id',
        verbose_name='Owner'
    )
    tsk_description = models.TextField(
        null=True,
        blank=True,
        db_column='tsk_description',
        verbose_name='Description'
    )
    tsk_sf_created_date = models.DateTimeField(
        db_column='tsk_sf_created_date',
        verbose_name='SF Created Date'
    )
    tsk_completed_date = models.DateTimeField(
        null=True,
        blank=True,
        db_column='tsk_completed_date',
        verbose_name='Completed Date'
    )
    tsk_last_modified_date = models.DateTimeField(
        db_column='tsk_last_modified_date',
        verbose_name='Last Modified Date'
    )
    tsk_last_modified_by_id = models.CharField(
        max_length=18,
        db_column='tsk_last_modified_by_id',
        verbose_name='Last Modified By ID'
    )
    tsk_active = models.SmallIntegerField(
        default=1,
        db_column='tsk_active',
        verbose_name='Active Flag'
    )
    tsk_created_at = models.DateTimeField(
        auto_now_add=True,
        db_column='tsk_created_at',
        verbose_name='Created At'
    )
    tsk_updated_at = models.DateTimeField(
        auto_now=True,
        db_column='tsk_updated_at',
        verbose_name='Updated At'
    )

    class Meta:
        db_table = 'tasks'
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'
        indexes = [
            models.Index(fields=['tsk_owner_id'], name='idx_tasks_owner'),
            models.Index(fields=['tsk_status'], name='idx_tasks_status'),
            models.Index(fields=['tsk_what_id', 'tsk_what_type'], name='idx_tasks_what'),
        ]

    def __str__(self):
        return self.tsk_subject
