-- ================================================================
-- Agent360 High-Volume Salesforce-like Data Load
-- Run AFTER Agent360_DDL.sql (and optionally after Agent360_MOCK_DATA.sql)
--
-- This script is deterministic and idempotent on PK/SF-ID tables.
-- It generates large volumes for:
-- Task, Campaign, Case, Case Comment, Case History, Forecast,
-- Product, Product Brands, Invoice, Invoice Line Item,
-- Frame Agreement + Target (past 5 years per account).
-- ================================================================

BEGIN;

-- Keep pseudo-random deterministic for repeatable load tests.
SELECT setseed(0.4206);

-- Compatibility guard for schema variants with NOT NULL timestamps and no defaults.
DO $$
DECLARE
    rec RECORD;
BEGIN
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
END
$$;

-- Deterministic Salesforce-like 18-char IDs.
CREATE OR REPLACE FUNCTION gen_sf_id(prefix TEXT, seed TEXT)
RETURNS VARCHAR(18)
LANGUAGE sql
IMMUTABLE
AS $$
SELECT prefix
    || substr(upper(md5(seed)), 1, 12)
    || substr(upper(md5(seed || 'chk')), 1, 3);
$$;

-- Deterministic integer helper.
CREATE OR REPLACE FUNCTION gen_int(seed TEXT, mod_val INT, base_val INT DEFAULT 0)
RETURNS INT
LANGUAGE sql
IMMUTABLE
AS $$
SELECT base_val + (abs(('x' || substr(md5(seed), 1, 8))::bit(32)::int) % mod_val);
$$;

-- ----------------------------------------------------------------
-- Ensure minimum master data exists
-- ----------------------------------------------------------------

INSERT INTO user_roles (ur_sf_id, ur_name, ur_last_modified_date, ur_system_modstamp, ur_active)
VALUES
    ('00E8b0000004Qx1EAE', 'System Administrator', NOW() - INTERVAL '365 days', NOW() - INTERVAL '365 days', 1),
    ('00E8b0000004Qx2EAE', 'Sales Manager',         NOW() - INTERVAL '365 days', NOW() - INTERVAL '365 days', 1),
    ('00E8b0000004Qx3EAE', 'Customer Support',      NOW() - INTERVAL '365 days', NOW() - INTERVAL '365 days', 1)
ON CONFLICT (ur_sf_id) DO NOTHING;

INSERT INTO users (
    usr_sf_id, usr_username, usr_email, usr_first_name, usr_last_name, usr_name, usr_is_active,
    usr_profile_id, usr_user_role_id, usr_federation_id, usr_time_zone, usr_language,
    usr_sf_created_date, usr_last_modified_date, usr_last_modified_by_id, usr_active
)
VALUES
    ('0058b00000K7mAQAQX', 'michael.clark', 'michael.clark@northbridgepharma.com', 'Michael', 'Clark', 'Michael Clark', TRUE, '00e8b000001LxR1AAK', '00E8b0000004Qx1EAE', 'mclark.nbp', 'America/New_York', 'en_US', NOW() - INTERVAL '400 days', NOW() - INTERVAL '2 days', '0058b00000K7mAQAQX', 1),
    ('0058b00000K7mBBAQX', 'sarah.lee',     'sarah.lee@northbridgepharma.com',     'Sarah',   'Lee',   'Sarah Lee',     TRUE, '00e8b000001LxR2AAK', '00E8b0000004Qx2EAE', 'slee.nbp',   'America/Chicago',  'en_US', NOW() - INTERVAL '350 days', NOW() - INTERVAL '2 days', '0058b00000K7mAQAQX', 1),
    ('0058b00000K7mCCAQX', 'john.keller',   'john.keller@northbridgepharma.com',   'John',    'Keller','John Keller',   TRUE, '00e8b000001LxR3AAK', '00E8b0000004Qx2EAE', 'jkeller.nbp','America/Denver',   'en_US', NOW() - INTERVAL '300 days', NOW() - INTERVAL '2 days', '0058b00000K7mAQAQX', 1),
    ('0058b00000K7mDDAQX', 'maria.ross',    'maria.ross@northbridgepharma.com',    'Maria',   'Ross',  'Maria Ross',    TRUE, '00e8b000001LxR4AAK', '00E8b0000004Qx3EAE', 'mross.nbp',  'America/New_York', 'en_US', NOW() - INTERVAL '280 days', NOW() - INTERVAL '2 days', '0058b00000K7mAQAQX', 1)
ON CONFLICT (usr_sf_id) DO NOTHING;

INSERT INTO record_types (
    rt_sf_id, rt_name, rt_developer_name, rt_sobject_type, rt_is_active,
    rt_sf_created_date, rt_last_modified_date, rt_last_modified_by_id, rt_active
)
VALUES
    ('0128b000000N4aEAAS', 'Marketing Campaign', 'Marketing_Campaign', 'Campaign', TRUE, NOW() - INTERVAL '200 days', NOW() - INTERVAL '1 days', '0058b00000K7mAQAQX', 1),
    ('0128b000000N4aFAAS', 'Trade Program',      'Trade_Program',      'Campaign', TRUE, NOW() - INTERVAL '200 days', NOW() - INTERVAL '1 days', '0058b00000K7mAQAQX', 1)
ON CONFLICT (rt_sf_id) DO NOTHING;

-- ----------------------------------------------------------------
-- Product Brands (large)
-- ----------------------------------------------------------------

WITH s AS (
    SELECT g AS n FROM generate_series(1, 24) g
)
INSERT INTO product_brands (
    pb_sf_id, pb_name, pb_brand_code, pb_description, pb_is_active,
    pb_sf_created_date, pb_last_modified_date, pb_active
)
SELECT
    gen_sf_id('a0B', 'bulk-brand-' || n),
    (ARRAY['NorthBridge','Altura','Crestline','Veridian','Pioneer','AstraVale','BlueRidge','SummitOne'])[1 + (n % 8)]
        || ' '
        || (ARRAY['Health','Life','Pharma','Care','Labs','Thera'])[1 + ((n * 3) % 6)],
    'BR' || lpad(n::text, 4, '0'),
    'National catalog brand ' || n,
    TRUE,
    NOW() - ((120 + n) || ' days')::interval,
    NOW() - ((n % 7) || ' days')::interval,
    1
FROM s
ON CONFLICT (pb_sf_id) DO NOTHING;

-- ----------------------------------------------------------------
-- Products (large, 2-4 families in use)
-- ----------------------------------------------------------------

CREATE TEMP TABLE tmp_brand_pool AS
SELECT row_number() OVER (ORDER BY pb_sf_id) AS rn, pb_sf_id, pb_name
FROM product_brands
WHERE pb_active = 1;

CREATE TEMP TABLE tmp_brand_count AS
SELECT COUNT(*)::INT AS total FROM tmp_brand_pool;

WITH s AS (
    SELECT g AS n FROM generate_series(1, 360) g
),
b AS (
    SELECT bp.rn, bp.pb_sf_id, bp.pb_name
    FROM tmp_brand_pool bp
)
INSERT INTO products (
    prd_sf_id, prd_name, prd_family, prd_classification, prd_central_product_code,
    prd_product_code, prd_product_brand_id, prd_brand, prd_is_active,
    prd_sf_created_date, prd_last_modified_date, prd_last_modified_by_id, prd_active
)
SELECT
    gen_sf_id('01t', 'bulk-product-' || s.n),
    (ARRAY['Aspirin','Ibuprofen','Vitamin D3','Zinc Complex','Pain Relief Gel','Omega 3','Hydration Mix','Sleep Support'])[1 + (s.n % 8)]
        || ' '
        || (ARRAY['50mg','100mg','250mg','500mg','1000IU'])[1 + ((s.n * 7) % 5)],
    (ARRAY['Pharma','Supplements','Topical','Devices'])[1 + (s.n % 4)],
    (ARRAY['OTC','Nutritional','Clinical','Retail'])[1 + ((s.n * 5) % 4)],
    'CP-' || lpad((10000 + s.n)::text, 6, '0'),
    'A360-P-' || lpad(s.n::text, 5, '0'),
    b.pb_sf_id,
    b.pb_name,
    TRUE,
    NOW() - ((500 + s.n) || ' days')::interval,
    NOW() - ((s.n % 10) || ' days')::interval,
    (SELECT usr_sf_id FROM users ORDER BY usr_sf_id LIMIT 1),
    1
FROM s
JOIN tmp_brand_count bc ON TRUE
JOIN b ON b.rn = 1 + ((s.n - 1) % bc.total)
ON CONFLICT (prd_sf_id) DO NOTHING;

-- ----------------------------------------------------------------
-- Accounts (large)
-- ----------------------------------------------------------------

CREATE TEMP TABLE tmp_owner_pool AS
SELECT row_number() OVER (ORDER BY usr_sf_id) AS rn, usr_sf_id
FROM users
WHERE usr_active = 1;

CREATE TEMP TABLE tmp_owner_count AS
SELECT COUNT(*)::INT AS total FROM tmp_owner_pool;

WITH s AS (
    SELECT g AS n FROM generate_series(1, 120) g
)
INSERT INTO accounts (
    acc_sf_id, acc_name, acc_owner_id, acc_credit_limit, acc_invoice_open_amount, acc_order_open_amount,
    acc_account_number, acc_currency_iso_code, acc_last_modified_date, acc_last_modified_by_id, acc_active
)
SELECT
    gen_sf_id('001', 'bulk-account-' || s.n),
    (ARRAY['North Valley','Summit Ridge','MetroCare','Pinecrest','Lakeside','Redwood','Harborview','Canyon'])[1 + (s.n % 8)]
        || ' '
        || (ARRAY['Medical Group','Health System','Clinic Network','Specialty Care','Regional Health'])[1 + ((s.n * 11) % 5)],
    op.usr_sf_id,
    (150000 + gen_int('credit-' || s.n, 850000))::numeric(18,2),
    (5000 + gen_int('open-inv-' || s.n, 120000))::numeric(18,2),
    (1000 + gen_int('open-ord-' || s.n, 65000))::numeric(18,2),
    'A360-' || lpad(s.n::text, 5, '0'),
    'USD',
    NOW() - ((s.n % 5) || ' days')::interval,
    op.usr_sf_id,
    1
FROM s
JOIN tmp_owner_count oc ON TRUE
JOIN tmp_owner_pool op
    ON op.rn = 1 + ((s.n - 1) % oc.total)
ON CONFLICT (acc_sf_id) DO NOTHING;

CREATE TEMP TABLE tmp_bulk_accounts AS
SELECT acc_sf_id, acc_owner_id, acc_name
FROM accounts
WHERE acc_account_number LIKE 'A360-%';

-- ----------------------------------------------------------------
-- Frame Agreements (past 5 years for each account) + Targets (4 per FA)
-- ----------------------------------------------------------------

WITH yrs AS (
    SELECT generate_series(
        extract(year FROM CURRENT_DATE)::INT - 5,
        extract(year FROM CURRENT_DATE)::INT - 1
    ) AS y
),
fa_src AS (
    SELECT
        a.acc_sf_id,
        a.acc_owner_id,
        y.y AS start_year,
        gen_sf_id('a2F', a.acc_sf_id || '-fa-' || y.y) AS fa_sf_id
    FROM tmp_bulk_accounts a
    CROSS JOIN yrs y
)
INSERT INTO frame_agreements (
    fa_sf_id, fa_account_id, fa_agreement_type, fa_start_date, fa_end_date, fa_start_year, fa_status,
    fa_is_active, fa_total_sales_ty, fa_total_sales_ly, fa_total_sales_q1, fa_total_sales_q2, fa_total_sales_q3, fa_total_sales_q4,
    fa_rebate_achieved, fa_total_rebate_achieved, fa_last_modified_date, fa_last_modified_by_id, fa_active
)
SELECT
    fs.fa_sf_id,
    fs.acc_sf_id,
    'Annual',
    make_date(fs.start_year, 1, 1),
    make_date(fs.start_year, 12, 31),
    fs.start_year,
    'Closed',
    TRUE,
    (200000 + gen_int(fs.fa_sf_id || '-ty', 450000))::numeric(18,2),
    (180000 + gen_int(fs.fa_sf_id || '-ly', 420000))::numeric(18,2),
    (40000 + gen_int(fs.fa_sf_id || '-q1', 90000))::numeric(18,0),
    (40000 + gen_int(fs.fa_sf_id || '-q2', 90000))::numeric(18,0),
    (40000 + gen_int(fs.fa_sf_id || '-q3', 90000))::numeric(18,0),
    (40000 + gen_int(fs.fa_sf_id || '-q4', 90000))::numeric(18,0),
    (0.02 + (gen_int(fs.fa_sf_id || '-rr', 500) / 10000.0))::numeric(6,4),
    (3000 + gen_int(fs.fa_sf_id || '-tra', 35000))::numeric(18,2),
    NOW() - INTERVAL '1 day',
    fs.acc_owner_id,
    1
FROM fa_src fs
ON CONFLICT (fa_sf_id) DO NOTHING;

WITH fa AS (
    SELECT fa_sf_id, fa_account_id, fa_last_modified_by_id
    FROM frame_agreements
    WHERE fa_account_id IN (SELECT acc_sf_id FROM tmp_bulk_accounts)
),
q AS (
    SELECT generate_series(1, 4) AS qn
)
INSERT INTO targets (
    tgt_sf_id, tgt_account_id, tgt_frame_agreement_id, tgt_quarter, tgt_net_turnover_target,
    tgt_rebate_rate, tgt_rebate_if_achieved, tgt_total_rebate, tgt_last_modified_date, tgt_last_modified_by_id, tgt_active
)
SELECT
    gen_sf_id('a3T', fa.fa_sf_id || '-tgt-' || q.qn),
    fa.fa_account_id,
    fa.fa_sf_id,
    'Q' || q.qn,
    (30000 + gen_int(fa.fa_sf_id || '-q-' || q.qn, 100000))::numeric(18,2),
    (0.02 + (gen_int(fa.fa_sf_id || '-rb-' || q.qn, 500) / 10000.0))::numeric(6,4),
    (1000 + gen_int(fa.fa_sf_id || '-ria-' || q.qn, 15000))::numeric(18,2),
    (1000 + gen_int(fa.fa_sf_id || '-tr-' || q.qn, 15000))::numeric(18,2),
    NOW() - INTERVAL '1 day',
    fa.fa_last_modified_by_id,
    1
FROM fa
CROSS JOIN q
ON CONFLICT (tgt_sf_id) DO NOTHING;

-- ----------------------------------------------------------------
-- Campaigns (parent + 2 children per account)
-- ----------------------------------------------------------------

CREATE TEMP TABLE tmp_campaign_parent AS
SELECT
    gen_sf_id('701', a.acc_sf_id || '-camp-parent') AS parent_id,
    a.acc_sf_id,
    a.acc_owner_id
FROM tmp_bulk_accounts a;

INSERT INTO campaigns (
    cmp_sf_id, cmp_name, cmp_record_type_id, cmp_type, cmp_parent_id, cmp_status,
    cmp_start_date, cmp_end_date, cmp_actual_cost, cmp_budgeted_cost, cmp_currency_iso_code,
    cmp_owner_id, cmp_account_id, cmp_initial_quantity, cmp_used_quantity, cmp_available_budget,
    cmp_is_active, cmp_sf_created_date, cmp_last_modified_date, cmp_last_modified_by_id, cmp_active
)
SELECT
    p.parent_id,
    'FY Program ' || right(p.acc_sf_id, 6),
    '0128b000000N4aFAAS',
    'Program',
    NULL,
    'In Progress',
    date_trunc('year', CURRENT_DATE)::date,
    (date_trunc('year', CURRENT_DATE) + INTERVAL '11 months 30 days')::date,
    (20000 + gen_int(p.parent_id || '-ac', 90000))::numeric(18,2),
    (25000 + gen_int(p.parent_id || '-bc', 120000))::numeric(18,2),
    'USD',
    p.acc_owner_id,
    p.acc_sf_id,
    (100 + gen_int(p.parent_id || '-iq', 900))::numeric(18,2),
    (30 + gen_int(p.parent_id || '-uq', 400))::numeric(18,2),
    (5000 + gen_int(p.parent_id || '-ab', 45000))::numeric(18,2),
    TRUE,
    NOW() - INTERVAL '120 days',
    NOW() - INTERVAL '1 day',
    p.acc_owner_id,
    1
FROM tmp_campaign_parent p
ON CONFLICT (cmp_sf_id) DO NOTHING;

WITH ch AS (
    SELECT
        p.parent_id,
        p.acc_sf_id,
        p.acc_owner_id,
        gs AS idx
    FROM tmp_campaign_parent p
    CROSS JOIN generate_series(1, 2) gs
)
INSERT INTO campaigns (
    cmp_sf_id, cmp_name, cmp_record_type_id, cmp_type, cmp_parent_id, cmp_status,
    cmp_start_date, cmp_end_date, cmp_actual_cost, cmp_budgeted_cost, cmp_currency_iso_code,
    cmp_owner_id, cmp_account_id, cmp_initial_quantity, cmp_used_quantity, cmp_available_budget,
    cmp_is_active, cmp_sf_created_date, cmp_last_modified_date, cmp_last_modified_by_id, cmp_active
)
SELECT
    gen_sf_id('701', ch.parent_id || '-child-' || ch.idx),
    CASE WHEN ch.idx = 1 THEN 'Spring Outreach ' ELSE 'Q3 Conversion ' END || right(ch.acc_sf_id, 5),
    '0128b000000N4aEAAS',
    CASE WHEN ch.idx = 1 THEN 'Email' ELSE 'Digital' END,
    ch.parent_id,
    CASE WHEN ch.idx = 1 THEN 'Completed' ELSE 'Planned' END,
    (CURRENT_DATE - (180 - ch.idx * 20)),
    (CURRENT_DATE - (120 - ch.idx * 25)),
    (5000 + gen_int(ch.parent_id || '-cac-' || ch.idx, 30000))::numeric(18,2),
    (7000 + gen_int(ch.parent_id || '-cbc-' || ch.idx, 35000))::numeric(18,2),
    'USD',
    ch.acc_owner_id,
    ch.acc_sf_id,
    (50 + gen_int(ch.parent_id || '-ciq-' || ch.idx, 400))::numeric(18,2),
    (20 + gen_int(ch.parent_id || '-cuq-' || ch.idx, 220))::numeric(18,2),
    (1500 + gen_int(ch.parent_id || '-cab-' || ch.idx, 9000))::numeric(18,2),
    TRUE,
    NOW() - INTERVAL '90 days',
    NOW() - INTERVAL '1 day',
    ch.acc_owner_id,
    1
FROM ch
ON CONFLICT (cmp_sf_id) DO NOTHING;

-- ----------------------------------------------------------------
-- Cases / Case History / Case Comments (large)
-- ----------------------------------------------------------------

CREATE TEMP TABLE tmp_bulk_cases AS
SELECT
    gen_sf_id('500', a.acc_sf_id || '-case-' || gs) AS cs_sf_id,
    a.acc_sf_id,
    a.acc_owner_id,
    gs AS seq
FROM tmp_bulk_accounts a
CROSS JOIN generate_series(1, 18) gs;

INSERT INTO cases (
    cs_sf_id, cs_case_number, cs_subject, cs_description, cs_status, cs_account_id, cs_owner_id, cs_priority,
    cs_sf_created_date, cs_last_modified_date, cs_last_modified_by_id, cs_active
)
SELECT
    c.cs_sf_id,
    'C-' || lpad((100000 + row_number() OVER (ORDER BY c.cs_sf_id))::text, 8, '0'),
    (ARRAY['Invoice discrepancy','Shipment delay','Credit memo request','Pricing clarification','Contract update'])[1 + (c.seq % 5)],
    'Customer issue logged from account operations queue.',
    (ARRAY['New','Working','Escalated','Closed'])[1 + (c.seq % 4)],
    c.acc_sf_id,
    c.acc_owner_id,
    (ARRAY['Low','Medium','High'])[1 + (c.seq % 3)],
    NOW() - ((10 + c.seq) || ' days')::interval,
    NOW() - ((c.seq % 5) || ' days')::interval,
    c.acc_owner_id,
    1
FROM tmp_bulk_cases c
ON CONFLICT (cs_sf_id) DO NOTHING;

WITH h AS (
    SELECT c.cs_sf_id, c.acc_owner_id, gs AS seq
    FROM tmp_bulk_cases c
    CROSS JOIN generate_series(1, 4) gs
)
INSERT INTO case_history (
    ch_sf_id, ch_case_id, ch_field, ch_old_value, ch_new_value, ch_created_date, ch_created_by_id, ch_active
)
SELECT
    gen_sf_id('017', h.cs_sf_id || '-hist-' || h.seq),
    h.cs_sf_id,
    (ARRAY['Status','Priority','Owner','Subject'])[h.seq],
    (ARRAY['New','Low','Queue','Initial'])[h.seq],
    (ARRAY['Working','Medium','Support Agent','Updated'])[h.seq],
    NOW() - ((8 - h.seq) || ' days')::interval,
    h.acc_owner_id,
    1
FROM h
ON CONFLICT (ch_sf_id) DO NOTHING;

WITH cm AS (
    SELECT c.cs_sf_id, c.acc_owner_id, gs AS seq
    FROM tmp_bulk_cases c
    CROSS JOIN generate_series(1, 6) gs
)
INSERT INTO case_comments (
    cc_sf_id, cc_case_id, cc_comment_body, cc_is_published, cc_sf_created_date, cc_sf_created_by_id,
    cc_last_modified_date, cc_last_modified_by_id, cc_agent_modified_by, cc_agent_modified_date,
    cc_agent_created_by, cc_agent_created_date, cc_agent360_source, cc_sync_status,
    cc_version, cc_retry_count, cc_last_sync_error, cc_active
)
SELECT
    gen_sf_id('00a', cm.cs_sf_id || '-comment-' || cm.seq),
    cm.cs_sf_id,
    CASE
        WHEN cm.seq IN (1,2) THEN 'Customer contacted and issue acknowledged.'
        WHEN cm.seq IN (3,4) THEN 'Investigation update shared with account team.'
        ELSE 'Resolution details documented and synced.'
    END,
    TRUE,
    NOW() - ((7 - cm.seq) || ' days')::interval,
    cm.acc_owner_id,
    NOW() - ((6 - cm.seq) || ' days')::interval,
    cm.acc_owner_id,
    cm.acc_owner_id,
    NOW() - ((6 - cm.seq) || ' days')::interval,
    cm.acc_owner_id,
    NOW() - ((7 - cm.seq) || ' days')::interval,
    TRUE,
    CASE WHEN cm.seq % 5 = 0 THEN 0 ELSE 1 END,
    1 + (cm.seq % 3),
    CASE WHEN cm.seq % 5 = 0 THEN 1 ELSE 0 END,
    CASE WHEN cm.seq % 5 = 0 THEN 'Queued for outbound sync retry' ELSE NULL END,
    1
FROM cm
ON CONFLICT (cc_sf_id) DO NOTHING;

-- ----------------------------------------------------------------
-- Tasks (large)
-- ----------------------------------------------------------------

WITH t AS (
    SELECT a.acc_sf_id, a.acc_owner_id, gs AS seq
    FROM tmp_bulk_accounts a
    CROSS JOIN generate_series(1, 24) gs
)
INSERT INTO tasks (
    tsk_sf_id, tsk_what_id, tsk_what_type, tsk_what_name, tsk_activity_date,
    tsk_status, tsk_priority, tsk_subject, tsk_owner_id, tsk_description,
    tsk_sf_created_date, tsk_completed_date, tsk_last_modified_date, tsk_last_modified_by_id, tsk_active
)
SELECT
    gen_sf_id('00T', t.acc_sf_id || '-task-' || t.seq),
    t.acc_sf_id,
    'Account',
    'Account Task',
    CURRENT_DATE + ((t.seq % 30) - 10),
    (ARRAY['Not Started','In Progress','Completed'])[1 + (t.seq % 3)],
    (ARRAY['Low','Medium','High'])[1 + (t.seq % 3)],
    (ARRAY['Account review','Invoice follow-up','Case update','Forecast validation'])[1 + (t.seq % 4)],
    t.acc_owner_id,
    'Auto-generated operational task for load testing.',
    NOW() - ((20 - (t.seq % 10)) || ' days')::interval,
    CASE WHEN t.seq % 3 = 0 THEN NOW() - ((t.seq % 7) || ' days')::interval ELSE NULL END,
    NOW() - ((t.seq % 4) || ' days')::interval,
    t.acc_owner_id,
    1
FROM t
ON CONFLICT (tsk_sf_id) DO NOTHING;

-- ----------------------------------------------------------------
-- Account-to-Product assignment (5-10 products/account)
-- ----------------------------------------------------------------

CREATE TEMP TABLE tmp_bulk_products AS
SELECT prd_sf_id
FROM products
WHERE prd_product_code LIKE 'A360-P-%';

CREATE TEMP TABLE tmp_account_products AS
WITH m AS (
    SELECT
        a.acc_sf_id,
        p.prd_sf_id
    FROM tmp_bulk_accounts a
    JOIN LATERAL (
        SELECT bp.prd_sf_id
        FROM tmp_bulk_products bp
        ORDER BY md5(a.acc_sf_id || bp.prd_sf_id)
        LIMIT 5 + gen_int('prod-per-account-' || a.acc_sf_id, 6, 0) -- 5..10
    ) p ON TRUE
)
SELECT
    row_number() OVER (ORDER BY acc_sf_id, prd_sf_id) AS map_id,
    acc_sf_id,
    prd_sf_id
FROM m;

CREATE TEMP TABLE tmp_map_volume AS
SELECT
    ap.map_id,
    ap.acc_sf_id,
    ap.prd_sf_id,
    10 + gen_int('inv-per-map-' || ap.map_id, 11, 0) AS inv_cnt,   -- 10..20
    30 + gen_int('ili-per-map-' || ap.map_id, 11, 0) AS line_cnt   -- 30..40
FROM tmp_account_products ap;

-- ----------------------------------------------------------------
-- Invoices (10-20 per account-product map)
-- ----------------------------------------------------------------

CREATE TEMP TABLE tmp_invoices AS
SELECT
    mv.map_id,
    gs AS seq_n,
    gen_sf_id('a4I', 'bulk-inv-' || mv.map_id || '-' || gs) AS inv_sf_id,
    mv.acc_sf_id,
    mv.prd_sf_id,
    ('INV-' || right(mv.acc_sf_id, 6) || '-' || lpad(gs::text, 3, '0'))::VARCHAR(255) AS inv_name,
    (CURRENT_DATE - (gen_int('inv-date-' || mv.map_id || '-' || gs, 720, 0)))::DATE AS inv_date,
    (ARRAY['Open','Paid','Overdue','Cancelled'])[1 + (gen_int('inv-status-' || mv.map_id || '-' || gs, 4, 0))] AS inv_status,
    (1500 + gen_int('inv-net-' || mv.map_id || '-' || gs, 45000, 0))::numeric(18,2) AS net_price
FROM tmp_map_volume mv
JOIN LATERAL generate_series(1, mv.inv_cnt) gs ON TRUE;

INSERT INTO invoices (
    inv_sf_id, inv_name, inv_account_id, inv_frame_agreement_id, inv_invoice_date, inv_invoice_year,
    inv_invoice_type, inv_status, inv_net_price, inv_total_vat, inv_total_invoice_value, inv_valid,
    inv_currency_iso_code, inv_sf_created_date, inv_last_modified_date, inv_last_modified_by_id, inv_active
)
SELECT
    ti.inv_sf_id,
    ti.inv_name,
    ti.acc_sf_id,
    (
        SELECT fa.fa_sf_id
        FROM frame_agreements fa
        WHERE fa.fa_account_id = ti.acc_sf_id
          AND fa.fa_start_year = extract(year FROM ti.inv_date)::INT
        LIMIT 1
    ),
    ti.inv_date,
    extract(year FROM ti.inv_date)::text,
    'Standard',
    ti.inv_status,
    ti.net_price,
    round(ti.net_price * 0.08, 2),
    round(ti.net_price * 1.08, 2),
    TRUE,
    'USD',
    ti.inv_date::timestamp,
    NOW() - INTERVAL '1 day',
    (SELECT acc_owner_id FROM accounts WHERE acc_sf_id = ti.acc_sf_id),
    1
FROM tmp_invoices ti
ON CONFLICT (inv_sf_id) DO NOTHING;

-- ----------------------------------------------------------------
-- Invoice Line Items (30-40 per account-product map)
-- ----------------------------------------------------------------

WITH li AS (
    SELECT
        mv.map_id,
        mv.prd_sf_id,
        mv.inv_cnt,
        gs AS seq_n
    FROM tmp_map_volume mv
    JOIN LATERAL generate_series(1, mv.line_cnt) gs ON TRUE
),
li_pick AS (
    SELECT
        li.map_id,
        li.prd_sf_id,
        li.seq_n,
        (
            SELECT ti.inv_sf_id
            FROM tmp_invoices ti
            WHERE ti.map_id = li.map_id
            ORDER BY ti.seq_n
            OFFSET ((li.seq_n - 1) % li.inv_cnt)
            LIMIT 1
        ) AS inv_sf_id
    FROM li
)
INSERT INTO invoice_line_items (
    ili_sf_id, ili_invoice_id, ili_product_id, ili_quantity, ili_unit_price, ili_net_price, ili_vat,
    ili_unique_line_code, ili_status, ili_valid, ili_sf_created_date, ili_last_modified_date, ili_last_modified_by_id, ili_active
)
SELECT
    gen_sf_id('a5L', 'bulk-ili-' || lp.map_id || '-' || lp.seq_n),
    lp.inv_sf_id,
    lp.prd_sf_id,
    (1 + gen_int('ili-qty-' || lp.map_id || '-' || lp.seq_n, 120, 0))::numeric(18,2),
    (5 + gen_int('ili-price-' || lp.map_id || '-' || lp.seq_n, 250, 0))::numeric(18,2),
    round(
        ((1 + gen_int('ili-qty-' || lp.map_id || '-' || lp.seq_n, 120, 0))::numeric
         * (5 + gen_int('ili-price-' || lp.map_id || '-' || lp.seq_n, 250, 0))::numeric),
        2
    ),
    round(
        (
            ((1 + gen_int('ili-qty-' || lp.map_id || '-' || lp.seq_n, 120, 0))::numeric
             * (5 + gen_int('ili-price-' || lp.map_id || '-' || lp.seq_n, 250, 0))::numeric)
            * 0.08
        ),
        2
    ),
    'ILC-' || substr(upper(md5(lp.map_id::text || '-' || lp.seq_n::text)), 1, 20),
    'Active',
    TRUE,
    NOW() - ((lp.seq_n % 30) || ' days')::interval,
    NOW() - INTERVAL '1 day',
    (SELECT inv_last_modified_by_id FROM invoices WHERE inv_sf_id = lp.inv_sf_id),
    1
FROM li_pick lp
WHERE lp.inv_sf_id IS NOT NULL
ON CONFLICT (ili_sf_id) DO NOTHING;

-- ----------------------------------------------------------------
-- Forecasts (past year + future year, monthly)
-- ----------------------------------------------------------------

WITH f AS (
    SELECT
        mv.map_id,
        mv.acc_sf_id,
        mv.prd_sf_id,
        m AS month_offset,
        (date_trunc('month', CURRENT_DATE) + (m || ' months')::interval)::date AS fc_date
    FROM tmp_map_volume mv
    CROSS JOIN generate_series(-12, 12) m
)
INSERT INTO arf_rolling_forecasts (
    arf_sf_id, arf_name, arf_account_id, arf_sales_rep_id, arf_product_id, arf_forecast_date, arf_status,
    arf_currency_iso_code, arf_owner_id,
    arf_draft_quantity, arf_draft_unit_price, arf_draft_value,
    arf_pending_quantity, arf_pending_unit_price, arf_pending_value,
    arf_approved_quantity, arf_approved_unit_price, arf_approved_value,
    arf_rejection_reason, arf_product_formula, arf_account_or_user_formula, arf_product_family, arf_product_brand,
    arf_sf_created_by_id, arf_last_modified_by_id, arf_agent_modified_by, arf_agent_modified_date,
    arf_agent_created_by, arf_agent_created_date, arf_agent360_source, arf_sync_status, arf_version,
    arf_retry_count, arf_last_sync_error, arf_active
)
SELECT
    gen_sf_id('a6R', 'bulk-arf-' || f.map_id || '-' || f.month_offset),
    'ARF-' || right(f.acc_sf_id, 5) || '-' || to_char(f.fc_date, 'YYYYMM'),
    f.acc_sf_id,
    a.acc_owner_id,
    f.prd_sf_id,
    f.fc_date,
    CASE
        WHEN f.month_offset < -6 THEN 'Approved'
        WHEN f.month_offset BETWEEN -6 AND -1 THEN 'Frozen'
        WHEN f.month_offset BETWEEN 0 AND 2 THEN 'Pending_Approval'
        WHEN f.month_offset BETWEEN 3 AND 8 THEN 'Draft'
        ELSE 'Draft'
    END,
    'USD',
    a.acc_owner_id,
    CASE WHEN f.month_offset >= 0 THEN (50 + gen_int('arf-dq-' || f.map_id || '-' || f.month_offset, 600, 0))::numeric(16,2) ELSE NULL END,
    CASE WHEN f.month_offset >= 0 THEN (10 + gen_int('arf-du-' || f.map_id || '-' || f.month_offset, 220, 0))::numeric(16,2) ELSE NULL END,
    CASE WHEN f.month_offset >= 0 THEN round(((50 + gen_int('arf-dq-' || f.map_id || '-' || f.month_offset, 600, 0))::numeric * (10 + gen_int('arf-du-' || f.map_id || '-' || f.month_offset, 220, 0))::numeric), 2) ELSE NULL END,
    CASE WHEN f.month_offset BETWEEN 0 AND 2 THEN (50 + gen_int('arf-pq-' || f.map_id || '-' || f.month_offset, 600, 0))::numeric(16,2) ELSE NULL END,
    CASE WHEN f.month_offset BETWEEN 0 AND 2 THEN (10 + gen_int('arf-pu-' || f.map_id || '-' || f.month_offset, 220, 0))::numeric(16,2) ELSE NULL END,
    CASE WHEN f.month_offset BETWEEN 0 AND 2 THEN round(((50 + gen_int('arf-pq-' || f.map_id || '-' || f.month_offset, 600, 0))::numeric * (10 + gen_int('arf-pu-' || f.map_id || '-' || f.month_offset, 220, 0))::numeric), 2) ELSE NULL END,
    CASE WHEN f.month_offset < 0 THEN (60 + gen_int('arf-aq-' || f.map_id || '-' || f.month_offset, 550, 0))::numeric(16,2) ELSE NULL END,
    CASE WHEN f.month_offset < 0 THEN (10 + gen_int('arf-au-' || f.map_id || '-' || f.month_offset, 210, 0))::numeric(16,2) ELSE NULL END,
    CASE WHEN f.month_offset < 0 THEN round(((60 + gen_int('arf-aq-' || f.map_id || '-' || f.month_offset, 550, 0))::numeric * (10 + gen_int('arf-au-' || f.map_id || '-' || f.month_offset, 210, 0))::numeric), 2) ELSE NULL END,
    CASE WHEN f.month_offset IN (1,2) AND gen_int('arf-rej-' || f.map_id || '-' || f.month_offset, 8, 0) = 0 THEN 'Price or volume requires revision' ELSE NULL END,
    (SELECT prd_name FROM products WHERE prd_sf_id = f.prd_sf_id),
    a.acc_name || ' / ' || a.acc_owner_id,
    (SELECT prd_family FROM products WHERE prd_sf_id = f.prd_sf_id),
    (SELECT prd_brand FROM products WHERE prd_sf_id = f.prd_sf_id),
    a.acc_owner_id,
    a.acc_owner_id,
    a.acc_owner_id,
    NOW() - INTERVAL '1 day',
    a.acc_owner_id,
    NOW() - INTERVAL '30 days',
    TRUE,
    CASE WHEN f.month_offset >= 0 THEN 0 ELSE 1 END,
    1 + (abs(f.month_offset) % 4),
    CASE WHEN f.month_offset >= 0 AND gen_int('arf-rtry-' || f.map_id || '-' || f.month_offset, 12, 0) = 0 THEN 1 ELSE 0 END,
    CASE WHEN f.month_offset >= 0 AND gen_int('arf-rtry-' || f.map_id || '-' || f.month_offset, 12, 0) = 0 THEN 'Queued for outbound sync' ELSE NULL END,
    1
FROM f
JOIN accounts a ON a.acc_sf_id = f.acc_sf_id
ON CONFLICT (arf_sf_id) DO NOTHING;

-- ----------------------------------------------------------------
-- Account Plans (3-year rolling plans)
-- ----------------------------------------------------------------

WITH p AS (
    SELECT
        a.acc_sf_id,
        a.acc_owner_id,
        y AS plan_year
    FROM tmp_bulk_accounts a
    CROSS JOIN generate_series(
        extract(year FROM CURRENT_DATE)::INT - 1,
        extract(year FROM CURRENT_DATE)::INT + 1
    ) y
)
INSERT INTO account_plans (
    ap_sf_id, ap_name, ap_account_id, ap_plan_name, ap_status, ap_start_date, ap_end_date,
    ap_sf_created_date, ap_last_modified_date, ap_last_modified_by_id, ap_active
)
SELECT
    gen_sf_id('a1H', p.acc_sf_id || '-plan-' || p.plan_year),
    ('Plan ' || p.plan_year || ' ' || right(p.acc_sf_id, 6))::varchar(80),
    p.acc_sf_id,
    'Commercial Plan ' || p.plan_year,
    CASE WHEN p.plan_year < extract(year FROM CURRENT_DATE)::INT THEN 'Completed' ELSE 'Active' END,
    make_date(p.plan_year, 1, 1),
    make_date(p.plan_year, 12, 31),
    NOW() - INTERVAL '90 days',
    NOW() - INTERVAL '1 day',
    p.acc_owner_id,
    1
FROM p
ON CONFLICT (ap_sf_id) DO NOTHING;

-- ----------------------------------------------------------------
-- AI chat threads/messages (large)
-- ----------------------------------------------------------------

CREATE TEMP TABLE tmp_chat_users AS
SELECT usr_sf_id
FROM users
WHERE usr_active = 1
ORDER BY usr_sf_id
LIMIT 3;

WITH t AS (
    SELECT
        u.usr_sf_id,
        a.acc_sf_id,
        a.acc_name
    FROM tmp_chat_users u
    CROSS JOIN (
        SELECT acc_sf_id, acc_name
        FROM tmp_bulk_accounts
        ORDER BY acc_sf_id
        LIMIT 80
    ) a
)
INSERT INTO ai_chat_threads (
    act_user_sf_id, act_account_sf_id, act_title, act_message_count, act_last_message_at,
    act_sf_synced, act_sf_synced_at
)
SELECT
    t.usr_sf_id,
    t.acc_sf_id,
    'Account Review ' || right(t.acc_sf_id, 6),
    8,
    NOW() - (gen_int('chat-last-' || t.usr_sf_id || t.acc_sf_id, 120, 0) || ' minutes')::interval,
    TRUE,
    NOW() - (gen_int('chat-sync-' || t.usr_sf_id || t.acc_sf_id, 180, 0) || ' minutes')::interval
FROM t
ON CONFLICT (act_user_sf_id, act_account_sf_id) DO NOTHING;

WITH msgs AS (
    SELECT
        th.act_id,
        gs AS seq
    FROM ai_chat_threads th
    CROSS JOIN generate_series(1, 8) gs
    WHERE th.act_account_sf_id IN (SELECT acc_sf_id FROM tmp_bulk_accounts)
)
INSERT INTO ai_chat_messages (
    acm_thread_id, acm_role, acm_content, acm_generated_sql, acm_sql_result_summary,
    acm_model_used, acm_tokens_in, acm_tokens_out, acm_latency_ms, acm_error, acm_sf_synced, acm_created_at
)
SELECT
    m.act_id,
    CASE WHEN m.seq % 2 = 1 THEN 'user' ELSE 'assistant' END,
    CASE
        WHEN m.seq % 2 = 1 THEN
            (ARRAY[
                'Show monthly invoice totals.',
                'List open cases for this account.',
                'Compare forecast vs invoiced value.',
                'Show overdue invoice count.'
            ])[1 + (m.seq % 4)]
        ELSE
            (ARRAY[
                'I found monthly totals for the last 12 months.',
                'Here are the open and escalated cases.',
                'Forecast variance is within expected threshold.',
                'Overdue invoices are listed by amount.'
            ])[1 + (m.seq % 4)]
    END,
    CASE WHEN m.seq % 2 = 0 THEN 'SELECT 1;' ELSE NULL END,
    CASE WHEN m.seq % 2 = 0 THEN 'Generated summary for account analytics.' ELSE NULL END,
    'gpt-4.1-mini',
    80 + gen_int('tok-in-' || m.act_id || '-' || m.seq, 120, 0),
    CASE WHEN m.seq % 2 = 0 THEN 40 + gen_int('tok-out-' || m.act_id || '-' || m.seq, 120, 0) ELSE 0 END,
    CASE WHEN m.seq % 2 = 0 THEN 300 + gen_int('lat-' || m.act_id || '-' || m.seq, 1700, 0) ELSE 0 END,
    NULL,
    TRUE,
    NOW() - ((9 - m.seq) || ' hours')::interval
FROM msgs m
WHERE NOT EXISTS (
    SELECT 1
    FROM ai_chat_messages x
    WHERE x.acm_thread_id = m.act_id
      AND x.acm_role = CASE WHEN m.seq % 2 = 1 THEN 'user' ELSE 'assistant' END
      AND x.acm_content = CASE
            WHEN m.seq % 2 = 1 THEN
                (ARRAY[
                    'Show monthly invoice totals.',
                    'List open cases for this account.',
                    'Compare forecast vs invoiced value.',
                    'Show overdue invoice count.'
                ])[1 + (m.seq % 4)]
            ELSE
                (ARRAY[
                    'I found monthly totals for the last 12 months.',
                    'Here are the open and escalated cases.',
                    'Forecast variance is within expected threshold.',
                    'Overdue invoices are listed by amount.'
                ])[1 + (m.seq % 4)]
        END
);

-- ----------------------------------------------------------------
-- AI config / rules / query examples
-- ----------------------------------------------------------------

WITH r AS (
    SELECT gs AS n FROM generate_series(1, 40) gs
)
INSERT INTO ai_business_rules (
    abr_rule_key, abr_category, abr_rule_text, abr_is_active, abr_sort_order, abr_updated_by
)
SELECT
    'A360_RULE_' || lpad(r.n::text, 3, '0'),
    (ARRAY['sql_safety','analytics','governance','filters'])[1 + (r.n % 4)],
    'Generated rule #' || r.n || ' for AI behavior control in load dataset.',
    TRUE,
    r.n,
    (SELECT usr_sf_id FROM users ORDER BY usr_sf_id LIMIT 1)
FROM r
ON CONFLICT (abr_rule_key) DO NOTHING;

WITH q AS (
    SELECT gs AS n FROM generate_series(1, 80) gs
)
INSERT INTO ai_query_examples (
    aqe_question, aqe_sql, aqe_explanation, aqe_category, aqe_is_active
)
SELECT
    'Generated analytics question #' || q.n,
    'SELECT ' || q.n || ' AS metric_value;',
    'Synthetic example used for prompt and SQL behavior testing.',
    (ARRAY['finance','support','forecast','sales'])[1 + (q.n % 4)],
    TRUE
FROM q
WHERE NOT EXISTS (
    SELECT 1 FROM ai_query_examples e WHERE e.aqe_question = 'Generated analytics question #' || q.n
);

INSERT INTO ai_schema_config (asc_config_key, asc_config_value, asc_version)
VALUES
    ('visible_tables', 'accounts,products,cases,campaigns,invoices,invoice_line_items,arf_rolling_forecasts,case_comments,case_history,tasks', 2),
    ('sql_timeout_sec', '10', 2),
    ('max_result_rows', '200', 1),
    ('allow_joins', 'true', 1),
    ('default_time_window_days', '90', 1)
ON CONFLICT (asc_config_key) DO UPDATE
SET
    asc_config_value = EXCLUDED.asc_config_value,
    asc_version = GREATEST(ai_schema_config.asc_version, EXCLUDED.asc_version),
    asc_updated_at = NOW();

-- ----------------------------------------------------------------
-- User login log (large)
-- ----------------------------------------------------------------

WITH l AS (
    SELECT
        u.usr_sf_id,
        gs AS n
    FROM users u
    CROSS JOIN generate_series(1, 90) gs
)
INSERT INTO user_login_log (
    ull_user_sf_id, ull_login_at, ull_ip_address, ull_user_agent, ull_session_duration_sec, ull_logout_at
)
SELECT
    l.usr_sf_id,
    NOW() - ((l.n * 4) || ' hours')::interval,
    ('10.42.' || (l.n % 255) || '.' || (10 + (l.n % 200)))::inet,
    (ARRAY[
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2)',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)'
    ])[1 + (l.n % 3)],
    600 + gen_int('sess-' || l.usr_sf_id || '-' || l.n, 10800, 0),
    NOW() - ((l.n * 4 - 1) || ' hours')::interval
FROM l
WHERE NOT EXISTS (
    SELECT 1
    FROM user_login_log x
    WHERE x.ull_user_sf_id = l.usr_sf_id
      AND x.ull_login_at = NOW() - ((l.n * 4) || ' hours')::interval
);

-- ----------------------------------------------------------------
-- Sync tables (watermarks, logs, conflicts)
-- ----------------------------------------------------------------

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
ON CONFLICT (sw_object_name) DO UPDATE
SET
    sw_sf_object_api = EXCLUDED.sw_sf_object_api,
    sw_sync_order = EXCLUDED.sw_sync_order,
    sw_sync_frequency = EXCLUDED.sw_sync_frequency,
    sw_sync_enabled = EXCLUDED.sw_sync_enabled,
    sw_updated_at = NOW();

WITH s AS (
    SELECT gs AS n FROM generate_series(1, 450) gs
)
INSERT INTO sync_log (
    sl_run_id, sl_job_name, sl_direction, sl_object_name, sl_sf_object_api, sl_started_at,
    sl_completed_at, sl_status, sl_records_queried, sl_records_inserted, sl_records_updated,
    sl_records_deleted, sl_records_skipped, sl_records_failed, sl_hwm_before, sl_hwm_after,
    sl_error_message, sl_error_details
)
SELECT
    (
        substr(md5('run-' || s.n), 1, 8) || '-' ||
        substr(md5('run-' || s.n), 9, 4) || '-' ||
        substr(md5('run-' || s.n), 13, 4) || '-' ||
        substr(md5('run-' || s.n), 17, 4) || '-' ||
        substr(md5('run-' || s.n), 21, 12)
    )::uuid,
    (ARRAY['hourly_pull','hourly_push','daily_snapshot'])[1 + (s.n % 3)] || '_' || (ARRAY['accounts','cases','invoices','forecasts'])[1 + (s.n % 4)],
    CASE WHEN s.n % 2 = 0 THEN 'sf_to_db' ELSE 'db_to_sf' END,
    (ARRAY['accounts','cases','invoices','invoice_line_items','arf_rolling_forecasts','case_comments'])[1 + (s.n % 6)],
    (ARRAY['Account','Case','Invoice__c','Invoice_Line_Item__c','ARF_Rolling_Forecast__c','CaseComment'])[1 + (s.n % 6)],
    NOW() - ((s.n * 20) || ' minutes')::interval,
    NOW() - ((s.n * 20 - 2) || ' minutes')::interval,
    CASE WHEN s.n % 19 = 0 THEN 'failed' WHEN s.n % 11 = 0 THEN 'partial' ELSE 'success' END,
    50 + gen_int('qry-' || s.n, 350, 0),
    10 + gen_int('ins-' || s.n, 80, 0),
    10 + gen_int('upd-' || s.n, 120, 0),
    gen_int('del-' || s.n, 10, 0),
    gen_int('skp-' || s.n, 20, 0),
    CASE WHEN s.n % 19 = 0 THEN 1 + gen_int('fail-' || s.n, 6, 0) WHEN s.n % 11 = 0 THEN 1 ELSE 0 END,
    NOW() - ((s.n * 20 + 60) || ' minutes')::interval,
    NOW() - ((s.n * 20) || ' minutes')::interval,
    CASE WHEN s.n % 19 = 0 THEN 'Outbound payload rejected' WHEN s.n % 11 = 0 THEN 'Partial due to validation skip' ELSE NULL END,
    CASE WHEN s.n % 19 = 0 THEN jsonb_build_object('code', 'SF_VALIDATION_ERROR', 'run_no', s.n) WHEN s.n % 11 = 0 THEN jsonb_build_object('code', 'PARTIAL_SUCCESS', 'run_no', s.n) ELSE NULL END
FROM s
WHERE NOT EXISTS (
    SELECT 1 FROM sync_log x
    WHERE x.sl_run_id = (
        substr(md5('run-' || s.n), 1, 8) || '-' ||
        substr(md5('run-' || s.n), 9, 4) || '-' ||
        substr(md5('run-' || s.n), 13, 4) || '-' ||
        substr(md5('run-' || s.n), 17, 4) || '-' ||
        substr(md5('run-' || s.n), 21, 12)
    )::uuid
);

WITH c AS (
    SELECT gs AS n FROM generate_series(1, 140) gs
)
INSERT INTO sync_conflicts (
    sc_object_name, sc_record_sf_id, sc_record_local_id, sc_conflict_type,
    sc_local_value, sc_sf_value, sc_resolution, sc_resolved_at, sc_resolved_by
)
SELECT
    (ARRAY['case_comments','arf_rolling_forecasts','invoices'])[1 + (c.n % 3)],
    CASE
        WHEN c.n % 3 = 1 THEN gen_sf_id('00a', 'conf-comment-' || c.n)
        WHEN c.n % 3 = 2 THEN gen_sf_id('a6R', 'conf-arf-' || c.n)
        ELSE gen_sf_id('a4I', 'conf-inv-' || c.n)
    END,
    c.n,
    (ARRAY['local_pending','sf_deleted','version_mismatch'])[1 + (c.n % 3)],
    jsonb_build_object('version', 1 + (c.n % 5), 'source', 'local'),
    jsonb_build_object('version', 2 + (c.n % 5), 'source', 'salesforce'),
    CASE WHEN c.n % 4 = 0 THEN 'manual' WHEN c.n % 5 = 0 THEN 'local_wins' ELSE NULL END,
    CASE WHEN c.n % 4 = 0 OR c.n % 5 = 0 THEN NOW() - ((c.n % 20) || ' hours')::interval ELSE NULL END,
    CASE WHEN c.n % 4 = 0 OR c.n % 5 = 0 THEN (SELECT usr_sf_id FROM users ORDER BY usr_sf_id LIMIT 1) ELSE NULL END
FROM c
WHERE NOT EXISTS (
    SELECT 1
    FROM sync_conflicts x
    WHERE x.sc_record_local_id = c.n
      AND x.sc_object_name = (ARRAY['case_comments','arf_rolling_forecasts','invoices'])[1 + (c.n % 3)]
);

COMMIT;
