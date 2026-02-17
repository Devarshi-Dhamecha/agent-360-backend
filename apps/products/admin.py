from django.contrib import admin
from .models import ProductBrand, Product


@admin.register(ProductBrand)
class ProductBrandAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'is_active', 'created_date']
    search_fields = ['name']
    list_filter = ['is_active', 'created_date']
    readonly_fields = ['created_date', 'last_modified_date']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'product_code', 'family', 'product_brand', 'is_active']
    search_fields = ['name', 'product_code', 'central_product_code']
    list_filter = ['is_active', 'family', 'product_brand']
    raw_id_fields = ['product_brand', 'created_by', 'last_modified_by']
    readonly_fields = ['created_date', 'last_modified_date']
