# Generated migration to align with DDL
# Removes AccountPlan model and updates FK constraints

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_alter_frameagreement_fa_agreement_type_and_more'),
    ]

    operations = [
        # Remove AccountPlan model
        migrations.DeleteModel(
            name='AccountPlan',
        ),
        # Update FrameAgreement.fa_last_modified_by_id from FK to CharField
        migrations.AlterField(
            model_name='frameagreement',
            name='fa_last_modified_by_id',
            field=models.CharField(blank=True, db_column='fa_last_modified_by_id', max_length=18, null=True, verbose_name='Last Modified By ID'),
        ),
        # Update Target.tgt_frame_agreement_id from FK to CharField
        migrations.AlterField(
            model_name='target',
            name='tgt_frame_agreement_id',
            field=models.CharField(db_column='tgt_frame_agreement_id', max_length=18, verbose_name='Frame Agreement ID'),
        ),
        # Update Account indexes
        migrations.RemoveIndex(
            model_name='account',
            name='idx_accounts_name',
        ),
        migrations.RemoveIndex(
            model_name='account',
            name='idx_accounts_number',
        ),
    ]
