# apps/forecasts/models.py

from django.conf import settings
from django.db import models


class Forecast(models.Model):

    STATUS_CHOICES = [
        ('Draft', 'Draft'),
        ('Submitted', 'Submitted'),
        ('Approved', 'Approved'),
        ('Revision Required', 'Revision Required'),
    ]

    id = models.CharField(max_length=18, primary_key=True)
    name = models.CharField(max_length=50)
    account = models.ForeignKey(
        'accounts.Account', on_delete=models.PROTECT,
        related_name='forecasts',
        db_column='AccountId', db_index=True
    )
    sales_rep = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='sales_forecasts',
        db_column='SalesRepId', db_index=True
    )
    product = models.ForeignKey(
        'products.Product', on_delete=models.PROTECT,
        related_name='forecasts',
        db_column='ProductId', db_index=True
    )
    forecast_date = models.DateField(db_index=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, db_index=True)
    quantity = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    revenue = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    currency_iso_code = models.CharField(max_length=3, blank=True, null=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='owned_forecasts',
        db_column='OwnerId'
    )
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='created_forecasts',
        db_column='CreatedById'
    )
    last_modified_date = models.DateTimeField(auto_now=True)
    last_modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='modified_forecasts',
        db_column='LastModifiedById'
    )

    class Meta:
        db_table = 'Forecasts'
        verbose_name = 'Forecast'
        verbose_name_plural = 'Forecasts'

    def __str__(self):
        return f"{self.name} — {self.account} / {self.product} ({self.forecast_date})"
