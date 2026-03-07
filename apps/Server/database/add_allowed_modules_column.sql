-- Migration: Add allowed_modules column to users table
-- allowed_modules: nullable JSONB array of module keys (e.g., ["legaldesk"])
-- NULL means "all access" (backwards compatible with existing users)

ALTER TABLE users ADD COLUMN IF NOT EXISTS allowed_modules JSONB DEFAULT NULL;

-- Insert Legal Desk demo user
-- Email: demo.legaldesk@tremarel.com
-- Password: LegalDesk2026!
INSERT INTO users (email, password_hash, first_name, last_name, role, allowed_modules)
VALUES (
  'demo.legaldesk@tremarel.com',
  '$2b$12$RbwHt6lDAAO7p1/KrlFOSuQG9DW8.SWDO7LgtkoazH9cu5EYXbeES',
  'Legal Desk',
  'Demo',
  'manager',
  '["legaldesk"]'
)
ON CONFLICT (email) DO UPDATE SET allowed_modules = '["legaldesk"]';
