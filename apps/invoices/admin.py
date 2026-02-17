from django.contrib import admin
from .models import Invoice, InvoiceLineItem


class InvoiceLineItemInline(admin.TabularInline):
    model = InvoiceLineItem
    extra = 0
    raw_id_fields = ['product', 'created_by', 'last_modified_by']
    readonly_fields = ['created_date', 'last_modified_date']


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['id', 'invoice_number', 'account', 'invoice_date', 'invoice_type', 'status', 'net_price']
    search_fields = ['invoice_number', 'account__name']
    list_filter = ['status', 'invoice_type', 'invoice_year']
    raw_id_fields = ['account', 'created_by', 'last_modified_by']
    readonly_fields = ['invoice_year', 'created_date', 'last_modified_date']
    inlines = [InvoiceLineItemInline]


@admin.register(InvoiceLineItem)
class InvoiceLineItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'invoice', 'product', 'quantity', 'unit_price', 'net_price', 'status', 'is_valid']
    search_fields = ['invoice__invoice_number', 'product__name', 'unique_line_code']
    list_filter = ['status', 'is_valid']
    raw_id_fields = ['invoice', 'product', 'created_by', 'last_modified_by']
    readonly_fields = ['created_date', 'last_modified_date']
