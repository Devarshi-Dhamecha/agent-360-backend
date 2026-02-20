# Add explicit FK constraint: tasks.tsk_what_id -> campaigns.cmp_sf_id
# (ensures the constraint exists in the DB even if AlterField didn't create it)

from django.db import migrations


# Add FK only if no FK on tasks.tsk_what_id exists yet (idempotent)
ADD_FK_SQL = """
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

REMOVE_FK_SQL = """
ALTER TABLE tasks DROP CONSTRAINT IF EXISTS tasks_tsk_what_id_campaign_fk;
"""


class Migration(migrations.Migration):

    dependencies = [
        ("campaigns", "0004_alter_task_tsk_what_id"),
    ]

    operations = [
        migrations.RunSQL(ADD_FK_SQL, REMOVE_FK_SQL, state_operations=[]),
    ]
