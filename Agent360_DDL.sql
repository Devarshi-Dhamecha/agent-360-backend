-- ════════════════════════════════════════════════════════════════
-- Agent360 — Complete Database DDL
-- PostgreSQL 17.6 | Database: agent360
-- Date: February 2026
-- Tables: 26 (17 SF-synced + 9 Application/System)
-- Naming: snake_case, table abbreviation prefix on all columns
-- ════════════════════════════════════════════════════════════════

-- Run as: agent360admin (RDS master user)
-- Order: Parents before children (FK dependency order)

BEGIN;

-- ════════════════════════════════════════════════════════════════
-- AI READ-ONLY ROLE (for Text-to-SQL queries)
-- ════════════════════════════════════════════════════════════════

DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'agent360_ai_readonly') THEN
        CREATE ROLE agent360_ai_readonly WITH LOGIN PASSWORD 'CHANGE_ME_IN_SECRETS_MANAGER';
    END IF;
END
$$;

ALTER ROLE agent360_ai_readonly SET statement_timeout = '10s';

-- ════════════════════════════════════════════════════════════════
-- 1. user_roles (SF: UserRole) — READ
-- ════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS user_roles (
    ur_sf_id                VARCHAR(18)     NOT NULL,
    ur_name                 VARCHAR(80)     NOT NULL,
    ur_last_modified_date   TIMESTAMP       NOT NULL,
    ur_system_modstamp      TIMESTAMP       NOT NULL,
    ur_active               SMALLINT        NOT NULL DEFAULT 1,
    ur_created_at           TIMESTAMP       NOT NULL DEFAULT NOW(),
    ur_updated_at           TIMESTAMP       NOT NULL DEFAULT NOW(),

    CONSTRAINT pk_user_roles PRIMARY KEY (ur_sf_id)
);

CREATE INDEX idx_user_roles_active ON user_roles (ur_active) WHERE ur_active = 1;

-- ════════════════════════════════════════════════════════════════
-- 2. users (SF: User) — READ
-- ════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS users (
    usr_sf_id               VARCHAR(18)     NOT NULL,
    usr_username            VARCHAR(80)     NOT NULL,
    usr_email               VARCHAR(255)    NOT NULL,
    usr_first_name          VARCHAR(255),
    usr_last_name           VARCHAR(255)    NOT NULL,
    usr_name                VARCHAR(255)    NOT NULL,
    usr_is_active           BOOLEAN         NOT NULL,
    usr_profile_id          VARCHAR(18),
    usr_user_role_id        VARCHAR(18),
    usr_federation_id       VARCHAR(255),
    usr_time_zone           VARCHAR(100)    NOT NULL,
    usr_language             VARCHAR(100)    NOT NULL,
    usr_sf_created_date     TIMESTAMP       NOT NULL,
    usr_last_modified_date  TIMESTAMP       NOT NULL,
    usr_last_modified_by_id VARCHAR(18)     NOT NULL,
    usr_active              SMALLINT        NOT NULL DEFAULT 1,
    usr_created_at          TIMESTAMP       NOT NULL DEFAULT NOW(),
    usr_updated_at          TIMESTAMP       NOT NULL DEFAULT NOW(),

    CONSTRAINT pk_users PRIMARY KEY (usr_sf_id),
    CONSTRAINT fk_users_role FOREIGN KEY (usr_user_role_id)
        REFERENCES user_roles (ur_sf_id) ON DELETE SET NULL
);

CREATE INDEX idx_users_email ON users (usr_email);
CREATE INDEX idx_users_active ON users (usr_active) WHERE usr_active = 1;
CREATE INDEX idx_users_federation ON users (usr_federation_id) WHERE usr_federation_id IS NOT NULL;

-- ════════════════════════════════════════════════════════════════
-- 3. record_types (SF: RecordType) — READ
-- ════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS record_types (
    rt_sf_id                VARCHAR(18)     NOT NULL,
    rt_name                 VARCHAR(80)     NOT NULL,
    rt_developer_name       VARCHAR(80)     NOT NULL,
    rt_sobject_type         VARCHAR(40)     NOT NULL,
    rt_is_active            BOOLEAN         NOT NULL,
    rt_sf_created_date      TIMESTAMP       NOT NULL,
    rt_last_modified_date   TIMESTAMP       NOT NULL,
    rt_last_modified_by_id  VARCHAR(18),
    rt_active               SMALLINT        NOT NULL DEFAULT 1,
    rt_created_at           TIMESTAMP       NOT NULL DEFAULT NOW(),
    rt_updated_at           TIMESTAMP       NOT NULL DEFAULT NOW(),

    CONSTRAINT pk_record_types PRIMARY KEY (rt_sf_id),
    CONSTRAINT fk_record_types_modified_by FOREIGN KEY (rt_last_modified_by_id)
        REFERENCES users (usr_sf_id) ON DELETE SET NULL
);

CREATE INDEX idx_record_types_sobject ON record_types (rt_sobject_type);

-- ════════════════════════════════════════════════════════════════
-- 4. product_brands (SF: Product_Brand__c) — READ
-- ════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS product_brands (
    pb_sf_id                VARCHAR(18)     NOT NULL,
    pb_name                 VARCHAR(255)    NOT NULL,
    pb_brand_code           VARCHAR(50),
    pb_description          TEXT,
    pb_is_active            BOOLEAN,
    pb_sf_created_date      TIMESTAMP       NOT NULL,
    pb_last_modified_date   TIMESTAMP       NOT NULL,
    pb_active               SMALLINT        NOT NULL DEFAULT 1,
    pb_created_at           TIMESTAMP       NOT NULL DEFAULT NOW(),
    pb_updated_at           TIMESTAMP       NOT NULL DEFAULT NOW(),

    CONSTRAINT pk_product_brands PRIMARY KEY (pb_sf_id)
);

-- ════════════════════════════════════════════════════════════════
-- 5. accounts (SF: Account) — READ
-- ════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS accounts (
    acc_sf_id               VARCHAR(18)     NOT NULL,
    acc_name                VARCHAR(255)    NOT NULL,
    acc_owner_id            VARCHAR(18)     NOT NULL,
    acc_credit_limit        NUMERIC(18,2),
    acc_invoice_open_amount NUMERIC(18,2),
    acc_order_open_amount   NUMERIC(18,2),
    acc_account_number      VARCHAR(255),
    acc_currency_iso_code   VARCHAR(10),
    acc_last_modified_date  TIMESTAMP       NOT NULL,
    acc_last_modified_by_id VARCHAR(18)     NOT NULL,
    acc_active              SMALLINT        NOT NULL DEFAULT 1,
    acc_created_at          TIMESTAMP       NOT NULL DEFAULT NOW(),
    acc_updated_at          TIMESTAMP       NOT NULL DEFAULT NOW(),

    CONSTRAINT pk_accounts PRIMARY KEY (acc_sf_id),
    CONSTRAINT fk_accounts_owner FOREIGN KEY (acc_owner_id)
        REFERENCES users (usr_sf_id) ON DELETE RESTRICT
);

CREATE INDEX idx_accounts_owner ON accounts (acc_owner_id);
CREATE INDEX idx_accounts_name ON accounts (acc_name);
CREATE INDEX idx_accounts_number ON accounts (acc_account_number) WHERE acc_account_number IS NOT NULL;
CREATE INDEX idx_accounts_active ON accounts (acc_active) WHERE acc_active = 1;

-- ════════════════════════════════════════════════════════════════
-- 6. products (SF: Product2) — READ
-- ════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS products (
    prd_sf_id               VARCHAR(18)     NOT NULL,
    prd_name                VARCHAR(255)    NOT NULL,
    prd_family              VARCHAR(100),
    prd_classification      VARCHAR(100),
    prd_central_product_code VARCHAR(20),
    prd_product_code        VARCHAR(255),
    prd_product_brand_id    VARCHAR(18),
    prd_brand               VARCHAR(100),
    prd_is_active           BOOLEAN,
    prd_sf_created_date     TIMESTAMP       NOT NULL,
    prd_last_modified_date  TIMESTAMP       NOT NULL,
    prd_last_modified_by_id VARCHAR(18)     NOT NULL,
    prd_active              SMALLINT        NOT NULL DEFAULT 1,
    prd_created_at          TIMESTAMP       NOT NULL DEFAULT NOW(),
    prd_updated_at          TIMESTAMP       NOT NULL DEFAULT NOW(),

    CONSTRAINT pk_products PRIMARY KEY (prd_sf_id),
    CONSTRAINT fk_products_brand FOREIGN KEY (prd_product_brand_id)
        REFERENCES product_brands (pb_sf_id) ON DELETE SET NULL
);

CREATE INDEX idx_products_family ON products (prd_family);
CREATE INDEX idx_products_brand ON products (prd_product_brand_id);
CREATE INDEX idx_products_code ON products (prd_product_code) WHERE prd_product_code IS NOT NULL;
CREATE INDEX idx_products_active ON products (prd_active) WHERE prd_active = 1;

-- ════════════════════════════════════════════════════════════════
-- 7. account_plans (SF: Account_Plan__c) — READ
-- ════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS account_plans (
    ap_sf_id                VARCHAR(18)     NOT NULL,
    ap_name                 VARCHAR(80)     NOT NULL,
    ap_account_id           VARCHAR(18)     NOT NULL,
    ap_plan_name            VARCHAR(255),
    ap_status               VARCHAR(100)    NOT NULL,
    ap_start_date           DATE,
    ap_end_date             DATE,
    ap_sf_created_date      TIMESTAMP       NOT NULL,
    ap_last_modified_date   TIMESTAMP       NOT NULL,
    ap_last_modified_by_id  VARCHAR(18)     NOT NULL,
    ap_active               SMALLINT        NOT NULL DEFAULT 1,
    ap_created_at           TIMESTAMP       NOT NULL DEFAULT NOW(),
    ap_updated_at           TIMESTAMP       NOT NULL DEFAULT NOW(),

    CONSTRAINT pk_account_plans PRIMARY KEY (ap_sf_id),
    CONSTRAINT fk_account_plans_account FOREIGN KEY (ap_account_id)
        REFERENCES accounts (acc_sf_id) ON DELETE CASCADE
);

CREATE INDEX idx_account_plans_account ON account_plans (ap_account_id);

-- ════════════════════════════════════════════════════════════════
-- 8. frame_agreements (SF: Frame_Agreement__c) — READ
-- ════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS frame_agreements (
    fa_sf_id                VARCHAR(18)     NOT NULL,
    fa_account_id           VARCHAR(18)     NOT NULL,
    fa_agreement_type       VARCHAR(100)    NOT NULL,
    fa_start_date           DATE            NOT NULL,
    fa_end_date             DATE            NOT NULL,
    fa_start_year           INTEGER,
    fa_status               VARCHAR(100)    NOT NULL,
    fa_is_active            BOOLEAN,
    fa_total_sales_ty       NUMERIC(18,2),
    fa_total_sales_ly       NUMERIC(18,2),
    fa_total_sales_q1       NUMERIC(18,0),
    fa_total_sales_q2       NUMERIC(18,0),
    fa_total_sales_q3       NUMERIC(18,0),
    fa_total_sales_q4       NUMERIC(18,0),
    fa_rebate_achieved      NUMERIC(6,4),
    fa_total_rebate_achieved NUMERIC(18,2),
    fa_last_modified_date   TIMESTAMP       NOT NULL,
    fa_last_modified_by_id  VARCHAR(18)     NOT NULL,
    fa_active               SMALLINT        NOT NULL DEFAULT 1,
    fa_created_at           TIMESTAMP       NOT NULL DEFAULT NOW(),
    fa_updated_at           TIMESTAMP       NOT NULL DEFAULT NOW(),

    CONSTRAINT pk_frame_agreements PRIMARY KEY (fa_sf_id),
    CONSTRAINT fk_frame_agreements_account FOREIGN KEY (fa_account_id)
        REFERENCES accounts (acc_sf_id) ON DELETE CASCADE,
    CONSTRAINT fk_frame_agreements_modified_by FOREIGN KEY (fa_last_modified_by_id)
        REFERENCES users (usr_sf_id) ON DELETE RESTRICT
);

CREATE INDEX idx_frame_agreements_account ON frame_agreements (fa_account_id);
CREATE INDEX idx_frame_agreements_status ON frame_agreements (fa_status);

-- ════════════════════════════════════════════════════════════════
-- 9. targets (SF: Target__c) — READ
-- ════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS targets (
    tgt_sf_id               VARCHAR(18)     NOT NULL,
    tgt_account_id          VARCHAR(18)     NOT NULL,
    tgt_frame_agreement_id  VARCHAR(18)     NOT NULL,
    tgt_quarter             VARCHAR(100)    NOT NULL,
    tgt_net_turnover_target NUMERIC(18,2)   NOT NULL,
    tgt_rebate_rate         NUMERIC(6,4)    NOT NULL,
    tgt_rebate_if_achieved  NUMERIC(18,2)   NOT NULL,
    tgt_total_rebate        NUMERIC(18,2),
    tgt_last_modified_date  TIMESTAMP       NOT NULL,
    tgt_last_modified_by_id VARCHAR(18)     NOT NULL,
    tgt_active              SMALLINT        NOT NULL DEFAULT 1,
    tgt_created_at          TIMESTAMP       NOT NULL DEFAULT NOW(),
    tgt_updated_at          TIMESTAMP       NOT NULL DEFAULT NOW(),

    CONSTRAINT pk_targets PRIMARY KEY (tgt_sf_id),
    CONSTRAINT fk_targets_account FOREIGN KEY (tgt_account_id)
        REFERENCES accounts (acc_sf_id) ON DELETE CASCADE,
    CONSTRAINT fk_targets_frame_agreement FOREIGN KEY (tgt_frame_agreement_id)
        REFERENCES frame_agreements (fa_sf_id) ON DELETE CASCADE
);

CREATE INDEX idx_targets_account ON targets (tgt_account_id);
CREATE INDEX idx_targets_frame_agreement ON targets (tgt_frame_agreement_id);

-- ════════════════════════════════════════════════════════════════
-- 10. campaigns (SF: Campaign) — READ (self-referencing)
-- ════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS campaigns (
    cmp_sf_id               VARCHAR(18)     NOT NULL,
    cmp_name                VARCHAR(80)     NOT NULL,
    cmp_record_type_id      VARCHAR(18),
    cmp_type                VARCHAR(100),
    cmp_parent_id           VARCHAR(18),
    cmp_status              VARCHAR(100)    NOT NULL,
    cmp_start_date          DATE,
    cmp_end_date            DATE,
    cmp_actual_cost         NUMERIC(18,2),
    cmp_budgeted_cost       NUMERIC(18,2),
    cmp_currency_iso_code   VARCHAR(10),
    cmp_owner_id            VARCHAR(18)     NOT NULL,
    cmp_account_id          VARCHAR(18),
    cmp_initial_quantity    NUMERIC(18,2),
    cmp_used_quantity       NUMERIC(18,2),
    cmp_available_budget    NUMERIC(18,2),
    cmp_is_active           BOOLEAN,
    cmp_sf_created_date     TIMESTAMP       NOT NULL,
    cmp_last_modified_date  TIMESTAMP       NOT NULL,
    cmp_last_modified_by_id VARCHAR(18)     NOT NULL,
    cmp_active              SMALLINT        NOT NULL DEFAULT 1,
    cmp_created_at          TIMESTAMP       NOT NULL DEFAULT NOW(),
    cmp_updated_at          TIMESTAMP       NOT NULL DEFAULT NOW(),

    CONSTRAINT pk_campaigns PRIMARY KEY (cmp_sf_id),
    CONSTRAINT fk_campaigns_record_type FOREIGN KEY (cmp_record_type_id)
        REFERENCES record_types (rt_sf_id) ON DELETE SET NULL,
    CONSTRAINT fk_campaigns_parent FOREIGN KEY (cmp_parent_id)
        REFERENCES campaigns (cmp_sf_id) ON DELETE SET NULL,
    CONSTRAINT fk_campaigns_owner FOREIGN KEY (cmp_owner_id)
        REFERENCES users (usr_sf_id) ON DELETE RESTRICT,
    CONSTRAINT fk_campaigns_account FOREIGN KEY (cmp_account_id)
        REFERENCES accounts (acc_sf_id) ON DELETE SET NULL
);

CREATE INDEX idx_campaigns_owner ON campaigns (cmp_owner_id);
CREATE INDEX idx_campaigns_account ON campaigns (cmp_account_id);
CREATE INDEX idx_campaigns_parent ON campaigns (cmp_parent_id) WHERE cmp_parent_id IS NOT NULL;
CREATE INDEX idx_campaigns_status ON campaigns (cmp_status);

-- ════════════════════════════════════════════════════════════════
-- 11. invoices (SF: Invoice__c) — READ
-- ════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS invoices (
    inv_sf_id               VARCHAR(18)     NOT NULL,
    inv_name                VARCHAR(255)    NOT NULL,
    inv_account_id          VARCHAR(18)     NOT NULL,
    inv_frame_agreement_id  VARCHAR(18),
    inv_invoice_date        DATE            NOT NULL,
    inv_invoice_year        VARCHAR(10),
    inv_invoice_type        VARCHAR(100)    NOT NULL,
    inv_status              VARCHAR(100)    NOT NULL,
    inv_net_price           NUMERIC(18,2)   NOT NULL,
    inv_total_vat           NUMERIC(18,2),
    inv_total_invoice_value NUMERIC(18,2),
    inv_valid               BOOLEAN,
    inv_currency_iso_code   VARCHAR(10),
    inv_sf_created_date     TIMESTAMP       NOT NULL,
    inv_last_modified_date  TIMESTAMP       NOT NULL,
    inv_last_modified_by_id VARCHAR(18)     NOT NULL,
    inv_active              SMALLINT        NOT NULL DEFAULT 1,
    inv_created_at          TIMESTAMP       NOT NULL DEFAULT NOW(),
    inv_updated_at          TIMESTAMP       NOT NULL DEFAULT NOW(),

    CONSTRAINT pk_invoices PRIMARY KEY (inv_sf_id),
    CONSTRAINT fk_invoices_account FOREIGN KEY (inv_account_id)
        REFERENCES accounts (acc_sf_id) ON DELETE CASCADE,
    CONSTRAINT fk_invoices_frame_agreement FOREIGN KEY (inv_frame_agreement_id)
        REFERENCES frame_agreements (fa_sf_id) ON DELETE SET NULL
);

CREATE INDEX idx_invoices_account ON invoices (inv_account_id);
CREATE INDEX idx_invoices_date ON invoices (inv_invoice_date);
CREATE INDEX idx_invoices_status ON invoices (inv_status);
CREATE INDEX idx_invoices_frame_agreement ON invoices (inv_frame_agreement_id) WHERE inv_frame_agreement_id IS NOT NULL;

-- ════════════════════════════════════════════════════════════════
-- 12. invoice_line_items (SF: Invoice_Line_Item__c) — READ
-- ════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS invoice_line_items (
    ili_sf_id               VARCHAR(18)     NOT NULL,
    ili_invoice_id          VARCHAR(18)     NOT NULL,
    ili_product_id          VARCHAR(18)     NOT NULL,
    ili_quantity            NUMERIC(18,2)   NOT NULL,
    ili_unit_price          NUMERIC(18,2)   NOT NULL,
    ili_net_price           NUMERIC(18,2)   NOT NULL,
    ili_vat                 NUMERIC(18,2),
    ili_unique_line_code    VARCHAR(255)    NOT NULL,
    ili_status              VARCHAR(100)    NOT NULL,
    ili_valid               BOOLEAN         NOT NULL,
    ili_sf_created_date     TIMESTAMP       NOT NULL,
    ili_last_modified_date  TIMESTAMP       NOT NULL,
    ili_last_modified_by_id VARCHAR(18)     NOT NULL,
    ili_active              SMALLINT        NOT NULL DEFAULT 1,
    ili_created_at          TIMESTAMP       NOT NULL DEFAULT NOW(),
    ili_updated_at          TIMESTAMP       NOT NULL DEFAULT NOW(),

    CONSTRAINT pk_invoice_line_items PRIMARY KEY (ili_sf_id),
    CONSTRAINT uq_invoice_line_items_code UNIQUE (ili_unique_line_code),
    CONSTRAINT fk_ili_invoice FOREIGN KEY (ili_invoice_id)
        REFERENCES invoices (inv_sf_id) ON DELETE CASCADE,
    CONSTRAINT fk_ili_product FOREIGN KEY (ili_product_id)
        REFERENCES products (prd_sf_id) ON DELETE RESTRICT
);

CREATE INDEX idx_ili_invoice ON invoice_line_items (ili_invoice_id);
CREATE INDEX idx_ili_product ON invoice_line_items (ili_product_id);

-- ════════════════════════════════════════════════════════════════
-- 13. tasks (SF: Task) — READ (polymorphic WhatId)
-- ════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS tasks (
    tsk_sf_id               VARCHAR(18)     NOT NULL,
    tsk_what_id             VARCHAR(18),
    tsk_what_type           VARCHAR(40),
    tsk_what_name           VARCHAR(255),
    tsk_activity_date       DATE,
    tsk_status              VARCHAR(100)    NOT NULL,
    tsk_priority            VARCHAR(100),
    tsk_subject             VARCHAR(255)    NOT NULL,
    tsk_owner_id            VARCHAR(18)     NOT NULL,
    tsk_description         TEXT,
    tsk_sf_created_date     TIMESTAMP       NOT NULL,
    tsk_completed_date      TIMESTAMP,
    tsk_last_modified_date  TIMESTAMP       NOT NULL,
    tsk_last_modified_by_id VARCHAR(18)     NOT NULL,
    tsk_active              SMALLINT        NOT NULL DEFAULT 1,
    tsk_created_at          TIMESTAMP       NOT NULL DEFAULT NOW(),
    tsk_updated_at          TIMESTAMP       NOT NULL DEFAULT NOW(),

    CONSTRAINT pk_tasks PRIMARY KEY (tsk_sf_id),
    CONSTRAINT fk_tasks_owner FOREIGN KEY (tsk_owner_id)
        REFERENCES users (usr_sf_id) ON DELETE RESTRICT
    -- Note: tsk_what_id is polymorphic (Account/Case/Campaign) — no FK constraint
);

CREATE INDEX idx_tasks_owner ON tasks (tsk_owner_id);
CREATE INDEX idx_tasks_what ON tasks (tsk_what_id, tsk_what_type) WHERE tsk_what_id IS NOT NULL;
CREATE INDEX idx_tasks_status ON tasks (tsk_status);

-- ════════════════════════════════════════════════════════════════
-- 14. cases (SF: Case) — READ
-- Note: "case" is a PG reserved word — table name uses plural "cases"
-- ════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS cases (
    cs_sf_id                VARCHAR(18)     NOT NULL,
    cs_case_number          VARCHAR(80)     NOT NULL,
    cs_subject              VARCHAR(255),
    cs_description          TEXT,
    cs_status               VARCHAR(100),
    cs_account_id           VARCHAR(18),
    cs_owner_id             VARCHAR(18),
    cs_priority             VARCHAR(100),
    cs_sf_created_date      TIMESTAMP       NOT NULL,
    cs_last_modified_date   TIMESTAMP       NOT NULL,
    cs_last_modified_by_id  VARCHAR(18)     NOT NULL,
    cs_active               SMALLINT        NOT NULL DEFAULT 1,
    cs_created_at           TIMESTAMP       NOT NULL DEFAULT NOW(),
    cs_updated_at           TIMESTAMP       NOT NULL DEFAULT NOW(),

    CONSTRAINT pk_cases PRIMARY KEY (cs_sf_id),
    CONSTRAINT fk_cases_account FOREIGN KEY (cs_account_id)
        REFERENCES accounts (acc_sf_id) ON DELETE SET NULL,
    CONSTRAINT fk_cases_owner FOREIGN KEY (cs_owner_id)
        REFERENCES users (usr_sf_id) ON DELETE SET NULL
);

CREATE INDEX idx_cases_account ON cases (cs_account_id);
CREATE INDEX idx_cases_owner ON cases (cs_owner_id);
CREATE INDEX idx_cases_status ON cases (cs_status);

-- ════════════════════════════════════════════════════════════════
-- 15. case_history (SF: CaseHistory) — READ (immutable)
-- ════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS case_history (
    ch_sf_id                VARCHAR(18)     NOT NULL,
    ch_case_id              VARCHAR(18)     NOT NULL,
    ch_field                VARCHAR(255)    NOT NULL,
    ch_old_value            TEXT,
    ch_new_value            TEXT,
    ch_created_date         TIMESTAMP       NOT NULL,
    ch_created_by_id        VARCHAR(18)     NOT NULL,
    ch_active               SMALLINT        NOT NULL DEFAULT 1,
    ch_created_at           TIMESTAMP       NOT NULL DEFAULT NOW(),
    ch_updated_at           TIMESTAMP       NOT NULL DEFAULT NOW(),

    CONSTRAINT pk_case_history PRIMARY KEY (ch_sf_id),
    CONSTRAINT fk_case_history_case FOREIGN KEY (ch_case_id)
        REFERENCES cases (cs_sf_id) ON DELETE CASCADE,
    CONSTRAINT fk_case_history_user FOREIGN KEY (ch_created_by_id)
        REFERENCES users (usr_sf_id) ON DELETE RESTRICT
);

CREATE INDEX idx_case_history_case ON case_history (ch_case_id);

-- ════════════════════════════════════════════════════════════════
-- 16. case_comments (SF: CaseComment) — READ+WRITE (bidirectional)
-- ════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS case_comments (
    cc_id                   SERIAL          NOT NULL,
    cc_sf_id                VARCHAR(18),
    cc_case_id              VARCHAR(18)     NOT NULL,
    cc_comment_body         TEXT,
    cc_is_published         BOOLEAN,
    cc_sf_created_date      TIMESTAMP,
    cc_sf_created_by_id     VARCHAR(18),
    cc_last_modified_date   TIMESTAMP,
    cc_last_modified_by_id  VARCHAR(18),
    -- Agent360 custom fields (synced to SF custom fields)
    cc_agent_modified_by    VARCHAR(18),
    cc_agent_modified_date  TIMESTAMP,
    cc_agent_created_by     VARCHAR(18),
    cc_agent_created_date   TIMESTAMP,
    cc_agent360_source      BOOLEAN,
    -- Sync admin columns
    cc_sync_status          SMALLINT        NOT NULL DEFAULT 1,
    cc_version              INTEGER         NOT NULL DEFAULT 1,
    cc_retry_count          INTEGER         NOT NULL DEFAULT 0,
    cc_last_sync_error      TEXT,
    cc_active               SMALLINT        NOT NULL DEFAULT 1,
    cc_created_at           TIMESTAMP       NOT NULL DEFAULT NOW(),
    cc_updated_at           TIMESTAMP       NOT NULL DEFAULT NOW(),

    CONSTRAINT pk_case_comments PRIMARY KEY (cc_id),
    CONSTRAINT uq_case_comments_sf_id UNIQUE (cc_sf_id),
    CONSTRAINT fk_case_comments_case FOREIGN KEY (cc_case_id)
        REFERENCES cases (cs_sf_id) ON DELETE CASCADE,
    CONSTRAINT fk_case_comments_sf_created_by FOREIGN KEY (cc_sf_created_by_id)
        REFERENCES users (usr_sf_id) ON DELETE SET NULL,
    CONSTRAINT fk_case_comments_agent_modified FOREIGN KEY (cc_agent_modified_by)
        REFERENCES users (usr_sf_id) ON DELETE SET NULL,
    CONSTRAINT fk_case_comments_agent_created FOREIGN KEY (cc_agent_created_by)
        REFERENCES users (usr_sf_id) ON DELETE SET NULL
);

CREATE INDEX idx_case_comments_case ON case_comments (cc_case_id);
CREATE INDEX idx_case_comments_sync ON case_comments (cc_sync_status) WHERE cc_sync_status = 0;
CREATE INDEX idx_case_comments_retry ON case_comments (cc_retry_count) WHERE cc_retry_count >= 5;

-- ════════════════════════════════════════════════════════════════
-- 17. arf_rolling_forecasts (SF: ARF_Rolling_Forecast__c) — READ+WRITE
-- ════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS arf_rolling_forecasts (
    arf_id                      SERIAL          NOT NULL,
    arf_sf_id                   VARCHAR(18),
    arf_name                    VARCHAR(80)     NOT NULL,
    arf_account_id              VARCHAR(18)     NOT NULL,
    arf_sales_rep_id            VARCHAR(18)     NOT NULL,
    arf_product_id              VARCHAR(18)     NOT NULL,
    arf_forecast_date           DATE            NOT NULL,
    arf_status                  VARCHAR(100)    NOT NULL,
    arf_currency_iso_code       VARCHAR(10),
    arf_owner_id                VARCHAR(18)     NOT NULL,
    -- Draft fields (WRITABLE by Agent360)
    arf_draft_quantity          NUMERIC(16,2),
    arf_draft_unit_price        NUMERIC(16,2),
    arf_draft_value             NUMERIC(16,2),
    -- Pending fields (READ-ONLY — system-set on publish)
    arf_pending_quantity        NUMERIC(16,2),
    arf_pending_unit_price      NUMERIC(16,2),
    arf_pending_value           NUMERIC(16,2),
    -- Approved fields (READ-ONLY — system-set on approval)
    arf_approved_quantity       NUMERIC(16,2),
    arf_approved_unit_price     NUMERIC(16,2),
    arf_approved_value          NUMERIC(16,2),
    -- Metadata
    arf_rejection_reason        TEXT,
    arf_product_formula         VARCHAR(255),
    arf_account_or_user_formula VARCHAR(255),
    arf_product_family          VARCHAR(100),
    arf_product_brand           VARCHAR(100),
    arf_sf_created_by_id        VARCHAR(18),
    arf_last_modified_by_id     VARCHAR(18),
    -- Agent360 custom fields (synced to SF custom fields)
    arf_agent_modified_by       VARCHAR(18),
    arf_agent_modified_date     TIMESTAMP,
    arf_agent_created_by        VARCHAR(18),
    arf_agent_created_date      TIMESTAMP,
    arf_agent360_source         BOOLEAN,
    -- Sync admin columns
    arf_sync_status             SMALLINT        NOT NULL DEFAULT 1,
    arf_version                 INTEGER         NOT NULL DEFAULT 1,
    arf_retry_count             INTEGER         NOT NULL DEFAULT 0,
    arf_last_sync_error         TEXT,
    arf_active                  SMALLINT        NOT NULL DEFAULT 1,
    arf_created_at              TIMESTAMP       NOT NULL DEFAULT NOW(),
    arf_updated_at              TIMESTAMP       NOT NULL DEFAULT NOW(),

    CONSTRAINT pk_arf PRIMARY KEY (arf_id),
    CONSTRAINT uq_arf_sf_id UNIQUE (arf_sf_id),
    CONSTRAINT fk_arf_account FOREIGN KEY (arf_account_id)
        REFERENCES accounts (acc_sf_id) ON DELETE CASCADE,
    CONSTRAINT fk_arf_sales_rep FOREIGN KEY (arf_sales_rep_id)
        REFERENCES users (usr_sf_id) ON DELETE RESTRICT,
    CONSTRAINT fk_arf_product FOREIGN KEY (arf_product_id)
        REFERENCES products (prd_sf_id) ON DELETE RESTRICT,
    CONSTRAINT fk_arf_owner FOREIGN KEY (arf_owner_id)
        REFERENCES users (usr_sf_id) ON DELETE RESTRICT,
    CONSTRAINT fk_arf_sf_created_by FOREIGN KEY (arf_sf_created_by_id)
        REFERENCES users (usr_sf_id) ON DELETE SET NULL,
    CONSTRAINT fk_arf_agent_modified FOREIGN KEY (arf_agent_modified_by)
        REFERENCES users (usr_sf_id) ON DELETE SET NULL,
    CONSTRAINT fk_arf_agent_created FOREIGN KEY (arf_agent_created_by)
        REFERENCES users (usr_sf_id) ON DELETE SET NULL,
    CONSTRAINT chk_arf_status CHECK (arf_status IN ('Draft', 'Pending_Approval', 'Approved', 'Fixes_Needed', 'Frozen'))
);

CREATE INDEX idx_arf_account ON arf_rolling_forecasts (arf_account_id);
CREATE INDEX idx_arf_sales_rep ON arf_rolling_forecasts (arf_sales_rep_id);
CREATE INDEX idx_arf_product ON arf_rolling_forecasts (arf_product_id);
CREATE INDEX idx_arf_status ON arf_rolling_forecasts (arf_status);
CREATE INDEX idx_arf_date ON arf_rolling_forecasts (arf_forecast_date);
CREATE INDEX idx_arf_sync ON arf_rolling_forecasts (arf_sync_status) WHERE arf_sync_status = 0;
CREATE INDEX idx_arf_retry ON arf_rolling_forecasts (arf_retry_count) WHERE arf_retry_count >= 5;

-- ════════════════════════════════════════════════════════════════
-- APPLICATION TABLES
-- ════════════════════════════════════════════════════════════════

-- ════════════════════════════════════════════════════════════════
-- 18. ai_chat_threads
-- ════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS ai_chat_threads (
    act_id                  SERIAL          NOT NULL,
    act_user_sf_id          VARCHAR(18)     NOT NULL,
    act_account_sf_id       VARCHAR(18)     NOT NULL,
    act_title               VARCHAR(255),
    act_message_count       INTEGER         NOT NULL DEFAULT 0,
    act_last_message_at     TIMESTAMP,
    act_sf_synced           BOOLEAN         NOT NULL DEFAULT FALSE,
    act_sf_synced_at        TIMESTAMP,
    act_created_at          TIMESTAMP       NOT NULL DEFAULT NOW(),
    act_updated_at          TIMESTAMP       NOT NULL DEFAULT NOW(),

    CONSTRAINT pk_ai_chat_threads PRIMARY KEY (act_id),
    CONSTRAINT uq_ai_chat_thread_pair UNIQUE (act_user_sf_id, act_account_sf_id),
    CONSTRAINT fk_ai_chat_threads_user FOREIGN KEY (act_user_sf_id)
        REFERENCES users (usr_sf_id) ON DELETE CASCADE,
    CONSTRAINT fk_ai_chat_threads_account FOREIGN KEY (act_account_sf_id)
        REFERENCES accounts (acc_sf_id) ON DELETE CASCADE
);

-- ════════════════════════════════════════════════════════════════
-- 19. ai_chat_messages
-- ════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS ai_chat_messages (
    acm_id                  SERIAL          NOT NULL,
    acm_thread_id           INTEGER         NOT NULL,
    acm_role                VARCHAR(20)     NOT NULL,
    acm_content             TEXT            NOT NULL,
    acm_generated_sql       TEXT,
    acm_sql_result_summary  TEXT,
    acm_model_used          VARCHAR(100),
    acm_tokens_in           INTEGER,
    acm_tokens_out          INTEGER,
    acm_latency_ms          INTEGER,
    acm_error               TEXT,
    acm_sf_synced           BOOLEAN         NOT NULL DEFAULT FALSE,
    acm_created_at          TIMESTAMP       NOT NULL DEFAULT NOW(),

    CONSTRAINT pk_ai_chat_messages PRIMARY KEY (acm_id),
    CONSTRAINT fk_ai_chat_messages_thread FOREIGN KEY (acm_thread_id)
        REFERENCES ai_chat_threads (act_id) ON DELETE CASCADE,
    CONSTRAINT chk_acm_role CHECK (acm_role IN ('user', 'assistant', 'system'))
);

CREATE INDEX idx_acm_thread ON ai_chat_messages (acm_thread_id);
CREATE INDEX idx_acm_created ON ai_chat_messages (acm_created_at);
CREATE INDEX idx_acm_sf_sync ON ai_chat_messages (acm_sf_synced) WHERE acm_sf_synced = FALSE;
CREATE INDEX idx_acm_cleanup ON ai_chat_messages (acm_created_at, acm_sf_synced)
    WHERE acm_sf_synced = TRUE;

-- ════════════════════════════════════════════════════════════════
-- 20. ai_business_rules
-- ════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS ai_business_rules (
    abr_id                  SERIAL          NOT NULL,
    abr_rule_key            VARCHAR(100)    NOT NULL,
    abr_category            VARCHAR(50)     NOT NULL,
    abr_rule_text           TEXT            NOT NULL,
    abr_is_active           BOOLEAN         NOT NULL DEFAULT TRUE,
    abr_sort_order          INTEGER         NOT NULL DEFAULT 0,
    abr_created_at          TIMESTAMP       NOT NULL DEFAULT NOW(),
    abr_updated_at          TIMESTAMP       NOT NULL DEFAULT NOW(),
    abr_updated_by          VARCHAR(18),

    CONSTRAINT pk_ai_business_rules PRIMARY KEY (abr_id),
    CONSTRAINT uq_abr_rule_key UNIQUE (abr_rule_key),
    CONSTRAINT fk_abr_updated_by FOREIGN KEY (abr_updated_by)
        REFERENCES users (usr_sf_id) ON DELETE SET NULL
);

-- ════════════════════════════════════════════════════════════════
-- 21. ai_query_examples
-- ════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS ai_query_examples (
    aqe_id                  SERIAL          NOT NULL,
    aqe_question            TEXT            NOT NULL,
    aqe_sql                 TEXT            NOT NULL,
    aqe_explanation         TEXT,
    aqe_category            VARCHAR(50),
    aqe_is_active           BOOLEAN         NOT NULL DEFAULT TRUE,
    aqe_created_at          TIMESTAMP       NOT NULL DEFAULT NOW(),
    aqe_updated_at          TIMESTAMP       NOT NULL DEFAULT NOW(),

    CONSTRAINT pk_ai_query_examples PRIMARY KEY (aqe_id)
);

-- ════════════════════════════════════════════════════════════════
-- 22. ai_schema_config
-- ════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS ai_schema_config (
    asc_id                  SERIAL          NOT NULL,
    asc_config_key          VARCHAR(100)    NOT NULL,
    asc_config_value        TEXT            NOT NULL,
    asc_version             INTEGER         NOT NULL DEFAULT 1,
    asc_generated_at        TIMESTAMP       NOT NULL DEFAULT NOW(),
    asc_updated_at          TIMESTAMP       NOT NULL DEFAULT NOW(),

    CONSTRAINT pk_ai_schema_config PRIMARY KEY (asc_id),
    CONSTRAINT uq_asc_config_key UNIQUE (asc_config_key)
);

-- ════════════════════════════════════════════════════════════════
-- 23. user_login_log
-- ════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS user_login_log (
    ull_id                  SERIAL          NOT NULL,
    ull_user_sf_id          VARCHAR(18)     NOT NULL,
    ull_login_at            TIMESTAMP       NOT NULL DEFAULT NOW(),
    ull_ip_address          VARCHAR(45),
    ull_user_agent          VARCHAR(500),
    ull_session_duration_sec INTEGER,
    ull_logout_at           TIMESTAMP,

    CONSTRAINT pk_user_login_log PRIMARY KEY (ull_id),
    CONSTRAINT fk_ull_user FOREIGN KEY (ull_user_sf_id)
        REFERENCES users (usr_sf_id) ON DELETE CASCADE
);

CREATE INDEX idx_ull_user ON user_login_log (ull_user_sf_id);
CREATE INDEX idx_ull_login_at ON user_login_log (ull_login_at);

-- ════════════════════════════════════════════════════════════════
-- SYSTEM TABLES
-- ════════════════════════════════════════════════════════════════

-- ════════════════════════════════════════════════════════════════
-- 24. sync_log
-- ════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS sync_log (
    sl_id                   SERIAL          NOT NULL,
    sl_run_id               UUID            NOT NULL DEFAULT gen_random_uuid(),
    sl_job_name             VARCHAR(50)     NOT NULL,
    sl_direction            VARCHAR(20)     NOT NULL,
    sl_object_name          VARCHAR(50)     NOT NULL,
    sl_sf_object_api        VARCHAR(50),
    sl_started_at           TIMESTAMP       NOT NULL DEFAULT NOW(),
    sl_completed_at         TIMESTAMP,
    sl_status               VARCHAR(20)     NOT NULL DEFAULT 'running',
    sl_records_queried      INTEGER         DEFAULT 0,
    sl_records_inserted     INTEGER         DEFAULT 0,
    sl_records_updated      INTEGER         DEFAULT 0,
    sl_records_deleted      INTEGER         DEFAULT 0,
    sl_records_skipped      INTEGER         DEFAULT 0,
    sl_records_failed       INTEGER         DEFAULT 0,
    sl_hwm_before           TIMESTAMP,
    sl_hwm_after            TIMESTAMP,
    sl_error_message        TEXT,
    sl_error_details        JSONB,

    CONSTRAINT pk_sync_log PRIMARY KEY (sl_id),
    CONSTRAINT chk_sl_status CHECK (sl_status IN ('running', 'success', 'partial', 'failed', 'skipped'))
);

CREATE INDEX idx_sl_run_id ON sync_log (sl_run_id);
CREATE INDEX idx_sl_job ON sync_log (sl_job_name, sl_started_at);
CREATE INDEX idx_sl_status ON sync_log (sl_status) WHERE sl_status IN ('failed', 'partial');

-- ════════════════════════════════════════════════════════════════
-- 25. sync_watermarks
-- ════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS sync_watermarks (
    sw_id                   SERIAL          NOT NULL,
    sw_object_name          VARCHAR(50)     NOT NULL,
    sw_sf_object_api        VARCHAR(50)     NOT NULL,
    sw_last_sync_ts         TIMESTAMP,
    sw_last_delete_check    TIMESTAMP,
    sw_sync_frequency       VARCHAR(20)     NOT NULL DEFAULT 'hourly',
    sw_sync_enabled         BOOLEAN         NOT NULL DEFAULT TRUE,
    sw_sync_order           INTEGER         NOT NULL DEFAULT 0,
    sw_updated_at           TIMESTAMP       NOT NULL DEFAULT NOW(),

    CONSTRAINT pk_sync_watermarks PRIMARY KEY (sw_id),
    CONSTRAINT uq_sw_object_name UNIQUE (sw_object_name),
    CONSTRAINT chk_sw_frequency CHECK (sw_sync_frequency IN ('hourly', 'daily', 'weekly'))
);

-- Seed watermarks for all 17 SF objects (sync order = parent-first)
INSERT INTO sync_watermarks (sw_object_name, sw_sf_object_api, sw_sync_order) VALUES
    ('user_roles',           'UserRole',                1),
    ('users',                'User',                    2),
    ('record_types',         'RecordType',              3),
    ('product_brands',       'Product_Brand__c',        4),
    ('accounts',             'Account',                 5),
    ('products',             'Product2',                6),
    ('account_plans',        'Account_Plan__c',         7),
    ('frame_agreements',     'Frame_Agreement__c',      8),
    ('targets',              'Target__c',               9),
    ('campaigns',            'Campaign',                10),
    ('invoices',             'Invoice__c',              11),
    ('invoice_line_items',   'Invoice_Line_Item__c',    12),
    ('tasks',                'Task',                    13),
    ('cases',                'Case',                    14),
    ('case_history',         'CaseHistory',             15),
    ('case_comments',        'CaseComment',             16),
    ('arf_rolling_forecasts','ARF_Rolling_Forecast__c', 17)
ON CONFLICT (sw_object_name) DO NOTHING;

-- ════════════════════════════════════════════════════════════════
-- 26. sync_conflicts
-- ════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS sync_conflicts (
    sc_id                   SERIAL          NOT NULL,
    sc_object_name          VARCHAR(50)     NOT NULL,
    sc_record_sf_id         VARCHAR(18)     NOT NULL,
    sc_record_local_id      INTEGER,
    sc_conflict_type        VARCHAR(30)     NOT NULL,
    sc_local_value          JSONB,
    sc_sf_value             JSONB,
    sc_resolution           VARCHAR(20),
    sc_resolved_at          TIMESTAMP,
    sc_resolved_by          VARCHAR(18),
    sc_created_at           TIMESTAMP       NOT NULL DEFAULT NOW(),

    CONSTRAINT pk_sync_conflicts PRIMARY KEY (sc_id),
    CONSTRAINT fk_sc_resolved_by FOREIGN KEY (sc_resolved_by)
        REFERENCES users (usr_sf_id) ON DELETE SET NULL,
    CONSTRAINT chk_sc_conflict_type CHECK (sc_conflict_type IN ('local_pending', 'sf_deleted', 'version_mismatch')),
    CONSTRAINT chk_sc_resolution CHECK (sc_resolution IN ('local_wins', 'sf_wins', 'manual') OR sc_resolution IS NULL)
);

CREATE INDEX idx_sc_object ON sync_conflicts (sc_object_name);
CREATE INDEX idx_sc_unresolved ON sync_conflicts (sc_resolution) WHERE sc_resolution IS NULL;

-- ════════════════════════════════════════════════════════════════
-- GRANT READ-ONLY ACCESS TO AI ROLE
-- ════════════════════════════════════════════════════════════════

GRANT USAGE ON SCHEMA public TO agent360_ai_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO agent360_ai_readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO agent360_ai_readonly;

-- ════════════════════════════════════════════════════════════════
-- TRIGGER: auto-update xx_updated_at on all SF-synced tables
-- ════════════════════════════════════════════════════════════════

CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW := jsonb_populate_record(NEW, jsonb_build_object(TG_ARGV[0], NOW()));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to all tables with an updated_at column
DO $$
DECLARE
    tbl RECORD;
    col_name TEXT;
BEGIN
    FOR tbl IN
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
    LOOP
        -- Find the updated_at column (prefixed)
        SELECT column_name INTO col_name
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = tbl.table_name
          AND column_name LIKE '%_updated_at';

        IF col_name IS NOT NULL THEN
            EXECUTE format(
                'CREATE OR REPLACE TRIGGER trg_%s_updated_at
                 BEFORE UPDATE ON %I
                 FOR EACH ROW
                 EXECUTE FUNCTION update_timestamp(%L)',
                tbl.table_name, tbl.table_name, col_name
            );
        END IF;
    END LOOP;
END
$$;

COMMIT;

-- ════════════════════════════════════════════════════════════════
-- SUMMARY
-- ════════════════════════════════════════════════════════════════
-- Tables created: 26
--   SF Read-only:    15 (user_roles → case_history)
--   SF Bidirectional: 2 (case_comments, arf_rolling_forecasts)
--   Application:      6 (ai_chat_*, user_login_log)
--   System:           3 (sync_log, sync_watermarks, sync_conflicts)
-- Roles created: 1 (agent360_ai_readonly)
-- Watermarks seeded: 17 (one per SF object)
-- Triggers: auto-update *_updated_at on all tables
-- ════════════════════════════════════════════════════════════════
