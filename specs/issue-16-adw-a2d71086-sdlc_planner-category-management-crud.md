# Feature: Category Management CRUD

## Metadata
issue_number: `16`
adw_id: `a2d71086`
issue_json: `{"number":16,"title":"[FinanceTracker] Wave 3: Category Management","body":"```markdown\n## Context\n**Project:** Finance Tracker - Income & Expense Management\n**Overview:** We are building a full-stack income/expense tracking application for family and startup company management. The system includes multi-entity support (family/startup separation), custom JWT authentication, transaction management, budgeting, reporting with charts, and CSV export. Frontend deploys to Vercel, backend to Render, database on Supabase PostgreSQL.\n\n**Current Wave:** Wave 3 of 6 - Layout & Core Features\n**Current Issue:** FT-008 (Issue 8 of 14)\n**Parallel Execution:** YES - This issue runs in parallel with FT-006 (Layout), FT-007 (Entity Management), and FT-009 (Transactions). All four are independent features.\n\n**Dependencies:** Requires Wave 2 completion (authentication must be in place).\n**What comes next:** After Wave 3 completes, Wave 4 implements the Dashboard (FT-010).\n\n## Request\nImplement income and expense categories with optional parent-child hierarchy. Users can create categories like \"Food\" with subcategories \"Groceries\" and \"Restaurants\". Add backend endpoints for category CRUD. Create a Categories page in frontend with a form to add/edit categories and a list view showing the category tree. Categories are entity-specific.\n```"}`

## Feature Description
This feature implements complete category management for the Finance Tracker application. It includes hierarchical income and expense categories with optional parent-child relationships (e.g., "Food" → "Groceries", "Restaurants"). The backend provides full CRUD endpoints for categories, and the frontend provides a Categories page with a form to create/edit categories and a tree view to display the category hierarchy. Categories are entity-specific, meaning each entity (family or startup) has its own set of categories.

## User Story
As a Finance Tracker user
I want to create and organize income and expense categories with optional subcategories
So that I can accurately categorize my transactions and track spending by category

## Problem Statement
The Finance Tracker application has a database schema for hierarchical categories but no backend endpoints or frontend UI to manage them. Users cannot create categories for their entities, which is required before they can add transactions. The system needs full CRUD operations for categories with support for parent-child hierarchy.

## Solution Statement
Implement a complete category management system that:
1. Provides backend CRUD endpoints for categories (create, read, update, delete)
2. Supports hierarchical parent-child relationships via parent_id
3. Filters categories by entity_id (entity-specific categories)
4. Creates a frontend Categories page with:
   - A form to add/edit categories (using react-hook-form)
   - A tree view displaying the category hierarchy
   - Category type selection (income/expense)
   - Optional parent category selection
5. Protects all routes with authentication (JWT)
6. Validates that users can only access categories for entities they belong to

## Relevant Files
Use these files to implement the feature:

### Existing Files to Modify
- `apps/Server/main.py`: Add category router registration
- `apps/Client/src/App.tsx`: Add route for Categories page
- `apps/Client/src/types/index.ts`: Category interface already exists, may need minor updates

### Reference Files (Read Only)
- `apps/Server/database/schema.sql`: Categories table definition (lines 98-137) - defines the schema structure
- `apps/Server/src/models/user.py`: Example model pattern
- `apps/Server/src/repository/user_repository.py`: Example repository pattern
- `apps/Server/src/core/services/auth_service.py`: Example service pattern
- `apps/Server/src/interface/auth_dto.py`: Example DTO pattern
- `apps/Server/src/adapter/rest/auth_routes.py`: Example routes pattern
- `apps/Server/src/adapter/rest/dependencies.py`: Auth dependency for protected routes
- `apps/Server/src/adapter/rest/rbac_dependencies.py`: Role-based access control
- `apps/Client/src/services/authService.ts`: Example frontend service pattern
- `apps/Client/src/pages/LoginPage.tsx`: Example page with react-hook-form
- `apps/Client/src/contexts/AuthContext.tsx`: Auth context for user access
- `apps/Client/src/components/auth/ProtectedRoute.tsx`: Protected route component
- `app_docs/feature-ed4cef49-backend-jwt-auth-rbac.md`: Backend auth patterns
- `app_docs/feature-db5f36c7-database-schema-tables.md`: Database schema documentation
- `.claude/commands/test_e2e.md`: E2E test runner format
- `.claude/commands/e2e/test_auth_login.md`: Example E2E test structure

### New Files
**Backend:**
- `apps/Server/src/models/category.py`: SQLAlchemy Category model
- `apps/Server/src/interface/category_dto.py`: Pydantic DTOs for category requests/responses
- `apps/Server/src/repository/category_repository.py`: Category data access layer
- `apps/Server/src/core/services/category_service.py`: Category business logic
- `apps/Server/src/adapter/rest/category_routes.py`: Category API endpoints
- `apps/Server/tests/test_category.py`: Category unit tests

**Frontend:**
- `apps/Client/src/services/categoryService.ts`: Category API wrapper
- `apps/Client/src/hooks/useCategories.ts`: Custom hook for category data
- `apps/Client/src/components/forms/TRCategoryForm.tsx`: Category form component
- `apps/Client/src/components/ui/TRCategoryTree.tsx`: Category tree display component
- `apps/Client/src/pages/CategoriesPage.tsx`: Categories management page

**E2E Test:**
- `.claude/commands/e2e/test_category_management.md`: E2E test for category management

## Implementation Plan
### Phase 1: Foundation
1. Create Category model following existing User model pattern
2. Create Category DTOs for request/response validation
3. Create Category repository for data access operations

### Phase 2: Core Implementation
4. Create Category service with business logic
5. Create Category routes with CRUD endpoints
6. Register routes in main.py
7. Create backend unit tests
8. Create frontend category service and hook
9. Create TRCategoryForm component
10. Create TRCategoryTree component

### Phase 3: Integration
11. Create CategoriesPage combining form and tree
12. Add route to App.tsx
13. Create E2E test specification
14. Run validation commands

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Task 1: Create E2E Test Specification
- Read `.claude/commands/test_e2e.md` and `.claude/commands/e2e/test_auth_login.md` to understand the E2E test format
- Create `.claude/commands/e2e/test_category_management.md` with:
  - User Story: As a user, I want to create, view, edit, and delete categories
  - Prerequisites: Backend running, Frontend running, User logged in, Entity exists
  - Test Steps covering:
    1. Navigate to home page, log in with test credentials
    2. Navigate to `/categories` page
    3. Verify categories page loads with form and tree view
    4. Create a new income category (e.g., "Salary")
    5. Verify category appears in tree view
    6. Create a new expense category (e.g., "Food")
    7. Verify category appears in tree view
    8. Create a subcategory (e.g., "Groceries" under "Food")
    9. Verify hierarchical display in tree
    10. Edit a category name
    11. Verify updated name in tree
    12. Delete a category (one without children)
    13. Verify category removed from tree
    14. Take screenshots at key steps
  - Success Criteria: All CRUD operations work correctly, hierarchy displays properly

### Task 2: Create Category Model
- Create `apps/Server/src/models/category.py`
- Import `Base` from `src.config.database`
- Import `Column`, `String`, `UUID`, `Boolean`, `DateTime`, `Text`, `ForeignKey` from SQLAlchemy
- Define `Category` class matching database schema:
  - `id`: UUID primary key with default uuid4
  - `entity_id`: UUID, not null, foreign key to entities
  - `name`: String(255), not null
  - `type`: String(50), not null (income/expense)
  - `parent_id`: UUID, nullable, foreign key to categories(id)
  - `description`: Text, nullable
  - `color`: String(50), nullable
  - `icon`: String(100), nullable
  - `is_active`: Boolean, default True
  - `created_at`: DateTime with timezone, default now
  - `updated_at`: DateTime with timezone, nullable
- Add `__repr__` method for debugging
- Add proper logging as per CLAUDE.md standards

### Task 3: Create Category DTOs
- Create `apps/Server/src/interface/category_dto.py`
- Import `BaseModel`, `Field`, `Optional` from Pydantic
- Import `UUID` from uuid
- Create DTOs:
  - `CategoryCreateDTO`:
    - `entity_id`: UUID (required)
    - `name`: str with min_length=1, max_length=255
    - `type`: str (must be 'income' or 'expense')
    - `parent_id`: Optional[UUID] = None
    - `description`: Optional[str] = None
    - `color`: Optional[str] = None
    - `icon`: Optional[str] = None
  - `CategoryUpdateDTO`:
    - `name`: Optional[str] = None
    - `parent_id`: Optional[UUID] = None
    - `description`: Optional[str] = None
    - `color`: Optional[str] = None
    - `icon`: Optional[str] = None
    - `is_active`: Optional[bool] = None
  - `CategoryResponseDTO`:
    - All fields from model
    - `model_config = {"from_attributes": True}`
  - `CategoryTreeDTO`:
    - Extends CategoryResponseDTO
    - `children`: List[CategoryTreeDTO] = []
    - Use `model_rebuild()` for forward reference

### Task 4: Create Category Repository
- Create `apps/Server/src/repository/category_repository.py`
- Import Session from SQLAlchemy
- Import Category model
- Create `CategoryRepository` class with methods:
  - `create_category(db, entity_id, name, type, parent_id, description, color, icon) -> Category`
  - `get_category_by_id(db, category_id) -> Category | None`
  - `get_categories_by_entity(db, entity_id, include_inactive=False) -> List[Category]`
  - `get_categories_by_parent(db, entity_id, parent_id) -> List[Category]`
  - `get_root_categories(db, entity_id) -> List[Category]` (where parent_id is None)
  - `update_category(db, category) -> Category`
  - `delete_category(db, category_id) -> bool`
  - `has_children(db, category_id) -> bool`
  - `has_transactions(db, category_id) -> bool` (check if category has any transactions)
- Add comprehensive logging for all operations
- Create singleton instance: `category_repository = CategoryRepository()`

### Task 5: Create Category Service
- Create `apps/Server/src/core/services/category_service.py`
- Import category_repository
- Import DTOs
- Create `CategoryService` class with methods:
  - `create_category(db, data: CategoryCreateDTO) -> Category`
    - Validate parent_id belongs to same entity if provided
    - Validate parent has same type (income/expense) if provided
    - Create category via repository
  - `get_category(db, category_id, entity_id) -> Category | None`
    - Validate category belongs to entity
  - `get_categories_for_entity(db, entity_id, include_inactive=False) -> List[Category]`
  - `get_category_tree(db, entity_id) -> List[CategoryTreeDTO]`
    - Build hierarchical tree structure from flat list
    - Return root categories with nested children
  - `update_category(db, category_id, entity_id, data: CategoryUpdateDTO) -> Category`
    - Validate category belongs to entity
    - Validate parent_id if being updated
    - Prevent circular references
  - `delete_category(db, category_id, entity_id) -> bool`
    - Validate category belongs to entity
    - Check if category has children (prevent delete if so, or cascade)
    - Check if category has transactions (prevent delete if so)
- Add comprehensive logging
- Create singleton instance: `category_service = CategoryService()`

### Task 6: Create Category Routes
- Create `apps/Server/src/adapter/rest/category_routes.py`
- Import `APIRouter`, `Depends`, `HTTPException`, `status` from FastAPI
- Import `get_current_user`, `get_db` from dependencies
- Import category_service
- Import DTOs
- Create router: `router = APIRouter(prefix="/api/categories", tags=["Categories"])`
- Create endpoints:
  - `POST /` - Create category
    - Protected route (get_current_user)
    - Validate user has access to entity_id
    - Return CategoryResponseDTO, status 201
  - `GET /entity/{entity_id}` - Get all categories for entity
    - Protected route
    - Validate user has access to entity_id
    - Query param: `include_inactive: bool = False`
    - Return List[CategoryResponseDTO]
  - `GET /entity/{entity_id}/tree` - Get category tree for entity
    - Protected route
    - Validate user has access to entity_id
    - Return List[CategoryTreeDTO]
  - `GET /{category_id}` - Get single category
    - Protected route
    - Query param: `entity_id: UUID` for validation
    - Return CategoryResponseDTO
  - `PUT /{category_id}` - Update category
    - Protected route
    - Query param: `entity_id: UUID` for validation
    - Return CategoryResponseDTO
  - `DELETE /{category_id}` - Delete category
    - Protected route
    - Query param: `entity_id: UUID` for validation
    - Return 204 No Content
- Add comprehensive logging for all endpoints

### Task 7: Register Category Routes in main.py
- Open `apps/Server/main.py`
- Import category_routes: `from src.adapter.rest.category_routes import router as category_router`
- Add router registration: `app.include_router(category_router)`
- Add logging for route registration

### Task 8: Create Backend Unit Tests
- Create `apps/Server/tests/test_category.py`
- Import pytest, AsyncClient, patch
- Follow test_auth.py patterns
- Test cases:
  - Create category success
  - Create category with parent
  - Create category validation errors (missing name, invalid type)
  - Get categories by entity
  - Get category tree structure
  - Update category
  - Update category parent_id
  - Delete category success
  - Delete category with children (should fail)
  - Unauthorized access (no token)
  - Access category from wrong entity (should fail)

### Task 9: Create Frontend Category Service
- Create `apps/Client/src/services/categoryService.ts`
- Import `apiClient` from `@/api/clients`
- Import Category type from `@/types`
- Create service object with methods:
  - `getCategories(entityId: string, includeInactive?: boolean): Promise<Category[]>`
  - `getCategoryTree(entityId: string): Promise<CategoryTree[]>`
  - `getCategory(categoryId: string, entityId: string): Promise<Category>`
  - `createCategory(data: CategoryCreateInput): Promise<Category>`
  - `updateCategory(categoryId: string, entityId: string, data: CategoryUpdateInput): Promise<Category>`
  - `deleteCategory(categoryId: string, entityId: string): Promise<void>`
- Add comprehensive logging per CLAUDE.md standards

### Task 10: Update Frontend Types
- Open `apps/Client/src/types/index.ts`
- Add or update Category-related types:
  - `CategoryType = 'income' | 'expense'`
  - `Category` interface with all fields
  - `CategoryTree` interface extending Category with children
  - `CategoryCreateInput` interface
  - `CategoryUpdateInput` interface

### Task 11: Create useCategories Hook
- Create `apps/Client/src/hooks/useCategories.ts`
- Import useState, useEffect, useCallback from React
- Import categoryService
- Import Category, CategoryTree types
- Create hook that:
  - Takes entityId as parameter
  - Manages categories state
  - Manages categoryTree state
  - Manages loading state
  - Manages error state
  - Provides fetchCategories function
  - Provides fetchCategoryTree function
  - Provides createCategory function
  - Provides updateCategory function
  - Provides deleteCategory function
  - Auto-fetches on entityId change
- Return state and functions

### Task 12: Create TRCategoryForm Component
- Create `apps/Client/src/components/forms/TRCategoryForm.tsx`
- Import react-hook-form: `useForm`
- Import MUI: TextField, Button, Box, MenuItem, Select, FormControl, InputLabel, FormHelperText
- Import Category types
- Props interface:
  - `onSubmit: (data: CategoryCreateInput | CategoryUpdateInput) => Promise<void>`
  - `category?: Category` (for edit mode)
  - `parentCategories: Category[]` (for parent selection dropdown)
  - `entityId: string`
  - `onCancel?: () => void`
- Create form with:
  - Name field (required, max 255 chars)
  - Type select (income/expense) - disabled in edit mode
  - Parent category select (optional, filtered by type)
  - Description field (optional, multiline)
  - Color field (optional)
  - Icon field (optional)
  - Submit button with loading state
  - Cancel button if onCancel provided
- Use react-hook-form validation
- Add proper logging

### Task 13: Create TRCategoryTree Component
- Create `apps/Client/src/components/ui/TRCategoryTree.tsx`
- Import MUI: List, ListItem, ListItemText, ListItemIcon, Collapse, IconButton, Typography, Box
- Import MUI icons: ExpandMore, ExpandLess, Edit, Delete, Folder, FolderOpen
- Import CategoryTree type
- Props interface:
  - `categories: CategoryTree[]`
  - `onEdit?: (category: CategoryTree) => void`
  - `onDelete?: (category: CategoryTree) => void`
  - `selectedId?: string`
- Create recursive tree component:
  - Display category name with type indicator (income/expense color)
  - Expand/collapse button for categories with children
  - Indent children visually
  - Edit and Delete action buttons (if handlers provided)
  - Highlight selected category
- Add proper logging

### Task 14: Create CategoriesPage
- Create `apps/Client/src/pages/CategoriesPage.tsx`
- Import React hooks
- Import MUI: Container, Grid, Paper, Typography, Button, Dialog, DialogTitle, DialogContent, DialogActions, Snackbar, Alert
- Import TRCategoryForm, TRCategoryTree
- Import useCategories hook
- Import useAuth hook (to verify authenticated)
- Create page with:
  - Page title "Categories"
  - Two-column layout (form on left, tree on right) or stacked on mobile
  - "Add Category" button opens form dialog
  - Category tree displays hierarchy
  - Edit action opens form dialog with category data
  - Delete action shows confirmation dialog
  - Success/error snackbar notifications
  - Loading states
  - Empty state message when no categories
- Note: For now, use a hardcoded entityId or get from URL params until EntityContext is implemented
- Add proper logging

### Task 15: Add Route to App.tsx
- Open `apps/Client/src/App.tsx`
- Import CategoriesPage from `@/pages/CategoriesPage`
- Import ProtectedRoute if not already imported
- Add route: `<Route path="/categories" element={<ProtectedRoute><CategoriesPage /></ProtectedRoute>} />`
- Optionally add route with entityId param: `<Route path="/categories/:entityId" element={<ProtectedRoute><CategoriesPage /></ProtectedRoute>} />`

### Task 16: Run Validation Commands
- Run all validation commands listed in the Validation Commands section
- Fix any errors that arise
- Ensure all tests pass
- Ensure build completes successfully

## Testing Strategy
### Unit Tests
- CategoryRepository: Test CRUD operations with mock database
- CategoryService: Test business logic including hierarchy validation, circular reference prevention
- Category Routes: Test endpoint responses, authentication, authorization
- TRCategoryForm: Test form validation, submit handling
- TRCategoryTree: Test rendering, expand/collapse, action handlers

### Edge Cases
- Creating category with non-existent parent_id
- Creating category with parent from different entity
- Creating category with parent of different type (income parent for expense child)
- Updating category to create circular reference (A → B → A)
- Deleting category with children
- Deleting category with transactions
- Accessing category from wrong entity
- Empty category name or very long name
- Special characters in category name

## Acceptance Criteria
- [ ] User can navigate to Categories page
- [ ] User can create an income category
- [ ] User can create an expense category
- [ ] User can create a subcategory with parent
- [ ] Categories display in hierarchical tree view
- [ ] User can edit category name and properties
- [ ] User can delete category without children or transactions
- [ ] Cannot delete category with children (shows error)
- [ ] Cannot delete category with transactions (shows error)
- [ ] Categories are filtered by entity
- [ ] All routes are protected by authentication
- [ ] Form validates required fields
- [ ] All TypeScript types are correct (no `any`)
- [ ] Backend tests pass
- [ ] Frontend build completes without errors

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && uv run pytest tests/test_category.py -v` - Run category-specific tests
- `cd apps/Server && uv run pytest` - Run all Server tests to validate zero regressions
- `cd apps/Client && npm run tsc` - Run Client type check to validate TypeScript types
- `cd apps/Client && npm run lint` - Run linting to check code quality
- `cd apps/Client && npm run build` - Run Client build to validate the feature works with zero regressions
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_category_management.md` to validate category management flow E2E

## Notes
- The categories table already exists in the database schema with full hierarchy support (parent_id, type, entity_id)
- Categories are entity-specific - each entity has its own set of categories
- The Category type must match parent Category type (income parent can only have income children)
- Consider adding default categories (Food, Transportation, Utilities, etc.) when an entity is created - this can be a future enhancement
- The frontend currently doesn't have EntityContext - for now, the entityId can be passed via URL params or hardcoded for testing. Entity management is being implemented in parallel (FT-007)
- Parent selection dropdown should only show categories of the same type to prevent type mismatch
- Categories with transactions cannot be deleted to maintain data integrity - consider adding a "soft delete" (is_active=False) option
- The color and icon fields are optional and can be used for visual distinction in the UI - can be enhanced later with color picker and icon selector
