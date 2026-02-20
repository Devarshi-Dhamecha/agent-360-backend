# Feature: Sales Order Drilldown APIs with RFC (Forecast)

Implement a 4-level Sales Drilldown Reporting Module.

---

# 🔥 Architecture Rule

Create separate APIs per level.

Do NOT create a dynamic level-based API.

---

# 📥 Mandatory Filters (All APIs)

All APIs must accept:

- accountId
- from (YYYY-MM)
- to (YYYY-MM)

Convert internally:

fromDate = first day of month  
toDate   = last day of month  

Use:

orders.ord_effective_date

---

# 🟦 LEVEL 1 — Product Family API

## Endpoint

GET /api/sales/family

---

## ACTUALS CTE

orders ord  
JOIN order_items ori  
JOIN products prd  

WHERE

- ord.ord_account_id = :accountId
- ord.ord_effective_date BETWEEN :fromDate AND :toDate
- ord.ord_active = 1
- ori.ori_active = 1
- prd.prd_active = 1

GROUP BY

prd.prd_family

Aggregate:

- SUM(ori.ori_ordered_amount) → actualSales
- SUM(ori.ori_open_amount)    → openSales

---

## LAST YEAR CTE

Same query but:

ord_effective_date BETWEEN  
(fromDate - INTERVAL '1 year')  
AND  
(toDate - INTERVAL '1 year')

Aggregate:

SUM(ori.ori_ordered_amount) → lastYearSales

---

## RFC CTE

forecast arf  
JOIN products prd  
ON prd.prd_sf_id = arf.arf_product_id

WHERE

- arf.arf_account_id = :accountId
- arf.arf_status = 'Approved'
- arf.arf_forecast_date BETWEEN :fromDate AND :toDate
- arf.arf_active = 1
- prd.prd_active = 1

GROUP BY

prd.prd_family

Aggregate:

SUM(arf.arf_approved_value) → rfc

---

## FINAL RESULT

LEFT JOIN all 3 CTEs on prd_family

DeviationPercent =  
CASE  
WHEN rfc = 0 THEN 0  
ELSE ((actualSales - rfc) / rfc) * 100  
END

---

# 🟦 LEVEL 2 — Product API

## Endpoint

GET /api/sales/product?family={familyName}

Repeat same 3 CTE logic but:

Add filter:

prd.prd_family = :familyName

Group by:

ori.ori_product_id  
prd.prd_name

RFC CTE:

GROUP BY arf.arf_product_id

Join on:

ori_product_id = arf_product_id

---

# 🟦 LEVEL 3 — Order Contribution API

## Endpoint

GET /api/sales/orders?productId={productId}

WHERE:

ori.ori_product_id = :productId

Group by:

ori.ori_order_id  
ord.ord_order_number  
ord.ord_status

Aggregate:

- SUM(ori.ori_ordered_quantity)
- SUM(ori.ori_ordered_amount)
- SUM(ori.ori_open_quantity)
- SUM(ori.ori_open_amount)

Show ONLY selected product contribution per order.

---

# 🟦 LEVEL 4 — Order Details API

## Endpoint

GET /api/sales/order-details?orderId={orderId}

WHERE:

ori.ori_order_id = :orderId

Group by:

ori.ori_product_id  
prd.prd_name  
ori.ori_status

Aggregate:

- SUM(ori.ori_ordered_quantity)
- SUM(ori.ori_ordered_amount)
- SUM(ori.ori_open_quantity)
- SUM(ori.ori_open_amount)

Show ALL products inside order.

---

# ⚙️ Index Check Rule

Check existence before creation:

- orders(ord_account_id)
- orders(ord_effective_date)
- order_items(ori_product_id)
- order_items(ori_order_id)
- products(prd_sf_id)
- products(prd_family)
- forecast(arf_account_id)
- forecast(arf_product_id)
- forecast(arf_forecast_date)

Create only if missing using migration.

Example:

CREATE INDEX IF NOT EXISTS idx_orders_account  
ON orders(ord_account_id);

---

# 🚀 Implementation Rules

- Follow Controller → Service → Repository pattern
- No raw SQL in controller
- Aggregation must be in repository layer
- Use parameter binding
- Use existing response wrapper
- Return empty array if no data
- Do not modify unrelated modules
- Add validation for required params

---

# 📦 Deliverables

- 4 Controller endpoints
- 4 Service methods
- Repository queries
- DTO mappings
- Optional migration for missing indexes

Frontend changes not required.