# Generated manually for Task -> Campaign FK (tsk_campaign_id -> cmp_sf_id)

import django.db.models.deletion
from django.db import migrations, models


def backfill_tsk_campaign_id(apps, schema_editor):
    """Set tsk_campaign_id from tsk_what_id where tsk_what_type = 'Campaign'."""
    Task = apps.get_model('campaigns', 'Task')
    Campaign = apps.get_model('campaigns', 'Campaign')
    campaign_ids = set(Campaign.objects.values_list('cmp_sf_id', flat=True))
    for task in Task.objects.filter(tsk_what_type='Campaign', tsk_what_id__isnull=False):
        if task.tsk_what_id in campaign_ids:
            task.tsk_campaign_id_id = task.tsk_what_id
            task.save(update_fields=['tsk_campaign_id_id'])


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('campaigns', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='tsk_campaign_id',
            field=models.ForeignKey(
                blank=True,
                db_column='tsk_campaign_id',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='tasks',
                to='campaigns.campaign',
                to_field='cmp_sf_id',
                verbose_name='Campaign',
            ),
        ),
        migrations.AddIndex(
            model_name='task',
            index=models.Index(fields=['tsk_campaign_id'], name='idx_tasks_campaign'),
        ),
        migrations.RunPython(backfill_tsk_campaign_id, noop_reverse),
    ]
