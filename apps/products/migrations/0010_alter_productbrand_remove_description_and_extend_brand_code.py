# Generated migration to remove pb_description and extend pb_brand_code length

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0009_remove_orderlineitem_ori_quantity'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productbrand',
            name='pb_description',
        ),
        migrations.AlterField(
            model_name='productbrand',
            name='pb_brand_code',
            field=models.CharField(
                blank=True,
                db_column='pb_brand_code',
                max_length=255,
                null=True,
                verbose_name='Brand Code'
            ),
        ),
    ]
