# apps/invoices/models.py

from django.conf import settings
from django.db import models


class Invoice(models.Model):

    STATUS_CHOICES = [
        ('Draft', 'Draft'),
        ('Open', 'Open'),
        ('Closed', 'Closed'),
        ('Cancelled', 'Cancelled'),
    ]

    INVOICE_TYPE_CHOICES = [
        ('Invoice', 'Invoice'),
        ('Credit Note', 'Credit Note'),
    ]

    id = models.CharField(max_length=18, primary_key=True)
    invoice_number = models.CharField(max_length=100)
    account = models.ForeignKey(
        'accounts.Account', on_delete=models.PROTECT,
        related_name='invoices',
        db_column='AccountId', db_index=True
    )
    invoice_date = models.DateField(db_index=True)
    invoice_year = models.CharField(max_length=4, blank=True, null=True, db_index=True)
    invoice_type = models.CharField(max_length=50, choices=INVOICE_TYPE_CHOICES, db_index=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, db_index=True)
    net_price = models.DecimalField(max_digits=18, decimal_places=2)
    total_vat = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    total_invoice_value = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    currency_iso_code = models.CharField(max_length=3, blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='created_invoices',
        db_column='CreatedById'
    )
    last_modified_date = models.DateTimeField(auto_now=True, db_index=True)
    last_modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='modified_invoices',
        db_column='LastModifiedById'
    )

    class Meta:
        db_table = 'Invoices'
        verbose_name = 'Invoice'
        verbose_name_plural = 'Invoices'

    def save(self, *args, **kwargs):
        # Auto-derive invoice_year from invoice_date (replaces DB trigger)
        if self.invoice_date:
            self.invoice_year = str(self.invoice_date.year)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.invoice_number


class InvoiceLineItem(models.Model):

    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Cancelled', 'Cancelled'),
    ]

    id = models.CharField(max_length=18, primary_key=True)
    invoice = models.ForeignKey(
        Invoice, on_delete=models.CASCADE,
        related_name='line_items',
        db_column='InvoiceId', db_index=True
    )
    product = models.ForeignKey(
        'products.Product', on_delete=models.PROTECT,
        related_name='invoice_lines',
        db_column='ProductId', db_index=True
    )
    quantity = models.DecimalField(max_digits=18, decimal_places=2)
    unit_price = models.DecimalField(max_digits=18, decimal_places=2)
    net_price = models.DecimalField(max_digits=18, decimal_places=2)
    vat = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    unique_line_code = models.CharField(max_length=255, unique=True, db_index=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    is_valid = models.BooleanField(default=True, db_index=True)
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='created_line_items',
        db_column='CreatedById'
    )
    last_modified_date = models.DateTimeField(auto_now=True)
    last_modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='modified_line_items',
        db_column='LastModifiedById'
    )

    class Meta:
        db_table = 'InvoiceLineItems'
        verbose_name = 'Invoice Line Item'
        verbose_name_plural = 'Invoice Line Items'

    def __str__(self):
        return f"{self.invoice} — {self.product} x {self.quantity}"
