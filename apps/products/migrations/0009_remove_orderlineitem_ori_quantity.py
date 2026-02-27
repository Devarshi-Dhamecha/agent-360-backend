# Generated migration to remove ori_quantity field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0008_remove_arf_formula_fields'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderlineitem',
            name='ori_quantity',
        ),
    ]
