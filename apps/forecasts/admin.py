from django.contrib import admin
from .models import Forecast


@admin.register(Forecast)
class ForecastAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'account', 'product', 'sales_rep', 'forecast_date', 'status', 'quantity', 'revenue']
    search_fields = ['name', 'account__name', 'product__name']
    list_filter = ['status', 'forecast_date']
    raw_id_fields = ['account', 'sales_rep', 'product', 'owner', 'created_by', 'last_modified_by']
    readonly_fields = ['created_date', 'last_modified_date']
