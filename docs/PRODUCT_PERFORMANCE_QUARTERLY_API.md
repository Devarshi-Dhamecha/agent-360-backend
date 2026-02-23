# Cursor Prompt: Quarterly & Year Performance API (Achieved + Rebate)

## API contract

- **Endpoint:** `GET /api/products/performance/achieved/`
- **Query parameters:**
  - `account_id` (required): Salesforce Account ID (e.g. `0011234567890ABC`)
  - `year` (required): Calendar year, e.g. `2026`

**Example:**  
`GET /api/products/performance/achieved/?account_id=001XXX&year=2026`

---

## Response shape (always return all quarters and year)

Return **Achieved** and **Rebate** for each of Q1, Q2, Q3, Q4 and **Year**. If no data exists for a period, use **0** (and still include the period).

- **Achieved:** target vs actual (invoices) for that period: **money difference** and **percentage** (e.g. “Exceeded Q1 Target by £2,000”, “120.0%”, or “Below target” when not met).
- **Rebate:** rebate earned for that period (e.g. “Rebate: £500 earned”). If none, return 0 / “£0”.

Example UI-style strings (backend can return structured data and let frontend format):

- **ACHIEVED:** “Exceeded Q1 Target by £2,000”, “£2,000”, “120.0%”
- **Rebate:** “£500 earned”

All periods must be present: **Q1, Q2, Q3, Q4, Year**. Missing data → **0** (and no nulls for numeric/string fields that the frontend will display).

---

## Data sources (DB / SF mapping)

- **Account:** `accounts.acc_sf_id` = `account_id`
- **Frame agreement (contact/account):** `frame_agreements.fa_account_id` = account, `frame_agreements.fa_agreement_type` = type.  
  (In SF this may be on Contact as `Frame_Agreement_Type_SP__c`; in this backend it is on **Frame Agreement** as `fa_agreement_type`.)
- **Agreement type** controls logic (see below): `Quarterly`, `Quarterly & Volume`, `Growth`.
- **Targets:** `targets.tgt_frame_agreement_id`, `tgt_quarter` (e.g. `Q1`, `Q2`, `Q3`, `Q4`, `Year`), `tgt_net_turnover_target` (= `Net_Turnover_Target__c`), `tgt_rebate_if_achieved`, `tgt_rebate_rate`, etc.
- **Actuals:** from **invoices**: same account, sum of `inv_net_price` (or equivalent total per invoice) by quarter and for full year. Use `inv_invoice_date` to assign quarter and year. Consider only closed/valid invoices if that matches existing product performance rules.

---

## Business logic by agreement type

### 1. Quarterly

- **Targets:**  
  - One target record **per quarter** (Q1–Q4) with `tgt_net_turnover_target`.  
  - One target record for the **year** with `tgt_quarter = 'Year'` (or equivalent) and `tgt_net_turnover_target`.
- **Actuals:**  
  - Per quarter: sum of invoice amount (e.g. `inv_net_price`) for that account and quarter (derive quarter from `inv_invoice_date`).  
  - Full year: sum for that account and year.
- **Achieved (per quarter and year):**  
  - Compare **actual** to **target** (`tgt_net_turnover_target`).  
  - Return: **money difference** (actual − target) and **percentage** (e.g. (actual / target) × 100).  
  - If no target for that period → treat as 0 target and still return money and % (or “N/A” only if product owner explicitly wants that).
- **Rebate:**  
  - From target: e.g. `tgt_rebate_if_achieved` when target is met for that period; otherwise 0.  
  - Return rebate amount per quarter and for the year (if there is a year-level rebate/target). If not available → 0.

### 2. Quarterly & Volume

- Same as **Quarterly** for:
  - Per-quarter targets and actuals, and year target vs full-year actual.
  - Achieved: money + % per quarter and for year.
  - Rebate per quarter and year as above.
- **Additionally:**  
  - There is a **year-level volume** target (again `tgt_net_turnover_target` on the year target record).  
  - Compare **full-year invoice total** to this year target; show **money + %** for the year (same format as above).  
  - Rebate for year as above (e.g. from year target’s `tgt_rebate_if_achieved` when achieved).

### 3. Growth

- **No target records** for quarters/year.
- **Formula (year-level):**  
  `IF((Total_Sales_This_Year__c - Total_Sales_Last_Year__c) * 0.15 < 0, 0, (Total_Sales_This_Year__c - Total_Sales_Last_Year__c) * 0.15)`
- **Mapping:**  
  - `Total_Sales_This_Year__c` → e.g. `frame_agreements.fa_total_sales_ty`  
  - `Total_Sales_Last_Year__c` → e.g. `frame_agreements.fa_total_sales_ly`  
  - So: **growth_rebate = max(0, (fa_total_sales_ty - fa_total_sales_ly) * 0.15)**.
- **Response:**  
  - **Q1–Q4:** No targets → return **Achieved** and **Rebate** as **0** (or “N/A” if agreed).  
  - **Year:** Return the **growth rebate** as money and, if useful, a percentage (e.g. vs last year).  
  - No per-quarter rebate/target for Growth.

---

## Quarter and year boundaries

- **Quarters:** Calendar quarters: Q1 = Jan–Mar, Q2 = Apr–Jun, Q3 = Jul–Sep, Q4 = Oct–Dec (based on `inv_invoice_date`).
- **Year:** Full calendar year for the given `year` parameter.

---

## Edge cases

- **No frame agreement** for account/year: return all periods (Q1–Q4, Year) with Achieved and Rebate **0**.
- **Unknown agreement type:** Treat like “no data” and return 0 for all, or map to the closest type (e.g. default to Quarterly) per product owner.
- **Missing target for a quarter/year:** Use target = 0 for that period; still return actual and % (or “N/A” if required).
- **No invoices for a period:** Actual = 0; Achieved = −target (money) and 0% (or as defined); Rebate = 0.

---

## Implementation checklist

1. Resolve **account** by `account_id` and **frame agreement** for that account covering the given **year** (e.g. `fa_start_date`/`fa_end_date` or `fa_start_year`).
2. Read **agreement type** (`fa_agreement_type`) and branch: **Quarterly**, **Quarterly & Volume**, or **Growth**.
3. For **Quarterly** and **Quarterly & Volume:**  
   - Load **targets** for the frame agreement: Q1, Q2, Q3, Q4, Year (use `tgt_quarter`).  
   - Compute **invoice totals** per quarter and full year (same account, `inv_invoice_date` in range, closed/valid as per existing rules).  
   - For each period: **Achieved** = (actual, target, difference, %) and **Rebate** = from target when achieved.
4. For **Growth:**  
   - Use `fa_total_sales_ty` and `fa_total_sales_ly`; compute growth rebate; return 0 for Q1–Q4 and year achieved/rebate as above.
5. **Response:** Always return a fixed structure: **Q1, Q2, Q3, Q4, Year**, each with **achieved** (money diff, percentage, label) and **rebate** (amount). Use **0** when data is not available.

This prompt is intended for Cursor (or similar) to implement the API and service logic consistently with the existing codebase and DB schema.
