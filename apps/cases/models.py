# apps/cases/models.py

from django.conf import settings
from django.db import models


class Case(models.Model):

    STATUS_CHOICES = [
        ('New', 'New'),
        ('In Progress', 'In Progress'),
        ('Escalated', 'Escalated'),
        ('Resolved', 'Resolved'),
        ('Closed', 'Closed'),
    ]

    PRIORITY_CHOICES = [
        ('High', 'High'),
        ('Medium', 'Medium'),
        ('Low', 'Low'),
    ]

    id = models.CharField(max_length=18, primary_key=True)
    case_number = models.CharField(max_length=50, unique=True, db_index=True)
    subject = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, null=True, blank=True, db_index=True)
    account = models.ForeignKey(
        'accounts.Account', on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='cases',
        db_column='AccountId', db_index=True
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='owned_cases',
        db_column='OwnerId', db_index=True
    )
    priority = models.CharField(max_length=50, choices=PRIORITY_CHOICES, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    is_closed = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True, db_index=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='created_cases',
        db_column='CreatedById'
    )
    last_modified_date = models.DateTimeField(auto_now=True)
    last_modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='modified_cases',
        db_column='LastModifiedById'
    )

    class Meta:
        db_table = 'Cases'
        verbose_name = 'Case'
        verbose_name_plural = 'Cases'

    def __str__(self):
        return f"[{self.case_number}] {self.subject}"


class CaseHistory(models.Model):
    id = models.CharField(max_length=18, primary_key=True)
    case = models.ForeignKey(
        Case, on_delete=models.CASCADE,
        related_name='history',
        db_column='CaseId', db_index=True
    )
    field = models.CharField(max_length=255)
    old_value = models.TextField(blank=True, null=True)
    new_value = models.TextField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True, db_index=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='case_history_entries',
        db_column='CreatedById'
    )

    class Meta:
        db_table = 'CaseHistories'
        verbose_name = 'Case History'
        verbose_name_plural = 'Case Histories'
        ordering = ['-created_date']

    def __str__(self):
        return f"Case {self.case_id} — {self.field} changed"


class CaseComment(models.Model):
    id = models.CharField(max_length=18, primary_key=True)
    case = models.ForeignKey(
        Case, on_delete=models.CASCADE,
        related_name='comments',
        db_column='CaseId', db_index=True
    )
    comment_body = models.TextField(blank=True, null=True)
    is_published = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True, db_index=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='case_comments',
        db_column='CreatedById'
    )
    last_modified_date = models.DateTimeField(auto_now=True)
    last_modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='modified_case_comments',
        db_column='LastModifiedById'
    )

    class Meta:
        db_table = 'CaseComments'
        verbose_name = 'Case Comment'
        verbose_name_plural = 'Case Comments'
        ordering = ['created_date']

    def __str__(self):
        return f"Comment on Case {self.case_id}"
