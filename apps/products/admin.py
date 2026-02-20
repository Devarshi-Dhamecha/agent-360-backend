from django.contrib import admin
from .models import ProductBrand, Product, Invoice, InvoiceLineItem, ArfRollingForecast, Order, OrderLineItem


@admin.register(ProductBrand)
class ProductBrandAdmin(admin.ModelAdmin):
    list_display = ('pb_sf_id', 'pb_name', 'pb_brand_code', 'pb_is_active', 'pb_active')
    list_filter = ('pb_is_active', 'pb_active')
    search_fields = ('pb_name', 'pb_brand_code', 'pb_sf_id')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('prd_sf_id', 'prd_name', 'prd_family', 'prd_product_code', 'prd_is_active')
    list_filter = ('prd_family', 'prd_is_active', 'prd_active')
    search_fields = ('prd_name', 'prd_product_code', 'prd_central_product_code', 'prd_sf_id')


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('inv_sf_id', 'inv_name', 'inv_account_id', 'inv_invoice_date', 'inv_status', 'inv_net_price')
    list_filter = ('inv_status', 'inv_invoice_type', 'inv_active')
    search_fields = ('inv_name', 'inv_sf_id')
    date_hierarchy = 'inv_invoice_date'


@admin.register(InvoiceLineItem)
class InvoiceLineItemAdmin(admin.ModelAdmin):
    list_display = ('ili_sf_id', 'ili_invoice_id', 'ili_product_id', 'ili_quantity', 'ili_net_price', 'ili_status')
    list_filter = ('ili_status', 'ili_valid', 'ili_active')
    search_fields = ('ili_unique_line_code', 'ili_sf_id')


@admin.register(ArfRollingForecast)
class ArfRollingForecastAdmin(admin.ModelAdmin):
    list_display = ('arf_id', 'arf_name', 'arf_account_id', 'arf_status', 'arf_forecast_date', 'arf_sync_status')
    list_filter = ('arf_status', 'arf_sync_status', 'arf_active')
    search_fields = ('arf_name', 'arf_sf_id')
    date_hierarchy = 'arf_forecast_date'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('ord_sf_id', 'ord_order_number', 'ord_account_id', 'ord_status', 'ord_effective_date', 'ord_total_amount')
    list_filter = ('ord_status', 'ord_type', 'ord_active')
    search_fields = ('ord_order_number', 'ord_sf_id')
    date_hierarchy = 'ord_effective_date'


@admin.register(OrderLineItem)
class OrderLineItemAdmin(admin.ModelAdmin):
    list_display = ('ori_sf_id', 'ori_order_id', 'ori_product_id', 'ori_quantity', 'ori_unit_price', 'ori_total_price', 'ori_status')
    list_filter = ('ori_status', 'ori_active')
    search_fields = ('ori_sf_id', 'ori_product_name', 'ori_product_code')
