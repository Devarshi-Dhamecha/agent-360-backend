import uuid
from django.db import models


class SyncLog(models.Model):
    """Sync Log - tracks Salesforce sync job execution"""
    
    STATUS_CHOICES = [
        ('running', 'Running'),
        ('success', 'Success'),
        ('partial', 'Partial'),
        ('failed', 'Failed'),
        ('skipped', 'Skipped'),
    ]
    
    sl_id = models.AutoField(
        primary_key=True,
        db_column='sl_id',
        verbose_name='ID'
    )
    sl_run_id = models.UUIDField(
        default=uuid.uuid4,
        db_column='sl_run_id',
        verbose_name='Run ID'
    )
    sl_job_name = models.CharField(
        max_length=50,
        db_column='sl_job_name',
        verbose_name='Job Name'
    )
    sl_direction = models.CharField(
        max_length=20,
        db_column='sl_direction',
        verbose_name='Direction'
    )
    sl_object_name = models.CharField(
        max_length=50,
        db_column='sl_object_name',
        verbose_name='Object Name'
    )
    sl_sf_object_api = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        db_column='sl_sf_object_api',
        verbose_name='SF Object API'
    )
    sl_started_at = models.DateTimeField(
        auto_now_add=True,
        db_column='sl_started_at',
        verbose_name='Started At'
    )
    sl_completed_at = models.DateTimeField(
        null=True,
        blank=True,
        db_column='sl_completed_at',
        verbose_name='Completed At'
    )
    sl_status = models.CharField(
        max_length=20,
        default='running',
        choices=STATUS_CHOICES,
        db_column='sl_status',
        verbose_name='Status'
    )
    sl_records_queried = models.IntegerField(
        default=0,
        db_column='sl_records_queried',
        verbose_name='Records Queried'
    )
    sl_records_inserted = models.IntegerField(
        default=0,
        db_column='sl_records_inserted',
        verbose_name='Records Inserted'
    )
    sl_records_updated = models.IntegerField(
        default=0,
        db_column='sl_records_updated',
        verbose_name='Records Updated'
    )
    sl_records_deleted = models.IntegerField(
        default=0,
        db_column='sl_records_deleted',
        verbose_name='Records Deleted'
    )
    sl_records_skipped = models.IntegerField(
        default=0,
        db_column='sl_records_skipped',
        verbose_name='Records Skipped'
    )
    sl_records_failed = models.IntegerField(
        default=0,
        db_column='sl_records_failed',
        verbose_name='Records Failed'
    )
    sl_hwm_before = models.DateTimeField(
        null=True,
        blank=True,
        db_column='sl_hwm_before',
        verbose_name='High Water Mark Before'
    )
    sl_hwm_after = models.DateTimeField(
        null=True,
        blank=True,
        db_column='sl_hwm_after',
        verbose_name='High Water Mark After'
    )
    sl_error_message = models.TextField(
        null=True,
        blank=True,
        db_column='sl_error_message',
        verbose_name='Error Message'
    )
    sl_error_details = models.JSONField(
        null=True,
        blank=True,
        db_column='sl_error_details',
        verbose_name='Error Details'
    )

    class Meta:
        db_table = 'sync_log'
        verbose_name = 'Sync Log'
        verbose_name_plural = 'Sync Logs'
        indexes = [
            models.Index(fields=['sl_run_id'], name='idx_sync_log_run_id'),
            models.Index(fields=['sl_job_name', 'sl_started_at'], name='idx_sync_log_job_started'),
            models.Index(fields=['sl_status'], name='idx_sync_log_status'),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(sl_status__in=['running', 'success', 'partial', 'failed', 'skipped']),
                name='chk_sync_log_status'
            ),
        ]

    def __str__(self):
        return f"{self.sl_job_name} - {self.sl_object_name} ({self.sl_status})"


class SyncWatermark(models.Model):
    """Sync Watermark - tracks last sync timestamp for each object"""
    
    FREQUENCY_CHOICES = [
        ('hourly', 'Hourly'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
    ]
    
    sw_id = models.AutoField(
        primary_key=True,
        db_column='sw_id',
        verbose_name='ID'
    )
    sw_object_name = models.CharField(
        max_length=50,
        unique=True,
        db_column='sw_object_name',
        verbose_name='Object Name'
    )
    sw_sf_object_api = models.CharField(
        max_length=50,
        db_column='sw_sf_object_api',
        verbose_name='SF Object API'
    )
    sw_last_sync_ts = models.DateTimeField(
        null=True,
        blank=True,
        db_column='sw_last_sync_ts',
        verbose_name='Last Sync Timestamp'
    )
    sw_last_delete_check = models.DateTimeField(
        null=True,
        blank=True,
        db_column='sw_last_delete_check',
        verbose_name='Last Delete Check'
    )
    sw_sync_frequency = models.CharField(
        max_length=20,
        default='hourly',
        choices=FREQUENCY_CHOICES,
        db_column='sw_sync_frequency',
        verbose_name='Sync Frequency'
    )
    sw_sync_enabled = models.BooleanField(
        default=True,
        db_column='sw_sync_enabled',
        verbose_name='Sync Enabled'
    )
    sw_sync_order = models.IntegerField(
        default=0,
        db_column='sw_sync_order',
        verbose_name='Sync Order'
    )
    sw_updated_at = models.DateTimeField(
        auto_now=True,
        db_column='sw_updated_at',
        verbose_name='Updated At'
    )

    class Meta:
        db_table = 'sync_watermarks'
        verbose_name = 'Sync Watermark'
        verbose_name_plural = 'Sync Watermarks'
        constraints = [
            models.CheckConstraint(
                condition=models.Q(sw_sync_frequency__in=['hourly', 'daily', 'weekly']),
                name='chk_sync_watermark_frequency'
            ),
        ]

    def __str__(self):
        return f"{self.sw_object_name} ({self.sw_sync_frequency})"


class SyncConflict(models.Model):
    """Sync Conflict - tracks conflicts between local and Salesforce data"""
    
    CONFLICT_TYPE_CHOICES = [
        ('local_pending', 'Local Pending'),
        ('sf_deleted', 'SF Deleted'),
        ('version_mismatch', 'Version Mismatch'),
    ]
    
    RESOLUTION_CHOICES = [
        ('local_wins', 'Local Wins'),
        ('sf_wins', 'SF Wins'),
        ('manual', 'Manual'),
    ]
    
    sc_id = models.AutoField(
        primary_key=True,
        db_column='sc_id',
        verbose_name='ID'
    )
    sc_object_name = models.CharField(
        max_length=50,
        db_column='sc_object_name',
        verbose_name='Object Name'
    )
    sc_record_sf_id = models.CharField(
        max_length=18,
        db_column='sc_record_sf_id',
        verbose_name='Record SF ID'
    )
    sc_record_local_id = models.IntegerField(
        null=True,
        blank=True,
        db_column='sc_record_local_id',
        verbose_name='Record Local ID'
    )
    sc_conflict_type = models.CharField(
        max_length=30,
        choices=CONFLICT_TYPE_CHOICES,
        db_column='sc_conflict_type',
        verbose_name='Conflict Type'
    )
    sc_local_value = models.JSONField(
        null=True,
        blank=True,
        db_column='sc_local_value',
        verbose_name='Local Value'
    )
    sc_sf_value = models.JSONField(
        null=True,
        blank=True,
        db_column='sc_sf_value',
        verbose_name='SF Value'
    )
    sc_resolution = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        choices=RESOLUTION_CHOICES,
        db_column='sc_resolution',
        verbose_name='Resolution'
    )
    sc_resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        db_column='sc_resolved_at',
        verbose_name='Resolved At'
    )
    sc_resolved_by = models.ForeignKey(
        'users.User',
        to_field='usr_sf_id',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        db_column='sc_resolved_by',
        verbose_name='Resolved By'
    )
    sc_created_at = models.DateTimeField(
        auto_now_add=True,
        db_column='sc_created_at',
        verbose_name='Created At'
    )

    class Meta:
        db_table = 'sync_conflicts'
        verbose_name = 'Sync Conflict'
        verbose_name_plural = 'Sync Conflicts'
        indexes = [
            models.Index(fields=['sc_object_name'], name='idx_sync_conflicts_object'),
            models.Index(fields=['sc_resolution'], name='idx_sync_conflicts_resolution'),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(sc_conflict_type__in=['local_pending', 'sf_deleted', 'version_mismatch']),
                name='chk_sync_conflict_type'
            ),
            models.CheckConstraint(
                condition=models.Q(sc_resolution__in=['local_wins', 'sf_wins', 'manual']) | models.Q(sc_resolution__isnull=True),
                name='chk_sync_conflict_resolution'
            ),
        ]

    def __str__(self):
        return f"{self.sc_object_name} - {self.sc_record_sf_id} ({self.sc_conflict_type})"
