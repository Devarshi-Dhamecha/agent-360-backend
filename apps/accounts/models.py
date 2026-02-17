# apps/accounts/models.py

from django.conf import settings
from django.db import models


class Account(models.Model):
    id = models.CharField(max_length=18, primary_key=True)
    name = models.CharField(max_length=255, db_index=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='owned_accounts',
        db_column='OwnerId', db_index=True
    )
    credit_limit = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    invoice_open_amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    order_open_amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    account_number = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    currency_iso_code = models.CharField(max_length=3, blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    last_modified_date = models.DateTimeField(auto_now=True, db_index=True)
    last_modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='modified_accounts',
        db_column='LastModifiedById'
    )

    class Meta:
        db_table = 'Accounts'
        verbose_name = 'Account'
        verbose_name_plural = 'Accounts'

    def __str__(self):
        return self.name


class AccountPlan(models.Model):

    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Closed', 'Closed'),
    ]

    id = models.CharField(max_length=18, primary_key=True)
    name = models.CharField(max_length=50)
    account = models.ForeignKey(
        Account, on_delete=models.CASCADE,
        related_name='plans',
        db_column='AccountId', db_index=True
    )
    account_plan_name = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, db_index=True)
    start_date = models.DateField(null=True, blank=True, db_index=True)
    end_date = models.DateField(null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='created_account_plans',
        db_column='CreatedById'
    )
    last_modified_date = models.DateTimeField(auto_now=True)
    last_modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='modified_account_plans',
        db_column='LastModifiedById'
    )

    class Meta:
        db_table = 'AccountPlans'
        verbose_name = 'Account Plan'
        verbose_name_plural = 'Account Plans'

    def __str__(self):
        return self.name
