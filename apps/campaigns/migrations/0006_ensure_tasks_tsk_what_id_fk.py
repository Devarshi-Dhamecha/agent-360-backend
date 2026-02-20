# Ensure FK exists in DB: tasks.tsk_what_id -> campaigns.cmp_sf_id
# Run again so any DB that missed it gets the constraint (idempotent).

from django.db import migrations

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
        ("campaigns", "0005_add_tasks_tsk_what_id_fk"),
    ]

    operations = [
        migrations.RunSQL(ADD_FK_SQL, REMOVE_FK_SQL),
    ]
