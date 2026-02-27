# Generated migration to remove calculated value fields from ArfRollingForecast
# Values are now calculated on-the-fly as quantity * unit_price

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0006_order_ord_delivered_amount_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='arfrollingforecast',
            name='arf_draft_value',
        ),
        migrations.RemoveField(
            model_name='arfrollingforecast',
            name='arf_pending_value',
        ),
        migrations.RemoveField(
            model_name='arfrollingforecast',
            name='arf_approved_value',
        ),
    ]
