-- Legal Desk Seed Data for Development
-- Depends on: create_legaldesk_tables.sql (LD-001 schema must exist)
--
-- Inserts realistic data across all core Legal Desk tables:
--   3 clients, 5 specialists, 12 expertise entries, 9 jurisdiction entries,
--   2 cases, 2 case-specialist assignments, 6 deliverables, 5 messages,
--   2 pricing history records.
--
-- Idempotent: Uses ON CONFLICT DO NOTHING so the script is safely re-runnable.
-- Atomic: Wrapped in a single transaction.

BEGIN;

-- ============================================================================
-- ld_clients (3 records)
-- ============================================================================
INSERT INTO ld_clients (id, name, client_type, contact_email, contact_phone, country, industry, notes, is_active)
VALUES
    (1, 'TechNova Solutions S.A.S.', 'company', 'legal@technova.co', '+57 601 555 1200', 'Colombia', 'technology', 'Large tech company, frequent corporate restructuring needs', TRUE),
    (2, 'Grupo Financiero Atlas', 'company', 'juridico@grupoatlas.mx', '+52 55 5555 3400', 'Mexico', 'finance', 'Mid-size financial group with IP portfolio', TRUE),
    (3, 'María Elena Rodríguez', 'individual', 'me.rodriguez@email.com', '+57 310 555 7890', 'Colombia', NULL, 'Individual client, labor dispute referral', TRUE)
ON CONFLICT (id) DO NOTHING;

-- Reset sequence to avoid ID conflicts on future inserts
SELECT setval('ld_clients_id_seq', (SELECT COALESCE(MAX(id), 0) FROM ld_clients));

-- ============================================================================
-- ld_specialists (5 records)
-- ============================================================================
INSERT INTO ld_specialists (id, full_name, email, phone, years_experience, hourly_rate, currency, max_concurrent_cases, current_workload, overall_score, is_active)
VALUES
    (1, 'Carlos Andrés Mejía', 'carlos.mejia@legaldesk.co', '+57 310 555 0101', 15, 250.00, 'EUR', 5, 1, 8.50, TRUE),
    (2, 'Laura Patricia Vega', 'laura.vega@vegaip.mx', '+52 55 5555 0202', 20, 350.00, 'EUR', 3, 1, 9.20, TRUE),
    (3, 'Andrés Felipe Castro', 'andres.castro@legaldesk.co', '+57 300 555 0303', 8, 180.00, 'EUR', 6, 0, 7.40, TRUE),
    (4, 'Diana Marcela Ríos', 'diana.rios@riostax.co', '+57 315 555 0404', 12, 200.00, 'EUR', 4, 0, 8.10, TRUE),
    (5, 'Pablo Ignacio Torres', 'pablo.torres@legaldesk.es', '+34 612 555 0505', 3, 120.00, 'EUR', 8, 0, 6.00, TRUE)
ON CONFLICT (id) DO NOTHING;

SELECT setval('ld_specialists_id_seq', (SELECT COALESCE(MAX(id), 0) FROM ld_specialists));

-- ============================================================================
-- ld_specialist_expertise (12 records)
-- ============================================================================
INSERT INTO ld_specialist_expertise (specialist_id, legal_domain, proficiency_level, years_in_domain)
VALUES
    -- Specialist 1: Carlos (Corporate)
    (1, 'corporate', 'expert', 15),
    (1, 'mergers_acquisitions', 'senior', 10),
    -- Specialist 2: Laura (IP)
    (2, 'ip', 'expert', 20),
    (2, 'trademark', 'senior', 15),
    (2, 'patent', 'intermediate', 8),
    -- Specialist 3: Andrés (Labor)
    (3, 'labor', 'senior', 8),
    (3, 'employment_contracts', 'intermediate', 5),
    -- Specialist 4: Diana (Tax)
    (4, 'tax', 'expert', 12),
    (4, 'corporate_tax', 'senior', 10),
    (4, 'international_tax', 'intermediate', 4),
    -- Specialist 5: Pablo (Litigation)
    (5, 'litigation', 'intermediate', 3),
    (5, 'civil_litigation', 'junior', 2)
ON CONFLICT (specialist_id, legal_domain) DO NOTHING;

-- ============================================================================
-- ld_specialist_jurisdictions (9 records)
-- ============================================================================
INSERT INTO ld_specialist_jurisdictions (specialist_id, country, region, is_primary)
VALUES
    -- Specialist 1: Carlos
    (1, 'Colombia', NULL, TRUE),
    (1, 'USA', NULL, FALSE),
    -- Specialist 2: Laura
    (2, 'Mexico', NULL, TRUE),
    (2, 'Spain', NULL, FALSE),
    -- Specialist 3: Andrés
    (3, 'Colombia', NULL, TRUE),
    -- Specialist 4: Diana
    (4, 'Colombia', NULL, TRUE),
    (4, 'Mexico', NULL, FALSE),
    -- Specialist 5: Pablo
    (5, 'Spain', NULL, TRUE),
    (5, 'USA', NULL, FALSE)
ON CONFLICT (specialist_id, country, region) DO NOTHING;

-- ============================================================================
-- ld_cases (2 records)
-- ============================================================================
INSERT INTO ld_cases (id, case_number, title, description, client_id, legal_domain, complexity, priority, status, budget, estimated_cost, deadline)
VALUES
    (1, 'LD-202603-0001', 'Corporate Restructuring Advisory', 'TechNova requires corporate restructuring advisory for subsidiary consolidation across LATAM operations.', 1, 'corporate', 'medium', 'medium', 'new', 15000.00, 12000.00, '2026-06-30'),
    (2, 'LD-202603-0002', 'IP Portfolio Protection Strategy', 'Grupo Financiero Atlas needs comprehensive IP portfolio assessment and trademark registration for fintech products across Mexico and Spain.', 2, 'ip', 'high', 'high', 'in_progress', 30000.00, 25000.00, '2026-05-15')
ON CONFLICT (id) DO NOTHING;

SELECT setval('ld_cases_id_seq', (SELECT COALESCE(MAX(id), 0) FROM ld_cases));

-- ============================================================================
-- ld_case_specialists (2 records)
-- ============================================================================
INSERT INTO ld_case_specialists (id, case_id, specialist_id, role, status, proposed_fee, agreed_fee, fee_currency, assigned_at, responded_at)
VALUES
    (1, 1, 1, 'lead', 'proposed', 5000.00, NULL, 'EUR', '2026-03-01 10:00:00+00', NULL),
    (2, 2, 2, 'lead', 'active', 8000.00, 7500.00, 'EUR', '2026-02-20 14:00:00+00', '2026-02-22 09:30:00+00')
ON CONFLICT (id) DO NOTHING;

SELECT setval('ld_case_specialists_id_seq', (SELECT COALESCE(MAX(id), 0) FROM ld_case_specialists));

-- ============================================================================
-- ld_case_deliverables (6 records, 3 per case)
-- ============================================================================
INSERT INTO ld_case_deliverables (id, case_id, specialist_id, title, description, status, due_date, completed_at)
VALUES
    -- Case 1 deliverables
    (1, 1, 1, 'Legal Due Diligence Report', 'Comprehensive due diligence review of subsidiary legal standing across LATAM jurisdictions.', 'pending', '2026-04-15', NULL),
    (2, 1, 1, 'Corporate Structure Analysis', 'Analysis of current corporate structure with recommendations for consolidation.', 'pending', '2026-05-01', NULL),
    (3, 1, 1, 'Regulatory Compliance Memo', 'Memorandum on regulatory compliance requirements per jurisdiction.', 'pending', '2026-05-30', NULL),
    -- Case 2 deliverables
    (4, 2, 2, 'IP Portfolio Assessment', 'Full assessment of existing intellectual property assets and registration status.', 'completed', '2026-03-01', '2026-02-28 16:00:00+00'),
    (5, 2, 2, 'Trademark Registration Filing', 'Prepare and file trademark applications for fintech product names in Mexico and Spain.', 'in_progress', '2026-04-01', NULL),
    (6, 2, 2, 'Patent Landscape Analysis', 'Analysis of patent landscape in fintech domain to identify risks and opportunities.', 'pending', '2026-04-30', NULL)
ON CONFLICT (id) DO NOTHING;

SELECT setval('ld_case_deliverables_id_seq', (SELECT COALESCE(MAX(id), 0) FROM ld_case_deliverables));

-- ============================================================================
-- ld_case_messages (5 records)
-- ============================================================================
INSERT INTO ld_case_messages (id, case_id, sender_type, sender_name, message, is_internal, created_at)
VALUES
    -- Case 1 messages
    (1, 1, 'client', 'TechNova Solutions S.A.S.', 'We need to consolidate three subsidiaries in Colombia, Peru, and Chile. Please advise on the best legal structure.', FALSE, '2026-03-01 11:00:00+00'),
    (2, 1, 'specialist', 'Carlos Andrés Mejía', 'Thank you for the details. I will start with a jurisdictional review and provide a preliminary assessment within two weeks.', FALSE, '2026-03-01 15:30:00+00'),
    -- Case 2 messages
    (3, 2, 'client', 'Grupo Financiero Atlas', 'We have four fintech product names that need trademark protection in Mexico and Spain. Attached is our brand guidelines document.', FALSE, '2026-02-20 15:00:00+00'),
    (4, 2, 'specialist', 'Laura Patricia Vega', 'I have completed the IP portfolio assessment. The trademark filings for Mexico are in progress. Spain filings will begin next week.', FALSE, '2026-03-01 10:00:00+00'),
    (5, 2, 'specialist', 'Laura Patricia Vega', 'Internal note: Client has prior art concerns on product name "AtlasPay" — recommend clearance search before filing.', TRUE, '2026-03-02 09:00:00+00')
ON CONFLICT (id) DO NOTHING;

SELECT setval('ld_case_messages_id_seq', (SELECT COALESCE(MAX(id), 0) FROM ld_case_messages));

-- ============================================================================
-- ld_pricing_history (2 records)
-- ============================================================================
INSERT INTO ld_pricing_history (id, case_id, action, previous_amount, new_amount, currency, changed_by, notes, created_at)
VALUES
    (1, 1, 'initial_quote', NULL, 15000.00, 'EUR', 'Carlos Andrés Mejía', 'Initial budget estimate based on scope of corporate restructuring across 3 jurisdictions.', '2026-03-01 10:30:00+00'),
    (2, 2, 'negotiation', 8000.00, 7500.00, 'EUR', 'Laura Patricia Vega', 'Fee reduced from 8000 to 7500 EUR after scope clarification on trademark filings.', '2026-02-22 09:30:00+00')
ON CONFLICT (id) DO NOTHING;

SELECT setval('ld_pricing_history_id_seq', (SELECT COALESCE(MAX(id), 0) FROM ld_pricing_history));

COMMIT;
