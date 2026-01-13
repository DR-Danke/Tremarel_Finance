# Entity Management CRUD

**ADW ID:** d6d0f56d
**Date:** 2026-01-13
**Specification:** specs/issue-15-adw-d6d0f56d-sdlc_planner-entity-management-crud.md

## Overview

Entity management system that allows users to create, view, update, and switch between different financial entities (Family, Startup). Each entity represents a separate financial tracking context with its own transactions, categories, and budgets. Users can belong to multiple entities with different roles per entity.

## What Was Built

- Backend Entity and UserEntity SQLAlchemy models
- Entity repository with full CRUD and membership operations
- Entity service with business logic and role-based access control
- RESTful API endpoints for entity and member management
- Frontend EntityContext with state management and localStorage persistence
- Entity selector component for switching between entities
- Full entity management page with create/edit/delete dialogs
- Comprehensive backend unit tests
- E2E test specification

## Technical Implementation

### Files Modified

- `apps/Server/main.py`: Registered entity router
- `apps/Client/src/main.tsx`: Wrapped App with EntityProvider
- `apps/Client/src/App.tsx`: Added /entities route
- `apps/Client/src/pages/DashboardPage.tsx`: Integrated TREntitySelector
- `apps/Client/src/types/index.ts`: Added entity-related type definitions

### New Files Created

**Backend:**
- `apps/Server/src/models/entity.py`: Entity SQLAlchemy model (id, name, type, description, timestamps)
- `apps/Server/src/models/user_entity.py`: UserEntity model for user-entity membership with roles
- `apps/Server/src/interface/entity_dto.py`: Pydantic DTOs for request/response serialization
- `apps/Server/src/repository/entity_repository.py`: Data access layer with CRUD and membership operations
- `apps/Server/src/core/services/entity_service.py`: Business logic with role-based access validation
- `apps/Server/src/adapter/rest/entity_routes.py`: FastAPI endpoints for entity management
- `apps/Server/tests/test_entity.py`: 679 lines of comprehensive unit tests

**Frontend:**
- `apps/Client/src/contexts/entityContextDef.ts`: EntityContext type definition
- `apps/Client/src/contexts/EntityContext.tsx`: EntityProvider with state management
- `apps/Client/src/hooks/useEntity.ts`: Hook for accessing entity context
- `apps/Client/src/services/entityService.ts`: API service for entity operations
- `apps/Client/src/components/ui/TREntitySelector.tsx`: Entity selector dropdown component
- `apps/Client/src/pages/EntitiesPage.tsx`: Full entity management page

**E2E:**
- `.claude/commands/e2e/test_entity_management.md`: E2E test specification

### Key Changes

- Entity types are constrained to 'family' or 'startup' via database CHECK constraint
- User creating an entity is automatically added as admin of that entity
- Role-based access: admin can do everything, manager can update/add members, others have read-only access
- Current entity persisted in localStorage and restored on page refresh
- EntityContext integrates with AuthContext to fetch entities on authentication

## How to Use

1. **Login** to the application with valid credentials
2. **Navigate** to the Entity Management page via the "Entities" link or `/entities` URL
3. **Create Entity**: Click "Create Entity" button, fill in name, type (Family/Startup), and optional description
4. **Switch Entity**: Click "Select" on any entity card or use the TREntitySelector dropdown in the Dashboard
5. **Edit Entity**: Click the edit icon on an entity card to update name or description
6. **Delete Entity**: Click the delete icon and confirm to remove an entity

## API Endpoints

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| POST | /api/entities | Create new entity | Authenticated |
| GET | /api/entities | List user's entities | Authenticated |
| GET | /api/entities/{id} | Get entity by ID | Member |
| PUT | /api/entities/{id} | Update entity | Admin/Manager |
| DELETE | /api/entities/{id} | Delete entity | Admin |
| POST | /api/entities/{id}/members | Add member | Admin/Manager |
| DELETE | /api/entities/{id}/members/{user_id} | Remove member | Admin |
| GET | /api/entities/{id}/members | List members | Member |

## Configuration

No additional configuration required. Entity management uses existing JWT authentication and database connection settings.

## Testing

**Backend Unit Tests:**
```bash
cd apps/Server && uv run pytest tests/test_entity.py -v
```

**E2E Tests:**
Read and execute `.claude/commands/e2e/test_entity_management.md`

**Frontend Type Check:**
```bash
cd apps/Client && npm run tsc
```

## Notes

- Entity type cannot be changed after creation (intentional design)
- Deleting an entity with a single admin is prevented to avoid orphaned entities
- Future features (Categories, Transactions, Budgets) will filter data by currentEntity from EntityContext
- The JWT token does not include entity information; entity context is managed separately on the frontend
