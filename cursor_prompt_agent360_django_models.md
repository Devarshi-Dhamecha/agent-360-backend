# Cursor Prompt: Agent360 Django Model Migration

## Context

We have a PostgreSQL 17 database called `agent360_db` with **26 tables** synced from Salesforce. We need to create Django models for these tables, **separated into Django apps by module/domain**. Do NOT put everything in one `models.py`.

---

## Module Structure (Django Apps)

Create the following Django apps, each with its own `models.py`:

```
agent360/
├── apps/
│   ├── core/              # user_roles, users, record_types
│   ├── catalog/           # product_brands, products
│   ├── accounts/          # accounts, account_plans, frame_agreements, targets
│   ├── campaigns/         # campaigns
│   ├── invoicing/         # invoices, invoice_line_items
│   ├── support/           # tasks, cases, case_history, case_comments
│   ├── forecasting/       # arf_rolling_forecasts
│   ├── ai_assistant/      # ai_chat_threads, ai_chat_messages, ai_business_rules,
│   │                      # ai_query_examples, ai_schema_config
│   └── system/            # sync_log, sync_watermarks, sync_conflicts,
│                          #  user_login_log
```

---

## Global Rules for ALL Models

Apply these rules consistently across every app:

1. **Use `managed = False`** in all `Meta` classes — we are NOT letting Django manage the schema (tables already exist).
2. **Map `db_table`** to the exact existing PostgreSQL table name.
3. **Map `db_column`** to the exact prefixed column name (e.g., `ur_sf_id`, `usr_email`).
4. **Primary keys**: Most tables use a `VARCHAR(18)` Salesforce ID as PK. Use `primary_key=True` on that field. Tables that use `SERIAL` PK should use `AutoField`.
5. **ForeignKey fields**: Use `to_field` pointing to the PK of the related model. Set `db_constraint=False` since constraints are already defined in the DB.
6. **`on_delete`**: Match what's in the DDL (`CASCADE` → `models.CASCADE`, `SET NULL` → `models.SET_NULL`, `RESTRICT` → `models.PROTECT`).
7. **`null=True, blank=True`** for all nullable columns. Required columns get `null=False, blank=False`.
8. **`SmallIntegerField`** for `SMALLINT` columns (e.g., `*_active`).
9. **`DecimalField`**: Use `max_digits` and `decimal_places` matching `NUMERIC(p,s)`.
10. **`auto_now_add=True`** for `*_created_at` columns, **`auto_now=True`** for `*_updated_at` columns.
11. **No duplicate `related_name`**: When a model has multiple FK fields pointing to the same model (e.g., `users`), use unique `related_name` values.
12. **Self-referencing FK** (e.g., `campaigns.cmp_parent_id`): Use `'self'` as the model reference.
13. **`JSONField`** for `JSONB` columns.
14. **`UUIDField`** for UUID columns.
15. Add a `class Meta` `ordering` only where it makes semantic sense (e.g., `sync_log` by `-sl_started_at`).
16. Add a `__str__` method to every model.

---

## App-by-App Instructions

### `apps/core/models.py`

**Tables:** `user_roles`, `users`, `record_types`

```
UserRole
  - ur_sf_id          → CharField(18, primary_key=True)
  - ur_name           → CharField(80)
  - ur_last_modified_date → DateTimeField()
  - ur_system_modstamp    → DateTimeField()
  - ur_active         → SmallIntegerField(default=1)
  - ur_created_at     → DateTimeField(auto_now_add=True)
  - ur_updated_at     → DateTimeField(auto_now=True)

User
  - usr_sf_id         → CharField(18, primary_key=True)
  - usr_username      → CharField(80)
  - usr_email         → CharField(255)
  - usr_first_name    → CharField(255, null=True, blank=True)
  - usr_last_name     → CharField(255)
  - usr_name          → CharField(255)
  - usr_is_active     → BooleanField()
  - usr_profile_id    → CharField(18, null=True, blank=True)
  - usr_user_role_id  → ForeignKey(UserRole, db_column='usr_user_role_id',
                         null=True, on_delete=SET_NULL, db_constraint=False)
  - usr_federation_id → CharField(255, null=True, blank=True)
  - usr_time_zone     → CharField(100)
  - usr_language      → CharField(100)
  - usr_sf_created_date     → DateTimeField()
  - usr_last_modified_date  → DateTimeField()
  - usr_last_modified_by_id → CharField(18)
  - usr_active        → SmallIntegerField(default=1)
  - usr_created_at    → DateTimeField(auto_now_add=True)
  - usr_updated_at    → DateTimeField(auto_now=True)

RecordType
  - rt_sf_id          → CharField(18, primary_key=True)
  - rt_name           → CharField(80)
  - rt_developer_name → CharField(80)
  - rt_sobject_type   → CharField(40)
  - rt_is_active      → BooleanField()
  - rt_sf_created_date      → DateTimeField()
  - rt_last_modified_date   → DateTimeField()
  - rt_last_modified_by_id  → ForeignKey(User, null=True, on_delete=SET_NULL,
                               db_constraint=False, related_name='modified_record_types')
  - rt_active         → SmallIntegerField(default=1)
  - rt_created_at     → DateTimeField(auto_now_add=True)
  - rt_updated_at     → DateTimeField(auto_now=True)
```

---

### `apps/catalog/models.py`

**Tables:** `product_brands`, `products`

```
ProductBrand
  - pb_sf_id          → CharField(18, primary_key=True)
  - pb_name           → CharField(255)
  - pb_brand_code     → CharField(50, null=True, blank=True)
  - pb_description    → TextField(null=True, blank=True)
  - pb_is_active      → BooleanField(null=True, blank=True)
  - pb_sf_created_date      → DateTimeField()
  - pb_last_modified_date   → DateTimeField()
  - pb_active         → SmallIntegerField(default=1)
  - pb_created_at     → DateTimeField(auto_now_add=True)
  - pb_updated_at     → DateTimeField(auto_now=True)

Product
  - prd_sf_id         → CharField(18, primary_key=True)
  - prd_name          → CharField(255)
  - prd_family        → CharField(100, null=True, blank=True)
  - prd_classification → CharField(100, null=True, blank=True)
  - prd_central_product_code → CharField(20, null=True, blank=True)
  - prd_product_code  → CharField(255, null=True, blank=True)
  - prd_product_brand → ForeignKey(ProductBrand, db_column='prd_product_brand_id',
                         null=True, on_delete=SET_NULL, db_constraint=False)
  - prd_brand         → CharField(100, null=True, blank=True)
  - prd_is_active     → BooleanField(null=True, blank=True)
  - prd_sf_created_date     → DateTimeField()
  - prd_last_modified_date  → DateTimeField()
  - prd_last_modified_by_id → CharField(18)
  - prd_active        → SmallIntegerField(default=1)
  - prd_created_at    → DateTimeField(auto_now_add=True)
  - prd_updated_at    → DateTimeField(auto_now=True)
```

---

### `apps/accounts/models.py`

**Tables:** `accounts`, `account_plans`, `frame_agreements`, `targets`

Import `User` from `apps.core.models`.

```
Account
  - acc_sf_id         → CharField(18, primary_key=True)
  - acc_name          → CharField(255)
  - acc_owner         → ForeignKey(User, db_column='acc_owner_id',
                         on_delete=PROTECT, db_constraint=False, related_name='owned_accounts')
  - acc_credit_limit      → DecimalField(max_digits=18, decimal_places=2, null=True)
  - acc_invoice_open_amount → DecimalField(max_digits=18, decimal_places=2, null=True)
  - acc_order_open_amount   → DecimalField(max_digits=18, decimal_places=2, null=True)
  - acc_account_number → CharField(255, null=True, blank=True)
  - acc_currency_iso_code → CharField(10, null=True, blank=True)
  - acc_last_modified_date  → DateTimeField()
  - acc_last_modified_by_id → CharField(18)
  - acc_active        → SmallIntegerField(default=1)
  - acc_created_at    → DateTimeField(auto_now_add=True)
  - acc_updated_at    → DateTimeField(auto_now=True)

AccountPlan
  - ap_sf_id          → CharField(18, primary_key=True)
  - ap_name           → CharField(80)
  - ap_account        → ForeignKey(Account, db_column='ap_account_id',
                         on_delete=CASCADE, db_constraint=False)
  - ap_plan_name      → CharField(255, null=True, blank=True)
  - ap_status         → CharField(100)
  - ap_start_date     → DateField(null=True, blank=True)
  - ap_end_date       → DateField(null=True, blank=True)
  - ap_sf_created_date      → DateTimeField()
  - ap_last_modified_date   → DateTimeField()
  - ap_last_modified_by_id  → CharField(18)
  - ap_active         → SmallIntegerField(default=1)
  - ap_created_at     → DateTimeField(auto_now_add=True)
  - ap_updated_at     → DateTimeField(auto_now=True)

FrameAgreement
  - fa_sf_id          → CharField(18, primary_key=True)
  - fa_account        → ForeignKey(Account, db_column='fa_account_id',
                         on_delete=CASCADE, db_constraint=False)
  - fa_agreement_type → CharField(100)
  - fa_start_date     → DateField()
  - fa_end_date       → DateField()
  - fa_start_year     → IntegerField(null=True, blank=True)
  - fa_status         → CharField(100)
  - fa_is_active      → BooleanField(null=True, blank=True)
  - fa_total_sales_ty → DecimalField(18, 2, null=True)
  - fa_total_sales_ly → DecimalField(18, 2, null=True)
  - fa_total_sales_q1 → DecimalField(18, 0, null=True)
  - fa_total_sales_q2 → DecimalField(18, 0, null=True)
  - fa_total_sales_q3 → DecimalField(18, 0, null=True)
  - fa_total_sales_q4 → DecimalField(18, 0, null=True)
  - fa_rebate_achieved → DecimalField(6, 4, null=True)
  - fa_total_rebate_achieved → DecimalField(18, 2, null=True)
  - fa_last_modified_date   → DateTimeField()
  - fa_last_modified_by     → ForeignKey(User, db_column='fa_last_modified_by_id',
                               on_delete=PROTECT, db_constraint=False,
                               related_name='modified_frame_agreements')
  - fa_active         → SmallIntegerField(default=1)
  - fa_created_at     → DateTimeField(auto_now_add=True)
  - fa_updated_at     → DateTimeField(auto_now=True)

Target
  - tgt_sf_id         → CharField(18, primary_key=True)
  - tgt_account       → ForeignKey(Account, db_column='tgt_account_id',
                         on_delete=CASCADE, db_constraint=False)
  - tgt_frame_agreement → ForeignKey(FrameAgreement, db_column='tgt_frame_agreement_id',
                           on_delete=CASCADE, db_constraint=False)
  - tgt_quarter       → CharField(100)
  - tgt_net_turnover_target → DecimalField(18, 2)
  - tgt_rebate_rate   → DecimalField(6, 4)
  - tgt_rebate_if_achieved → DecimalField(18, 2)
  - tgt_total_rebate  → DecimalField(18, 2, null=True)
  - tgt_last_modified_date  → DateTimeField()
  - tgt_last_modified_by_id → CharField(18)
  - tgt_active        → SmallIntegerField(default=1)
  - tgt_created_at    → DateTimeField(auto_now_add=True)
  - tgt_updated_at    → DateTimeField(auto_now=True)
```

---

### `apps/campaigns/models.py`

**Tables:** `campaigns`

Import `User` from `apps.core.models`, `Account` from `apps.accounts.models`, `RecordType` from `apps.core.models`.

```
Campaign
  - cmp_sf_id         → CharField(18, primary_key=True)
  - cmp_name          → CharField(80)
  - cmp_record_type   → ForeignKey(RecordType, db_column='cmp_record_type_id',
                         null=True, on_delete=SET_NULL, db_constraint=False)
  - cmp_type          → CharField(100, null=True, blank=True)
  - cmp_parent        → ForeignKey('self', db_column='cmp_parent_id',
                         null=True, on_delete=SET_NULL, db_constraint=False,
                         related_name='child_campaigns')
  - cmp_status        → CharField(100)
  - cmp_start_date    → DateField(null=True, blank=True)
  - cmp_end_date      → DateField(null=True, blank=True)
  - cmp_actual_cost   → DecimalField(18, 2, null=True)
  - cmp_budgeted_cost → DecimalField(18, 2, null=True)
  - cmp_currency_iso_code → CharField(10, null=True, blank=True)
  - cmp_owner         → ForeignKey(User, db_column='cmp_owner_id',
                         on_delete=PROTECT, db_constraint=False, related_name='owned_campaigns')
  - cmp_account       → ForeignKey(Account, db_column='cmp_account_id',
                         null=True, on_delete=SET_NULL, db_constraint=False)
  - cmp_initial_quantity  → DecimalField(18, 2, null=True)
  - cmp_used_quantity     → DecimalField(18, 2, null=True)
  - cmp_available_budget  → DecimalField(18, 2, null=True)
  - cmp_is_active     → BooleanField(null=True, blank=True)
  - cmp_sf_created_date     → DateTimeField()
  - cmp_last_modified_date  → DateTimeField()
  - cmp_last_modified_by_id → CharField(18)
  - cmp_active        → SmallIntegerField(default=1)
  - cmp_created_at    → DateTimeField(auto_now_add=True)
  - cmp_updated_at    → DateTimeField(auto_now=True)
```

---

### `apps/invoicing/models.py`

**Tables:** `invoices`, `invoice_line_items`

Import `Account` from `apps.accounts.models`, `FrameAgreement` from `apps.accounts.models`, `Product` from `apps.catalog.models`.

```
Invoice
  - inv_sf_id         → CharField(18, primary_key=True)
  - inv_name          → CharField(255)
  - inv_account       → ForeignKey(Account, db_column='inv_account_id',
                         on_delete=CASCADE, db_constraint=False)
  - inv_frame_agreement → ForeignKey(FrameAgreement, db_column='inv_frame_agreement_id',
                           null=True, on_delete=SET_NULL, db_constraint=False)
  - inv_invoice_date  → DateField()
  - inv_invoice_year  → CharField(10, null=True, blank=True)
  - inv_invoice_type  → CharField(100)
  - inv_status        → CharField(100)
  - inv_net_price     → DecimalField(18, 2)
  - inv_total_vat     → DecimalField(18, 2, null=True)
  - inv_total_invoice_value → DecimalField(18, 2, null=True)
  - inv_valid         → BooleanField(null=True, blank=True)
  - inv_currency_iso_code → CharField(10, null=True, blank=True)
  - inv_sf_created_date     → DateTimeField()
  - inv_last_modified_date  → DateTimeField()
  - inv_last_modified_by_id → CharField(18)
  - inv_active        → SmallIntegerField(default=1)
  - inv_created_at    → DateTimeField(auto_now_add=True)
  - inv_updated_at    → DateTimeField(auto_now=True)

InvoiceLineItem
  - ili_sf_id         → CharField(18, primary_key=True)
  - ili_invoice       → ForeignKey(Invoice, db_column='ili_invoice_id',
                         on_delete=CASCADE, db_constraint=False)
  - ili_product       → ForeignKey(Product, db_column='ili_product_id',
                         on_delete=PROTECT, db_constraint=False)
  - ili_quantity      → DecimalField(18, 2)
  - ili_unit_price    → DecimalField(18, 2)
  - ili_net_price     → DecimalField(18, 2)
  - ili_vat           → DecimalField(18, 2, null=True)
  - ili_unique_line_code → CharField(255, unique=True)
  - ili_status        → CharField(100)
  - ili_valid         → BooleanField()
  - ili_sf_created_date     → DateTimeField()
  - ili_last_modified_date  → DateTimeField()
  - ili_last_modified_by_id → CharField(18)
  - ili_active        → SmallIntegerField(default=1)
  - ili_created_at    → DateTimeField(auto_now_add=True)
  - ili_updated_at    → DateTimeField(auto_now=True)
```

---

### `apps/support/models.py`

**Tables:** `tasks`, `cases`, `case_history`, `case_comments`

Import `User` from `apps.core.models`, `Account` from `apps.accounts.models`.

```
Task
  - tsk_sf_id         → CharField(18, primary_key=True)
  - tsk_what_id       → CharField(18, null=True, blank=True)   # polymorphic, no FK
  - tsk_what_type     → CharField(40, null=True, blank=True)
  - tsk_what_name     → CharField(255, null=True, blank=True)
  - tsk_activity_date → DateField(null=True, blank=True)
  - tsk_status        → CharField(100)
  - tsk_priority      → CharField(100, null=True, blank=True)
  - tsk_subject       → CharField(255)
  - tsk_owner         → ForeignKey(User, db_column='tsk_owner_id',
                         on_delete=PROTECT, db_constraint=False)
  - tsk_description   → TextField(null=True, blank=True)
  - tsk_sf_created_date     → DateTimeField()
  - tsk_completed_date      → DateTimeField(null=True, blank=True)
  - tsk_last_modified_date  → DateTimeField()
  - tsk_last_modified_by_id → CharField(18)
  - tsk_active        → SmallIntegerField(default=1)
  - tsk_created_at    → DateTimeField(auto_now_add=True)
  - tsk_updated_at    → DateTimeField(auto_now=True)

Case
  - cs_sf_id          → CharField(18, primary_key=True)
  - cs_case_number    → CharField(80)
  - cs_subject        → CharField(255, null=True, blank=True)
  - cs_description    → TextField(null=True, blank=True)
  - cs_status         → CharField(100, null=True, blank=True)
  - cs_account        → ForeignKey(Account, db_column='cs_account_id',
                         null=True, on_delete=SET_NULL, db_constraint=False)
  - cs_owner          → ForeignKey(User, db_column='cs_owner_id',
                         null=True, on_delete=SET_NULL, db_constraint=False)
  - cs_priority       → CharField(100, null=True, blank=True)
  - cs_sf_created_date      → DateTimeField()
  - cs_last_modified_date   → DateTimeField()
  - cs_last_modified_by_id  → CharField(18)
  - cs_active         → SmallIntegerField(default=1)
  - cs_created_at     → DateTimeField(auto_now_add=True)
  - cs_updated_at     → DateTimeField(auto_now=True)

CaseHistory
  - ch_sf_id          → CharField(18, primary_key=True)
  - ch_case           → ForeignKey(Case, db_column='ch_case_id',
                         on_delete=CASCADE, db_constraint=False)
  - ch_field          → CharField(255)
  - ch_old_value      → TextField(null=True, blank=True)
  - ch_new_value      → TextField(null=True, blank=True)
  - ch_created_date   → DateTimeField()
  - ch_created_by     → ForeignKey(User, db_column='ch_created_by_id',
                         on_delete=PROTECT, db_constraint=False,
                         related_name='created_case_history')
  - ch_active         → SmallIntegerField(default=1)
  - ch_created_at     → DateTimeField(auto_now_add=True)
  - ch_updated_at     → DateTimeField(auto_now=True)

CaseComment
  - cc_id             → AutoField(primary_key=True)
  - cc_sf_id          → CharField(18, unique=True, null=True, blank=True)
  - cc_case           → ForeignKey(Case, db_column='cc_case_id',
                         on_delete=CASCADE, db_constraint=False)
  - cc_comment_body   → TextField(null=True, blank=True)
  - cc_is_published   → BooleanField(null=True, blank=True)
  - cc_sf_created_date      → DateTimeField(null=True, blank=True)
  - cc_sf_created_by  → ForeignKey(User, db_column='cc_sf_created_by_id',
                         null=True, on_delete=SET_NULL, db_constraint=False,
                         related_name='sf_created_case_comments')
  - cc_last_modified_date   → DateTimeField(null=True, blank=True)
  - cc_last_modified_by_id  → CharField(18, null=True, blank=True)
  - cc_agent_modified_by    → ForeignKey(User, db_column='cc_agent_modified_by',
                               null=True, on_delete=SET_NULL, db_constraint=False,
                               related_name='agent_modified_case_comments')
  - cc_agent_modified_date  → DateTimeField(null=True, blank=True)
  - cc_agent_created_by     → ForeignKey(User, db_column='cc_agent_created_by',
                               null=True, on_delete=SET_NULL, db_constraint=False,
                               related_name='agent_created_case_comments')
  - cc_agent_created_date   → DateTimeField(null=True, blank=True)
  - cc_agent360_source      → BooleanField(null=True, blank=True)
  - cc_sync_status    → SmallIntegerField(default=1)
  - cc_version        → IntegerField(default=1)
  - cc_retry_count    → IntegerField(default=0)
  - cc_last_sync_error → TextField(null=True, blank=True)
  - cc_active         → SmallIntegerField(default=1)
  - cc_created_at     → DateTimeField(auto_now_add=True)
  - cc_updated_at     → DateTimeField(auto_now=True)
```

---

### `apps/forecasting/models.py`

**Tables:** `arf_rolling_forecasts`

Import `Account`, `User`, `Product` from respective apps.

```
ArfRollingForecast
  - arf_id            → AutoField(primary_key=True)
  - arf_sf_id         → CharField(18, unique=True, null=True, blank=True)
  - arf_name          → CharField(80)
  - arf_account       → ForeignKey(Account, db_column='arf_account_id',
                         on_delete=CASCADE, db_constraint=False)
  - arf_sales_rep     → ForeignKey(User, db_column='arf_sales_rep_id',
                         on_delete=PROTECT, db_constraint=False,
                         related_name='sales_rep_forecasts')
  - arf_product       → ForeignKey(Product, db_column='arf_product_id',
                         on_delete=PROTECT, db_constraint=False)
  - arf_forecast_date → DateField()
  - arf_status        → CharField(100)  # choices: Draft/Pending_Approval/Approved/Fixes_Needed/Frozen
  - arf_currency_iso_code → CharField(10, null=True, blank=True)
  - arf_owner         → ForeignKey(User, db_column='arf_owner_id',
                         on_delete=PROTECT, db_constraint=False,
                         related_name='owned_forecasts')
  # Draft fields
  - arf_draft_quantity   → DecimalField(16, 2, null=True)
  - arf_draft_unit_price → DecimalField(16, 2, null=True)
  - arf_draft_value      → DecimalField(16, 2, null=True)
  # Pending fields (read-only)
  - arf_pending_quantity   → DecimalField(16, 2, null=True)
  - arf_pending_unit_price → DecimalField(16, 2, null=True)
  - arf_pending_value      → DecimalField(16, 2, null=True)
  # Approved fields (read-only)
  - arf_approved_quantity   → DecimalField(16, 2, null=True)
  - arf_approved_unit_price → DecimalField(16, 2, null=True)
  - arf_approved_value      → DecimalField(16, 2, null=True)
  # Metadata
  - arf_rejection_reason    → TextField(null=True, blank=True)
  - arf_product_formula     → CharField(255, null=True, blank=True)
  - arf_account_or_user_formula → CharField(255, null=True, blank=True)
  - arf_product_family      → CharField(100, null=True, blank=True)
  - arf_product_brand       → CharField(100, null=True, blank=True)
  - arf_sf_created_by       → ForeignKey(User, db_column='arf_sf_created_by_id',
                               null=True, on_delete=SET_NULL, db_constraint=False,
                               related_name='sf_created_forecasts')
  - arf_last_modified_by    → ForeignKey(User, db_column='arf_last_modified_by_id',
                               null=True, on_delete=SET_NULL, db_constraint=False,
                               related_name='modified_forecasts')
  - arf_agent_modified_by   → ForeignKey(User, db_column='arf_agent_modified_by',
                               null=True, on_delete=SET_NULL, db_constraint=False,
                               related_name='agent_modified_forecasts')
  - arf_agent_modified_date → DateTimeField(null=True, blank=True)
  - arf_agent_created_by    → ForeignKey(User, db_column='arf_agent_created_by',
                               null=True, on_delete=SET_NULL, db_constraint=False,
                               related_name='agent_created_forecasts')
  - arf_agent_created_date  → DateTimeField(null=True, blank=True)
  - arf_agent360_source     → BooleanField(null=True, blank=True)
  - arf_sync_status         → SmallIntegerField(default=1)
  - arf_version             → IntegerField(default=1)
  - arf_retry_count         → IntegerField(default=0)
  - arf_last_sync_error     → TextField(null=True, blank=True)
  - arf_active              → SmallIntegerField(default=1)
  - arf_created_at          → DateTimeField(auto_now_add=True)
  - arf_updated_at          → DateTimeField(auto_now=True)
```

---

### `apps/ai_assistant/models.py`

**Tables:** `ai_chat_threads`, `ai_chat_messages`, `ai_business_rules`, `ai_query_examples`, `ai_schema_config`

Import `User` from `apps.core.models`, `Account` from `apps.accounts.models`.

```
AiChatThread
  - act_id            → AutoField(primary_key=True)
  - act_user          → ForeignKey(User, db_column='act_user_sf_id',
                         on_delete=CASCADE, db_constraint=False)
  - act_account       → ForeignKey(Account, db_column='act_account_sf_id',
                         on_delete=CASCADE, db_constraint=False)
  - act_title         → CharField(255, null=True, blank=True)
  - act_message_count → IntegerField(default=0)
  - act_last_message_at → DateTimeField(null=True, blank=True)
  - act_sf_synced     → BooleanField(default=False)
  - act_sf_synced_at  → DateTimeField(null=True, blank=True)
  - act_created_at    → DateTimeField(auto_now_add=True)
  - act_updated_at    → DateTimeField(auto_now=True)
  Meta: unique_together = [('act_user', 'act_account')]

AiChatMessage
  - acm_id            → AutoField(primary_key=True)
  - acm_thread        → ForeignKey(AiChatThread, db_column='acm_thread_id',
                         on_delete=CASCADE, db_constraint=False)
  - acm_role          → CharField(20)  # choices: user/assistant/system
  - acm_content       → TextField()
  - acm_generated_sql → TextField(null=True, blank=True)
  - acm_sql_result_summary → TextField(null=True, blank=True)
  - acm_model_used    → CharField(100, null=True, blank=True)
  - acm_tokens_in     → IntegerField(null=True, blank=True)
  - acm_tokens_out    → IntegerField(null=True, blank=True)
  - acm_latency_ms    → IntegerField(null=True, blank=True)
  - acm_error         → TextField(null=True, blank=True)
  - acm_sf_synced     → BooleanField(default=False)
  - acm_created_at    → DateTimeField(auto_now_add=True)

AiBusinessRule
  - abr_id            → AutoField(primary_key=True)
  - abr_rule_key      → CharField(100, unique=True)
  - abr_category      → CharField(50)
  - abr_rule_text     → TextField()
  - abr_is_active     → BooleanField(default=True)
  - abr_sort_order    → IntegerField(default=0)
  - abr_created_at    → DateTimeField(auto_now_add=True)
  - abr_updated_at    → DateTimeField(auto_now=True)
  - abr_updated_by    → ForeignKey(User, db_column='abr_updated_by',
                         null=True, on_delete=SET_NULL, db_constraint=False)

AiQueryExample
  - aqe_id            → AutoField(primary_key=True)
  - aqe_question      → TextField()
  - aqe_sql           → TextField()
  - aqe_explanation   → TextField(null=True, blank=True)
  - aqe_category      → CharField(50, null=True, blank=True)
  - aqe_is_active     → BooleanField(default=True)
  - aqe_created_at    → DateTimeField(auto_now_add=True)
  - aqe_updated_at    → DateTimeField(auto_now=True)

AiSchemaConfig
  - asc_id            → AutoField(primary_key=True)
  - asc_config_key    → CharField(100, unique=True)
  - asc_config_value  → TextField()
  - asc_version       → IntegerField(default=1)
  - asc_generated_at  → DateTimeField(auto_now_add=True)
  - asc_updated_at    → DateTimeField(auto_now=True)
```

---

### `apps/system/models.py`

**Tables:** `sync_log`, `sync_watermarks`, `sync_conflicts`, `user_login_log`

Import `User` from `apps.core.models`.

```
SyncLog
  - sl_id             → AutoField(primary_key=True)
  - sl_run_id         → UUIDField(default=uuid.uuid4)
  - sl_job_name       → CharField(50)
  - sl_direction      → CharField(20)
  - sl_object_name    → CharField(50)
  - sl_sf_object_api  → CharField(50, null=True, blank=True)
  - sl_started_at     → DateTimeField(auto_now_add=True)
  - sl_completed_at   → DateTimeField(null=True, blank=True)
  - sl_status         → CharField(20, default='running')
    # choices: running/success/partial/failed/skipped
  - sl_records_queried  → IntegerField(default=0, null=True)
  - sl_records_inserted → IntegerField(default=0, null=True)
  - sl_records_updated  → IntegerField(default=0, null=True)
  - sl_records_deleted  → IntegerField(default=0, null=True)
  - sl_records_skipped  → IntegerField(default=0, null=True)
  - sl_records_failed   → IntegerField(default=0, null=True)
  - sl_hwm_before     → DateTimeField(null=True, blank=True)
  - sl_hwm_after      → DateTimeField(null=True, blank=True)
  - sl_error_message  → TextField(null=True, blank=True)
  - sl_error_details  → JSONField(null=True, blank=True)
  Meta: ordering = ['-sl_started_at']

SyncWatermark
  - sw_id             → AutoField(primary_key=True)
  - sw_object_name    → CharField(50, unique=True)
  - sw_sf_object_api  → CharField(50)
  - sw_last_sync_ts   → DateTimeField(null=True, blank=True)
  - sw_last_delete_check → DateTimeField(null=True, blank=True)
  - sw_sync_frequency → CharField(20, default='hourly')
    # choices: hourly/daily/weekly
  - sw_sync_enabled   → BooleanField(default=True)
  - sw_sync_order     → IntegerField(default=0)
  - sw_updated_at     → DateTimeField(auto_now=True)

SyncConflict
  - sc_id             → AutoField(primary_key=True)
  - sc_object_name    → CharField(50)
  - sc_record_sf_id   → CharField(18)
  - sc_record_local_id → IntegerField(null=True, blank=True)
  - sc_conflict_type  → CharField(30)
    # choices: local_pending/sf_deleted/version_mismatch
  - sc_local_value    → JSONField(null=True, blank=True)
  - sc_sf_value       → JSONField(null=True, blank=True)
  - sc_resolution     → CharField(20, null=True, blank=True)
    # choices: local_wins/sf_wins/manual
  - sc_resolved_at    → DateTimeField(null=True, blank=True)
  - sc_resolved_by    → ForeignKey(User, db_column='sc_resolved_by',
                         null=True, on_delete=SET_NULL, db_constraint=False)
  - sc_created_at     → DateTimeField(auto_now_add=True)

UserLoginLog
  - ull_id            → AutoField(primary_key=True)
  - ull_user          → ForeignKey(User, db_column='ull_user_sf_id',
                         on_delete=CASCADE, db_constraint=False)
  - ull_login_at      → DateTimeField(auto_now_add=True)
  - ull_ip_address    → CharField(45, null=True, blank=True)
  - ull_user_agent    → CharField(500, null=True, blank=True)
  - ull_session_duration_sec → IntegerField(null=True, blank=True)
  - ull_logout_at     → DateTimeField(null=True, blank=True)
  Meta: ordering = ['-ull_login_at']
```

---

## Migration Instructions

After generating all model files:

1. Register all 8 apps in `INSTALLED_APPS` in `settings.py`.
2. Run:
   ```bash
   python manage.py makemigrations core catalog accounts campaigns invoicing support forecasting ai_assistant system
   ```
3. Since all models have `managed = False`, the migration files will be created but **will not attempt to create or alter any database tables**.
4. Run `python manage.py migrate` to record the migrations as applied.
5. Verify with `python manage.py check` — there should be no errors.

---

## Notes & Caveats

- **`tasks.tsk_what_id`** is a polymorphic Salesforce field (can point to Account, Case, or Campaign). Do NOT add a ForeignKey for it — leave it as a plain `CharField`.
- **`auto_now_add=True`** means Django won't let you set `*_created_at` manually. If your sync logic needs to set these explicitly (e.g., when importing historical SF records), use `editable=True` and `default=django.utils.timezone.now` instead, and remove `auto_now_add`.
- **`auto_now=True`** similarly overrides any value you try to set. If the sync layer needs control over `*_updated_at`, use `default=now` without `auto_now=True` and manage it manually.
- The `update_timestamp()` trigger in PostgreSQL will still fire on DB-level UPDATEs regardless of how Django models are configured.
- For `arf_rolling_forecasts` and `case_comments`, there are multiple FK fields pointing to the same `User` model — make sure every one of them has a **distinct `related_name`**.
