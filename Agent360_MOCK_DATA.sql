-- ================================================================
-- Agent360 Salesforce-like Seed Data
-- Run AFTER Agent360_DDL.sql
-- PostgreSQL 17+
-- ================================================================

BEGIN;

-- Compatibility guard:
-- Some environments (e.g. ORM-created tables) keep *_created_at / *_updated_at as NOT NULL
-- without DEFAULT values. This block sets safe defaults so inserts work consistently.
DO $$
DECLARE
    rec RECORD;
BEGIN
    -- Default NOW() for any NOT NULL timestamp column missing a default.
    -- This handles schema variants like asc_generated_at and audit columns.
    FOR rec IN
        SELECT table_schema, table_name, column_name
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND is_nullable = 'NO'
          AND column_default IS NULL
          AND data_type LIKE 'timestamp%'
    LOOP
        EXECUTE format(
            'ALTER TABLE %I.%I ALTER COLUMN %I SET DEFAULT NOW()',
            rec.table_schema, rec.table_name, rec.column_name
        );
    END LOOP;

    -- Default 1 for smallint active flags
    FOR rec IN
        SELECT table_schema, table_name, column_name
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND is_nullable = 'NO'
          AND column_default IS NULL
          AND data_type = 'smallint'
          AND column_name LIKE '%\_active' ESCAPE '\'
    LOOP
        EXECUTE format(
            'ALTER TABLE %I.%I ALTER COLUMN %I SET DEFAULT 1',
            rec.table_schema, rec.table_name, rec.column_name
        );
    END LOOP;
END
$$;

-- 1) user_roles
INSERT INTO user_roles (ur_sf_id, ur_name, ur_last_modified_date, ur_system_modstamp, ur_active)
VALUES
    ('00E8b0000004Qx1EAE', 'System Administrator', NOW() - INTERVAL '30 days', NOW() - INTERVAL '30 days', 1),
    ('00E8b0000004Qx2EAE', 'Sales Manager',         NOW() - INTERVAL '15 days', NOW() - INTERVAL '15 days', 1),
    ('00E8b0000004Qx3EAE', 'Customer Support',      NOW() - INTERVAL '10 days', NOW() - INTERVAL '10 days', 1)
ON CONFLICT (ur_sf_id) DO NOTHING;

-- 2) users
INSERT INTO users (
    usr_sf_id, usr_username, usr_email, usr_first_name, usr_last_name, usr_name,
    usr_is_active, usr_profile_id, usr_user_role_id, usr_federation_id,
    usr_time_zone, usr_language, usr_sf_created_date, usr_last_modified_date, usr_last_modified_by_id, usr_active
)
VALUES
    ('0058b00000K7mAQAQX', 'michael.clark', 'michael.clark@northbridgepharma.com', 'Michael', 'Clark', 'Michael Clark', TRUE, '00e8b000001LxR1AAK', '00E8b0000004Qx1EAE', 'mclark.nbp',  'America/New_York', 'en_US', NOW() - INTERVAL '365 days', NOW() - INTERVAL '2 days', '0058b00000K7mAQAQX', 1),
    ('0058b00000K7mBBAQX', 'sarah.lee',     'sarah.lee@northbridgepharma.com',     'Sarah',   'Lee',   'Sarah Lee',     TRUE, '00e8b000001LxR2AAK', '00E8b0000004Qx2EAE', 'slee.nbp',    'America/Chicago',  'en_US', NOW() - INTERVAL '300 days', NOW() - INTERVAL '1 days', '0058b00000K7mAQAQX', 1),
    ('0058b00000K7mCCAQX', 'john.keller',   'john.keller@northbridgepharma.com',   'John',    'Keller','John Keller',   TRUE, '00e8b000001LxR3AAK', '00E8b0000004Qx2EAE', 'jkeller.nbp', 'America/Denver',   'en_US', NOW() - INTERVAL '250 days', NOW() - INTERVAL '1 days', '0058b00000K7mAQAQX', 1),
    ('0058b00000K7mDDAQX', 'maria.ross',    'maria.ross@northbridgepharma.com',    'Maria',   'Ross',  'Maria Ross',    TRUE, '00e8b000001LxR4AAK', '00E8b0000004Qx3EAE', 'mross.nbp',   'America/New_York', 'en_US', NOW() - INTERVAL '220 days', NOW() - INTERVAL '1 days', '0058b00000K7mAQAQX', 1)
ON CONFLICT (usr_sf_id) DO NOTHING;

-- 3) record_types
INSERT INTO record_types (
    rt_sf_id, rt_name, rt_developer_name, rt_sobject_type, rt_is_active,
    rt_sf_created_date, rt_last_modified_date, rt_last_modified_by_id, rt_active
)
VALUES
    ('0128b000000N4aEAAS', 'Marketing Campaign', 'Marketing_Campaign', 'Campaign', TRUE, NOW() - INTERVAL '180 days', NOW() - INTERVAL '5 days', '0058b00000K7mAQAQX', 1),
    ('0128b000000N4aFAAS', 'Trade Program',      'Trade_Program',      'Campaign', TRUE, NOW() - INTERVAL '180 days', NOW() - INTERVAL '5 days', '0058b00000K7mAQAQX', 1)
ON CONFLICT (rt_sf_id) DO NOTHING;

-- 4) product_brands
INSERT INTO product_brands (
    pb_sf_id, pb_name, pb_brand_code, pb_description, pb_is_active,
    pb_sf_created_date, pb_last_modified_date, pb_active
)
VALUES
    ('a0B8b00000BrdA1EAF', 'Alpha Health', 'ALPHA', 'Core healthcare portfolio', TRUE, NOW() - INTERVAL '200 days', NOW() - INTERVAL '3 days', 1),
    ('a0B8b00000BrdB2EAF', 'Nova Care',    'NOVA',  'Supplement and wellness line', TRUE, NOW() - INTERVAL '190 days', NOW() - INTERVAL '3 days', 1)
ON CONFLICT (pb_sf_id) DO NOTHING;

-- 5) accounts
INSERT INTO accounts (
    acc_sf_id, acc_name, acc_owner_id, acc_credit_limit, acc_invoice_open_amount, acc_order_open_amount,
    acc_account_number, acc_currency_iso_code, acc_last_modified_date, acc_last_modified_by_id, acc_active
)
VALUES
    ('0018b00002HkL1AAAV', 'North Valley Health', '0058b00000K7mBBAQX', 500000.00, 42000.00, 15000.00, 'ACC-1001', 'USD', NOW() - INTERVAL '1 days', '0058b00000K7mBBAQX', 1),
    ('0018b00002HkL2AAAV', 'Summit Medical Group', '0058b00000K7mCCAQX', 750000.00, 68000.00, 22000.00, 'ACC-1002', 'USD', NOW() - INTERVAL '1 days', '0058b00000K7mCCAQX', 1),
    ('0018b00002HkL3AAAV', 'Metro Clinic Network', '0058b00000K7mBBAQX', 300000.00, 12000.00,  5000.00, 'ACC-1003', 'USD', NOW() - INTERVAL '1 days', '0058b00000K7mBBAQX', 1)
ON CONFLICT (acc_sf_id) DO NOTHING;

-- 6) products
INSERT INTO products (
    prd_sf_id, prd_name, prd_family, prd_classification, prd_central_product_code, prd_product_code,
    prd_product_brand_id, prd_brand, prd_is_active, prd_sf_created_date, prd_last_modified_date,
    prd_last_modified_by_id, prd_active
)
VALUES
    ('01t8b00001PrdA1AAH', 'Aspirin 500mg', 'Pharma',     'OTC',       'CP-0001', 'P-ASP-500', 'a0B8b00000BrdA1EAF', 'Alpha Health', TRUE, NOW() - INTERVAL '150 days', NOW() - INTERVAL '2 days', '0058b00000K7mAQAQX', 1),
    ('01t8b00001PrdB2AAH', 'Vitamin D3',    'Supplements','Nutritional','CP-0002', 'P-VD3-100', 'a0B8b00000BrdB2EAF', 'Nova Care',    TRUE, NOW() - INTERVAL '140 days', NOW() - INTERVAL '2 days', '0058b00000K7mAQAQX', 1),
    ('01t8b00001PrdC3AAH', 'Pain Relief Gel','Topical',   'OTC',        'CP-0003', 'P-PRG-050', 'a0B8b00000BrdA1EAF', 'Alpha Health', TRUE, NOW() - INTERVAL '130 days', NOW() - INTERVAL '2 days', '0058b00000K7mAQAQX', 1)
ON CONFLICT (prd_sf_id) DO NOTHING;

-- 7) account_plans
INSERT INTO account_plans (
    ap_sf_id, ap_name, ap_account_id, ap_plan_name, ap_status, ap_start_date, ap_end_date,
    ap_sf_created_date, ap_last_modified_date, ap_last_modified_by_id, ap_active
)
VALUES
    ('a1H8b00000AplA1EAF', 'NVH 2026 Plan', '0018b00002HkL1AAAV', 'Growth Plan 2026', 'Active', DATE '2026-01-01', DATE '2026-12-31', NOW() - INTERVAL '45 days', NOW() - INTERVAL '1 days', '0058b00000K7mBBAQX', 1),
    ('a1H8b00000AplB2EAF', 'SMG 2026 Plan', '0018b00002HkL2AAAV', 'Retention Plan 2026', 'Active', DATE '2026-01-01', DATE '2026-12-31', NOW() - INTERVAL '45 days', NOW() - INTERVAL '1 days', '0058b00000K7mCCAQX', 1)
ON CONFLICT (ap_sf_id) DO NOTHING;

-- 8) frame_agreements
INSERT INTO frame_agreements (
    fa_sf_id, fa_account_id, fa_agreement_type, fa_start_date, fa_end_date, fa_start_year, fa_status,
    fa_is_active, fa_total_sales_ty, fa_total_sales_ly, fa_total_sales_q1, fa_total_sales_q2, fa_total_sales_q3, fa_total_sales_q4,
    fa_rebate_achieved, fa_total_rebate_achieved, fa_last_modified_date, fa_last_modified_by_id, fa_active
)
VALUES
    ('a2F8b00000FrmA1EAF', '0018b00002HkL1AAAV', 'Annual', DATE '2026-01-01', DATE '2026-12-31', 2026, 'Active', TRUE, 240000.00, 210000.00, 55000, 60000, 65000, 60000, 0.0450, 10800.00, NOW() - INTERVAL '1 days', '0058b00000K7mBBAQX', 1),
    ('a2F8b00000FrmB2EAF', '0018b00002HkL2AAAV', 'Annual', DATE '2026-01-01', DATE '2026-12-31', 2026, 'Active', TRUE, 360000.00, 300000.00, 80000, 90000, 95000, 95000, 0.0500, 18000.00, NOW() - INTERVAL '1 days', '0058b00000K7mCCAQX', 1)
ON CONFLICT (fa_sf_id) DO NOTHING;

-- 9) targets
INSERT INTO targets (
    tgt_sf_id, tgt_account_id, tgt_frame_agreement_id, tgt_quarter, tgt_net_turnover_target,
    tgt_rebate_rate, tgt_rebate_if_achieved, tgt_total_rebate, tgt_last_modified_date, tgt_last_modified_by_id, tgt_active
)
VALUES
    ('a3T8b00000TgtA1EAF', '0018b00002HkL1AAAV', 'a2F8b00000FrmA1EAF', 'Q1', 55000.00, 0.0400, 2200.00, 2200.00, NOW() - INTERVAL '1 days', '0058b00000K7mBBAQX', 1),
    ('a3T8b00000TgtB2EAF', '0018b00002HkL1AAAV', 'a2F8b00000FrmA1EAF', 'Q2', 60000.00, 0.0450, 2700.00, 2700.00, NOW() - INTERVAL '1 days', '0058b00000K7mBBAQX', 1),
    ('a3T8b00000TgtC3EAF', '0018b00002HkL2AAAV', 'a2F8b00000FrmB2EAF', 'Q1', 80000.00, 0.0500, 4000.00, 4000.00, NOW() - INTERVAL '1 days', '0058b00000K7mCCAQX', 1)
ON CONFLICT (tgt_sf_id) DO NOTHING;

-- 10) campaigns (parent + child)
INSERT INTO campaigns (
    cmp_sf_id, cmp_name, cmp_record_type_id, cmp_type, cmp_parent_id, cmp_status,
    cmp_start_date, cmp_end_date, cmp_actual_cost, cmp_budgeted_cost, cmp_currency_iso_code,
    cmp_owner_id, cmp_account_id, cmp_initial_quantity, cmp_used_quantity, cmp_available_budget,
    cmp_is_active, cmp_sf_created_date, cmp_last_modified_date, cmp_last_modified_by_id, cmp_active
)
VALUES
    ('7018b00000CmpA1AAH', '2026 Strategic Programs', '0128b000000N4aFAAS', 'Program', NULL, 'In Progress',
     DATE '2026-01-01', DATE '2026-12-31', 120000.00, 150000.00, 'USD',
     '0058b00000K7mBBAQX', '0018b00002HkL1AAAV', 1000.00, 350.00, 30000.00,
     TRUE, NOW() - INTERVAL '40 days', NOW() - INTERVAL '1 days', '0058b00000K7mBBAQX', 1),
    ('7018b00000CmpB2AAH', 'Q1 Awareness Blast', '0128b000000N4aEAAS', 'Email', '7018b00000CmpA1AAH', 'Completed',
     DATE '2026-01-10', DATE '2026-03-15', 18000.00, 20000.00, 'USD',
     '0058b00000K7mBBAQX', '0018b00002HkL1AAAV', 400.00, 400.00, 2000.00,
     TRUE, NOW() - INTERVAL '35 days', NOW() - INTERVAL '1 days', '0058b00000K7mBBAQX', 1)
ON CONFLICT (cmp_sf_id) DO NOTHING;

-- 11) invoices
INSERT INTO invoices (
    inv_sf_id, inv_name, inv_account_id, inv_frame_agreement_id, inv_invoice_date, inv_invoice_year,
    inv_invoice_type, inv_status, inv_net_price, inv_total_vat, inv_total_invoice_value, inv_valid,
    inv_currency_iso_code, inv_sf_created_date, inv_last_modified_date, inv_last_modified_by_id, inv_active
)
VALUES
    ('a4I8b00000InvA1EAF', 'INV-2026-0001', '0018b00002HkL1AAAV', 'a2F8b00000FrmA1EAF', DATE '2026-01-18', '2026', 'Standard', 'Paid',   12500.00, 1000.00, 13500.00, TRUE, 'USD', NOW() - INTERVAL '31 days', NOW() - INTERVAL '1 days', '0058b00000K7mBBAQX', 1),
    ('a4I8b00000InvB2EAF', 'INV-2026-0002', '0018b00002HkL1AAAV', 'a2F8b00000FrmA1EAF', DATE '2026-02-05', '2026', 'Standard', 'Open',    17800.00, 1424.00, 19224.00, TRUE, 'USD', NOW() - INTERVAL '12 days', NOW() - INTERVAL '1 days', '0058b00000K7mBBAQX', 1),
    ('a4I8b00000InvC3EAF', 'INV-2026-0003', '0018b00002HkL2AAAV', 'a2F8b00000FrmB2EAF', DATE '2026-02-10', '2026', 'Standard', 'Overdue', 22300.00, 1784.00, 24084.00, TRUE, 'USD', NOW() - INTERVAL '8 days',  NOW() - INTERVAL '1 days', '0058b00000K7mCCAQX', 1)
ON CONFLICT (inv_sf_id) DO NOTHING;

-- 12) invoice_line_items
INSERT INTO invoice_line_items (
    ili_sf_id, ili_invoice_id, ili_product_id, ili_quantity, ili_unit_price, ili_net_price, ili_vat,
    ili_unique_line_code, ili_status, ili_valid, ili_sf_created_date, ili_last_modified_date, ili_last_modified_by_id, ili_active
)
VALUES
    ('a5L8b00000IliA1EAF', 'a4I8b00000InvA1EAF', '01t8b00001PrdA1AAH', 100.00,  50.00,  5000.00, 400.00, 'INV-2026-0001-L1', 'Active', TRUE, NOW() - INTERVAL '31 days', NOW() - INTERVAL '1 days', '0058b00000K7mBBAQX', 1),
    ('a5L8b00000IliB2EAF', 'a4I8b00000InvA1EAF', '01t8b00001PrdB2AAH', 150.00,  50.00,  7500.00, 600.00, 'INV-2026-0001-L2', 'Active', TRUE, NOW() - INTERVAL '31 days', NOW() - INTERVAL '1 days', '0058b00000K7mBBAQX', 1),
    ('a5L8b00000IliC3EAF', 'a4I8b00000InvB2EAF', '01t8b00001PrdC3AAH', 200.00,  89.00, 17800.00,1424.00, 'INV-2026-0002-L1', 'Active', TRUE, NOW() - INTERVAL '12 days', NOW() - INTERVAL '1 days', '0058b00000K7mBBAQX', 1),
    ('a5L8b00000IliD4EAF', 'a4I8b00000InvC3EAF', '01t8b00001PrdA1AAH', 250.00,  89.20, 22300.00,1784.00, 'INV-2026-0003-L1', 'Active', TRUE, NOW() - INTERVAL '8 days',  NOW() - INTERVAL '1 days', '0058b00000K7mCCAQX', 1)
ON CONFLICT (ili_sf_id) DO NOTHING;

-- 13) tasks (polymorphic what_id)
INSERT INTO tasks (
    tsk_sf_id, tsk_what_id, tsk_what_type, tsk_what_name, tsk_activity_date, tsk_status, tsk_priority, tsk_subject,
    tsk_owner_id, tsk_description, tsk_sf_created_date, tsk_completed_date, tsk_last_modified_date, tsk_last_modified_by_id, tsk_active
)
VALUES
    ('00T8b000000TkA1EAG', '0018b00002HkL1AAAV', 'Account',  'North Valley Health', DATE '2026-02-20', 'Not Started', 'High',   'Quarterly business review prep', '0058b00000K7mBBAQX', 'Prepare Q1 account review deck.', NOW() - INTERVAL '4 days', NULL, NOW() - INTERVAL '1 days', '0058b00000K7mBBAQX', 1),
    ('00T8b000000TkB2EAG', '5008b00000CsA1EAGX', 'Case',     'Case #00010234',      DATE '2026-02-17', 'Completed',   'Medium', 'Follow-up on delayed shipment',  '0058b00000K7mDDAQX', 'Customer informed and ETA shared.', NOW() - INTERVAL '7 days', NOW() - INTERVAL '2 days', NOW() - INTERVAL '1 days', '0058b00000K7mDDAQX', 1),
    ('00T8b000000TkC3EAG', '7018b00000CmpB2AAH', 'Campaign', 'Q1 Awareness Blast',   DATE '2026-02-25', 'In Progress', 'Low',    'Close campaign performance',      '0058b00000K7mBBAQX', 'Finalize response rates and spend.', NOW() - INTERVAL '3 days', NULL, NOW() - INTERVAL '1 days', '0058b00000K7mBBAQX', 1)
ON CONFLICT (tsk_sf_id) DO NOTHING;

-- 14) cases
INSERT INTO cases (
    cs_sf_id, cs_case_number, cs_subject, cs_description, cs_status, cs_account_id, cs_owner_id, cs_priority,
    cs_sf_created_date, cs_last_modified_date, cs_last_modified_by_id, cs_active
)
VALUES
    ('5008b00000CsA1EAGX', '00010234', 'Invoice discrepancy', 'Customer reported mismatch in tax value on INV-2026-0002.', 'Working', '0018b00002HkL1AAAV', '0058b00000K7mDDAQX', 'High', NOW() - INTERVAL '7 days', NOW() - INTERVAL '1 days', '0058b00000K7mDDAQX', 1),
    ('5008b00000CsB2EAGX', '00010235', 'Delivery delay',      'Shipment of Pain Relief Gel delayed by carrier.',            'New',     '0018b00002HkL2AAAV', '0058b00000K7mDDAQX', 'Medium', NOW() - INTERVAL '3 days', NOW() - INTERVAL '1 days', '0058b00000K7mDDAQX', 1)
ON CONFLICT (cs_sf_id) DO NOTHING;

-- 15) case_history
INSERT INTO case_history (
    ch_sf_id, ch_case_id, ch_field, ch_old_value, ch_new_value, ch_created_date, ch_created_by_id, ch_active
)
VALUES
    ('0178b00000ChA1EAGX', '5008b00000CsA1EAGX', 'Status', 'New', 'Working', NOW() - INTERVAL '5 days', '0058b00000K7mDDAQX', 1),
    ('0178b00000ChB2EAGX', '5008b00000CsA1EAGX', 'Priority', 'Medium', 'High', NOW() - INTERVAL '4 days', '0058b00000K7mDDAQX', 1)
ON CONFLICT (ch_sf_id) DO NOTHING;

-- 16) case_comments (mix synced + local Agent360 comment)
INSERT INTO case_comments (
    cc_sf_id, cc_case_id, cc_comment_body, cc_is_published, cc_sf_created_date, cc_sf_created_by_id,
    cc_last_modified_date, cc_last_modified_by_id, cc_agent_modified_by, cc_agent_modified_date,
    cc_agent_created_by, cc_agent_created_date, cc_agent360_source, cc_sync_status, cc_version,
    cc_retry_count, cc_last_sync_error, cc_active
)
VALUES
    ('00a8b00000CcA1EAGX', '5008b00000CsA1EAGX', 'Investigating invoice line-level VAT mapping.', TRUE, NOW() - INTERVAL '4 days', '0058b00000K7mDDAQX',
     NOW() - INTERVAL '3 days', '0058b00000K7mDDAQX', NULL, NULL, NULL, NULL, FALSE, 1, 2, 0, NULL, 1),
    (NULL, '5008b00000CsA1EAGX', 'Agent360 note: customer asked for credit memo draft.', TRUE, NULL, NULL,
     NOW() - INTERVAL '1 days', '0058b00000K7mDDAQX', '0058b00000K7mDDAQX', NOW() - INTERVAL '1 days', '0058b00000K7mDDAQX', NOW() - INTERVAL '1 days', TRUE, 0, 1, 0, NULL, 1),
    (NULL, '5008b00000CsB2EAGX', 'Agent360 note: waiting for logistics confirmation.', TRUE, NULL, NULL,
     NOW() - INTERVAL '1 days', '0058b00000K7mDDAQX', '0058b00000K7mDDAQX', NOW() - INTERVAL '1 days', '0058b00000K7mDDAQX', NOW() - INTERVAL '2 days', TRUE, 0, 1, 1, 'Pending carrier response payload', 1)
ON CONFLICT (cc_sf_id) DO NOTHING;

-- 17) arf_rolling_forecasts (all key workflow statuses)
INSERT INTO arf_rolling_forecasts (
    arf_sf_id, arf_name, arf_account_id, arf_sales_rep_id, arf_product_id, arf_forecast_date, arf_status,
    arf_currency_iso_code, arf_owner_id, arf_draft_quantity, arf_draft_unit_price, arf_draft_value,
    arf_pending_quantity, arf_pending_unit_price, arf_pending_value,
    arf_approved_quantity, arf_approved_unit_price, arf_approved_value,
    arf_rejection_reason, arf_product_formula, arf_account_or_user_formula, arf_product_family, arf_product_brand,
    arf_sf_created_by_id, arf_last_modified_by_id, arf_agent_modified_by, arf_agent_modified_date,
    arf_agent_created_by, arf_agent_created_date, arf_agent360_source, arf_sync_status, arf_version,
    arf_retry_count, arf_last_sync_error, arf_active
)
VALUES
    ('a6R8b00000ArfA1EAF', 'ARF-NVH-ASP-2026-03', '0018b00002HkL1AAAV', '0058b00000K7mBBAQX', '01t8b00001PrdA1AAH', DATE '2026-03-01', 'Draft',
     'USD', '0058b00000K7mBBAQX', 450.00, 52.00, 23400.00, NULL, NULL, NULL, NULL, NULL, NULL,
     NULL, 'Aspirin 500mg', 'North Valley Health / Sarah Lee', 'Pharma', 'Alpha Health',
     '0058b00000K7mBBAQX', '0058b00000K7mBBAQX', '0058b00000K7mBBAQX', NOW() - INTERVAL '1 days',
     '0058b00000K7mBBAQX', NOW() - INTERVAL '6 days', TRUE, 0, 1, 0, NULL, 1),
    ('a6R8b00000ArfB2EAF', 'ARF-SMG-PRG-2026-03', '0018b00002HkL2AAAV', '0058b00000K7mCCAQX', '01t8b00001PrdC3AAH', DATE '2026-03-01', 'Pending_Approval',
     'USD', '0058b00000K7mCCAQX', 380.00, 90.00, 34200.00, 380.00, 90.00, 34200.00, NULL, NULL, NULL,
     NULL, 'Pain Relief Gel', 'Summit Medical Group / John Keller', 'Topical', 'Alpha Health',
     '0058b00000K7mCCAQX', '0058b00000K7mCCAQX', '0058b00000K7mCCAQX', NOW() - INTERVAL '1 days',
     '0058b00000K7mCCAQX', NOW() - INTERVAL '5 days', TRUE, 1, 2, 0, NULL, 1),
    ('a6R8b00000ArfC3EAF', 'ARF-NVH-VD3-2026-02', '0018b00002HkL1AAAV', '0058b00000K7mBBAQX', '01t8b00001PrdB2AAH', DATE '2026-02-01', 'Approved',
     'USD', '0058b00000K7mBBAQX', NULL, NULL, NULL, 500.00, 49.00, 24500.00, 500.00, 48.00, 24000.00,
     NULL, 'Vitamin D3', 'North Valley Health / Sarah Lee', 'Supplements', 'Nova Care',
     '0058b00000K7mBBAQX', '0058b00000K7mAQAQX', '0058b00000K7mAQAQX', NOW() - INTERVAL '10 days',
     '0058b00000K7mBBAQX', NOW() - INTERVAL '20 days', TRUE, 1, 3, 0, NULL, 1),
    ('a6R8b00000ArfD4EAF', 'ARF-SMG-ASP-2026-02', '0018b00002HkL2AAAV', '0058b00000K7mCCAQX', '01t8b00001PrdA1AAH', DATE '2026-02-01', 'Fixes_Needed',
     'USD', '0058b00000K7mCCAQX', 600.00, 54.00, 32400.00, NULL, NULL, NULL, NULL, NULL, NULL,
     'Unit price exceeds contract threshold', 'Aspirin 500mg', 'Summit Medical Group / John Keller', 'Pharma', 'Alpha Health',
     '0058b00000K7mCCAQX', '0058b00000K7mAQAQX', '0058b00000K7mAQAQX', NOW() - INTERVAL '2 days',
     '0058b00000K7mCCAQX', NOW() - INTERVAL '15 days', TRUE, 0, 2, 1, 'Validation warning not yet synced', 1)
ON CONFLICT (arf_sf_id) DO NOTHING;

-- 18) ai_chat_threads
INSERT INTO ai_chat_threads (
    act_user_sf_id, act_account_sf_id, act_title, act_message_count, act_last_message_at,
    act_sf_synced, act_sf_synced_at
)
VALUES
    ('0058b00000K7mBBAQX', '0018b00002HkL1AAAV', 'Q1 performance deep dive', 2, NOW() - INTERVAL '1 hours', TRUE, NOW() - INTERVAL '50 minutes'),
    ('0058b00000K7mDDAQX', '0018b00002HkL2AAAV', 'Open support issues summary', 1, NOW() - INTERVAL '2 hours', FALSE, NULL)
ON CONFLICT (act_user_sf_id, act_account_sf_id) DO NOTHING;

-- 19) ai_chat_messages
INSERT INTO ai_chat_messages (
    acm_thread_id, acm_role, acm_content, acm_generated_sql, acm_sql_result_summary,
    acm_model_used, acm_tokens_in, acm_tokens_out, acm_latency_ms, acm_error, acm_sf_synced, acm_created_at
)
VALUES
    (
        (SELECT act_id FROM ai_chat_threads WHERE act_user_sf_id = '0058b00000K7mBBAQX' AND act_account_sf_id = '0018b00002HkL1AAAV'),
        'user',
        'Show total invoice value for this account in 2026.',
        NULL, NULL,
        'gpt-4.1-mini', 120, 0, 0, NULL, TRUE, NOW() - INTERVAL '70 minutes'
    ),
    (
        (SELECT act_id FROM ai_chat_threads WHERE act_user_sf_id = '0058b00000K7mBBAQX' AND act_account_sf_id = '0018b00002HkL1AAAV'),
        'assistant',
        'Total invoice value is 32,724 USD for 2026.',
        'SELECT SUM(inv_total_invoice_value) FROM invoices WHERE inv_account_id = ''0018b00002HkL1AAAV'' AND inv_invoice_year = ''2026'';',
        '2 invoices included.',
        'gpt-4.1-mini', 140, 65, 810, NULL, TRUE, NOW() - INTERVAL '68 minutes'
    ),
    (
        (SELECT act_id FROM ai_chat_threads WHERE act_user_sf_id = '0058b00000K7mDDAQX' AND act_account_sf_id = '0018b00002HkL2AAAV'),
        'user',
        'List open cases and priorities.',
        NULL, NULL,
        'gpt-4.1-mini', 85, 0, 0, NULL, FALSE, NOW() - INTERVAL '2 hours'
    );

-- 20) ai_business_rules
INSERT INTO ai_business_rules (
    abr_rule_key, abr_category, abr_rule_text, abr_is_active, abr_sort_order, abr_updated_by
)
VALUES
    ('LIMIT_200_ROWS',      'sql_safety', 'Never return more than 200 rows unless user explicitly asks.', TRUE, 10, '0058b00000K7mAQAQX'),
    ('BLOCK_DML',           'sql_safety', 'Reject UPDATE/DELETE/INSERT/ALTER/DROP from AI query flow.', TRUE, 20, '0058b00000K7mAQAQX'),
    ('DEFAULT_DATE_WINDOW', 'analytics',  'Use last 90 days when user asks for recent trends without dates.', TRUE, 30, '0058b00000K7mAQAQX')
ON CONFLICT (abr_rule_key) DO NOTHING;

-- 21) ai_query_examples
INSERT INTO ai_query_examples (
    aqe_question, aqe_sql, aqe_explanation, aqe_category, aqe_is_active
)
VALUES
    (
        'What are overdue invoices by account?',
        'SELECT acc.acc_name, inv.inv_name, inv.inv_total_invoice_value FROM invoices inv JOIN accounts acc ON acc.acc_sf_id = inv.inv_account_id WHERE inv.inv_status = ''Overdue'';',
        'Joins accounts and invoices to surface overdue balances.',
        'finance',
        TRUE
    ),
    (
        'Show case volume by status.',
        'SELECT cs_status, COUNT(*) AS total FROM cases GROUP BY cs_status ORDER BY total DESC;',
        'Simple support operations summary.',
        'support',
        TRUE
    );

-- 22) ai_schema_config
INSERT INTO ai_schema_config (
    asc_config_key, asc_config_value, asc_version
)
VALUES
    ('visible_tables', 'accounts,products,invoices,invoice_line_items,cases,tasks,arf_rolling_forecasts', 1),
    ('sql_timeout_sec', '10', 1)
ON CONFLICT (asc_config_key) DO NOTHING;

-- 23) user_login_log
INSERT INTO user_login_log (
    ull_user_sf_id, ull_login_at, ull_ip_address, ull_user_agent, ull_session_duration_sec, ull_logout_at
)
VALUES
    ('0058b00000K7mBBAQX', NOW() - INTERVAL '6 hours', '203.0.113.10', 'Mozilla/5.0 (Macintosh; Intel Mac OS X)', 5400, NOW() - INTERVAL '4.5 hours'),
    ('0058b00000K7mDDAQX', NOW() - INTERVAL '3 hours', '203.0.113.22', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', 3600, NOW() - INTERVAL '2 hours');

-- 24) sync_log
INSERT INTO sync_log (
    sl_run_id, sl_job_name, sl_direction, sl_object_name, sl_sf_object_api, sl_started_at,
    sl_completed_at, sl_status, sl_records_queried, sl_records_inserted, sl_records_updated,
    sl_records_deleted, sl_records_skipped, sl_records_failed, sl_hwm_before, sl_hwm_after,
    sl_error_message, sl_error_details
)
VALUES
    (
        '5b10637f-3c9d-4a67-9a1f-2af0a3f4c111',
        'hourly_pull_accounts',
        'sf_to_db',
        'accounts',
        'Account',
        NOW() - INTERVAL '2 hours',
        NOW() - INTERVAL '1 hour 58 minutes',
        'success',
        3, 0, 3, 0, 0, 0,
        NOW() - INTERVAL '3 hours',
        NOW() - INTERVAL '2 hours',
        NULL,
        NULL
    ),
    (
        '7c8d22be-2d6e-4f4f-9d2a-5d9333aeb222',
        'push_case_comments',
        'db_to_sf',
        'case_comments',
        'CaseComment',
        NOW() - INTERVAL '50 minutes',
        NOW() - INTERVAL '49 minutes',
        'partial',
        2, 1, 0, 0, 0, 1,
        NOW() - INTERVAL '2 hours',
        NOW() - INTERVAL '50 minutes',
        '1 comment failed validation',
        '{"failed_cc_id":[3],"reason":"Missing required SF field"}'::jsonb
    );

-- 25) sync_watermarks (idempotent; DDL already inserts these)
INSERT INTO sync_watermarks (sw_object_name, sw_sf_object_api, sw_sync_order, sw_sync_frequency, sw_sync_enabled)
VALUES
    ('user_roles',           'UserRole',                1,  'hourly', TRUE),
    ('users',                'User',                    2,  'hourly', TRUE),
    ('record_types',         'RecordType',              3,  'daily',  TRUE),
    ('product_brands',       'Product_Brand__c',        4,  'daily',  TRUE),
    ('accounts',             'Account',                 5,  'hourly', TRUE),
    ('products',             'Product2',                6,  'daily',  TRUE),
    ('account_plans',        'Account_Plan__c',         7,  'daily',  TRUE),
    ('frame_agreements',     'Frame_Agreement__c',      8,  'daily',  TRUE),
    ('targets',              'Target__c',               9,  'daily',  TRUE),
    ('campaigns',            'Campaign',                10, 'daily',  TRUE),
    ('invoices',             'Invoice__c',              11, 'hourly', TRUE),
    ('invoice_line_items',   'Invoice_Line_Item__c',    12, 'hourly', TRUE),
    ('tasks',                'Task',                    13, 'hourly', TRUE),
    ('cases',                'Case',                    14, 'hourly', TRUE),
    ('case_history',         'CaseHistory',             15, 'hourly', TRUE),
    ('case_comments',        'CaseComment',             16, 'hourly', TRUE),
    ('arf_rolling_forecasts','ARF_Rolling_Forecast__c', 17, 'hourly', TRUE)
ON CONFLICT (sw_object_name) DO NOTHING;

-- 26) sync_conflicts
INSERT INTO sync_conflicts (
    sc_object_name, sc_record_sf_id, sc_record_local_id, sc_conflict_type,
    sc_local_value, sc_sf_value, sc_resolution, sc_resolved_at, sc_resolved_by
)
VALUES
    (
        'arf_rolling_forecasts',
        'a6R8b00000ArfD4EAF',
        4,
        'version_mismatch',
        '{"status":"Draft","draft_unit_price":54.00}'::jsonb,
        '{"status":"Fixes_Needed","draft_unit_price":54.00}'::jsonb,
        NULL,
        NULL,
        NULL
    ),
    (
        'case_comments',
        '00a8b00000CcA1EAGX',
        1,
        'local_pending',
        '{"comment":"Investigating invoice line-level VAT mapping."}'::jsonb,
        '{"comment":"Investigating invoice line-level VAT mapping."}'::jsonb,
        'local_wins',
        NOW() - INTERVAL '2 days',
        '0058b00000K7mAQAQX'
    );

COMMIT;
