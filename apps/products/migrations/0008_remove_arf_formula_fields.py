# Generated migration to remove unused formula fields from ArfRollingForecast

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0007_remove_arf_value_fields'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='arfrollingforecast',
            name='arf_product_formula',
        ),
        migrations.RemoveField(
            model_name='arfrollingforecast',
            name='arf_account_or_user_formula',
        ),
    ]
