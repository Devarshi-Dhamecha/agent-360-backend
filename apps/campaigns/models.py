# apps/campaigns/models.py

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class RecordType(models.Model):
    id = models.CharField(max_length=18, primary_key=True)
    name = models.CharField(max_length=255)
    developer_name = models.CharField(max_length=255)
    sobject_type = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'RecordTypes'
        verbose_name = 'Record Type'
        verbose_name_plural = 'Record Types'

    def __str__(self):
        return self.name


class Campaign(models.Model):

    STATUS_CHOICES = [
        ('Planned', 'Planned'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    CAMPAIGN_TYPE_CHOICES = [
        ('Promotional', 'Promotional'),
        ('Tactical', 'Tactical'),
        ('Strategic', 'Strategic'),
    ]

    id = models.CharField(max_length=18, primary_key=True)
    name = models.CharField(max_length=80)
    record_type = models.ForeignKey(
        RecordType, on_delete=models.PROTECT,
        db_column='RecordTypeId', db_index=True
    )
    type = models.CharField(max_length=255, choices=CAMPAIGN_TYPE_CHOICES, blank=True, null=True)
    parent = models.ForeignKey(
        'self', on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='sub_campaigns',
        db_column='ParentId', db_index=True
    )
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, db_index=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='created_campaigns',
        db_column='CreatedById'
    )
    last_modified_date = models.DateTimeField(auto_now=True)
    last_modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='modified_campaigns',
        db_column='LastModifiedById'
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='owned_campaigns',
        db_column='OwnerId', db_index=True
    )

    class Meta:
        db_table = 'Campaigns'
        verbose_name = 'Campaign'
        verbose_name_plural = 'Campaigns'
        indexes = [
            models.Index(fields=['start_date', 'end_date']),
        ]

    def __str__(self):
        return self.name


class Task(models.Model):

    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    PRIORITY_CHOICES = [
        ('High', 'High'),
        ('Normal', 'Normal'),
        ('Low', 'Low'),
    ]

    id = models.CharField(max_length=18, primary_key=True)

    # Polymorphic FK — relates to Campaign, Account, or Case
    what_content_type = models.ForeignKey(
        ContentType, on_delete=models.SET_NULL,
        null=True, blank=True,
        db_column='WhatContentTypeId'
    )
    what_id = models.CharField(max_length=18, null=True, blank=True, db_index=True, db_column='WhatId')
    what_object = GenericForeignKey('what_content_type', 'what_id')

    activity_date = models.DateField(null=True, blank=True, db_index=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, db_index=True)
    priority = models.CharField(max_length=50, choices=PRIORITY_CHOICES, null=True, blank=True)
    subject = models.CharField(max_length=255)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='tasks',
        db_column='OwnerId', db_index=True
    )
    description = models.TextField(blank=True, null=True)
    is_closed = models.BooleanField(default=False, db_index=True)
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='created_tasks',
        db_column='CreatedById'
    )
    last_modified_date = models.DateTimeField(auto_now=True)
    last_modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='modified_tasks',
        db_column='LastModifiedById'
    )

    class Meta:
        db_table = 'Tasks'
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'

    def __str__(self):
        return self.subject
