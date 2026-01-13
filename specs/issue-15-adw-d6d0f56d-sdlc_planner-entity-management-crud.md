# Feature: Entity Management CRUD

## Metadata
issue_number: `15`
adw_id: `d6d0f56d`
issue_json: `{"number":15,"title":"[FinanceTracker] Wave 3: Entity Management","body":"..."}`

## Feature Description
Implement entity management allowing users to create, view, update, and switch between different financial entities (Family, Startup). Each entity represents a separate financial tracking context with its own transactions, categories, and budgets. Users can belong to multiple entities with different roles per entity. The system provides an EntityContext in the frontend to track the current entity, ensuring all data queries filter by the selected entity.

## User Story
As a Finance Tracker user
I want to create and switch between different entities like Family and Startup
So that I can keep my personal finances separate from my business finances

## Problem Statement
Users need to manage multiple financial contexts (family budget vs startup finances) within a single application. Without entity management, all financial data would be mixed together, making it impossible to track finances for different purposes separately.

## Solution Statement
Implement a complete entity management system with:
1. Backend CRUD endpoints for entities and user-entity membership
2. EntityContext in frontend to track and switch between entities
3. Entity selector UI component for switching entities
4. All existing and future data queries will filter by the selected entity

## Relevant Files
Use these files to implement the feature:

**Backend - Existing patterns to follow:**
- `apps/Server/main.py` - Entry point, register entity router here (line 56 pattern)
- `apps/Server/src/models/user.py` - Model pattern for creating Entity model
- `apps/Server/src/repository/user_repository.py` - Repository pattern for EntityRepository
- `apps/Server/src/core/services/auth_service.py` - Service pattern for EntityService
- `apps/Server/src/adapter/rest/auth_routes.py` - Routes pattern for entity_routes
- `apps/Server/src/interface/auth_dto.py` - DTO pattern for entity_dto
- `apps/Server/src/adapter/rest/dependencies.py` - Dependency injection patterns
- `apps/Server/src/adapter/rest/rbac_dependencies.py` - RBAC pattern for entity access control
- `apps/Server/database/schema.sql` - Database schema reference (entities, user_entities tables)
- `apps/Server/tests/test_auth.py` - Test pattern for entity tests

**Frontend - Existing patterns to follow:**
- `apps/Client/src/main.tsx` - Entry point, wrap with EntityProvider (line 15 pattern)
- `apps/Client/src/App.tsx` - Routing, add entity routes
- `apps/Client/src/contexts/AuthContext.tsx` - Context pattern for EntityContext
- `apps/Client/src/contexts/authContextDef.ts` - Context definition pattern
- `apps/Client/src/hooks/useAuth.ts` - Hook pattern for useEntity
- `apps/Client/src/services/authService.ts` - Service pattern for entityService
- `apps/Client/src/types/index.ts` - Type definitions (Entity interface exists at line 50)
- `apps/Client/src/api/clients/index.ts` - API client configuration
- `apps/Client/src/pages/DashboardPage.tsx` - Page to integrate entity display

**E2E Testing:**
- `.claude/commands/test_e2e.md` - E2E test runner instructions
- `.claude/commands/e2e/test_auth_login.md` - E2E test example for format reference

### New Files

**Backend:**
- `apps/Server/src/models/entity.py` - Entity SQLAlchemy model
- `apps/Server/src/models/user_entity.py` - UserEntity SQLAlchemy model
- `apps/Server/src/interface/entity_dto.py` - Entity Pydantic DTOs
- `apps/Server/src/repository/entity_repository.py` - Entity data access layer
- `apps/Server/src/core/services/entity_service.py` - Entity business logic
- `apps/Server/src/adapter/rest/entity_routes.py` - Entity API endpoints
- `apps/Server/tests/test_entity.py` - Entity endpoint tests

**Frontend:**
- `apps/Client/src/contexts/EntityContext.tsx` - EntityProvider component
- `apps/Client/src/contexts/entityContextDef.ts` - EntityContext definition
- `apps/Client/src/hooks/useEntity.ts` - useEntity hook
- `apps/Client/src/services/entityService.ts` - Entity API service
- `apps/Client/src/components/ui/TREntitySelector.tsx` - Entity selector dropdown
- `apps/Client/src/pages/EntitiesPage.tsx` - Entity management page

**E2E:**
- `.claude/commands/e2e/test_entity_management.md` - E2E test for entity management

## Implementation Plan

### Phase 1: Foundation
1. Create Entity and UserEntity SQLAlchemy models following the existing User model pattern
2. Create Entity DTOs for request/response serialization
3. Create EntityRepository for database operations

### Phase 2: Core Implementation
1. Implement EntityService with business logic for CRUD operations and user-entity membership
2. Create entity_routes with FastAPI endpoints
3. Register entity router in main.py
4. Write backend unit tests

### Phase 3: Integration
1. Create EntityContext and useEntity hook on frontend
2. Create entityService for API calls
3. Build TREntitySelector component for entity switching
4. Create EntitiesPage for entity management
5. Integrate EntityProvider in main.tsx and display current entity in DashboardPage
6. Write E2E tests

## Step by Step Tasks

### Step 1: Create Backend Entity Models

- Create `apps/Server/src/models/entity.py` with Entity SQLAlchemy model:
  - id (UUID, primary key)
  - name (String, required)
  - type (String: 'family' | 'startup')
  - description (Text, optional)
  - created_at, updated_at timestamps
- Create `apps/Server/src/models/user_entity.py` with UserEntity SQLAlchemy model:
  - id (UUID, primary key)
  - user_id (UUID, foreign key to users)
  - entity_id (UUID, foreign key to entities)
  - role (String: admin/manager/user/viewer)
  - created_at timestamp
  - Unique constraint on (user_id, entity_id)
- Export models from `apps/Server/src/models/__init__.py`

### Step 2: Create Entity DTOs

- Create `apps/Server/src/interface/entity_dto.py` with:
  - EntityCreateDTO (name, type, description)
  - EntityUpdateDTO (name, description - partial update)
  - EntityResponseDTO (id, name, type, description, created_at, updated_at)
  - UserEntityCreateDTO (user_id, entity_id, role)
  - UserEntityResponseDTO (id, user_id, entity_id, role, created_at)
- Export DTOs from `apps/Server/src/interface/__init__.py`

### Step 3: Create Entity Repository

- Create `apps/Server/src/repository/entity_repository.py` following user_repository pattern:
  - create_entity(db, name, type, description) -> Entity
  - get_entity_by_id(db, entity_id) -> Entity | None
  - get_entities_by_user_id(db, user_id) -> list[Entity]
  - update_entity(db, entity) -> Entity
  - delete_entity(db, entity_id) -> bool
  - add_user_to_entity(db, user_id, entity_id, role) -> UserEntity
  - remove_user_from_entity(db, user_id, entity_id) -> bool
  - get_user_entity_role(db, user_id, entity_id) -> str | None
- Export repository from `apps/Server/src/repository/__init__.py`

### Step 4: Create Entity Service

- Create `apps/Server/src/core/services/entity_service.py` following auth_service pattern:
  - create_entity(db, user_id, entity_data) -> Entity (also adds creator as admin)
  - get_user_entities(db, user_id) -> list[Entity]
  - get_entity(db, entity_id, user_id) -> Entity (validates user access)
  - update_entity(db, entity_id, user_id, entity_data) -> Entity (validates admin/manager role)
  - delete_entity(db, entity_id, user_id) -> bool (validates admin role)
  - add_member(db, entity_id, user_id, target_user_id, role) -> UserEntity
  - remove_member(db, entity_id, user_id, target_user_id) -> bool
  - get_user_role_in_entity(db, user_id, entity_id) -> str | None
- Export service singleton from `apps/Server/src/core/services/__init__.py`

### Step 5: Create Entity Routes

- Create `apps/Server/src/adapter/rest/entity_routes.py` following auth_routes pattern:
  - POST /api/entities - Create entity (authenticated)
  - GET /api/entities - List user's entities (authenticated)
  - GET /api/entities/{id} - Get entity by ID (authenticated, member access)
  - PUT /api/entities/{id} - Update entity (admin/manager role)
  - DELETE /api/entities/{id} - Delete entity (admin role only)
  - POST /api/entities/{id}/members - Add member (admin/manager role)
  - DELETE /api/entities/{id}/members/{user_id} - Remove member (admin role)
  - GET /api/entities/{id}/members - List entity members (member access)
- Register router in `apps/Server/main.py`

### Step 6: Write Backend Tests

- Create `apps/Server/tests/test_entity.py` following test_auth.py pattern:
  - Test entity creation success
  - Test entity creation validation (invalid type)
  - Test list user entities (returns only user's entities)
  - Test get entity (access control)
  - Test update entity (role-based access)
  - Test delete entity (admin only)
  - Test add member (role-based access)
  - Test remove member (admin only)
  - Test get user role in entity

### Step 7: Create E2E Test File

- Create `.claude/commands/e2e/test_entity_management.md` following test_auth_login.md pattern:
  - Test navigation to entities page
  - Test entity creation form
  - Test entity list display
  - Test entity switching
  - Test entity update
  - Test error handling
  - Screenshot requirements

### Step 8: Create Frontend Entity Context Definition

- Create `apps/Client/src/contexts/entityContextDef.ts` following authContextDef.ts pattern:
  - EntityContextType interface with:
    - entities: Entity[]
    - currentEntity: Entity | null
    - isLoading: boolean
    - switchEntity: (entityId: string) => void
    - createEntity: (data: CreateEntityData) => Promise<Entity>
    - updateEntity: (id: string, data: UpdateEntityData) => Promise<Entity>
    - deleteEntity: (id: string) => Promise<void>
    - refreshEntities: () => Promise<void>
  - Export EntityContext

### Step 9: Create Frontend Entity Service

- Create `apps/Client/src/services/entityService.ts` following authService.ts pattern:
  - getEntities() -> Entity[]
  - getEntity(id) -> Entity
  - createEntity(data) -> Entity
  - updateEntity(id, data) -> Entity
  - deleteEntity(id) -> void
  - Include proper logging

### Step 10: Create Entity Context Provider

- Create `apps/Client/src/contexts/EntityContext.tsx` following AuthContext.tsx pattern:
  - State: entities, currentEntity, isLoading
  - On mount: fetch user's entities, select first or stored entity from localStorage
  - switchEntity: update currentEntity and persist to localStorage
  - Provide CRUD operations via context
  - Export EntityProvider

### Step 11: Create useEntity Hook

- Create `apps/Client/src/hooks/useEntity.ts` following useAuth.ts pattern:
  - Return EntityContext value
  - Throw error if used outside EntityProvider

### Step 12: Update Frontend Types

- Update `apps/Client/src/types/index.ts`:
  - Enhance existing Entity interface with description field
  - Add CreateEntityData interface
  - Add UpdateEntityData interface
  - Add UserEntity interface
  - Add EntityMember interface

### Step 13: Create TREntitySelector Component

- Create `apps/Client/src/components/ui/TREntitySelector.tsx`:
  - Material-UI Select component
  - Display current entity name
  - Dropdown with all user entities
  - On change: call switchEntity
  - Add to DashboardPage header or sidebar

### Step 14: Create Entities Page

- Create `apps/Client/src/pages/EntitiesPage.tsx`:
  - List all user entities with cards/table
  - Create entity button with modal form (using react-hook-form)
  - Edit entity button per entity
  - Delete entity button with confirmation dialog
  - Display entity type and description

### Step 15: Integrate EntityProvider and Update Routes

- Update `apps/Client/src/main.tsx`:
  - Wrap App with EntityProvider (inside AuthProvider)
- Update `apps/Client/src/App.tsx`:
  - Add route for /entities page (protected)
- Update `apps/Client/src/pages/DashboardPage.tsx`:
  - Display current entity info
  - Add TREntitySelector to header/top bar

### Step 16: Run Validation Commands

- Execute all validation commands to ensure zero regressions

## Testing Strategy

### Unit Tests
- EntityRepository: CRUD operations with mock database
- EntityService: Business logic including access control
- Entity routes: HTTP endpoints with mock service

### Edge Cases
- User tries to access entity they don't belong to (403)
- User tries to delete entity without admin role (403)
- User tries to create entity with invalid type (422)
- User tries to switch to non-existent entity (404)
- Last admin tries to remove themselves from entity
- Empty entity list for new user

## Acceptance Criteria
- Users can create new entities with name, type (family/startup), and description
- Users can view list of all entities they belong to
- Users can switch between entities using a selector component
- Current entity is persisted in localStorage and restored on page refresh
- Users can update entities they have admin/manager role in
- Users with admin role can delete entities
- All entity operations require authentication
- Entity routes validate user membership before allowing access
- Frontend displays current entity context throughout the application
- E2E tests pass demonstrating the complete entity management flow

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_entity_management.md` to validate entity management E2E functionality
- `cd apps/Server && uv run pytest tests/test_entity.py -v` - Run entity-specific tests
- `cd apps/Server && uv run pytest` - Run all Server tests to validate zero regressions
- `cd apps/Client && npm run tsc` - Run Client type check
- `cd apps/Client && npm run build` - Run Client build

## Notes
- The Entity interface already exists in `apps/Client/src/types/index.ts` at line 50-56 with basic fields
- The database schema for `entities` and `user_entities` tables already exists in `apps/Server/database/schema.sql` (lines 51-95)
- Entity type is constrained to 'family' or 'startup' per database CHECK constraint
- User-entity roles are: admin, manager, user, viewer (same as user global roles)
- When a user creates an entity, they should automatically become the admin of that entity
- The JWT token does not include entity information - entity context is managed separately on the frontend
- Future features (Categories, Transactions, Budgets) will use the current entity from EntityContext to filter data
