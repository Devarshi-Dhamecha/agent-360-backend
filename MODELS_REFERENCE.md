# Agent 360 - Models Quick Reference

## 📚 Complete Model Reference

### Module 1: User Management (`apps.users`)

#### Profile
- **Purpose**: User profile templates
- **Key Fields**: `id`, `name`, `description`
- **Relationships**: Referenced by `Users`

#### UserRole
- **Purpose**: Hierarchical user roles
- **Key Fields**: `id`, `name`, `parent_role`
- **Relationships**: Self-referential (parent-child hierarchy)

#### Users (Custom User Model)
- **Purpose**: System users with authentication
- **Key Fields**: `id`, `username`, `email`, `first_name`, `last_name`, `name`, `is_active`, `is_staff`
- **Relationships**:
  - `profile` → Profile (PROTECT)
  - `user_role` → UserRole (SET_NULL)
  - `manager` → Users (self, SET_NULL)
  - `last_modified_by` → Users (self, SET_NULL)
- **Special**: Extends `AbstractBaseUser`, used as `AUTH_USER_MODEL`

---

### Module 2: Account Management (`apps.accounts`)

#### Account
- **Purpose**: Customer accounts with credit tracking
- **Key Fields**: `id`, `name`, `account_number`, `credit_limit`, `invoice_open_amount`, `order_open_amount`
- **Relationships**:
  - `owner` → Users (PROTECT)
  - `last_modified_by` → Users (PROTECT)
- **Reverse Relations**: `frame_agreements`, `invoices`, `targets`, `cases`, `forecasts`

#### AccountPlan
- **Purpose**: Account planning and strategy
- **Key Fields**: `id`, `name`, `status`, `start_date`, `end_date`
- **Relationships**:
  - `account` → Account (CASCADE)
  - `created_by` → Users (PROTECT)
  - `last_modified_by` → Users (PROTECT)
- **Status Choices**: Active, Closed

---

### Module 3: Product Management (`apps.products`)

#### ProductBrand
- **Purpose**: Product brand definitions
- **Key Fields**: `id`, `name`, `description`, `is_active`
- **Relationships**: Referenced by `Product`

#### Product
- **Purpose**: Product catalog with SKUs
- **Key Fields**: `id`, `name`, `family`, `classification`, `central_product_code`, `product_code`, `brand`
- **Relationships**:
  - `product_brand` → ProductBrand (SET_NULL)
  - `created_by` → Users (PROTECT)
  - `last_modified_by` → Users (SET_NULL)
- **Reverse Relations**: `invoice_lines`, `forecasts`
- **Unique Fields**: `central_product_code`, `product_code`

---

### Module 4: Frame Agreements & Targets (`apps.agreements`)

#### FrameAgreement
- **Purpose**: Sales agreements with terms
- **Key Fields**: `id`, `agreement_type`, `start_date`, `end_date`, `start_year`, `status`, `is_active`
- **Relationships**:
  - `account` → Account (PROTECT)
  - `created_by` → Users (PROTECT)
  - `last_modified_by` → Users (PROTECT)
- **Status Choices**: Draft, Active, Expired, Terminated
- **Agreement Types**: Standard, Premium, Strategic
- **Auto-populated**: `start_year` (from `start_date`)

#### Target
- **Purpose**: Quarterly sales targets with rebates
- **Key Fields**: `id`, `quarter`, `net_turnover_target`, `rebate_rate`, `rebate_if_achieved`, `total_rebate`
- **Relationships**:
  - `account` → Account (PROTECT)
  - `frame_agreement` → FrameAgreement (CASCADE)
  - `created_by` → Users (PROTECT)
  - `last_modified_by` → Users (PROTECT)
- **Quarter Choices**: Q1, Q2, Q3, Q4
- **Unique Constraint**: (`frame_agreement`, `quarter`)

---

### Module 5: Invoicing (`apps.invoices`)

#### Invoice
- **Purpose**: Customer invoices with revenue tracking
- **Key Fields**: `id`, `invoice_number`, `invoice_date`, `invoice_year`, `invoice_type`, `status`, `net_price`, `total_vat`, `total_invoice_value`
- **Relationships**:
  - `account` → Account (PROTECT)
  - `created_by` → Users (PROTECT)
  - `last_modified_by` → Users (PROTECT)
- **Status Choices**: Draft, Open, Closed, Cancelled
- **Invoice Types**: Invoice, Credit Note
- **Auto-populated**: `invoice_year` (from `invoice_date`)

#### InvoiceLineItem
- **Purpose**: Individual line items within invoices
- **Key Fields**: `id`, `quantity`, `unit_price`, `net_price`, `vat`, `unique_line_code`, `status`, `is_valid`
- **Relationships**:
  - `invoice` → Invoice (CASCADE)
  - `product` → Product (PROTECT)
  - `created_by` → Users (PROTECT)
  - `last_modified_by` → Users (SET_NULL)
- **Status Choices**: Active, Cancelled
- **Unique Field**: `unique_line_code`

---

### Module 6: Campaign Management (`apps.campaigns`)

#### RecordType
- **Purpose**: Salesforce-style record type definitions
- **Key Fields**: `id`, `name`, `developer_name`, `sobject_type`, `is_active`
- **Relationships**: Referenced by `Campaign`

#### Campaign
- **Purpose**: Marketing campaigns with hierarchy
- **Key Fields**: `id`, `name`, `type`, `status`, `start_date`, `end_date`, `is_active`
- **Relationships**:
  - `record_type` → RecordType (PROTECT)
  - `parent` → Campaign (self, SET_NULL)
  - `owner` → Users (PROTECT)
  - `created_by` → Users (PROTECT)
  - `last_modified_by` → Users (PROTECT)
- **Status Choices**: Planned, In Progress, Completed, Cancelled
- **Campaign Types**: Promotional, Tactical, Strategic

#### Task
- **Purpose**: User tasks related to various business objects
- **Key Fields**: `id`, `subject`, `status`, `priority`, `activity_date`, `is_closed`
- **Polymorphic Relationship**:
  - `what_content_type` → ContentType
  - `what_id` → Generic ID (Campaign, Account, or Case)
  - `what_object` → GenericForeignKey
- **Other Relationships**:
  - `owner` → Users (PROTECT)
  - `created_by` → Users (PROTECT)
  - `last_modified_by` → Users (PROTECT)
- **Status Choices**: Open, In Progress, Completed, Cancelled
- **Priority Choices**: High, Normal, Low

---

### Module 7: Case Management (`apps.cases`)

#### Case
- **Purpose**: Customer service cases
- **Key Fields**: `id`, `case_number`, `subject`, `status`, `priority`, `is_closed`
- **Relationships**:
  - `account` → Account (SET_NULL)
  - `owner` → Users (SET_NULL)
  - `created_by` → Users (PROTECT)
  - `last_modified_by` → Users (PROTECT)
- **Status Choices**: New, In Progress, Escalated, Resolved, Closed
- **Priority Choices**: High, Medium, Low
- **Unique Field**: `case_number`

#### CaseHistory
- **Purpose**: Audit trail for case changes
- **Key Fields**: `id`, `field`, `old_value`, `new_value`
- **Relationships**:
  - `case` → Case (CASCADE)
  - `created_by` → Users (PROTECT)
- **Ordering**: `-created_date` (newest first)

#### CaseComment
- **Purpose**: Comments on cases (internal/public)
- **Key Fields**: `id`, `comment_body`, `is_published`
- **Relationships**:
  - `case` → Case (CASCADE)
  - `created_by` → Users (PROTECT)
  - `last_modified_by` → Users (PROTECT)
- **Ordering**: `created_date` (oldest first)

---

### Module 8: Rolling Forecast (`apps.forecasts`)

#### Forecast
- **Purpose**: Sales forecasting and pipeline management
- **Key Fields**: `id`, `name`, `forecast_date`, `status`, `quantity`, `revenue`
- **Relationships**:
  - `account` → Account (PROTECT)
  - `sales_rep` → Users (PROTECT)
  - `product` → Product (PROTECT)
  - `owner` → Users (PROTECT)
  - `created_by` → Users (PROTECT)
  - `last_modified_by` → Users (PROTECT)
- **Status Choices**: Draft, Submitted, Approved, Revision Required

---

## 🔗 Relationship Diagram

```
Users (AUTH_USER_MODEL)
  ↓
  ├─→ Profile (many-to-one)
  ├─→ UserRole (many-to-one)
  ├─→ Users.manager (self-referential)
  │
  └─→ Account
        ├─→ AccountPlan (one-to-many)
        ├─→ FrameAgreement (one-to-many)
        │     └─→ Target (one-to-many)
        ├─→ Invoice (one-to-many)
        │     └─→ InvoiceLineItem (one-to-many)
        │           └─→ Product
        ├─→ Case (one-to-many)
        │     ├─→ CaseHistory (one-to-many)
        │     └─→ CaseComment (one-to-many)
        └─→ Forecast (one-to-many)
              └─→ Product

Campaign
  ├─→ RecordType (many-to-one)
  ├─→ Campaign.parent (self-referential)
  └─→ Task (polymorphic via GenericForeignKey)

ProductBrand
  └─→ Product (one-to-many)
```

---

## 📊 Field Patterns

### Audit Fields (Common across most models)
- `created_date` → DateTimeField (auto_now_add=True)
- `created_by` → FK to Users
- `last_modified_date` → DateTimeField (auto_now=True)
- `last_modified_by` → FK to Users

### Primary Keys
- All models use: `id = CharField(max_length=18, primary_key=True)`
- Salesforce-style 18-character IDs

### Status Fields
- Most models have a `status` field with specific choices
- Common pattern: Draft → Active/In Progress → Completed/Closed

### Indexes
- All ForeignKeys have `db_index=True`
- Frequently queried fields are indexed
- Date ranges use composite indexes

---

## 🎯 Common Queries

### Get all active users
```python
from apps.users.models import Users
active_users = Users.objects.filter(is_active=True)
```

### Get account with invoices
```python
from apps.accounts.models import Account
account = Account.objects.prefetch_related('invoices').get(id='xxx')
invoices = account.invoices.all()
```

### Get targets for a frame agreement
```python
from apps.agreements.models import FrameAgreement
agreement = FrameAgreement.objects.prefetch_related('targets').get(id='xxx')
targets = agreement.targets.all()
```

### Get invoice with line items
```python
from apps.invoices.models import Invoice
invoice = Invoice.objects.prefetch_related('line_items__product').get(id='xxx')
line_items = invoice.line_items.all()
```

### Get tasks for a specific owner
```python
from apps.campaigns.models import Task
my_tasks = Task.objects.filter(owner__username='john', is_closed=False)
```

### Get case with full history
```python
from apps.cases.models import Case
case = Case.objects.prefetch_related('history', 'comments').get(case_number='12345')
```

---

## 🔑 Important Notes

1. **Custom User Model**: Always use `settings.AUTH_USER_MODEL` for ForeignKeys to users
2. **Migrations Order**: Apps are ordered by dependencies in `INSTALLED_APPS`
3. **Cascade Behavior**: Master-detail relationships use `CASCADE`, others use `PROTECT` or `SET_NULL`
4. **Unique Constraints**: Check `unique=True` and `unique_together` before inserting data
5. **Auto-populated Fields**: `start_year` and `invoice_year` are automatically set on save
6. **Polymorphic Relations**: `Task.what_id` can point to Campaign, Account, or Case

---

## 📖 Related Documentation

- Full implementation details: `IMPLEMENTATION_SUMMARY.md`
- Original specification: `cursor_prompt_django_models.md`
- Database schema: `Agent360_Database_Schema.sql`
- Django documentation: https://docs.djangoproject.com/
