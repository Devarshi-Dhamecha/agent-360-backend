# Generated migration to align with DDL
# Updates FK constraints and indexes

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cases', '0002_alter_casehistory_ch_created_by_id'),
    ]

    operations = [
        # Update CaseComment.cc_sf_created_by_id from FK to CharField
        migrations.AlterField(
            model_name='casecomment',
            name='cc_sf_created_by_id',
            field=models.CharField(blank=True, db_column='cc_sf_created_by_id', max_length=18, null=True, verbose_name='SF Created By ID'),
        ),
        # Update CaseHistory.ch_created_by_id from FK to CharField
        migrations.AlterField(
            model_name='casehistory',
            name='ch_created_by_id',
            field=models.CharField(db_column='ch_created_by_id', max_length=18, verbose_name='Created By ID'),
        ),
        # Update Case indexes
        migrations.RemoveIndex(
            model_name='case',
            name='idx_cases_owner',
        ),
        # Remove CaseComment retry_count index
        migrations.RemoveIndex(
            model_name='casecomment',
            name='idx_case_comments_retry_count',
        ),
    ]
