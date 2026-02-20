-- ================================================================
-- Agent360 API Readiness Checks (SQL)
-- Run AFTER Agent360_MOCK_DATA.sql
-- ================================================================

-- 1) Accounts list (for /accounts)
SELECT acc_sf_id, acc_name, acc_credit_limit, acc_invoice_open_amount, acc_order_open_amount
FROM accounts
ORDER BY acc_name;

-- 2) Account dashboard summary (for /accounts/{id}/summary)
SELECT
    acc.acc_sf_id,
    acc.acc_name,
    COUNT(DISTINCT inv.inv_sf_id) AS invoice_count,
    COALESCE(SUM(inv.inv_total_invoice_value), 0) AS total_invoice_value,
    COUNT(DISTINCT cs.cs_sf_id) AS case_count
FROM accounts acc
LEFT JOIN invoices inv ON inv.inv_account_id = acc.acc_sf_id
LEFT JOIN cases cs ON cs.cs_account_id = acc.acc_sf_id
WHERE acc.acc_sf_id = '0018b00002HkL1AAAV'
GROUP BY acc.acc_sf_id, acc.acc_name;

-- 3) Invoice list with line item totals (for /invoices + /invoices/{id}/items)
SELECT
    inv.inv_sf_id,
    inv.inv_name,
    inv.inv_status,
    inv.inv_total_invoice_value,
    COUNT(ili.ili_sf_id) AS line_count,
    COALESCE(SUM(ili.ili_net_price), 0) AS line_net_total
FROM invoices inv
LEFT JOIN invoice_line_items ili ON ili.ili_invoice_id = inv.inv_sf_id
GROUP BY inv.inv_sf_id, inv.inv_name, inv.inv_status, inv.inv_total_invoice_value
ORDER BY inv.inv_invoice_date DESC;

-- 4) Open/overdue finance queue (for /finance/open-items)
SELECT inv_sf_id, inv_name, inv_account_id, inv_status, inv_total_invoice_value
FROM invoices
WHERE inv_status IN ('Open', 'Overdue')
ORDER BY inv_invoice_date DESC;

-- 5) Cases list + latest comment indicator (for /cases)
SELECT
    cs.cs_sf_id,
    cs.cs_case_number,
    cs.cs_subject,
    cs.cs_status,
    cs.cs_priority,
    MAX(cc.cc_updated_at) AS latest_comment_at
FROM cases cs
LEFT JOIN case_comments cc ON cc.cc_case_id = cs.cs_sf_id
GROUP BY cs.cs_sf_id, cs.cs_case_number, cs.cs_subject, cs.cs_status, cs.cs_priority
ORDER BY cs.cs_last_modified_date DESC;

-- 6) Pending SF sync queues (for /sync/queues)
SELECT 'case_comments' AS object_name, COUNT(*) AS pending_count
FROM case_comments
WHERE cc_sync_status = 0
UNION ALL
SELECT 'arf_rolling_forecasts' AS object_name, COUNT(*) AS pending_count
FROM arf_rolling_forecasts
WHERE arf_sync_status = 0;

-- 7) Forecast workflow split (for /forecasts/status-breakdown)
SELECT arf_status, COUNT(*) AS total
FROM arf_rolling_forecasts
GROUP BY arf_status
ORDER BY total DESC;

-- 8) AI chat thread/message integrity (for /ai/threads and /ai/threads/{id}/messages)
SELECT
    t.act_id,
    t.act_user_sf_id,
    t.act_account_sf_id,
    t.act_message_count,
    COUNT(m.acm_id) AS actual_messages
FROM ai_chat_threads t
LEFT JOIN ai_chat_messages m ON m.acm_thread_id = t.act_id
GROUP BY t.act_id, t.act_user_sf_id, t.act_account_sf_id, t.act_message_count
ORDER BY t.act_id;

-- 9) Sync health (for /sync/runs and /sync/conflicts)
SELECT sl_job_name, sl_status, sl_records_failed, sl_started_at, sl_completed_at
FROM sync_log
ORDER BY sl_started_at DESC;

SELECT sc_object_name, sc_conflict_type, sc_resolution, sc_created_at
FROM sync_conflicts
ORDER BY sc_created_at DESC;
