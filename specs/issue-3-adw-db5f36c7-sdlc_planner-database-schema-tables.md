# Feature: Database Schema for Finance Tracker

## Metadata
issue_number: `3`
adw_id: `db5f36c7`
issue_json: `{"number":3,"title":"[FinanceTracker] Wave 1: Database Schema","body":"..."}`

## Feature Description
Create the complete PostgreSQL database schema for the Finance Tracker application. This schema defines all tables needed for multi-entity income/expense tracking, including custom JWT authentication, hierarchical categories, transactions, and budget management. The schema will be deployed to Supabase PostgreSQL and serves as the data foundation for the entire application.

## User Story
As a Finance Tracker developer
I want to have a complete and well-structured database schema
So that the backend can store and query all application data including users, entities, categories, transactions, and budgets

## Problem Statement
The Finance Tracker application requires persistent storage for multiple data domains: user authentication, multi-entity support (family/startup separation), financial transactions, hierarchical category management, and budget tracking. Without a properly designed database schema, the application cannot store or retrieve any business data.

## Solution Statement
Create a comprehensive PostgreSQL schema file (`apps/Server/database/schema.sql`) that defines:
1. **users** table - Custom authentication with password_hash, email, and role
2. **entities** table - Separate financial tracking contexts (family, startup)
3. **user_entities** table - Many-to-many relationship with per-entity roles
4. **categories** table - Hierarchical income/expense categories with parent_id
5. **transactions** table - Income and expense records with full metadata
6. **budgets** table - Budget tracking per category per entity

Include appropriate indexes for query performance, foreign key constraints for data integrity, and default values for common columns.

## Relevant Files
Use these files to implement the feature:

- `CLAUDE.md` - Contains the database schema design requirements, key tables, and architectural principles
- `apps/` - Current application layer structure (minimal setup exists)

### New Files
- `apps/Server/database/schema.sql` - The complete PostgreSQL schema with all tables, indexes, and constraints

## Implementation Plan
### Phase 1: Foundation
- Create the `apps/Server/database/` directory structure
- Design the users table with password_hash for custom JWT authentication
- Design the entities table for multi-entity (family/startup) support

### Phase 2: Core Implementation
- Create the user_entities junction table with role-based access per entity
- Design the hierarchical categories table with parent_id for tree structure
- Create the transactions table with all required financial data fields
- Create the budgets table for category-level budget tracking

### Phase 3: Integration
- Add foreign key constraints between all related tables
- Create indexes for frequently queried columns (entity_id, user_id, category_id, date ranges)
- Add appropriate CHECK constraints for data validation (amounts, types, roles)

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### 1. Create Directory Structure
- Create the `apps/Server/database/` directory to house the schema file
- This follows the project structure defined in CLAUDE.md

### 2. Create Users Table
- Define `users` table with columns:
  - `id` (UUID, primary key, auto-generated)
  - `email` (VARCHAR, unique, not null)
  - `password_hash` (VARCHAR, not null) - for custom JWT auth
  - `first_name` (VARCHAR)
  - `last_name` (VARCHAR)
  - `role` (VARCHAR) - global role (admin, manager, user, viewer)
  - `is_active` (BOOLEAN, default true)
  - `created_at` (TIMESTAMP, default now)
  - `updated_at` (TIMESTAMP)
- Add index on `email` for login lookups

### 3. Create Entities Table
- Define `entities` table with columns:
  - `id` (UUID, primary key, auto-generated)
  - `name` (VARCHAR, not null)
  - `type` (VARCHAR, not null) - 'family' or 'startup'
  - `description` (TEXT)
  - `created_at` (TIMESTAMP, default now)
  - `updated_at` (TIMESTAMP)
- Add CHECK constraint for valid entity types

### 4. Create User-Entities Junction Table
- Define `user_entities` table with columns:
  - `id` (UUID, primary key, auto-generated)
  - `user_id` (UUID, foreign key to users)
  - `entity_id` (UUID, foreign key to entities)
  - `role` (VARCHAR, not null) - entity-specific role
  - `created_at` (TIMESTAMP, default now)
- Add unique constraint on (user_id, entity_id) to prevent duplicates
- Add indexes on user_id and entity_id for efficient lookups

### 5. Create Categories Table with Hierarchy Support
- Define `categories` table with columns:
  - `id` (UUID, primary key, auto-generated)
  - `entity_id` (UUID, foreign key to entities)
  - `name` (VARCHAR, not null)
  - `type` (VARCHAR, not null) - 'income' or 'expense'
  - `parent_id` (UUID, self-referential foreign key) - for hierarchy
  - `description` (TEXT)
  - `color` (VARCHAR) - for UI display
  - `icon` (VARCHAR) - for UI display
  - `is_active` (BOOLEAN, default true)
  - `created_at` (TIMESTAMP, default now)
  - `updated_at` (TIMESTAMP)
- Add indexes on entity_id and parent_id
- Add CHECK constraint for valid category types

### 6. Create Transactions Table
- Define `transactions` table with columns:
  - `id` (UUID, primary key, auto-generated)
  - `entity_id` (UUID, foreign key to entities, not null)
  - `category_id` (UUID, foreign key to categories, not null)
  - `user_id` (UUID, foreign key to users) - who created it
  - `amount` (DECIMAL(15,2), not null)
  - `type` (VARCHAR, not null) - 'income' or 'expense'
  - `description` (TEXT)
  - `date` (DATE, not null) - transaction date
  - `notes` (TEXT)
  - `created_at` (TIMESTAMP, default now)
  - `updated_at` (TIMESTAMP)
- Add indexes on entity_id, category_id, user_id, and date for efficient queries
- Add CHECK constraint for positive amounts and valid types

### 7. Create Budgets Table
- Define `budgets` table with columns:
  - `id` (UUID, primary key, auto-generated)
  - `entity_id` (UUID, foreign key to entities, not null)
  - `category_id` (UUID, foreign key to categories, not null)
  - `amount` (DECIMAL(15,2), not null)
  - `period_type` (VARCHAR, not null) - 'monthly', 'quarterly', 'yearly'
  - `start_date` (DATE, not null)
  - `end_date` (DATE)
  - `is_active` (BOOLEAN, default true)
  - `created_at` (TIMESTAMP, default now)
  - `updated_at` (TIMESTAMP)
- Add unique constraint on (entity_id, category_id, period_type, start_date)
- Add indexes on entity_id and category_id
- Add CHECK constraint for valid period types and positive amounts

### 8. Add All Foreign Key Constraints
- Ensure all foreign keys have ON DELETE behavior defined:
  - user_entities: CASCADE on user/entity delete
  - categories: SET NULL on parent delete, CASCADE on entity delete
  - transactions: RESTRICT on category delete, CASCADE on entity delete
  - budgets: RESTRICT on category delete, CASCADE on entity delete

### 9. Create Updated_at Trigger Function
- Create a PostgreSQL function to automatically update `updated_at` timestamps
- Apply the trigger to all tables with `updated_at` columns

### 10. Validate Schema Implementation
- Review the complete schema for consistency
- Verify all indexes are properly defined
- Ensure all foreign key relationships are correct
- Run validation commands to confirm SQL syntax is valid

## Testing Strategy
### Unit Tests
- No unit tests required for pure SQL schema file
- Schema will be validated by attempting to execute in PostgreSQL

### Edge Cases
- Self-referential foreign key in categories (parent_id)
- Unique constraints on user_entities (user_id, entity_id)
- Budget uniqueness per entity/category/period/start_date
- Valid enum-like values for type and role columns

## Acceptance Criteria
- [ ] `apps/Server/database/schema.sql` file exists and contains valid PostgreSQL syntax
- [ ] users table includes password_hash column for custom JWT auth
- [ ] entities table supports family/startup type separation
- [ ] user_entities table enables many-to-many relationships with per-entity roles
- [ ] categories table supports hierarchical structure via parent_id
- [ ] transactions table includes all required financial data fields
- [ ] budgets table supports period-based budget tracking
- [ ] All tables have appropriate indexes for performance
- [ ] All foreign key constraints are properly defined
- [ ] CHECK constraints validate data integrity (types, amounts, roles)
- [ ] updated_at trigger function is included

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `ls apps/Server/database/schema.sql` - Verify the schema file was created in the correct location
- `head -100 apps/Server/database/schema.sql` - Review the beginning of the schema for proper structure
- `grep -c "CREATE TABLE" apps/Server/database/schema.sql` - Should return 6 (users, entities, user_entities, categories, transactions, budgets)
- `grep -c "CREATE INDEX" apps/Server/database/schema.sql` - Should return multiple indexes
- `grep "password_hash" apps/Server/database/schema.sql` - Verify users table has password_hash column
- `grep "parent_id" apps/Server/database/schema.sql` - Verify categories table has hierarchical support
- `grep "FOREIGN KEY" apps/Server/database/schema.sql` - Verify foreign key constraints exist

## Notes
- This is Wave 1 (Foundation) and runs in parallel with FT-001 (Backend Setup) and FT-002 (Frontend Setup)
- The schema uses UUIDs for primary keys as is common with PostgreSQL/Supabase
- DECIMAL(15,2) allows amounts up to 9,999,999,999,999.99 which is sufficient for personal/startup finance tracking
- The hierarchical categories design allows unlimited depth of category nesting
- Role columns use VARCHAR with CHECK constraints rather than PostgreSQL ENUM types for easier future modifications
- After Wave 1 completes, Wave 2 begins with authentication implementation (FT-004 Backend Auth, then FT-005 Frontend Auth) which will use this schema
