# Person Entity CRUD Backend

**ADW ID:** 14633eae
**Date:** 2026-03-03
**Specification:** specs/issue-79-adw-14633eae-sdlc_planner-person-entity-crud-backend.md

## Overview

Full backend CRUD implementation for the Person entity in the RestaurantOS module. A Person represents employees, suppliers, or owners within a restaurant. This is the second of four Wave 1 core entities (after Restaurant) and is scoped to a restaurant via `restaurant_id` for multi-tenant isolation. Backend-only feature — no UI components.

## What Was Built

- SQL migration for the `person` table with UUID primary key, indexes, and `updated_at` trigger
- SQLAlchemy `Person` model with restaurant foreign key and type classification
- Pydantic DTOs (`PersonCreateDTO`, `PersonUpdateDTO`, `PersonResponseDTO`) with `PersonType` enum and `EmailStr` validation
- Repository layer with CRUD operations and ILIKE name search
- Service layer with restaurant-scoped authorization via `user_restaurants` membership
- REST API with 6 endpoints under `/api/persons` with JWT authentication
- Comprehensive unit tests (DTO/model) and API integration tests

## Technical Implementation

### Files Modified

- `apps/Server/main.py`: Registered `person_router` and added startup log line
- `apps/Server/src/models/__init__.py`: Added `Person` to model exports

### Files Created

- `apps/Server/database/create_person_table.sql`: SQL migration with UUID PK, `restaurant_id` FK (CASCADE), indexes on `restaurant_id` and `type`, and `updated_at` trigger
- `apps/Server/src/models/person.py`: SQLAlchemy model mapping all columns — `id`, `restaurant_id`, `name`, `role`, `email`, `whatsapp`, `type`, `created_at`, `updated_at`
- `apps/Server/src/interface/person_dto.py`: `PersonType` enum (employee/supplier/owner), `PersonCreateDTO` with `EmailStr` validation, `PersonUpdateDTO` with all-optional partial updates, `PersonResponseDTO` with `from_attributes`
- `apps/Server/src/repository/person_repository.py`: Singleton `PersonRepository` with `create`, `get_by_id`, `get_by_restaurant` (optional type filter), `update`, `delete`, `search` (ILIKE on name)
- `apps/Server/src/core/services/person_service.py`: Singleton `PersonService` with `_check_restaurant_access` authorization helper, wraps repository calls with membership checks via `restaurant_repository.get_user_restaurant_role`
- `apps/Server/src/adapter/rest/person_routes.py`: APIRouter at `/api/persons` with 6 endpoints
- `apps/Server/tests/test_person_model.py`: 333 lines of DTO validation and model unit tests
- `apps/Server/tests/test_person_api.py`: 674 lines of API endpoint integration tests with mocked DB/auth

### Key Changes

- **PersonType enum**: `employee`, `supplier`, `owner` — stored as VARCHAR in DB, validated via Pydantic `PersonType(str, Enum)`
- **Role field**: Free-text (not enum) to allow flexibility — chef, mesero, dueño, proveedor, etc.
- **Authorization**: All operations check `user_restaurants` membership before proceeding; raises `PermissionError` (→ HTTP 403) for unauthorized access
- **Search route ordering**: `GET /api/persons/search` is defined before `GET /api/persons/{person_id}` to prevent FastAPI from interpreting "search" as a UUID path parameter
- **Cascading delete**: `restaurant_id` FK uses `ON DELETE CASCADE` — deleting a restaurant removes all its persons

### API Endpoints

| Method | Path | Description | Status |
|--------|------|-------------|--------|
| POST | `/api/persons` | Create a person | 201 |
| GET | `/api/persons` | List persons by restaurant (optional type filter) | 200 |
| GET | `/api/persons/search` | Search persons by name within a restaurant | 200 |
| GET | `/api/persons/{person_id}` | Get person by ID | 200 |
| PUT | `/api/persons/{person_id}` | Update a person | 200 |
| DELETE | `/api/persons/{person_id}` | Delete a person | 204 |

### Database Schema

```sql
CREATE TABLE person (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    restaurant_id UUID NOT NULL REFERENCES restaurant(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(100) NOT NULL,
    email VARCHAR(255),
    whatsapp VARCHAR(50),
    type VARCHAR(50) NOT NULL DEFAULT 'employee',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

Indexes: `idx_person_restaurant` on `restaurant_id`, `idx_person_type` on `type`.

## How to Use

1. Run the SQL migration `apps/Server/database/create_person_table.sql` against the database
2. Start the backend server
3. Authenticate to get a JWT token
4. Create a person: `POST /api/persons` with body `{ "restaurant_id": "<uuid>", "name": "...", "role": "...", "type": "employee" }`
5. List persons: `GET /api/persons?restaurant_id=<uuid>&type=employee`
6. Search by name: `GET /api/persons/search?restaurant_id=<uuid>&query=<name>`
7. Get/update/delete by ID: `GET/PUT/DELETE /api/persons/{person_id}`

All endpoints require `Authorization: Bearer <token>` and the user must have membership in the person's restaurant.

## Configuration

No additional configuration required beyond existing environment variables. The Person entity uses the same database connection, JWT authentication, and CORS settings as other endpoints.

## Testing

```bash
# Person DTO and model unit tests
cd apps/Server && python -m pytest tests/test_person_model.py -v

# Person API endpoint integration tests
cd apps/Server && python -m pytest tests/test_person_api.py -v

# All server tests (zero regression check)
cd apps/Server && python -m pytest tests/ -v
```

## Notes

- This is part of RestaurantOS **Wave 1** (ROS-002), running in parallel with Restaurant (ROS-001) and Resource (ROS-003)
- Wave 2 entities (Document, Event) will reference Person via foreign keys — the Person model and API must remain stable
- WhatsApp field accepts international format strings (e.g., "+52 555 123 4567") with max 50 characters, no strict format validation
- Email validation uses Pydantic `EmailStr` (from `pydantic[email]` / `email-validator`)
