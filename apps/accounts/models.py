from django.db import models


class Account(models.Model):
    """Salesforce Account - represents customer accounts"""
    acc_sf_id = models.CharField(
        max_length=18, 
        primary_key=True, 
        db_column='acc_sf_id',
        verbose_name='Salesforce ID'
    )
    acc_name = models.CharField(
        max_length=255, 
        db_column='acc_name',
        verbose_name='Account Name'
    )
    acc_owner_id = models.ForeignKey(
        'users.User',
        to_field='usr_sf_id',
        on_delete=models.RESTRICT,
        db_column='acc_owner_id',
        verbose_name='Owner'
    )
    acc_credit_limit = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
        db_column='acc_credit_limit',
        verbose_name='Credit Limit'
    )
    acc_invoice_open_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
        db_column='acc_invoice_open_amount',
        verbose_name='Invoice Open Amount'
    )
    acc_order_open_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
        db_column='acc_order_open_amount',
        verbose_name='Order Open Amount'
    )
    acc_account_number = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_column='acc_account_number',
        verbose_name='Account Number'
    )
    acc_currency_iso_code = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        db_column='acc_currency_iso_code',
        verbose_name='Currency ISO Code'
    )
    acc_last_modified_date = models.DateTimeField(
        db_column='acc_last_modified_date',
        verbose_name='Last Modified Date'
    )
    acc_last_modified_by_id = models.CharField(
        max_length=18,
        db_column='acc_last_modified_by_id',
        verbose_name='Last Modified By ID'
    )
    acc_active = models.SmallIntegerField(
        default=1,
        db_column='acc_active',
        verbose_name='Active Flag'
    )
    acc_created_at = models.DateTimeField(
        auto_now_add=True,
        db_column='acc_created_at',
        verbose_name='Created At'
    )
    acc_updated_at = models.DateTimeField(
        auto_now=True,
        db_column='acc_updated_at',
        verbose_name='Updated At'
    )

    class Meta:
        db_table = 'accounts'
        verbose_name = 'Account'
        verbose_name_plural = 'Accounts'
        indexes = [
            models.Index(fields=['acc_owner_id'], name='idx_accounts_owner'),
            models.Index(fields=['acc_name'], name='idx_accounts_name'),
            models.Index(fields=['acc_account_number'], name='idx_accounts_number'),
            models.Index(fields=['acc_active'], name='idx_accounts_active'),
        ]

    def __str__(self):
        return self.acc_name


class AccountPlan(models.Model):
    """Salesforce Account Plan - strategic planning for accounts"""
    ap_sf_id = models.CharField(
        max_length=18,
        primary_key=True,
        db_column='ap_sf_id',
        verbose_name='Salesforce ID'
    )
    ap_name = models.CharField(
        max_length=80,
        db_column='ap_name',
        verbose_name='Name'
    )
    ap_account_id = models.ForeignKey(
        'accounts.Account',
        to_field='acc_sf_id',
        on_delete=models.CASCADE,
        db_column='ap_account_id',
        verbose_name='Account'
    )
    ap_plan_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_column='ap_plan_name',
        verbose_name='Plan Name'
    )
    ap_status = models.CharField(
        max_length=100,
        db_column='ap_status',
        verbose_name='Status'
    )
    ap_start_date = models.DateField(
        null=True,
        blank=True,
        db_column='ap_start_date',
        verbose_name='Start Date'
    )
    ap_end_date = models.DateField(
        null=True,
        blank=True,
        db_column='ap_end_date',
        verbose_name='End Date'
    )
    ap_sf_created_date = models.DateTimeField(
        db_column='ap_sf_created_date',
        verbose_name='SF Created Date'
    )
    ap_last_modified_date = models.DateTimeField(
        db_column='ap_last_modified_date',
        verbose_name='Last Modified Date'
    )
    ap_last_modified_by_id = models.CharField(
        max_length=18,
        db_column='ap_last_modified_by_id',
        verbose_name='Last Modified By ID'
    )
    ap_active = models.SmallIntegerField(
        default=1,
        db_column='ap_active',
        verbose_name='Active Flag'
    )
    ap_created_at = models.DateTimeField(
        auto_now_add=True,
        db_column='ap_created_at',
        verbose_name='Created At'
    )
    ap_updated_at = models.DateTimeField(
        auto_now=True,
        db_column='ap_updated_at',
        verbose_name='Updated At'
    )

    class Meta:
        db_table = 'account_plans'
        verbose_name = 'Account Plan'
        verbose_name_plural = 'Account Plans'
        indexes = [
            models.Index(fields=['ap_account_id'], name='idx_account_plans_account'),
        ]

    def __str__(self):
        return self.ap_name


class FrameAgreement(models.Model):
    """Frame Agreement - rebate and sales target agreements with accounts"""
    fa_sf_id = models.CharField(
        max_length=18,
        primary_key=True,
        db_column='fa_sf_id',
        verbose_name='Salesforce ID'
    )
    fa_account_id = models.ForeignKey(
        'accounts.Account',
        to_field='acc_sf_id',
        on_delete=models.CASCADE,
        db_column='fa_account_id',
        verbose_name='Account'
    )
    fa_agreement_type = models.CharField(
        max_length=100,
        db_column='fa_agreement_type',
        verbose_name='Agreement Type'
    )
    fa_start_date = models.DateField(
        db_column='fa_start_date',
        verbose_name='Start Date'
    )
    fa_end_date = models.DateField(
        db_column='fa_end_date',
        verbose_name='End Date'
    )
    fa_start_year = models.IntegerField(
        null=True,
        blank=True,
        db_column='fa_start_year',
        verbose_name='Start Year'
    )
    fa_status = models.CharField(
        max_length=100,
        db_column='fa_status',
        verbose_name='Status'
    )
    fa_is_active = models.BooleanField(
        null=True,
        blank=True,
        db_column='fa_is_active',
        verbose_name='Is Active'
    )
    fa_total_sales_ty = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
        db_column='fa_total_sales_ty',
        verbose_name='Total Sales This Year'
    )
    fa_total_sales_ly = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
        db_column='fa_total_sales_ly',
        verbose_name='Total Sales Last Year'
    )
    fa_total_sales_q1 = models.DecimalField(
        max_digits=18,
        decimal_places=0,
        null=True,
        blank=True,
        db_column='fa_total_sales_q1',
        verbose_name='Total Sales Q1'
    )
    fa_total_sales_q2 = models.DecimalField(
        max_digits=18,
        decimal_places=0,
        null=True,
        blank=True,
        db_column='fa_total_sales_q2',
        verbose_name='Total Sales Q2'
    )
    fa_total_sales_q3 = models.DecimalField(
        max_digits=18,
        decimal_places=0,
        null=True,
        blank=True,
        db_column='fa_total_sales_q3',
        verbose_name='Total Sales Q3'
    )
    fa_total_sales_q4 = models.DecimalField(
        max_digits=18,
        decimal_places=0,
        null=True,
        blank=True,
        db_column='fa_total_sales_q4',
        verbose_name='Total Sales Q4'
    )
    fa_rebate_achieved = models.DecimalField(
        max_digits=6,
        decimal_places=4,
        null=True,
        blank=True,
        db_column='fa_rebate_achieved',
        verbose_name='Rebate Achieved'
    )
    fa_total_rebate_achieved = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
        db_column='fa_total_rebate_achieved',
        verbose_name='Total Rebate Achieved'
    )
    fa_last_modified_date = models.DateTimeField(
        db_column='fa_last_modified_date',
        verbose_name='Last Modified Date'
    )
    fa_last_modified_by_id = models.ForeignKey(
        'users.User',
        to_field='usr_sf_id',
        on_delete=models.RESTRICT,
        db_column='fa_last_modified_by_id',
        verbose_name='Last Modified By'
    )
    fa_active = models.SmallIntegerField(
        default=1,
        db_column='fa_active',
        verbose_name='Active Flag'
    )
    fa_created_at = models.DateTimeField(
        auto_now_add=True,
        db_column='fa_created_at',
        verbose_name='Created At'
    )
    fa_updated_at = models.DateTimeField(
        auto_now=True,
        db_column='fa_updated_at',
        verbose_name='Updated At'
    )

    class Meta:
        db_table = 'frame_agreements'
        verbose_name = 'Frame Agreement'
        verbose_name_plural = 'Frame Agreements'
        indexes = [
            models.Index(fields=['fa_account_id'], name='idx_frame_agreements_account'),
            models.Index(fields=['fa_status'], name='idx_frame_agreements_status'),
        ]

    def __str__(self):
        return f"FA: {self.fa_account_id} ({self.fa_start_date} - {self.fa_end_date})"


class Target(models.Model):
    """Quarterly sales targets linked to frame agreements"""
    tgt_sf_id = models.CharField(
        max_length=18,
        primary_key=True,
        db_column='tgt_sf_id',
        verbose_name='Salesforce ID'
    )
    tgt_account_id = models.ForeignKey(
        'accounts.Account',
        to_field='acc_sf_id',
        on_delete=models.CASCADE,
        db_column='tgt_account_id',
        verbose_name='Account'
    )
    tgt_frame_agreement_id = models.ForeignKey(
        'accounts.FrameAgreement',
        to_field='fa_sf_id',
        on_delete=models.CASCADE,
        db_column='tgt_frame_agreement_id',
        verbose_name='Frame Agreement'
    )
    tgt_quarter = models.CharField(
        max_length=100,
        db_column='tgt_quarter',
        verbose_name='Quarter'
    )
    tgt_net_turnover_target = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        db_column='tgt_net_turnover_target',
        verbose_name='Net Turnover Target'
    )
    tgt_rebate_rate = models.DecimalField(
        max_digits=6,
        decimal_places=4,
        db_column='tgt_rebate_rate',
        verbose_name='Rebate Rate'
    )
    tgt_rebate_if_achieved = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        db_column='tgt_rebate_if_achieved',
        verbose_name='Rebate If Achieved'
    )
    tgt_total_rebate = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
        db_column='tgt_total_rebate',
        verbose_name='Total Rebate'
    )
    tgt_last_modified_date = models.DateTimeField(
        db_column='tgt_last_modified_date',
        verbose_name='Last Modified Date'
    )
    tgt_last_modified_by_id = models.CharField(
        max_length=18,
        db_column='tgt_last_modified_by_id',
        verbose_name='Last Modified By ID'
    )
    tgt_active = models.SmallIntegerField(
        default=1,
        db_column='tgt_active',
        verbose_name='Active Flag'
    )
    tgt_created_at = models.DateTimeField(
        auto_now_add=True,
        db_column='tgt_created_at',
        verbose_name='Created At'
    )
    tgt_updated_at = models.DateTimeField(
        auto_now=True,
        db_column='tgt_updated_at',
        verbose_name='Updated At'
    )

    class Meta:
        db_table = 'targets'
        verbose_name = 'Target'
        verbose_name_plural = 'Targets'
        indexes = [
            models.Index(fields=['tgt_account_id'], name='idx_targets_account'),
            models.Index(fields=['tgt_frame_agreement_id'], name='idx_targets_frame_agreement'),
        ]

    def __str__(self):
        return f"Target: {self.tgt_account_id} - {self.tgt_quarter}"
