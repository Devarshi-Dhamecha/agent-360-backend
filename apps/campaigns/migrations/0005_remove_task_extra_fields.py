# Generated migration to remove extra fields from Task model
# These fields were not in the DDL specification

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('campaigns', '0004_update_task_model_align_with_ddl'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='tsk_what_name',
        ),
        migrations.RemoveField(
            model_name='task',
            name='tsk_what_type',
        ),
    ]
