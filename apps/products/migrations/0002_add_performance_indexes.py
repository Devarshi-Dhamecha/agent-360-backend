"""
Migration to add indexes for product performance queries.

This migration adds indexes only if they don't already exist to optimize
the product performance variance API queries.
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        # Invoice indexes
        migrations.RunSQL(
            sql="""
                CREATE INDEX IF NOT EXISTS idx_invoices_invoice_date 
                ON invoices(inv_invoice_date);
            """,
            reverse_sql="DROP INDEX IF EXISTS idx_invoices_invoice_date;",
        ),
        migrations.RunSQL(
            sql="""
                CREATE INDEX IF NOT EXISTS idx_invoices_status 
                ON invoices(inv_status);
            """,
            reverse_sql="DROP INDEX IF EXISTS idx_invoices_status;",
        ),
        migrations.RunSQL(
            sql="""
                CREATE INDEX IF NOT EXISTS idx_invoices_valid 
                ON invoices(inv_valid);
            """,
            reverse_sql="DROP INDEX IF EXISTS idx_invoices_valid;",
        ),
        migrations.RunSQL(
            sql="""
                CREATE INDEX IF NOT EXISTS idx_invoices_invoice_type 
                ON invoices(inv_invoice_type);
            """,
            reverse_sql="DROP INDEX IF EXISTS idx_invoices_invoice_type;",
        ),
        
        # Invoice line items indexes
        migrations.RunSQL(
            sql="""
                CREATE INDEX IF NOT EXISTS idx_invoice_line_items_valid 
                ON invoice_line_items(ili_valid);
            """,
            reverse_sql="DROP INDEX IF EXISTS idx_invoice_line_items_valid;",
        ),
        
        # ARF Rolling Forecast indexes
        migrations.RunSQL(
            sql="""
                CREATE INDEX IF NOT EXISTS idx_arf_forecast_date 
                ON arf_rolling_forecasts(arf_forecast_date);
            """,
            reverse_sql="DROP INDEX IF EXISTS idx_arf_forecast_date;",
        ),
        migrations.RunSQL(
            sql="""
                CREATE INDEX IF NOT EXISTS idx_arf_status 
                ON arf_rolling_forecasts(arf_status);
            """,
            reverse_sql="DROP INDEX IF EXISTS idx_arf_status;",
        ),
    ]
