-- Legal Desk Migration: Drop old tables and recreate with correct schema
-- The old tables were created from an earlier schema version with different column names.
-- This script drops all Legal Desk tables (CASCADE) and recreates them from the current schema.
-- Safe to run: Legal Desk is a POC module with no production data.

-- ============================================================================
-- STEP 1: Drop all old Legal Desk tables in correct dependency order
-- ============================================================================
DROP TABLE IF EXISTS ld_specialist_scores CASCADE;
DROP TABLE IF EXISTS ld_pricing_history CASCADE;
DROP TABLE IF EXISTS ld_case_documents CASCADE;
DROP TABLE IF EXISTS ld_case_messages CASCADE;
DROP TABLE IF EXISTS ld_case_deliverables CASCADE;
DROP TABLE IF EXISTS ld_case_specialists CASCADE;
DROP TABLE IF EXISTS ld_cases CASCADE;
DROP TABLE IF EXISTS ld_specialist_jurisdictions CASCADE;
DROP TABLE IF EXISTS ld_specialist_expertise CASCADE;
DROP TABLE IF EXISTS ld_specialists CASCADE;
DROP TABLE IF EXISTS ld_clients CASCADE;

-- ============================================================================
-- STEP 2: Recreate all tables with correct schema
-- (copied from create_legaldesk_tables.sql)
-- ============================================================================

-- Trigger function (idempotent)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- TABLE 1: ld_clients
CREATE TABLE IF NOT EXISTS ld_clients (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    client_type VARCHAR(50) NOT NULL DEFAULT 'company',
    contact_email VARCHAR(255),
    contact_phone VARCHAR(100),
    country VARCHAR(100),
    industry VARCHAR(100),
    notes TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- TABLE 2: ld_specialists
CREATE TABLE IF NOT EXISTS ld_specialists (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(100),
    years_experience INTEGER DEFAULT 0,
    hourly_rate DECIMAL(10, 2),
    currency VARCHAR(10) DEFAULT 'EUR',
    max_concurrent_cases INTEGER DEFAULT 5,
    current_workload INTEGER DEFAULT 0,
    overall_score DECIMAL(3, 2) DEFAULT 0.00,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- TABLE 3: ld_specialist_expertise
CREATE TABLE IF NOT EXISTS ld_specialist_expertise (
    id SERIAL PRIMARY KEY,
    specialist_id INTEGER NOT NULL,
    legal_domain VARCHAR(100) NOT NULL,
    proficiency_level VARCHAR(50) DEFAULT 'intermediate',
    years_in_domain INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_expertise_specialist FOREIGN KEY (specialist_id) REFERENCES ld_specialists(id) ON DELETE CASCADE,
    CONSTRAINT uq_specialist_expertise UNIQUE (specialist_id, legal_domain)
);

-- TABLE 4: ld_specialist_jurisdictions
CREATE TABLE IF NOT EXISTS ld_specialist_jurisdictions (
    id SERIAL PRIMARY KEY,
    specialist_id INTEGER NOT NULL,
    country VARCHAR(100) NOT NULL,
    region VARCHAR(100),
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_jurisdiction_specialist FOREIGN KEY (specialist_id) REFERENCES ld_specialists(id) ON DELETE CASCADE,
    CONSTRAINT uq_specialist_jurisdiction UNIQUE (specialist_id, country, region)
);

-- TABLE 5: ld_cases
CREATE TABLE IF NOT EXISTS ld_cases (
    id SERIAL PRIMARY KEY,
    case_number VARCHAR(20) UNIQUE NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    client_id INTEGER NOT NULL,
    legal_domain VARCHAR(100) NOT NULL,
    complexity VARCHAR(50) DEFAULT 'medium',
    priority VARCHAR(50) DEFAULT 'medium',
    status VARCHAR(50) DEFAULT 'new',
    budget DECIMAL(15, 2),
    estimated_cost DECIMAL(15, 2),
    final_quote DECIMAL(15, 2),
    margin_percentage DECIMAL(5, 2),
    deadline DATE,
    ai_classification JSONB,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_cases_client FOREIGN KEY (client_id) REFERENCES ld_clients(id) ON DELETE CASCADE
);

-- TABLE 6: ld_case_specialists
CREATE TABLE IF NOT EXISTS ld_case_specialists (
    id SERIAL PRIMARY KEY,
    case_id INTEGER NOT NULL,
    specialist_id INTEGER NOT NULL,
    role VARCHAR(50) DEFAULT 'assigned',
    status VARCHAR(50) DEFAULT 'pending',
    proposed_fee DECIMAL(15, 2),
    agreed_fee DECIMAL(15, 2),
    fee_currency VARCHAR(10) DEFAULT 'EUR',
    assigned_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    responded_at TIMESTAMPTZ,
    CONSTRAINT fk_case_specialists_case FOREIGN KEY (case_id) REFERENCES ld_cases(id) ON DELETE CASCADE,
    CONSTRAINT fk_case_specialists_specialist FOREIGN KEY (specialist_id) REFERENCES ld_specialists(id) ON DELETE CASCADE
);

-- TABLE 7: ld_case_deliverables
CREATE TABLE IF NOT EXISTS ld_case_deliverables (
    id SERIAL PRIMARY KEY,
    case_id INTEGER NOT NULL,
    specialist_id INTEGER,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    due_date DATE,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_deliverables_case FOREIGN KEY (case_id) REFERENCES ld_cases(id) ON DELETE CASCADE,
    CONSTRAINT fk_deliverables_specialist FOREIGN KEY (specialist_id) REFERENCES ld_specialists(id) ON DELETE SET NULL
);

-- TABLE 8: ld_case_messages
CREATE TABLE IF NOT EXISTS ld_case_messages (
    id SERIAL PRIMARY KEY,
    case_id INTEGER NOT NULL,
    sender_type VARCHAR(50) NOT NULL,
    sender_name VARCHAR(255),
    message TEXT NOT NULL,
    is_internal BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_messages_case FOREIGN KEY (case_id) REFERENCES ld_cases(id) ON DELETE CASCADE
);

-- TABLE 9: ld_case_documents
CREATE TABLE IF NOT EXISTS ld_case_documents (
    id SERIAL PRIMARY KEY,
    case_id INTEGER NOT NULL,
    file_name VARCHAR(500) NOT NULL,
    file_url VARCHAR(1000) NOT NULL,
    file_type VARCHAR(100),
    file_size_bytes BIGINT,
    uploaded_by VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_documents_case FOREIGN KEY (case_id) REFERENCES ld_cases(id) ON DELETE CASCADE
);

-- TABLE 10: ld_pricing_history
CREATE TABLE IF NOT EXISTS ld_pricing_history (
    id SERIAL PRIMARY KEY,
    case_id INTEGER NOT NULL,
    action VARCHAR(100) NOT NULL,
    previous_amount DECIMAL(15, 2),
    new_amount DECIMAL(15, 2),
    currency VARCHAR(10) DEFAULT 'EUR',
    changed_by VARCHAR(255),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_pricing_case FOREIGN KEY (case_id) REFERENCES ld_cases(id) ON DELETE CASCADE
);

-- TABLE 11: ld_specialist_scores
CREATE TABLE IF NOT EXISTS ld_specialist_scores (
    id SERIAL PRIMARY KEY,
    specialist_id INTEGER NOT NULL,
    case_id INTEGER NOT NULL,
    quality_score DECIMAL(3, 2),
    teamwork_score DECIMAL(3, 2),
    delivery_score DECIMAL(3, 2),
    satisfaction_score DECIMAL(3, 2),
    overall_score DECIMAL(3, 2),
    feedback TEXT,
    scored_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_scores_specialist FOREIGN KEY (specialist_id) REFERENCES ld_specialists(id) ON DELETE CASCADE,
    CONSTRAINT fk_scores_case FOREIGN KEY (case_id) REFERENCES ld_cases(id) ON DELETE CASCADE
);

-- ============================================================================
-- INDEXES
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_ld_cases_status ON ld_cases(status);
CREATE INDEX IF NOT EXISTS idx_ld_cases_legal_domain ON ld_cases(legal_domain);
CREATE INDEX IF NOT EXISTS idx_ld_cases_client ON ld_cases(client_id);
CREATE INDEX IF NOT EXISTS idx_ld_cases_priority ON ld_cases(priority);
CREATE INDEX IF NOT EXISTS idx_ld_case_specialists_case ON ld_case_specialists(case_id);
CREATE INDEX IF NOT EXISTS idx_ld_case_specialists_specialist ON ld_case_specialists(specialist_id);
CREATE INDEX IF NOT EXISTS idx_ld_deliverables_case ON ld_case_deliverables(case_id);
CREATE INDEX IF NOT EXISTS idx_ld_messages_case ON ld_case_messages(case_id);
CREATE INDEX IF NOT EXISTS idx_ld_documents_case ON ld_case_documents(case_id);
CREATE INDEX IF NOT EXISTS idx_ld_pricing_case ON ld_pricing_history(case_id);
CREATE INDEX IF NOT EXISTS idx_ld_scores_specialist ON ld_specialist_scores(specialist_id);
CREATE INDEX IF NOT EXISTS idx_ld_expertise_specialist ON ld_specialist_expertise(specialist_id);
CREATE INDEX IF NOT EXISTS idx_ld_jurisdictions_specialist ON ld_specialist_jurisdictions(specialist_id);

-- ============================================================================
-- TRIGGERS
-- ============================================================================
DROP TRIGGER IF EXISTS update_ld_clients_updated_at ON ld_clients;
CREATE TRIGGER update_ld_clients_updated_at
    BEFORE UPDATE ON ld_clients FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_ld_specialists_updated_at ON ld_specialists;
CREATE TRIGGER update_ld_specialists_updated_at
    BEFORE UPDATE ON ld_specialists FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_ld_cases_updated_at ON ld_cases;
CREATE TRIGGER update_ld_cases_updated_at
    BEFORE UPDATE ON ld_cases FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_ld_deliverables_updated_at ON ld_case_deliverables;
CREATE TRIGGER update_ld_deliverables_updated_at
    BEFORE UPDATE ON ld_case_deliverables FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
