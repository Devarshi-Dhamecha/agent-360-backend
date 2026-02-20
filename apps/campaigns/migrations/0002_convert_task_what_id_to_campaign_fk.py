# Convert Task.tsk_what_id from CharField to ForeignKey to Campaign

import django.db.models.deletion
from django.db import migrations, models


def cleanup_and_prepare_tsk_what_id(apps, schema_editor):
    """
    Clean up tsk_what_id to only contain valid Campaign IDs.
    This ensures data integrity before converting to ForeignKey.
    """
    Task = apps.get_model('campaigns', 'Task')
    Campaign = apps.get_model('campaigns', 'Campaign')
    
    valid_campaign_ids = set(Campaign.objects.values_list('cmp_sf_id', flat=True))
    
    # Null out any invalid or non-campaign references
    for task in Task.objects.all():
        if task.tsk_what_id and task.tsk_what_id not in valid_campaign_ids:
            task.tsk_what_id = None
            task.save(update_fields=['tsk_what_id'])


def reverse_to_charfield(apps, schema_editor):
    """Reverse migration - no data loss since we're keeping the same column."""
    pass


# Ensure FK constraint exists in database (idempotent)
ADD_FK_CONSTRAINT_SQL = """
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint c
    JOIN pg_class t ON t.oid = c.conrelid AND t.relname = 'tasks'
    JOIN pg_attribute a ON a.attrelid = c.conrelid
      AND a.attnum = ANY(c.conkey)
      AND a.attname = 'tsk_what_id'
    WHERE c.contype = 'f'
  ) THEN
    ALTER TABLE tasks
    ADD CONSTRAINT tasks_tsk_what_id_campaign_fk
    FOREIGN KEY (tsk_what_id) REFERENCES campaigns(cmp_sf_id) ON DELETE SET NULL;
  END IF;
END $$;
"""

DROP_FK_CONSTRAINT_SQL = """
ALTER TABLE tasks DROP CONSTRAINT IF EXISTS tasks_tsk_what_id_campaign_fk;
"""


class Migration(migrations.Migration):

    dependencies = [
        ('campaigns', '0001_initial'),
    ]

    operations = [
        # Step 1: Clean up invalid data
        migrations.RunPython(
            cleanup_and_prepare_tsk_what_id,
            reverse_to_charfield,
        ),
        
        # Step 2: Convert CharField to ForeignKey
        migrations.AlterField(
            model_name='task',
            name='tsk_what_id',
            field=models.ForeignKey(
                blank=True,
                db_column='tsk_what_id',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='tasks',
                to='campaigns.campaign',
                to_field='cmp_sf_id',
                verbose_name='Campaign',
            ),
        ),
        
        # Step 3: Ensure FK constraint exists in database
        # (Django's AlterField doesn't always create the actual DB constraint)
        migrations.RunSQL(
            ADD_FK_CONSTRAINT_SQL,
            DROP_FK_CONSTRAINT_SQL,
        ),
    ]
