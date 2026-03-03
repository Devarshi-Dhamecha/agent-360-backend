# Generated migration to align with DDL
# Updates FK constraints and indexes

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0011_remove_order_idx_orders_last_modified_and_more'),
    ]

    operations = [
        # Update Invoice.inv_frame_agreement_id from FK to CharField
        migrations.AlterField(
            model_name='invoice',
            name='inv_frame_agreement_id',
            field=models.CharField(blank=True, db_column='inv_frame_agreement_id', max_length=18, null=True, verbose_name='Frame Agreement ID'),
        ),
        # Update Order indexes
        migrations.RemoveIndex(
            model_name='order',
            name='idx_orders_account_id',
        ),
        migrations.RemoveIndex(
            model_name='order',
            name='idx_orders_owner_id',
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['ord_account_id'], name='idx_orders_account'),
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['ord_owner_id'], name='idx_orders_owner'),
        ),
        # Update Product indexes
        migrations.RemoveIndex(
            model_name='product',
            name='idx_products_family',
        ),
    ]
