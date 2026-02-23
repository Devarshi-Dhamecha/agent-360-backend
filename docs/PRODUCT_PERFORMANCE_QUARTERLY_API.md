# Product Performance Achieved API (by Quarter or Year)

## Overview

API endpoint to fetch achieved (target vs actual) and rebate for each quarter (Q1–Q4) and for the full year. Logic depends on the account’s frame agreement type: **Quarterly**, **Quarterly & Volume**, or **Growth**. Missing data is returned as 0. Currency symbol is derived from the account’s `acc_currency_iso_code`.

## Endpoint

```
GET /api/products/performance/achieved/
```

## Query Parameters

| Parameter   | Type   | Required | Format     | Description                          |
|------------|--------|----------|------------|--------------------------------------|
| `account_id` | string | Yes      | Salesforce ID | Account ID to filter by              |
| `year`       | integer | Yes     | e.g. 2026  | Calendar year for quarters and year  |

### Examples

```
GET /api/products/performance/achieved/?account_id=0011234567890ABC&year=2026
GET /api/products/performance/achieved/?account_id=001XXX&year=2025
```

## Business Logic

### Data Sources

- **Account:** `accounts.acc_sf_id` = `account_id`
- **Frame agreement:** `frame_agreements.fa_account_id` = account, `frame_agreements.fa_agreement_type` = type (Salesforce: `Frame_Agreement_Type_SP__c`; backend: `fa_agreement_type`)
- **Agreement types:** `Quarterly`, `Quarterly & Volume`, `Growth`
- **Targets:** `targets.tgt_frame_agreement_id`, `tgt_quarter` (Q1, Q2, Q3, Q4, Year), `tgt_net_turnover_target`, `tgt_rebate_if_achieved`, `tgt_rebate_rate`
- **Actuals:** Invoices for the account; sum of `inv_net_price` by quarter and full year using `inv_invoice_date`

### Invoice Actuals (Quarter and Year)

**Source:** `invoices.inv_net_price`

**Filters:**
- `invoices.inv_account_id` = :account_id
- `invoices.inv_invoice_date` within quarter or year range
- `invoices.inv_status` = 'Closed'
- `invoices.inv_valid` = true
- `invoices.inv_invoice_type` != 'Credit Note'

**Aggregation:**
- Per quarter: sum for dates in that quarter (Q1: Jan–Mar, Q2: Apr–Jun, Q3: Jul–Sep, Q4: Oct–Dec)
- Full year: sum for dates in the given calendar year

### Agreement Type: Quarterly

- **Targets:** One target record per quarter (Q1–Q4) and one for the year (`tgt_quarter` = 'Year') with `tgt_net_turnover_target`.
- **Actuals:** Invoice sum per quarter and for full year (as above).
- **Achieved (per quarter and year):**
  - `difference = actual - target`
  - `percent = (actual / target) * 100` (if target > 0; else 0 or 100 as defined)
  - Label: e.g. "Exceeded target by £X" or "Below target by £X"
- **Rebate:** `tgt_rebate_if_achieved` when actual ≥ target for that period; otherwise 0.

### Agreement Type: Quarterly & Volume

- Same as **Quarterly** for per-quarter and year targets, actuals, achieved (money + %), and rebate.
- Additionally: year-level volume target (`tgt_net_turnover_target` for `tgt_quarter` = 'Year'); compare full-year invoice total to this target; rebate from year target when achieved.

### Agreement Type: Growth

- **No target records** for quarters or year.
- **Year rebate formula:** `growth_rebate = max(0, (fa_total_sales_ty - fa_total_sales_ly) * 0.15)`
  - `fa_total_sales_ty` = Total Sales This Year (`Total_Sales_This_Year__c`)
  - `fa_total_sales_ly` = Total Sales Last Year (`Total_Sales_Last_Year__c`)
- **Q1–Q4:** Achieved and rebate returned as 0.
- **Year:** Return growth rebate as money; achieved can show "Growth (no target)" with actual = fa_total_sales_ty.

### Quarter and Year Boundaries

- **Quarters:** Calendar: Q1 = Jan–Mar, Q2 = Apr–Jun, Q3 = Jul–Sep, Q4 = Oct–Dec (from `inv_invoice_date`).
- **Year:** Full calendar year for the given `year` parameter.

### Edge Cases

- **No frame agreement** for account/year: return all periods (Q1–Q4, Year) with achieved and rebate 0.
- **Missing target for a period:** Use target = 0; still return actual, difference, and percent (or N/A as defined).
- **No invoices for a period:** Actual = 0; achieved = −target (money), 0% (or as defined); rebate = 0.
- **Unknown agreement type:** Treat as no data; return 0 for all periods or map to closest type per product owner.

## Response Format

### Success Response (200 OK)

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
          "target": 10000.0,
          "actual": 12000.0,
          "difference": 2000.0,
          "percent": 120.0,
          "label": "Exceeded target by £2,000.00"
        },
        "rebate": 500.0,
        "rebate_label": "£500.00 earned"
      },
      "Q2": {
        "period": "Q2",
        "achieved": {
          "target": 10000.0,
          "actual": 9500.0,
          "difference": -500.0,
          "percent": 95.0,
          "label": "Below target by £500.00"
        },
        "rebate": 0.0,
        "rebate_label": "£0"
      },
      "Q3": {
        "period": "Q3",
        "achieved": {
          "target": 0.0,
          "actual": 0.0,
          "difference": 0.0,
          "percent": 0.0,
          "label": "No target"
        },
        "rebate": 0.0,
        "rebate_label": "£0"
      },
      "Q4": {
        "period": "Q4",
        "achieved": {
          "target": 0.0,
          "actual": 0.0,
          "difference": 0.0,
          "percent": 0.0,
          "label": "No target"
        },
        "rebate": 0.0,
        "rebate_label": "£0"
      },
      "Year": {
        "period": "Year",
        "achieved": {
          "target": 40000.0,
          "actual": 41500.0,
          "difference": 1500.0,
          "percent": 103.75,
          "label": "Exceeded target by £1,500.00"
        },
        "rebate": 1200.0,
        "rebate_label": "£1,200.00 earned"
      }
    }
  }
}
```

All periods (Q1, Q2, Q3, Q4, Year) are always present. Missing data uses 0 for numeric fields and appropriate labels (e.g. "No target", "£0").

### Error Responses

#### 422 Unprocessable Entity - Missing account_id

```json
{
  "success": false,
  "message": "Invalid query parameters",
  "errors": [
    {
      "field": "account_id",
      "message": "account_id is required"
    }
  ]
}
```

#### 422 Unprocessable Entity - Missing year

```json
{
  "success": false,
  "message": "Invalid query parameters",
  "errors": [
    {
      "field": "year",
      "message": "year is required"
    }
  ]
}
```

#### 422 Unprocessable Entity - Invalid year

```json
{
  "success": false,
  "message": "Invalid query parameters",
  "errors": [
    {
      "field": "year",
      "message": "year must be an integer (e.g. 2026)"
    }
  ]
}
```

#### 422 Unprocessable Entity - Year out of range

```json
{
  "success": false,
  "message": "Invalid query parameters",
  "errors": [
    {
      "field": "year",
      "message": "year must be between 2000 and 2100"
    }
  ]
}
```

## Implementation Architecture

### Layer Structure

```
Controller Layer (views.py)
    ↓
Service Layer (services.py)
    ↓
Models: Account, FrameAgreement, Target, Invoice
```

### Components

1. **Service Layer**
   - Resolve account and frame agreement for the given account_id and year (date overlap: `fa_start_date` / `fa_end_date`).
   - Read `fa_agreement_type` and branch: Quarterly, Quarterly & Volume, or Growth.
   - For Quarterly / Quarterly & Volume: load targets (Q1–Q4, Year); compute invoice sums per quarter and full year; for each period compute achieved (target, actual, difference, percent, label) and rebate.
   - For Growth: use `fa_total_sales_ty` and `fa_total_sales_ly`; compute growth rebate; return 0 for Q1–Q4.
   - Resolve currency symbol from account’s `acc_currency_iso_code` (e.g. GBP → £).

2. **Controller Layer**
   - Validate query parameters (account_id required, year required, year integer and in 2000–2100).
   - Call service layer (`get_quarterly_performance`).
   - Return standardized response format (success, message, data).

## Database Indexes

### Relevant Indexes

- `frame_agreements`: `fa_account_id`, `fa_start_date`, `fa_end_date`
- `targets`: `tgt_frame_agreement_id`, `tgt_quarter`
- `invoices`: `inv_account_id`, `inv_invoice_date`, `inv_status`, `inv_valid`
- `accounts`: `acc_sf_id` (primary key), `acc_currency_iso_code`

## Performance Considerations

1. **Single account and year:** Queries are scoped by account_id and year; frame agreement and targets are filtered accordingly.
2. **Invoice aggregation:** Sum `inv_net_price` per quarter and year in one or few queries (e.g. by quarter buckets or single pass with date filters).
3. **Currency symbol:** One account lookup for `acc_currency_iso_code`; map to symbol via a small static map (e.g. GBP → £).
4. **Missing data:** No nulls in response; use 0 and fixed structure (Q1–Q4, Year) for predictable frontend consumption.

## Implementation Checklist

- [x] Resolve account and frame agreement for account_id and year
- [x] Branch logic by agreement type (Quarterly, Quarterly & Volume, Growth)
- [x] Load targets for Q1–Q4 and Year where applicable
- [x] Compute invoice actuals per quarter and full year with correct filters
- [x] Compute achieved (target, actual, difference, percent, label) and rebate per period
- [x] Growth: compute year rebate from fa_total_sales_ty and fa_total_sales_ly; Q1–Q4 = 0
- [x] Return fixed structure with all periods; use 0 for missing data
- [x] Validate account_id and year; return 422 with field errors
- [x] Use account currency for symbol in labels and response

## Notes

- Uses existing project response wrapper structure (success, message, data).
- Currency symbol comes from `accounts.acc_currency_iso_code`; extend `CURRENCY_SYMBOLS` in services for more codes.
- Frame agreement is selected by account and date overlap with the requested year; one active agreement per account/year in scope.
- This document aligns with the structure and style of the Product Performance Deviation API doc.
