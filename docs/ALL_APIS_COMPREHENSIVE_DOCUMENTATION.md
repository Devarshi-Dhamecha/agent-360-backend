# Complete API Documentation - All APIs Internal Workings

This document provides a comprehensive overview of all APIs in the Agent360 system, including database fields, business logic, formulas, aggregations, and how data flows through each API.

## Table of Contents

1. [Users API](#users-api)
2. [Accounts API](#accounts-api)
3. [Campaigns & Tasks API](#campaigns--tasks-api)
4. [Complaints & Cases API](#complaints--cases-api)
5. [Product Performance APIs](#product-performance-apis)
6. [Sales Analytics APIs](#sales-analytics-apis)
7. [RFC (Rolling Forecast) APIs](#rfc-rolling-forecast-apis)

---

## Users API

### Endpoint
- **GET** `/api/users/`

### Database Tables & Fields Used
- **Table:** `users`
- **Fields:** `usr_sf_id`, `usr_name`, `usr_email`, `usr_user_role_id`, `usr_active`
- **Related Table:** `user_roles` (via `usr_user_role_id`)
- **Related Fields:** `ur_name`

### Business Logic
1. Fetch all active users where `usr_active = 1`
2. Join with `user_roles` to get role name
3. Order by `usr_name`
4. Apply pagination (default 20 items per page, max 100)

### Data Transformation (Serializer)
```
Input DB Fields → Output API Fields
usr_sf_id → id
usr_name → full_name
usr_email → email
ur_name (from user_roles) → role
```

### Response Structure
```json
{
  "success": true,
  "message": "Users retrieved successfully",
  "data": [
    {
      "id": "0051234567890ABC",
      "full_name": "John Smith",
      "email": "john@example.com",
      "role": "Sales Manager"
    }
  ],
  "meta": {
    "pagination": {
      "current_page": 1,
      "page_size": 20,
      "total_count": 150,
      "total_pages": 8
    }
  }
}
```

---

## Accounts API

### Endpoints
- **GET** `/api/accounts/` - List all accounts
- **GET** `/api/accounts/user/{user_id}/` - List accounts by owner

### Database Tables & Fields Used
- **Table:** `accounts`
- **Fields:** `acc_sf_id`, `acc_name`, `acc_owner_id`, `acc_account_number`, `acc_currency_iso_code`, `acc_credit_limit`, `acc_active`
- **Related Table:** `users` (via `acc_owner_id`)
- **Related Fields:** `usr_sf_id`

### Business Logic
1. Fetch accounts where `acc_active = 1`
2. Join with `users` to get owner information
3. Order by `acc_name`
4. Optional pagination (if page or page_size provided)

### Data Transformation
```
Input DB Fields → Output API Fields
acc_sf_id → id
acc_name → name
acc_owner_id → owner_id
acc_account_number → account_number
acc_currency_iso_code → currency_iso_code
acc_credit_limit → credit_limit
acc_active → active
```

### Response Structure
```json
{
  "success": true,
  "message": "Accounts retrieved successfully",
  "data": [
    {
      "id": "0011234567890ABC",
      "name": "Acme Corporation",
      "owner_id": "0051234567890ABC",
      "account_number": "ACC-001",
      "currency_iso_code": "GBP",
      "credit_limit": 50000.00,
      "active": 1
    }
  ]
}
```

---

## Campaigns & Tasks API

### Endpoints
- **GET** `/api/campaigns/` - List campaigns with mapped tasks
- **GET** `/api/campaigns/tasks/` - List tasks by campaign

### Database Tables & Fields Used

#### Campaigns Table
- **Table:** `campaigns`
- **Fields:** `cmp_sf_id`, `cmp_name`, `cmp_status`, `cmp_start_date`, `cmp_end_date`, `cmp_account_id`

#### Tasks Table
- **Table:** `tasks`
- **Fields:** `tsk_sf_id`, `tsk_subject`, `tsk_status`, `tsk_priority`, `tsk_activity_date`, `tsk_owner_id`, `tsk_what_id`, `tsk_what_type`, `tsk_what_name`

### Business Logic

#### Campaign Filtering
1. Filter by `cmp_account_id` (required)
2. Optional filters:
   - **overdue:** `cmp_end_date < today`
   - **next_month:** `cmp_end_date` within next 30 days
   - **closed:** `cmp_status` contains 'Completed' or 'Closed'
3. Map tasks to campaigns based on `tsk_what_id = cmp_sf_id`

#### Task Filtering
- **type=all:** Return all tasks for campaign
- **type=my:** Return only tasks where `tsk_owner_id = user_id`

### Response Structure
```json
{
  "success": true,
  "message": "Campaigns retrieved successfully",
  "data": [
    {
      "id": "7011234567890ABC",
      "name": "Q1 2026 Campaign",
      "status": "In Progress",
      "start_date": "2026-01-01",
      "end_date": "2026-03-31",
      "tasks": [
        {
          "id": "0011234567890ABC",
          "subject": "Follow up call",
          "status": "Open",
          "priority": "High",
          "activity_date": "2026-02-15",
          "owner_id": "0051234567890ABC",
          "what_type": "Campaign",
          "what_name": "Q1 2026 Campaign"
        }
      ]
    }
  ]
}
```

---

## Complaints & Cases API

### Endpoints
- **GET** `/api/complaints-cases/summary/` - Summary counts
- **GET** `/api/complaints-cases/` - List cases
- **GET** `/api/complaints-cases/{case_id}/` - Case detail
- **GET** `/api/complaints-cases/{case_id}/comments/` - Case comments
- **POST** `/api/complaints-cases/{case_id}/comments/` - Create comment
- **GET** `/api/complaints-cases/{case_id}/timeline/` - Case history

### Database Tables & Fields Used

#### Cases Table
- **Table:** `cases`
- **Fields:** `cs_sf_id`, `cs_case_number`, `cs_subject`, `cs_status`, `cs_account_id`, `cs_owner_id`, `cs_priority`, `cs_sf_created_date`, `cs_last_modified_date`

#### Case Comments Table
- **Table:** `case_comments`
- **Fields:** `cc_sf_id`, `cc_case_id`, `cc_body`, `cc_created_by_id`, `cc_sf_created_date`, `cc_agent_created_date`

#### Case History Table
- **Table:** `case_history`
- **Fields:** `ch_sf_id`, `ch_case_id`, `ch_field`, `ch_old_value`, `ch_new_value`, `ch_created_date`

### Business Logic

#### Summary Calculation
```
open_count = COUNT(cases WHERE cs_status = 'Open' AND cs_account_id = account_id)
closed_count = COUNT(cases WHERE cs_status = 'Closed' AND cs_account_id = account_id)
total_count = open_count + closed_count
```

#### Case Listing
1. Filter by `cs_account_id` (required)
2. Optional date filters: `cs_sf_created_date` BETWEEN opened_from AND opened_to
3. Annotate with counts:
   - `comments_count = COUNT(case_comments WHERE cc_case_id = cs_sf_id)`
   - `timeline_count = COUNT(case_history WHERE ch_case_id = cs_sf_id)`

### Response Structure
```json
{
  "success": true,
  "message": "Cases retrieved successfully",
  "data": [
    {
      "id": "5001234567890ABC",
      "case_number": "00001234",
      "title": "Product defect",
      "status": "Open",
      "opened_at": "2026-02-01T10:30:00Z",
      "opened_at_display": "01/02/2026",
      "comments_count": 3,
      "timeline_count": 5
    }
  ]
}
```

---

## Product Performance APIs

### 1. Product Performance Deviation API

#### Endpoint
- **GET** `/api/products/performance/deviation/`

#### Query Parameters
- `account_id` (required): Salesforce Account ID
- `from` (required): Start month (YYYY-MM)
- `to` (required): End month (YYYY-MM)

#### Database Tables & Fields Used

**Actual Revenue:**
- **Table:** `invoice_line_items`, `invoices`, `products`
- **Fields:** `ili_net_price`, `inv_account_id`, `inv_invoice_date`, `inv_status`, `inv_valid`, `inv_invoice_type`

**Forecast Revenue:**
- **Table:** `arf_rolling_forecasts`, `products`
- **Fields:** `arf_approved_quantity`, `arf_approved_unit_price`, `arf_account_id`, `arf_forecast_date`

#### Business Logic & Formulas

**Actual Revenue Calculation:**
```sql
actualRevenue = SUM(ili_net_price)
WHERE:
  - inv_account_id = :account_id
  - inv_invoice_date BETWEEN :from_date AND :to_date
  - inv_status = 'Closed'
  - inv_valid = true
  - ili_valid = true
  - inv_invoice_type != 'Credit Note'
GROUP BY product
```

**Forecast Revenue Calculation:**
```sql
forecastRevenue = SUM(arf_approved_quantity * arf_approved_unit_price)
WHERE:
  - arf_account_id = :account_id
  - arf_forecast_date BETWEEN :from_date AND :to_date
  - arf_status = 'Approved'
GROUP BY product
```

**Deviation Calculation:**
```
deviation = actualRevenue - forecastRevenue
deviationPercent = (deviation / forecastRevenue) * 100
```

**Top/Bottom Performers:**
- Top 3: Highest positive deviation
- Bottom 2: Highest negative deviation

#### Response Structure
```json
{
  "success": true,
  "message": "Product performance retrieved successfully",
  "data": {
    "topPerformers": [
      {
        "productId": "PRD-001",
        "productName": "Roundup",
        "actualRevenue": 125000.00,
        "forecastRevenue": 100000.00,
        "deviation": 25000.00,
        "deviationPercent": 25.00
      }
    ],
    "bottomPerformers": [
      {
        "productId": "PRD-002",
        "productName": "Typhoon",
        "actualRevenue": 75000.00,
        "forecastRevenue": 100000.00,
        "deviation": -25000.00,
        "deviationPercent": -25.00
      }
    ]
  }
}
```

---

## Sales Analytics APIs

### 1. Product Family Analytics

#### Endpoint
- **GET** `/api/sales/family`

#### Query Parameters
- `accountId` (required): Salesforce Account ID
- `from` (required): Start month (YYYY-MM)
- `to` (required): End month (YYYY-MM)
- `page` (optional): Page number
- `page_size` (optional): Items per page (default 20, max 100)
- `search` (optional): Filter by family name

#### Database Tables & Fields Used
- **Actual Sales:** `invoice_line_items.ili_net_price`, `invoices`, `products.prd_family`
- **Last Year Sales:** Same as actual, but date range shifted back 1 year
- **Open Sales:** `order_items.ori_open_amount`, `orders`, `products.prd_family`
- **RFC:** `arf_rolling_forecasts.arf_approved_quantity`, `arf_rolling_forecasts.arf_approved_unit_price`

#### Business Logic & Formulas

**Actual Sales (Current Period):**
```sql
actualSales = SUM(ili_net_price)
WHERE:
  - inv_account_id = :account_id
  - inv_invoice_date BETWEEN :from_date AND :to_date
  - inv_status = 'Closed'
  - inv_valid = true
  - inv_invoice_type != 'Credit Note'
GROUP BY prd_family
```

**Last Year Sales (Same Period, Previous Year):**
```sql
lastYearSales = SUM(ili_net_price)
WHERE:
  - inv_account_id = :account_id
  - inv_invoice_date BETWEEN :ly_from_date AND :ly_to_date
  - inv_status = 'Closed'
  - inv_valid = true
  - inv_invoice_type != 'Credit Note'
GROUP BY prd_family
```

**Open Sales (Current Period):**
```sql
openSales = SUM(ori_open_amount)
WHERE:
  - ord_account_id = :account_id
  - ord_effective_date BETWEEN :from_date AND :to_date
  - ord_status = 'Open'
GROUP BY prd_family
```

**RFC (Rolling Forecast):**
```sql
rfc = SUM(arf_approved_quantity * arf_approved_unit_price)
WHERE:
  - arf_account_id = :account_id
  - arf_forecast_date BETWEEN :from_date AND :to_date
  - arf_status = 'Approved'
GROUP BY prd_family
```

**Deviation Percentage:**
```
deviationPercent = ((actualSales - rfc) / rfc) * 100
(Returns 0 if rfc = 0)
```

#### Response Structure
```json
{
  "success": true,
  "message": "Product family analytics retrieved successfully",
  "data": [
    {
      "family": "Herbicides",
      "actualSales": 250000.00,
      "openSales": 50000.00,
      "lastYearSales": 200000.00,
      "rfc": 240000.00,
      "deviationPercent": 4.17
    }
  ],
  "meta": {
    "pagination": {
      "current_page": 1,
      "page_size": 20,
      "total_count": 5
    }
  }
}
```

---

### 2. Product Analytics (by Family)

#### Endpoint
- **GET** `/api/sales/product`

#### Query Parameters
- `accountId` (required): Salesforce Account ID
- `family` (required): Product family name
- `from` (required): Start month (YYYY-MM)
- `to` (required): End month (YYYY-MM)
- `topX` (optional): Filter top X products (5, 10, 20, 30)
- `search` (optional): Filter by product name

#### Business Logic
Same formulas as Product Family Analytics, but:
1. Filter by `prd_family = :family`
2. Group by product instead of family
3. Order by `actualSales DESC`
4. Apply TopX filter if provided:
   - topX=5: Products ranked 1-5
   - topX=10: Products ranked 1-10
   - topX=20: Products ranked 11-20
   - topX=30: Products ranked 21-30

---

### 3. Order Contribution

#### Endpoint
- **GET** `/api/sales/orders`

#### Query Parameters
- `accountId` (required): Salesforce Account ID
- `productId` (required): Product Salesforce ID
- `from` (required): Start month (YYYY-MM)
- `to` (required): End month (YYYY-MM)
- `search` (optional): Filter by order number

#### Business Logic
```sql
SELECT order_number, order_status, 
       SUM(ori_ordered_quantity) as ordered_quantity,
       SUM(ori_ordered_amount) as ordered_amount,
       SUM(ori_open_quantity) as open_quantity,
       SUM(ori_open_amount) as open_amount
FROM order_items
JOIN orders ON ord_sf_id = ori_order_id
WHERE:
  - ord_account_id = :account_id
  - ori_product_id = :product_id
  - ord_effective_date BETWEEN :from_date AND :to_date
GROUP BY order_number, order_status
ORDER BY order_number
```

---

### 4. Order Details

#### Endpoint
- **GET** `/api/sales/order-details`

#### Query Parameters
- `accountId` (required): Salesforce Account ID
- `orderId` (required): Order Salesforce ID
- `from` (required): Start month (YYYY-MM)
- `to` (required): End month (YYYY-MM)
- `search` (optional): Filter by product name

#### Business Logic
Returns complete order information with all products in the order:
```sql
SELECT ord.*, ori.*, prd.prd_name
FROM orders ord
JOIN order_items ori ON ori_order_id = ord_sf_id
JOIN products prd ON prd_sf_id = ori_product_id
WHERE:
  - ord_account_id = :account_id
  - ori_order_id = :order_id
  - ord_effective_date BETWEEN :from_date AND :to_date
ORDER BY prd_name
```

---

## RFC (Rolling Forecast) APIs

### 1. RFC by Month API

#### Endpoint
- **GET** `/api/products/rfc-by-month/`

#### Query Parameters
- `account_id` (required): Salesforce Account ID
- `product_ids` (required): Comma-separated product IDs
- `from` (optional): Start month (YYYY-MM)
- `to` (optional): End month (YYYY-MM)

#### Default Date Range (when from/to not provided)
```
Current (RFC) period: Current month → Same month next year (13 months)
Last Year (LY) period: Same window shifted back 1 year
```

#### Database Tables & Fields Used

**Current Year RFC:**
- **Table:** `arf_rolling_forecasts`
- **Fields:** `arf_draft_quantity`, `arf_draft_value`, `arf_draft_unit_price`, `arf_approved_quantity`, `arf_approved_value`, `arf_approved_unit_price`, `arf_rejection_reason`

**Last Year Data:**
- **Table:** `invoice_line_items`, `invoices`
- **Fields:** `ili_quantity`, `ili_net_price`, `inv_invoice_date`

#### Business Logic & Formulas

**Last Year (LY) Aggregation:**
```sql
lyQty = SUM(ili_quantity)
lyValue = SUM(ili_net_price)
WHERE:
  - inv_account_id = :account_id
  - ili_product_id IN :product_ids
  - inv_invoice_date BETWEEN :ly_from_date AND :ly_to_date
  - inv_status IN ('Closed', 'Posted')
  - inv_valid = true
  - inv_invoice_type != 'Credit Note'
GROUP BY product_id, MONTH(inv_invoice_date)
```

**Draft RFC Aggregation:**
```sql
draftRfcQty = SUM(arf_draft_quantity)
draftRfcValue = SUM(arf_draft_value)
draftRfcUnitPrice = MAX(arf_draft_unit_price)
WHERE:
  - arf_account_id = :account_id
  - arf_product_id IN :product_ids
  - arf_forecast_date BETWEEN :from_date AND :to_date
  - arf_status IN ('Draft', 'Pending_Approval', 'Fixes_Needed')
GROUP BY product_id, MONTH(arf_forecast_date)
```

**Approved RFC Aggregation:**
```sql
approvedRfcQty = SUM(arf_approved_quantity)
approvedRfcValue = SUM(arf_approved_value)
approvedRfcUnitPrice = MAX(arf_approved_unit_price)
WHERE:
  - arf_account_id = :account_id
  - arf_product_id IN :product_ids
  - arf_forecast_date BETWEEN :from_date AND :to_date
  - arf_status = 'Approved'
GROUP BY product_id, MONTH(arf_forecast_date)
```

#### Response Structure
```json
{
  "success": true,
  "message": "RFC by month retrieved successfully",
  "data": {
    "accountId": "0011234567890ABC",
    "from": "2026-02",
    "to": "2026-07",
    "currencySymbol": "£",
    "products": [
      {
        "productId": "PRD-001",
        "productName": "Roundup",
        "months": [
          {
            "month": "2026-02",
            "monthLabel": "February 2026",
            "lyQty": 100,
            "lyValue": 35000.00,
            "draftRfcQty": 250,
            "draftRfcValue": 225000.00,
            "draftRfcUnitPrice": 900.00,
            "approvedRfcQty": 240,
            "approvedRfcValue": 216000.00,
            "approvedRfcUnitPrice": 900.00,
            "rejectionReason": null
          }
        ]
      }
    ]
  }
}
```

---

### 2. Update RFC API

#### Endpoint
- **PATCH** `/api/products/update-rfc/`

#### Request Body
```json
{
  "accountId": "0011234567890ABC",
  "updates": [
    {
      "productId": "PRD-001",
      "month": "2026-03",
      "draftRfcQty": 280
    }
  ]
}
```

#### Business Logic & Validation

**Validation Rules:**
1. `accountId` is required and must exist
2. `updates` array is required and non-empty
3. Each `month` must be YYYY-MM format and strictly in the future
4. Each `productId` must exist in products table
5. `draftRfcQty` must be non-negative number
6. Target row must exist with status IN ('Draft', 'Pending_Approval', 'Fixes_Needed')

**Update Logic:**
```
1. Parse month to forecast_date (first day of month)
2. Validate month is in future: forecast_date > today
3. Find row: arf_account_id = :account_id, 
             arf_product_id = :product_id,
             arf_forecast_date = :forecast_date,
             arf_status IN ('Draft', 'Pending_Approval', 'Fixes_Needed'),
             arf_active = 1
4. If row found:
   - Set arf_draft_quantity = draftRfcQty
   - Calculate arf_draft_value = draftRfcQty * unit_price
     (unit_price from existing row's arf_draft_unit_price or arf_approved_unit_price)
   - Set arf_agent_modified_by = current_user
   - Set arf_agent_modified_date = now()
   - Save row
5. Return updated count and list
```

#### Response Structure
```json
{
  "success": true,
  "message": "RFC updated successfully",
  "data": {
    "accountId": "0011234567890ABC",
    "updatedCount": 1,
    "updated": [
      {
        "rfcId": 12345,
        "productId": "PRD-001",
        "month": "2026-03"
      }
    ],
    "notUpdated": []
  }
}
```

---

### 3. Quarterly Performance (Achieved) API

#### Endpoint
- **GET** `/api/products/performance/achieved/`

#### Query Parameters
- `account_id` (required): Salesforce Account ID
- `year` (required): Calendar year (e.g., 2026)

#### Database Tables & Fields Used

**Frame Agreement:**
- **Table:** `frame_agreements`
- **Fields:** `fa_account_id`, `fa_agreement_type`, `fa_total_sales_ty`, `fa_total_sales_ly`

**Targets:**
- **Table:** `targets`
- **Fields:** `tgt_frame_agreement_id`, `tgt_quarter`, `tgt_net_turnover_target`, `tgt_rebate_if_achieved`, `tgt_rebate_rate`

**Actuals:**
- **Table:** `invoices`
- **Fields:** `inv_net_price`, `inv_invoice_date`, `inv_account_id`, `inv_status`

#### Business Logic & Formulas

**Invoice Actuals by Quarter:**
```sql
Q1_actual = SUM(inv_net_price) WHERE MONTH(inv_invoice_date) IN (1,2,3)
Q2_actual = SUM(inv_net_price) WHERE MONTH(inv_invoice_date) IN (4,5,6)
Q3_actual = SUM(inv_net_price) WHERE MONTH(inv_invoice_date) IN (7,8,9)
Q4_actual = SUM(inv_net_price) WHERE MONTH(inv_invoice_date) IN (10,11,12)
Year_actual = SUM(inv_net_price) WHERE YEAR(inv_invoice_date) = :year

WHERE:
  - inv_account_id = :account_id
  - inv_status = 'Closed'
  - inv_valid = true
  - inv_invoice_type != 'Credit Note'
```

**Agreement Type: Quarterly**
```
For each quarter (Q1-Q4) and Year:
  target = tgt_net_turnover_target (from targets table)
  actual = invoice sum for that period
  difference = actual - target
  percent = (actual / target) * 100 (if target > 0, else 0)
  rebate = tgt_rebate_if_achieved (if actual >= target, else 0)
```

**Agreement Type: Quarterly & Volume**
```
Same as Quarterly, with additional year-level volume target
```

**Agreement Type: Growth**
```
Q1-Q4: achieved = 0, rebate = 0
Year:
  growth_rebate = MAX(0, (fa_total_sales_ty - fa_total_sales_ly) * 0.15)
  actual = fa_total_sales_ty
```

#### Response Structure
```json
{
  "success": true,
  "message": "Achieved (by quarter or year) retrieved successfully",
  "data": {
    "accountId": "0011234567890ABC",
    "year": 2026,
    "currencySymbol": "£",
    "agreementType": "Quarterly",
    "periods": {
      "Q1": {
        "period": "Q1",
        "achieved": {
          "target": 10000.00,
          "actual": 12000.00,
          "difference": 2000.00,
          "percent": 120.00,
          "label": "Exceeded target by £2,000.00"
        },
        "rebate": 500.00,
        "rebate_label": "£500.00 earned"
      },
      "Year": {
        "period": "Year",
        "achieved": {
          "target": 40000.00,
          "actual": 41500.00,
          "difference": 1500.00,
          "percent": 103.75,
          "label": "Exceeded target by £1,500.00"
        },
        "rebate": 1200.00,
        "rebate_label": "£1,200.00 earned"
      }
    }
  }
}
```

---

## Summary

This document provides a complete reference for all APIs in the Agent360 system. Each API section includes:

- **Endpoints:** HTTP method and URL path
- **Query Parameters:** Required and optional parameters
- **Database Tables & Fields:** Exact tables and columns used
- **Business Logic & Formulas:** Step-by-step calculation logic
- **Response Structure:** Example JSON responses

All APIs follow a standardized response format with `success`, `message`, and `data` fields. Pagination is supported where applicable with `meta.pagination` information.
