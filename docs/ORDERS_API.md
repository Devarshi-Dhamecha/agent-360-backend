# Orders API Documentation

## Overview
This document describes the Orders and Order Line Items data models in the products module.

## Database Tables

### 1. Orders Table (`orders`)

Stores Salesforce Order records representing customer orders.

**Salesforce Object:** `Order`  
**Sync Direction:** READ (from Salesforce to Agent360)

#### Fields

| Field Name | Column Name | Data Type | Nullable | Key | Description |
|------------|-------------|-----------|----------|-----|-------------|
| Order ID | ord_sf_id | VARCHAR(18) | NOT NULL | PK | Salesforce record ID |
| Order Number | ord_order_number | VARCHAR(30) | NOT NULL | | Auto-generated order reference |
| Account | ord_account_id | VARCHAR(18) | NOT NULL | FK → accounts | Parent customer account |
| Status | ord_status | VARCHAR(100) | NOT NULL | | Draft / Activated / Shipped / Closed |
| Order Start Date | ord_effective_date | DATE | NOT NULL | | Contract / order start date |
| End Date | ord_end_date | DATE | YES | | Order end date |
| Type | ord_type | VARCHAR(100) | YES | | Order type |
| Total Amount | ord_total_amount | NUMERIC(18,2) | YES | | Sum of all order product lines |
| Open Amount | ord_open_amount | NUMERIC(18,2) | YES | | Sum of all order product open sales amount |
| Open Quantity | ord_open_quantity | NUMERIC(18,2) | YES | | Open quantity |
| Open Amount with Tax | ord_open_amount_tax | NUMERIC(18,2) | YES | | Open amount including tax |
| Ordered Quantity | ord_ordered_quantity | NUMERIC(18,2) | YES | | Total ordered quantity |
| Ordered Amount with Tax | ord_ordered_amount_tax | NUMERIC(18,2) | YES | | Ordered amount including tax |
| Currency | ord_currency_iso_code | VARCHAR(10) | YES | | Currency code (if multi-currency enabled) |
| Owner | ord_owner_id | VARCHAR(18) | NOT NULL | FK → users | Sales rep owner |
| Contract | ord_contract_id | VARCHAR(18) | YES | | Linked contract if applicable |
| Created Date | ord_sf_created_date | TIMESTAMP | NOT NULL | | Salesforce creation date |
| Last Modified Date | ord_last_modified_date | TIMESTAMP | NOT NULL | | Last modification date (for incremental sync) |
| Last Modified By | ord_last_modified_by_id | VARCHAR(18) | NOT NULL | | User who last modified |
| Active Flag | ord_active | SMALLINT | NOT NULL | | System flag (default 1) |
| Created At | ord_created_at | TIMESTAMP | NOT NULL | | Agent360 creation timestamp |
| Updated At | ord_updated_at | TIMESTAMP | NOT NULL | | Agent360 update timestamp |

#### Indexes
- `idx_orders_account` on `ord_account_id`
- `idx_orders_status` on `ord_status`
- `idx_orders_effective_date` on `ord_effective_date`
- `idx_orders_owner` on `ord_owner_id`

---

### 2. Order Line Items Table (`order_line_items`)

Stores individual line items for each order.

**Salesforce Object:** `OrderItem`  
**Sync Direction:** READ (from Salesforce to Agent360)

#### Fields

| Field Name | Column Name | Data Type | Nullable | Key | Description |
|------------|-------------|-----------|----------|-----|-------------|
| Record ID | ori_sf_id | VARCHAR(18) | NOT NULL | PK | Salesforce OrderItem ID |
| Order | ori_order_id | VARCHAR(18) | NOT NULL | FK → orders | Parent order |
| Product | ori_product_id | VARCHAR(18) | NOT NULL | FK → products | Product reference |
| Product Name | ori_product_name | VARCHAR(255) | YES | | Denormalized product name for display |
| Product Code | ori_product_code | VARCHAR(255) | YES | | SKU - denormalized for query performance |
| Quantity | ori_quantity | NUMERIC(18,2) | NOT NULL | | Order quantity |
| Unit Price | ori_unit_price | NUMERIC(18,2) | NOT NULL | | Sales price per unit |
| Total Price | ori_total_price | NUMERIC(18,2) | YES | | Qty × UnitPrice (SF calculated field) |
| Open Amount | ori_open_amount | NUMERIC(18,2) | YES | | Order item open sales amount |
| Open Amount with Tax | ori_open_amount_tax | NUMERIC(18,2) | YES | | Order item open sales amount with tax |
| Open Quantity | ori_open_quantity | NUMERIC(18,2) | YES | | Open quantity remaining |
| Ordered Amount | ori_ordered_amount | NUMERIC(18,2) | YES | | Total ordered amount |
| Ordered Quantity | ori_ordered_quantity | NUMERIC(18,2) | YES | | Total ordered quantity |
| Status | ori_status | VARCHAR(100) | YES | | Item status |
| Description | ori_description | TEXT | YES | | Line item description |
| Service Date | ori_service_date | DATE | YES | | Delivery / service date for this line |
| Created Date | ori_sf_created_date | TIMESTAMP | NOT NULL | | Salesforce creation date |
| Last Modified Date | ori_last_modified_date | TIMESTAMP | NOT NULL | | Last modification date (for incremental sync) |
| Last Modified By | ori_last_modified_by_id | VARCHAR(18) | NOT NULL | | User who last modified |
| Active Flag | ori_active | SMALLINT | NOT NULL | | System flag (default 1) |
| Created At | ori_created_at | TIMESTAMP | NOT NULL | | Agent360 creation timestamp |
| Updated At | ori_updated_at | TIMESTAMP | NOT NULL | | Agent360 update timestamp |

#### Indexes
- `idx_order_line_items_order` on `ori_order_id`
- `idx_order_line_items_product` on `ori_product_id`

---

## Relationships

```
accounts (Account)
    ↓ (1:N)
orders (Order)
    ↓ (1:N)
order_line_items (OrderItem)
    ↓ (N:1)
products (Product)

users (User) ← (N:1) ← orders (Owner)
```

## Django Models

### Order Model
- **Model Class:** `Order`
- **Location:** `apps/products/models.py`
- **Admin:** Registered in `apps/products/admin.py`

### OrderLineItem Model
- **Model Class:** `OrderLineItem`
- **Location:** `apps/products/models.py`
- **Admin:** Registered in `apps/products/admin.py`

## Migration

The models were created in migration:
- **File:** `apps/products/migrations/0003_order_orderlineitem_order_idx_orders_account_and_more.py`
- **Status:** Applied successfully

## Notes

1. Both tables are READ-ONLY from Salesforce perspective
2. Foreign key relationships:
   - Orders link to Accounts and Users
   - Order Line Items link to Orders and Products
3. Denormalized fields (product_name, product_code) improve query performance
4. All monetary fields use NUMERIC(18,2) for precision
5. Indexes are optimized for common query patterns (by account, status, date, product)
