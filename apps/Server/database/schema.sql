-- Finance Tracker Database Schema
-- PostgreSQL schema for multi-entity income/expense tracking
-- Deployed to Supabase PostgreSQL

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- TRIGGER FUNCTION: Auto-update updated_at timestamp
-- ============================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- TABLE: users
-- Custom authentication with password_hash for JWT auth
-- ============================================================================
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    role VARCHAR(50) DEFAULT 'user',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT users_role_check CHECK (role IN ('admin', 'manager', 'user', 'viewer'))
);

-- Index for login lookups
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_is_active ON users(is_active);

-- Trigger for updated_at
CREATE TRIGGER users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- TABLE: entities
-- Separate financial tracking contexts (family, startup)
-- ============================================================================
CREATE TABLE entities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT entities_type_check CHECK (type IN ('family', 'startup'))
);

-- Trigger for updated_at
CREATE TRIGGER entities_updated_at
    BEFORE UPDATE ON entities
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- TABLE: user_entities
-- Many-to-many relationship between users and entities with per-entity roles
-- ============================================================================
CREATE TABLE user_entities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    entity_id UUID NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'user',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT user_entities_role_check CHECK (role IN ('admin', 'manager', 'user', 'viewer')),
    CONSTRAINT user_entities_unique UNIQUE (user_id, entity_id),

    CONSTRAINT fk_user_entities_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_user_entities_entity
        FOREIGN KEY (entity_id)
        REFERENCES entities(id)
        ON DELETE CASCADE
);

-- Indexes for efficient lookups
CREATE INDEX idx_user_entities_user_id ON user_entities(user_id);
CREATE INDEX idx_user_entities_entity_id ON user_entities(entity_id);

-- ============================================================================
-- TABLE: categories
-- Hierarchical income/expense categories with parent_id for tree structure
-- ============================================================================
CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_id UUID NOT NULL,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,
    parent_id UUID,
    description TEXT,
    color VARCHAR(50),
    icon VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT categories_type_check CHECK (type IN ('income', 'expense')),

    CONSTRAINT fk_categories_entity
        FOREIGN KEY (entity_id)
        REFERENCES entities(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_categories_parent
        FOREIGN KEY (parent_id)
        REFERENCES categories(id)
        ON DELETE SET NULL
);

-- Indexes for efficient queries
CREATE INDEX idx_categories_entity_id ON categories(entity_id);
CREATE INDEX idx_categories_parent_id ON categories(parent_id);
CREATE INDEX idx_categories_type ON categories(type);
CREATE INDEX idx_categories_is_active ON categories(is_active);

-- Trigger for updated_at
CREATE TRIGGER categories_updated_at
    BEFORE UPDATE ON categories
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- TABLE: transactions
-- Income and expense records with full metadata
-- ============================================================================
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_id UUID NOT NULL,
    category_id UUID NOT NULL,
    user_id UUID,
    amount DECIMAL(15, 2) NOT NULL,
    type VARCHAR(50) NOT NULL,
    description TEXT,
    date DATE NOT NULL,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT transactions_type_check CHECK (type IN ('income', 'expense')),
    CONSTRAINT transactions_amount_check CHECK (amount > 0),

    CONSTRAINT fk_transactions_entity
        FOREIGN KEY (entity_id)
        REFERENCES entities(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_transactions_category
        FOREIGN KEY (category_id)
        REFERENCES categories(id)
        ON DELETE RESTRICT,

    CONSTRAINT fk_transactions_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE SET NULL
);

-- Indexes for efficient queries
CREATE INDEX idx_transactions_entity_id ON transactions(entity_id);
CREATE INDEX idx_transactions_category_id ON transactions(category_id);
CREATE INDEX idx_transactions_user_id ON transactions(user_id);
CREATE INDEX idx_transactions_date ON transactions(date);
CREATE INDEX idx_transactions_type ON transactions(type);
CREATE INDEX idx_transactions_entity_date ON transactions(entity_id, date);

-- Trigger for updated_at
CREATE TRIGGER transactions_updated_at
    BEFORE UPDATE ON transactions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- TABLE: budgets
-- Budget tracking per category per entity with period support
-- ============================================================================
CREATE TABLE budgets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_id UUID NOT NULL,
    category_id UUID NOT NULL,
    amount DECIMAL(15, 2) NOT NULL,
    period_type VARCHAR(50) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT budgets_period_type_check CHECK (period_type IN ('monthly', 'quarterly', 'yearly')),
    CONSTRAINT budgets_amount_check CHECK (amount > 0),
    CONSTRAINT budgets_unique UNIQUE (entity_id, category_id, period_type, start_date),

    CONSTRAINT fk_budgets_entity
        FOREIGN KEY (entity_id)
        REFERENCES entities(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_budgets_category
        FOREIGN KEY (category_id)
        REFERENCES categories(id)
        ON DELETE RESTRICT
);

-- Indexes for efficient queries
CREATE INDEX idx_budgets_entity_id ON budgets(entity_id);
CREATE INDEX idx_budgets_category_id ON budgets(category_id);
CREATE INDEX idx_budgets_is_active ON budgets(is_active);
CREATE INDEX idx_budgets_entity_period ON budgets(entity_id, period_type);

-- Trigger for updated_at
CREATE TRIGGER budgets_updated_at
    BEFORE UPDATE ON budgets
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- TABLE: recurring_templates
-- Recurring transaction templates with recurrence patterns
-- ============================================================================
CREATE TABLE recurring_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_id UUID NOT NULL,
    category_id UUID NOT NULL,
    name VARCHAR(255) NOT NULL,
    amount DECIMAL(15, 2) NOT NULL,
    type VARCHAR(50) NOT NULL,
    description TEXT,
    notes TEXT,
    frequency VARCHAR(50) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT recurring_templates_type_check CHECK (type IN ('income', 'expense')),
    CONSTRAINT recurring_templates_amount_check CHECK (amount > 0),
    CONSTRAINT recurring_templates_frequency_check CHECK (frequency IN ('daily', 'weekly', 'monthly', 'yearly')),
    CONSTRAINT recurring_templates_dates_check CHECK (end_date IS NULL OR end_date >= start_date),

    CONSTRAINT fk_recurring_templates_entity
        FOREIGN KEY (entity_id)
        REFERENCES entities(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_recurring_templates_category
        FOREIGN KEY (category_id)
        REFERENCES categories(id)
        ON DELETE RESTRICT
);

-- Indexes for efficient queries
CREATE INDEX idx_recurring_templates_entity_id ON recurring_templates(entity_id);
CREATE INDEX idx_recurring_templates_category_id ON recurring_templates(category_id);
CREATE INDEX idx_recurring_templates_is_active ON recurring_templates(is_active);
CREATE INDEX idx_recurring_templates_frequency ON recurring_templates(frequency);

-- Trigger for updated_at
CREATE TRIGGER recurring_templates_updated_at
    BEFORE UPDATE ON recurring_templates
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- ALTER TABLE: transactions
-- Add recurring_template_id foreign key to link transactions to templates
-- ============================================================================
ALTER TABLE transactions
    ADD COLUMN recurring_template_id UUID,
    ADD CONSTRAINT fk_transactions_recurring_template
        FOREIGN KEY (recurring_template_id)
        REFERENCES recurring_templates(id)
        ON DELETE SET NULL;

-- Index for recurring template lookups
CREATE INDEX idx_transactions_recurring_template_id ON transactions(recurring_template_id);

-- ============================================================================
-- TABLE: prospects
-- CRM pipeline prospects — entity-scoped companies/contacts being tracked
-- ============================================================================
CREATE TABLE prospects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_id UUID NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    contact_name VARCHAR(255),
    contact_email VARCHAR(255),
    contact_phone VARCHAR(100),
    stage VARCHAR(50) NOT NULL DEFAULT 'lead',
    estimated_value DECIMAL(15, 2),
    source VARCHAR(100),
    notes TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT prospects_stage_check CHECK (stage IN ('lead', 'contacted', 'qualified', 'proposal', 'negotiation', 'won', 'lost')),
    CONSTRAINT prospects_estimated_value_check CHECK (estimated_value IS NULL OR estimated_value >= 0),

    CONSTRAINT fk_prospects_entity
        FOREIGN KEY (entity_id)
        REFERENCES entities(id)
        ON DELETE CASCADE
);

-- Indexes for efficient queries
CREATE INDEX idx_prospects_entity_id ON prospects(entity_id);
CREATE INDEX idx_prospects_stage ON prospects(stage);
CREATE INDEX idx_prospects_is_active ON prospects(is_active);
CREATE INDEX idx_prospects_entity_stage ON prospects(entity_id, stage);

-- Trigger for updated_at
CREATE TRIGGER prospects_updated_at
    BEFORE UPDATE ON prospects
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- TABLE: pipeline_stages
-- Configurable pipeline stages per entity for Kanban column display
-- ============================================================================
CREATE TABLE pipeline_stages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_id UUID NOT NULL,
    name VARCHAR(100) NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    order_index INTEGER NOT NULL,
    color VARCHAR(50),
    is_default BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT uq_pipeline_stages_entity_name UNIQUE (entity_id, name),
    CONSTRAINT uq_pipeline_stages_entity_order UNIQUE (entity_id, order_index),

    CONSTRAINT fk_pipeline_stages_entity
        FOREIGN KEY (entity_id)
        REFERENCES entities(id)
        ON DELETE CASCADE
);

-- Indexes for efficient queries
CREATE INDEX idx_pipeline_stages_entity_id ON pipeline_stages(entity_id);
CREATE INDEX idx_pipeline_stages_is_active ON pipeline_stages(is_active);
CREATE INDEX idx_pipeline_stages_entity_order ON pipeline_stages(entity_id, order_index);

-- Trigger for updated_at
CREATE TRIGGER pipeline_stages_updated_at
    BEFORE UPDATE ON pipeline_stages
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- TABLE: stage_transitions
-- Immutable audit trail of prospect stage changes
-- ============================================================================
CREATE TABLE stage_transitions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    prospect_id UUID NOT NULL,
    entity_id UUID NOT NULL,
    from_stage_id UUID,
    to_stage_id UUID NOT NULL,
    transitioned_by UUID,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT fk_stage_transitions_prospect
        FOREIGN KEY (prospect_id)
        REFERENCES prospects(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_stage_transitions_entity
        FOREIGN KEY (entity_id)
        REFERENCES entities(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_stage_transitions_from_stage
        FOREIGN KEY (from_stage_id)
        REFERENCES pipeline_stages(id)
        ON DELETE SET NULL,

    CONSTRAINT fk_stage_transitions_to_stage
        FOREIGN KEY (to_stage_id)
        REFERENCES pipeline_stages(id)
        ON DELETE SET NULL,

    CONSTRAINT fk_stage_transitions_user
        FOREIGN KEY (transitioned_by)
        REFERENCES users(id)
        ON DELETE SET NULL
);

-- Indexes for efficient queries
CREATE INDEX idx_stage_transitions_prospect_id ON stage_transitions(prospect_id);
CREATE INDEX idx_stage_transitions_entity_id ON stage_transitions(entity_id);
CREATE INDEX idx_stage_transitions_prospect_created ON stage_transitions(prospect_id, created_at);
