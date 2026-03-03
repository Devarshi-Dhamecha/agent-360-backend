# Generated migration to align with DDL
# Updates Task model to remove FK and extra fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('campaigns', '0003_alter_task_tsk_what_id'),
    ]

    operations = [
        # Update Task.tsk_what_id from FK to CharField
        migrations.AlterField(
            model_name='task',
            name='tsk_what_id',
            field=models.CharField(blank=True, db_column='tsk_what_id', max_length=18, null=True, verbose_name='What ID'),
        ),
        # Remove Task indexes
        migrations.RemoveIndex(
            model_name='task',
            name='idx_tasks_what',
        ),
        # Add correct Task index
        migrations.AddIndex(
            model_name='task',
            index=models.Index(fields=['tsk_what_id'], name='idx_tasks_campaign'),
        ),
    ]
