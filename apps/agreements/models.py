# apps/agreements/models.py

from django.conf import settings
from django.db import models


class FrameAgreement(models.Model):

    STATUS_CHOICES = [
        ('Draft', 'Draft'),
        ('Active', 'Active'),
        ('Expired', 'Expired'),
        ('Terminated', 'Terminated'),
    ]

    AGREEMENT_TYPE_CHOICES = [
        ('Standard', 'Standard'),
        ('Premium', 'Premium'),
        ('Strategic', 'Strategic'),
    ]

    id = models.CharField(max_length=18, primary_key=True)
    account = models.ForeignKey(
        'accounts.Account', on_delete=models.PROTECT,
        related_name='frame_agreements',
        db_column='AccountId', db_index=True
    )
    agreement_type = models.CharField(max_length=100, choices=AGREEMENT_TYPE_CHOICES)
    start_date = models.DateField(db_index=True)
    end_date = models.DateField()
    start_year = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, db_index=True)
    is_active = models.BooleanField(default=False, db_index=True)
    total_sales_this_year = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    total_sales_last_year = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='created_agreements',
        db_column='CreatedById'
    )
    last_modified_date = models.DateTimeField(auto_now=True)
    last_modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='modified_agreements',
        db_column='LastModifiedById'
    )

    class Meta:
        db_table = 'FrameAgreements'
        verbose_name = 'Frame Agreement'
        verbose_name_plural = 'Frame Agreements'
        indexes = [
            models.Index(fields=['start_date', 'end_date']),
        ]

    def save(self, *args, **kwargs):
        # Auto-derive start_year from start_date (replaces DB trigger)
        if self.start_date:
            self.start_year = self.start_date.year
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.account} — {self.agreement_type} ({self.start_date} to {self.end_date})"


class Target(models.Model):

    QUARTER_CHOICES = [
        ('Q1', 'Q1'),
        ('Q2', 'Q2'),
        ('Q3', 'Q3'),
        ('Q4', 'Q4'),
    ]

    id = models.CharField(max_length=18, primary_key=True)
    account = models.ForeignKey(
        'accounts.Account', on_delete=models.PROTECT,
        related_name='targets',
        db_column='AccountId', db_index=True
    )
    frame_agreement = models.ForeignKey(
        FrameAgreement, on_delete=models.CASCADE,
        related_name='targets',
        db_column='FrameAgreementId', db_index=True
    )
    quarter = models.CharField(max_length=2, choices=QUARTER_CHOICES, db_index=True)
    net_turnover_target = models.DecimalField(max_digits=18, decimal_places=2)
    rebate_rate = models.DecimalField(max_digits=5, decimal_places=2)
    rebate_if_achieved = models.DecimalField(max_digits=18, decimal_places=2)
    total_rebate = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='created_targets',
        db_column='CreatedById'
    )
    last_modified_date = models.DateTimeField(auto_now=True)
    last_modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='modified_targets',
        db_column='LastModifiedById'
    )

    class Meta:
        db_table = 'Targets'
        verbose_name = 'Target'
        verbose_name_plural = 'Targets'
        unique_together = [('frame_agreement', 'quarter')]

    def __str__(self):
        return f"{self.account} — {self.quarter} Target: {self.net_turnover_target}"
