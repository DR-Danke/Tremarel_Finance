# Category Management CRUD

**ADW ID:** a2d71086
**Date:** 2026-01-13
**Specification:** specs/issue-16-adw-a2d71086-sdlc_planner-category-management-crud.md

## Overview

This feature implements complete category management for the Finance Tracker application. It provides hierarchical income and expense categories with optional parent-child relationships (e.g., "Food" → "Groceries", "Restaurants"). Categories are entity-specific, meaning each entity (family or startup) has its own set of categories.

## What Was Built

- **Backend REST API** - Full CRUD endpoints for categories at `/api/categories`
- **Category hierarchy support** - Parent-child relationships with circular reference prevention
- **Category tree endpoint** - Returns hierarchical tree structure for UI display
- **Frontend Categories page** - Complete page with tree view and create/edit/delete dialogs
- **TRCategoryForm component** - React Hook Form component for creating/editing categories
- **TRCategoryTree component** - Recursive tree display component with expand/collapse
- **useCategories hook** - Custom hook managing category state and operations
- **648 lines of backend unit tests** - Comprehensive test coverage for all operations

## Technical Implementation

### Files Modified

- `apps/Server/main.py`: Added category router registration
- `apps/Client/src/App.tsx`: Added protected route for `/categories` page
- `apps/Client/src/types/index.ts`: Added Category-related TypeScript interfaces

### New Backend Files

- `apps/Server/src/models/category.py`: SQLAlchemy Category model
- `apps/Server/src/interface/category_dto.py`: Pydantic DTOs (Create, Update, Response, Tree)
- `apps/Server/src/repository/category_repository.py`: Data access layer with CRUD operations
- `apps/Server/src/core/services/category_service.py`: Business logic with hierarchy validation
- `apps/Server/src/adapter/rest/category_routes.py`: REST API endpoints
- `apps/Server/tests/test_category.py`: Unit tests for all operations

### New Frontend Files

- `apps/Client/src/services/categoryService.ts`: API wrapper service
- `apps/Client/src/hooks/useCategories.ts`: Custom hook for category state management
- `apps/Client/src/components/forms/TRCategoryForm.tsx`: Form component with react-hook-form
- `apps/Client/src/components/ui/TRCategoryTree.tsx`: Recursive tree display component
- `apps/Client/src/pages/CategoriesPage.tsx`: Main categories management page

### Key Changes

- **Hierarchical validation**: Parent category must exist, belong to same entity, and have same type (income/expense)
- **Circular reference prevention**: Service validates that updating parent_id won't create cycles
- **Delete protection**: Categories with children or transactions cannot be deleted
- **Entity isolation**: All category operations validate user access to the entity

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/categories/` | Create a new category |
| GET | `/api/categories/entity/{entity_id}` | Get all categories for entity (flat list) |
| GET | `/api/categories/entity/{entity_id}/tree` | Get hierarchical category tree |
| GET | `/api/categories/{category_id}` | Get single category by ID |
| PUT | `/api/categories/{category_id}` | Update category |
| DELETE | `/api/categories/{category_id}` | Delete category |

All endpoints require JWT authentication via `Authorization: Bearer <token>` header.

## How to Use

1. Log in to the application
2. Navigate to `/categories` page
3. Click "Add Category" to create a new category
4. Fill in the form:
   - **Name**: Required, category name
   - **Type**: Select income or expense
   - **Parent**: Optional, select parent category (filtered by type)
   - **Description**: Optional description
5. View categories in the tree view with expand/collapse functionality
6. Click edit icon on any category to modify it
7. Click delete icon to remove a category (only if no children or transactions)

## Configuration

No additional configuration required. The feature uses the existing JWT authentication and database connection settings from environment variables.

## Testing

### Backend Tests

```bash
cd apps/Server && uv run pytest tests/test_category.py -v
```

Test coverage includes:
- Create category with/without parent
- Validation errors (missing name, invalid type, wrong entity)
- Get categories by entity (flat and tree)
- Update category including parent changes
- Delete category (success and failure cases)
- Unauthorized access (no token)
- Circular reference prevention

### Frontend Validation

```bash
cd apps/Client && npm run tsc    # Type checking
cd apps/Client && npm run lint   # Linting
cd apps/Client && npm run build  # Production build
```

### E2E Testing

Run the E2E test specification:
```
.claude/commands/e2e/test_category_management.md
```

## Notes

- Categories use the existing `categories` table in the database schema
- The `type` field cannot be changed after creation (enforced in UI by disabling field in edit mode)
- Parent category must have the same type as child category
- The frontend uses a hardcoded default entity ID for development; in production this will come from EntityContext
- Color and icon fields are optional and can be used for visual distinction (UI enhancement for future)
