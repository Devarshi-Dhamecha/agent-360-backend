# Generated migration to align with DDL
# Updates FK constraints and indexes

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_user_idx_users_usage_company'),
    ]

    operations = [
        # Update RecordType.rt_last_modified_by_id from FK to CharField
        migrations.AlterField(
            model_name='recordtype',
            name='rt_last_modified_by_id',
            field=models.CharField(blank=True, db_column='rt_last_modified_by_id', max_length=18, null=True, verbose_name='Last Modified By ID'),
        ),
        # Update User indexes
        migrations.RemoveIndex(
            model_name='user',
            name='idx_users_federation_id',
        ),
        migrations.AddIndex(
            model_name='user',
            index=models.Index(fields=['usr_user_role_id'], name='idx_users_role'),
        ),
    ]
