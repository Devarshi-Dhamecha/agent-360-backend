from django.db import models


class ProductBrand(models.Model):
    """Product Brand - categorizes products by brand"""
    pb_sf_id = models.CharField(
        max_length=18,
        primary_key=True,
        db_column='pb_sf_id',
        verbose_name='Salesforce ID'
    )
    pb_name = models.CharField(
        max_length=255,
        db_column='pb_name',
        verbose_name='Brand Name'
    )
    pb_brand_code = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        db_column='pb_brand_code',
        verbose_name='Brand Code'
    )
    pb_description = models.TextField(
        null=True,
        blank=True,
        db_column='pb_description',
        verbose_name='Description'
    )
    pb_is_active = models.BooleanField(
        null=True,
        blank=True,
        db_column='pb_is_active',
        verbose_name='Is Active'
    )
    pb_sf_created_date = models.DateTimeField(
        db_column='pb_sf_created_date',
        verbose_name='SF Created Date'
    )
    pb_last_modified_date = models.DateTimeField(
        db_column='pb_last_modified_date',
        verbose_name='Last Modified Date'
    )
    pb_active = models.SmallIntegerField(
        default=1,
        db_column='pb_active',
        verbose_name='Active Flag'
    )
    pb_created_at = models.DateTimeField(
        auto_now_add=True,
        db_column='pb_created_at',
        verbose_name='Created At'
    )
    pb_updated_at = models.DateTimeField(
        auto_now=True,
        db_column='pb_updated_at',
        verbose_name='Updated At'
    )

    class Meta:
        db_table = 'product_brands'
        verbose_name = 'Product Brand'
        verbose_name_plural = 'Product Brands'

    def __str__(self):
        return self.pb_name


class Product(models.Model):
    """Salesforce Product - represents sellable products"""
    prd_sf_id = models.CharField(
        max_length=18,
        primary_key=True,
        db_column='prd_sf_id',
        verbose_name='Salesforce ID'
    )
    prd_name = models.CharField(
        max_length=255,
        db_column='prd_name',
        verbose_name='Product Name'
    )
    prd_family = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        db_column='prd_family',
        verbose_name='Product Family'
    )
    prd_classification = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        db_column='prd_classification',
        verbose_name='Classification'
    )
    prd_central_product_code = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        db_column='prd_central_product_code',
        verbose_name='Central Product Code'
    )
    prd_product_code = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_column='prd_product_code',
        verbose_name='Product Code'
    )
    prd_product_brand_id = models.ForeignKey(
        'products.ProductBrand',
        to_field='pb_sf_id',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        db_column='prd_product_brand_id',
        verbose_name='Product Brand'
    )
    prd_brand = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        db_column='prd_brand',
        verbose_name='Brand'
    )
    prd_is_active = models.BooleanField(
        null=True,
        blank=True,
        db_column='prd_is_active',
        verbose_name='Is Active'
    )
    prd_sf_created_date = models.DateTimeField(
        db_column='prd_sf_created_date',
        verbose_name='SF Created Date'
    )
    prd_last_modified_date = models.DateTimeField(
        db_column='prd_last_modified_date',
        verbose_name='Last Modified Date'
    )
    prd_last_modified_by_id = models.CharField(
        max_length=18,
        db_column='prd_last_modified_by_id',
        verbose_name='Last Modified By ID'
    )
    prd_active = models.SmallIntegerField(
        default=1,
        db_column='prd_active',
        verbose_name='Active Flag'
    )
    prd_created_at = models.DateTimeField(
        auto_now_add=True,
        db_column='prd_created_at',
        verbose_name='Created At'
    )
    prd_updated_at = models.DateTimeField(
        auto_now=True,
        db_column='prd_updated_at',
        verbose_name='Updated At'
    )

    class Meta:
        db_table = 'products'
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        indexes = [
            models.Index(fields=['prd_family'], name='idx_products_family'),
            models.Index(fields=['prd_product_brand_id'], name='idx_products_brand'),
            models.Index(fields=['prd_product_code'], name='idx_products_code'),
            models.Index(fields=['prd_active'], name='idx_products_active'),
        ]

    def __str__(self):
        return self.prd_name


class Invoice(models.Model):
    """Salesforce Invoice - customer invoices"""
    inv_sf_id = models.CharField(
        max_length=18,
        primary_key=True,
        db_column='inv_sf_id',
        verbose_name='Salesforce ID'
    )
    inv_name = models.CharField(
        max_length=255,
        db_column='inv_name',
        verbose_name='Invoice Name'
    )
    inv_account_id = models.ForeignKey(
        'accounts.Account',
        to_field='acc_sf_id',
        on_delete=models.CASCADE,
        db_column='inv_account_id',
        verbose_name='Account'
    )
    inv_frame_agreement_id = models.ForeignKey(
        'accounts.FrameAgreement',
        to_field='fa_sf_id',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        db_column='inv_frame_agreement_id',
        verbose_name='Frame Agreement'
    )
    inv_invoice_date = models.DateField(
        db_column='inv_invoice_date',
        verbose_name='Invoice Date'
    )
    inv_invoice_year = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        db_column='inv_invoice_year',
        verbose_name='Invoice Year'
    )
    inv_invoice_type = models.CharField(
        max_length=100,
        db_column='inv_invoice_type',
        verbose_name='Invoice Type'
    )
    inv_status = models.CharField(
        max_length=100,
        db_column='inv_status',
        verbose_name='Status'
    )
    inv_net_price = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        db_column='inv_net_price',
        verbose_name='Net Price'
    )
    inv_total_vat = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
        db_column='inv_total_vat',
        verbose_name='Total VAT'
    )
    inv_total_invoice_value = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
        db_column='inv_total_invoice_value',
        verbose_name='Total Invoice Value'
    )
    inv_valid = models.BooleanField(
        null=True,
        blank=True,
        db_column='inv_valid',
        verbose_name='Valid'
    )
    inv_currency_iso_code = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        db_column='inv_currency_iso_code',
        verbose_name='Currency ISO Code'
    )
    inv_sf_created_date = models.DateTimeField(
        db_column='inv_sf_created_date',
        verbose_name='SF Created Date'
    )
    inv_last_modified_date = models.DateTimeField(
        db_column='inv_last_modified_date',
        verbose_name='Last Modified Date'
    )
    inv_last_modified_by_id = models.CharField(
        max_length=18,
        db_column='inv_last_modified_by_id',
        verbose_name='Last Modified By ID'
    )
    inv_active = models.SmallIntegerField(
        default=1,
        db_column='inv_active',
        verbose_name='Active Flag'
    )
    inv_created_at = models.DateTimeField(
        auto_now_add=True,
        db_column='inv_created_at',
        verbose_name='Created At'
    )
    inv_updated_at = models.DateTimeField(
        auto_now=True,
        db_column='inv_updated_at',
        verbose_name='Updated At'
    )

    class Meta:
        db_table = 'invoices'
        verbose_name = 'Invoice'
        verbose_name_plural = 'Invoices'
        indexes = [
            models.Index(fields=['inv_account_id'], name='idx_invoices_account'),
            models.Index(fields=['inv_invoice_date'], name='idx_invoices_date'),
            models.Index(fields=['inv_status'], name='idx_invoices_status'),
            models.Index(fields=['inv_frame_agreement_id'], name='idx_invoices_frame_agreement'),
        ]

    def __str__(self):
        return self.inv_name


class InvoiceLineItem(models.Model):
    """Invoice Line Item - individual line items on invoices"""
    ili_sf_id = models.CharField(
        max_length=18,
        primary_key=True,
        db_column='ili_sf_id',
        verbose_name='Salesforce ID'
    )
    ili_invoice_id = models.ForeignKey(
        'products.Invoice',
        to_field='inv_sf_id',
        on_delete=models.CASCADE,
        db_column='ili_invoice_id',
        verbose_name='Invoice'
    )
    ili_product_id = models.ForeignKey(
        'products.Product',
        to_field='prd_sf_id',
        on_delete=models.RESTRICT,
        db_column='ili_product_id',
        verbose_name='Product'
    )
    ili_quantity = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        db_column='ili_quantity',
        verbose_name='Quantity'
    )
    ili_unit_price = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        db_column='ili_unit_price',
        verbose_name='Unit Price'
    )
    ili_net_price = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        db_column='ili_net_price',
        verbose_name='Net Price'
    )
    ili_vat = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
        db_column='ili_vat',
        verbose_name='VAT'
    )
    ili_unique_line_code = models.CharField(
        max_length=255,
        unique=True,
        db_column='ili_unique_line_code',
        verbose_name='Unique Line Code'
    )
    ili_status = models.CharField(
        max_length=100,
        db_column='ili_status',
        verbose_name='Status'
    )
    ili_valid = models.BooleanField(
        db_column='ili_valid',
        verbose_name='Valid'
    )
    ili_sf_created_date = models.DateTimeField(
        db_column='ili_sf_created_date',
        verbose_name='SF Created Date'
    )
    ili_last_modified_date = models.DateTimeField(
        db_column='ili_last_modified_date',
        verbose_name='Last Modified Date'
    )
    ili_last_modified_by_id = models.CharField(
        max_length=18,
        db_column='ili_last_modified_by_id',
        verbose_name='Last Modified By ID'
    )
    ili_active = models.SmallIntegerField(
        default=1,
        db_column='ili_active',
        verbose_name='Active Flag'
    )
    ili_created_at = models.DateTimeField(
        auto_now_add=True,
        db_column='ili_created_at',
        verbose_name='Created At'
    )
    ili_updated_at = models.DateTimeField(
        auto_now=True,
        db_column='ili_updated_at',
        verbose_name='Updated At'
    )

    class Meta:
        db_table = 'invoice_line_items'
        verbose_name = 'Invoice Line Item'
        verbose_name_plural = 'Invoice Line Items'
        indexes = [
            models.Index(fields=['ili_invoice_id'], name='idx_invoice_line_items_invoice'),
            models.Index(fields=['ili_product_id'], name='idx_invoice_line_items_product'),
        ]

    def __str__(self):
        return f"{self.ili_invoice_id} - {self.ili_product_id}"


class ArfRollingForecast(models.Model):
    """ARF Rolling Forecast - sales forecasts created by users or AI agent"""
    
    STATUS_CHOICES = [
        ('Draft', 'Draft'),
        ('Pending_Approval', 'Pending Approval'),
        ('Approved', 'Approved'),
        ('Fixes_Needed', 'Fixes Needed'),
        ('Frozen', 'Frozen'),
    ]
    
    arf_id = models.AutoField(
        primary_key=True,
        db_column='arf_id',
        verbose_name='ID'
    )
    arf_sf_id = models.CharField(
        max_length=18,
        null=True,
        blank=True,
        unique=True,
        db_column='arf_sf_id',
        verbose_name='Salesforce ID'
    )
    arf_name = models.CharField(
        max_length=80,
        db_column='arf_name',
        verbose_name='Name'
    )
    arf_account_id = models.ForeignKey(
        'accounts.Account',
        to_field='acc_sf_id',
        on_delete=models.CASCADE,
        db_column='arf_account_id',
        verbose_name='Account'
    )
    arf_sales_rep_id = models.ForeignKey(
        'users.User',
        to_field='usr_sf_id',
        on_delete=models.RESTRICT,
        related_name='arf_sales_rep',
        db_column='arf_sales_rep_id',
        verbose_name='Sales Rep'
    )
    arf_product_id = models.ForeignKey(
        'products.Product',
        to_field='prd_sf_id',
        on_delete=models.RESTRICT,
        db_column='arf_product_id',
        verbose_name='Product'
    )
    arf_forecast_date = models.DateField(
        db_column='arf_forecast_date',
        verbose_name='Forecast Date'
    )
    arf_status = models.CharField(
        max_length=100,
        choices=STATUS_CHOICES,
        db_column='arf_status',
        verbose_name='Status'
    )
    arf_currency_iso_code = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        db_column='arf_currency_iso_code',
        verbose_name='Currency ISO Code'
    )
    arf_owner_id = models.ForeignKey(
        'users.User',
        to_field='usr_sf_id',
        on_delete=models.RESTRICT,
        related_name='arf_owner',
        db_column='arf_owner_id',
        verbose_name='Owner'
    )
    # Draft stage fields
    arf_draft_quantity = models.DecimalField(
        max_digits=16,
        decimal_places=2,
        null=True,
        blank=True,
        db_column='arf_draft_quantity',
        verbose_name='Draft Quantity'
    )
    arf_draft_unit_price = models.DecimalField(
        max_digits=16,
        decimal_places=2,
        null=True,
        blank=True,
        db_column='arf_draft_unit_price',
        verbose_name='Draft Unit Price'
    )
    arf_draft_value = models.DecimalField(
        max_digits=16,
        decimal_places=2,
        null=True,
        blank=True,
        db_column='arf_draft_value',
        verbose_name='Draft Value'
    )
    # Pending stage fields
    arf_pending_quantity = models.DecimalField(
        max_digits=16,
        decimal_places=2,
        null=True,
        blank=True,
        db_column='arf_pending_quantity',
        verbose_name='Pending Quantity'
    )
    arf_pending_unit_price = models.DecimalField(
        max_digits=16,
        decimal_places=2,
        null=True,
        blank=True,
        db_column='arf_pending_unit_price',
        verbose_name='Pending Unit Price'
    )
    arf_pending_value = models.DecimalField(
        max_digits=16,
        decimal_places=2,
        null=True,
        blank=True,
        db_column='arf_pending_value',
        verbose_name='Pending Value'
    )
    # Approved stage fields
    arf_approved_quantity = models.DecimalField(
        max_digits=16,
        decimal_places=2,
        null=True,
        blank=True,
        db_column='arf_approved_quantity',
        verbose_name='Approved Quantity'
    )
    arf_approved_unit_price = models.DecimalField(
        max_digits=16,
        decimal_places=2,
        null=True,
        blank=True,
        db_column='arf_approved_unit_price',
        verbose_name='Approved Unit Price'
    )
    arf_approved_value = models.DecimalField(
        max_digits=16,
        decimal_places=2,
        null=True,
        blank=True,
        db_column='arf_approved_value',
        verbose_name='Approved Value'
    )
    arf_rejection_reason = models.TextField(
        null=True,
        blank=True,
        db_column='arf_rejection_reason',
        verbose_name='Rejection Reason'
    )
    arf_product_formula = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_column='arf_product_formula',
        verbose_name='Product Formula'
    )
    arf_account_or_user_formula = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_column='arf_account_or_user_formula',
        verbose_name='Account or User Formula'
    )
    arf_product_family = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        db_column='arf_product_family',
        verbose_name='Product Family'
    )
    arf_product_brand = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        db_column='arf_product_brand',
        verbose_name='Product Brand'
    )
    # Salesforce audit fields
    arf_sf_created_by_id = models.ForeignKey(
        'users.User',
        to_field='usr_sf_id',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='arf_sf_created',
        db_column='arf_sf_created_by_id',
        verbose_name='SF Created By'
    )
    arf_last_modified_by_id = models.CharField(
        max_length=18,
        null=True,
        blank=True,
        db_column='arf_last_modified_by_id',
        verbose_name='Last Modified By ID'
    )
    # Agent360 audit fields
    arf_agent_modified_by = models.ForeignKey(
        'users.User',
        to_field='usr_sf_id',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='arf_agent_modified',
        db_column='arf_agent_modified_by',
        verbose_name='Agent Modified By'
    )
    arf_agent_modified_date = models.DateTimeField(
        null=True,
        blank=True,
        db_column='arf_agent_modified_date',
        verbose_name='Agent Modified Date'
    )
    arf_agent_created_by = models.ForeignKey(
        'users.User',
        to_field='usr_sf_id',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='arf_agent_created',
        db_column='arf_agent_created_by',
        verbose_name='Agent Created By'
    )
    arf_agent_created_date = models.DateTimeField(
        null=True,
        blank=True,
        db_column='arf_agent_created_date',
        verbose_name='Agent Created Date'
    )
    arf_agent360_source = models.BooleanField(
        null=True,
        blank=True,
        db_column='arf_agent360_source',
        verbose_name='Agent360 Source'
    )
    # Sync control fields
    arf_sync_status = models.SmallIntegerField(
        default=1,
        db_column='arf_sync_status',
        verbose_name='Sync Status'
    )
    arf_version = models.IntegerField(
        default=1,
        db_column='arf_version',
        verbose_name='Version'
    )
    arf_retry_count = models.IntegerField(
        default=0,
        db_column='arf_retry_count',
        verbose_name='Retry Count'
    )
    arf_last_sync_error = models.TextField(
        null=True,
        blank=True,
        db_column='arf_last_sync_error',
        verbose_name='Last Sync Error'
    )
    arf_active = models.SmallIntegerField(
        default=1,
        db_column='arf_active',
        verbose_name='Active Flag'
    )
    arf_created_at = models.DateTimeField(
        auto_now_add=True,
        db_column='arf_created_at',
        verbose_name='Created At'
    )
    arf_updated_at = models.DateTimeField(
        auto_now=True,
        db_column='arf_updated_at',
        verbose_name='Updated At'
    )

    class Meta:
        db_table = 'arf_rolling_forecasts'
        verbose_name = 'ARF Rolling Forecast'
        verbose_name_plural = 'ARF Rolling Forecasts'
        indexes = [
            models.Index(fields=['arf_account_id'], name='idx_arf_account'),
            models.Index(fields=['arf_sales_rep_id'], name='idx_arf_sales_rep'),
            models.Index(fields=['arf_product_id'], name='idx_arf_product'),
            models.Index(fields=['arf_status'], name='idx_arf_status'),
            models.Index(fields=['arf_forecast_date'], name='idx_arf_forecast_date'),
            models.Index(fields=['arf_sync_status'], name='idx_arf_sync_status'),
            models.Index(fields=['arf_retry_count'], name='idx_arf_retry_count'),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(arf_status__in=['Draft', 'Pending_Approval', 'Approved', 'Fixes_Needed', 'Frozen']),
                name='chk_arf_status'
            ),
        ]

    def __str__(self):
        return self.arf_name


class Order(models.Model):
    """Salesforce Order - customer orders"""
    ord_sf_id = models.CharField(
        max_length=18,
        primary_key=True,
        db_column='ord_sf_id',
        verbose_name='Salesforce ID'
    )
    ord_order_number = models.CharField(
        max_length=30,
        db_column='ord_order_number',
        verbose_name='Order Number'
    )
    ord_account_id = models.ForeignKey(
        'accounts.Account',
        to_field='acc_sf_id',
        on_delete=models.CASCADE,
        db_column='ord_account_id',
        verbose_name='Account'
    )
    ord_status = models.CharField(
        max_length=100,
        db_column='ord_status',
        verbose_name='Status'
    )
    ord_effective_date = models.DateField(
        db_column='ord_effective_date',
        verbose_name='Order Start Date'
    )
    ord_end_date = models.DateField(
        null=True,
        blank=True,
        db_column='ord_end_date',
        verbose_name='End Date'
    )
    ord_type = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        db_column='ord_type',
        verbose_name='Type'
    )
    ord_total_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
        db_column='ord_total_amount',
        verbose_name='Total Amount'
    )
    ord_open_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
        db_column='ord_open_amount',
        verbose_name='Open Amount'
    )
    ord_open_quantity = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
        db_column='ord_open_quantity',
        verbose_name='Open Quantity'
    )
    ord_open_amount_tax = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
        db_column='ord_open_amount_tax',
        verbose_name='Open Amount with Tax'
    )
    ord_ordered_quantity = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
        db_column='ord_ordered_quantity',
        verbose_name='Ordered Quantity'
    )
    ord_ordered_amount_tax = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
        db_column='ord_ordered_amount_tax',
        verbose_name='Ordered Amount with Tax'
    )
    ord_currency_iso_code = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        db_column='ord_currency_iso_code',
        verbose_name='Currency ISO Code'
    )
    ord_owner_id = models.ForeignKey(
        'users.User',
        to_field='usr_sf_id',
        on_delete=models.RESTRICT,
        db_column='ord_owner_id',
        verbose_name='Owner'
    )
    ord_contract_id = models.CharField(
        max_length=18,
        null=True,
        blank=True,
        db_column='ord_contract_id',
        verbose_name='Contract ID'
    )
    ord_sf_created_date = models.DateTimeField(
        db_column='ord_sf_created_date',
        verbose_name='SF Created Date'
    )
    ord_last_modified_date = models.DateTimeField(
        db_column='ord_last_modified_date',
        verbose_name='Last Modified Date'
    )
    ord_last_modified_by_id = models.CharField(
        max_length=18,
        db_column='ord_last_modified_by_id',
        verbose_name='Last Modified By ID'
    )
    ord_active = models.SmallIntegerField(
        default=1,
        db_column='ord_active',
        verbose_name='Active Flag'
    )
    ord_created_at = models.DateTimeField(
        auto_now_add=True,
        db_column='ord_created_at',
        verbose_name='Created At'
    )
    ord_updated_at = models.DateTimeField(
        auto_now=True,
        db_column='ord_updated_at',
        verbose_name='Updated At'
    )

    class Meta:
        db_table = 'orders'
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        indexes = [
            models.Index(fields=['ord_account_id'], name='idx_orders_account'),
            models.Index(fields=['ord_status'], name='idx_orders_status'),
            models.Index(fields=['ord_effective_date'], name='idx_orders_effective_date'),
            models.Index(fields=['ord_owner_id'], name='idx_orders_owner'),
        ]

    def __str__(self):
        return self.ord_order_number


class OrderLineItem(models.Model):
    """Order Line Item - individual line items on orders"""
    ori_sf_id = models.CharField(
        max_length=18,
        primary_key=True,
        db_column='ori_sf_id',
        verbose_name='Salesforce ID'
    )
    ori_order_id = models.ForeignKey(
        'products.Order',
        to_field='ord_sf_id',
        on_delete=models.CASCADE,
        db_column='ori_order_id',
        verbose_name='Order'
    )
    ori_product_id = models.ForeignKey(
        'products.Product',
        to_field='prd_sf_id',
        on_delete=models.RESTRICT,
        db_column='ori_product_id',
        verbose_name='Product'
    )
    ori_product_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_column='ori_product_name',
        verbose_name='Product Name'
    )
    ori_product_code = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_column='ori_product_code',
        verbose_name='Product Code'
    )
    ori_quantity = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        db_column='ori_quantity',
        verbose_name='Quantity'
    )
    ori_unit_price = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        db_column='ori_unit_price',
        verbose_name='Unit Price'
    )
    ori_total_price = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
        db_column='ori_total_price',
        verbose_name='Total Price'
    )
    ori_open_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
        db_column='ori_open_amount',
        verbose_name='Open Amount'
    )
    ori_open_amount_tax = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
        db_column='ori_open_amount_tax',
        verbose_name='Open Amount with Tax'
    )
    ori_open_quantity = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
        db_column='ori_open_quantity',
        verbose_name='Open Quantity'
    )
    ori_ordered_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
        db_column='ori_ordered_amount',
        verbose_name='Ordered Amount'
    )
    ori_ordered_quantity = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
        db_column='ori_ordered_quantity',
        verbose_name='Ordered Quantity'
    )
    ori_status = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        db_column='ori_status',
        verbose_name='Status'
    )
    ori_description = models.TextField(
        null=True,
        blank=True,
        db_column='ori_description',
        verbose_name='Description'
    )
    ori_service_date = models.DateField(
        null=True,
        blank=True,
        db_column='ori_service_date',
        verbose_name='Service Date'
    )
    ori_sf_created_date = models.DateTimeField(
        db_column='ori_sf_created_date',
        verbose_name='SF Created Date'
    )
    ori_last_modified_date = models.DateTimeField(
        db_column='ori_last_modified_date',
        verbose_name='Last Modified Date'
    )
    ori_last_modified_by_id = models.CharField(
        max_length=18,
        db_column='ori_last_modified_by_id',
        verbose_name='Last Modified By ID'
    )
    ori_active = models.SmallIntegerField(
        default=1,
        db_column='ori_active',
        verbose_name='Active Flag'
    )
    ori_created_at = models.DateTimeField(
        auto_now_add=True,
        db_column='ori_created_at',
        verbose_name='Created At'
    )
    ori_updated_at = models.DateTimeField(
        auto_now=True,
        db_column='ori_updated_at',
        verbose_name='Updated At'
    )

    class Meta:
        db_table = 'order_line_items'
        verbose_name = 'Order Line Item'
        verbose_name_plural = 'Order Line Items'
        indexes = [
            models.Index(fields=['ori_order_id'], name='idx_order_line_items_order'),
            models.Index(fields=['ori_product_id'], name='idx_order_line_items_product'),
        ]

    def __str__(self):
        return f"{self.ori_order_id} - {self.ori_product_id}"
