from django.db import migrations, models


def cleanup_tsk_what_id(apps, schema_editor):
    """
    Ensure tsk_what_id only contains valid Campaign IDs before adding FK.
    """
    Task = apps.get_model("campaigns", "Task")
    Campaign = apps.get_model("campaigns", "Campaign")

    valid_ids = set(Campaign.objects.values_list("cmp_sf_id", flat=True))

    # Null out any non-campaign or invalid references to satisfy FK constraint
    for task in Task.objects.all():
        value = getattr(task, "tsk_what_id", None)
        if not value or value not in valid_ids:
            setattr(task, "tsk_what_id", None)
            task.save(update_fields=["tsk_what_id"])


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("campaigns", "0002_task_tsk_campaign_id"),
    ]

    operations = [
        # First, clean up invalid data
        migrations.RunPython(cleanup_tsk_what_id, noop_reverse),
        # Then drop the extra FK we no longer need
        migrations.RemoveIndex(
            model_name="task",
            name="idx_tasks_campaign",
        ),
        migrations.RemoveField(
            model_name="task",
            name="tsk_campaign_id",
        ),
        # Finally, turn tsk_what_id into an actual FK to Campaign.cmp_sf_id
        migrations.AlterField(
            model_name="task",
            name="tsk_what_id",
            field=models.ForeignKey(
                blank=True,
                db_column="tsk_what_id",
                null=True,
                on_delete=models.SET_NULL,
                related_name="tasks",
                to="campaigns.campaign",
                to_field="cmp_sf_id",
                verbose_name="Campaign",
            ),
        ),
    ]

