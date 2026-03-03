# Feature: Person Management Page

## Metadata
issue_number: `87`
adw_id: `de82eb81`
issue_json: `{"number":87,"title":"[RestaurantOS] Wave 4: Person Management Page"}`

## Feature Description
Build a full CRUD frontend page for managing persons (employees, suppliers, owners) within a RestaurantOS restaurant. The page provides a data table with search by name and filter by person type, plus dialog-based forms for creating and editing persons. All UI text is in Spanish (Colombian). The backend API already exists (`/api/persons`), so this feature is purely frontend: types, service, hook, form component, and page component.

## User Story
As a restaurant manager
I want to list, create, edit, and delete persons associated with my restaurant
So that I can maintain an up-to-date registry of employees, suppliers, and owners

## Problem Statement
The RestaurantOS Persons page (`/poc/restaurant-os/persons`) currently shows a placeholder "Próximamente" message. Restaurant managers need a fully functional interface to manage their staff, suppliers, and owners with search and filter capabilities.

## Solution Statement
Replace the placeholder `RestaurantOSPersonsPage` with a complete CRUD page that uses the existing backend Person API. Create a person service, custom hook, and form component following established codebase patterns (restaurantService, useProspects, TRProspectForm). The page will include a data table, type filter dropdown, name search, and MUI dialogs for create/edit/delete operations.

## Relevant Files
Use these files to implement the feature:

**Existing files to modify:**
- `apps/Client/src/pages/restaurantos/RestaurantOSPersonsPage.tsx` — Replace placeholder with full CRUD page
- `apps/Client/src/types/index.ts` — Add re-export for person types

**Reference files (read for patterns, do not modify):**
- `apps/Client/src/services/restaurantService.ts` — Service pattern with try/catch and console logging
- `apps/Client/src/hooks/useProspects.ts` — Custom CRUD hook pattern with useState/useCallback/useEffect
- `apps/Client/src/components/forms/TRProspectForm.tsx` — Form pattern with react-hook-form, Controller for selects, create/edit modes
- `apps/Client/src/pages/TransactionsPage.tsx` — Table-based CRUD page pattern with dialogs, filters, loading/empty states
- `apps/Client/src/contexts/RestaurantContext.tsx` — RestaurantContext providing currentRestaurant
- `apps/Client/src/hooks/useRestaurant.ts` — useRestaurant hook
- `apps/Client/src/pages/restaurantos/TRNoRestaurantPrompt.tsx` — No-restaurant guard component
- `apps/Client/src/api/clients/index.ts` — apiClient with JWT interceptor
- `apps/Client/src/App.tsx` — Route already registered, no changes needed
- `apps/Server/src/interface/person_dto.py` — Backend DTOs defining field constraints
- `apps/Server/src/adapter/rest/person_routes.py` — Backend API endpoints for reference

**Conditional documentation files (read before implementation):**
- `app_docs/feature-14633eae-person-entity-crud-backend.md` — Person backend API documentation
- `app_docs/feature-342b3948-restaurant-selector-multitenant-navigation.md` — RestaurantContext and navigation documentation

**E2E test reference files (read for E2E test creation):**
- `.claude/commands/test_e2e.md` — E2E test runner instructions
- `.claude/commands/e2e/test_entity_management.md` — E2E test format for CRUD page
- `.claude/commands/e2e/test_transaction_crud.md` — E2E test format for table CRUD flow

### New Files
- `apps/Client/src/types/person.ts` — Person, PersonCreate, PersonUpdate, PersonFilters interfaces and PersonType type
- `apps/Client/src/services/personService.ts` — Person API service with getAll, create, update, delete methods
- `apps/Client/src/hooks/usePersons.ts` — Custom hook for person CRUD state management
- `apps/Client/src/components/forms/TRPersonForm.tsx` — react-hook-form person form with create/edit modes
- `.claude/commands/e2e/test_person_management.md` — E2E test specification for person management page

## Implementation Plan
### Phase 1: Foundation
Create the TypeScript types and API service layer that the UI components will depend on. Define the Person interface matching the backend PersonResponseDTO, plus PersonCreate, PersonUpdate, and PersonFilters interfaces. Create the personService with methods mapping to each backend endpoint.

### Phase 2: Core Implementation
Build the usePersons custom hook following the useProspects pattern — managing persons state, loading, errors, and CRUD operations scoped to a restaurantId. Then build the TRPersonForm component with react-hook-form, supporting both create and edit modes with Spanish labels. Finally, replace the RestaurantOSPersonsPage placeholder with a full CRUD page featuring a data table, search, type filter, and dialog-based forms.

### Phase 3: Integration
The route `/poc/restaurant-os/persons` is already registered in App.tsx pointing to RestaurantOSPersonsPage. No routing changes needed. Add the person types re-export to `types/index.ts`. Create the E2E test specification. Run all validation commands to confirm zero regressions.

## Step by Step Tasks

### Step 1: Create E2E Test Specification
- Read `.claude/commands/test_e2e.md` to understand the E2E test runner
- Read `.claude/commands/e2e/test_entity_management.md` and `.claude/commands/e2e/test_transaction_crud.md` for CRUD test patterns
- Create `.claude/commands/e2e/test_person_management.md` with the following test flow:
  - Prerequisites: backend at http://localhost:8000, frontend at http://localhost:5173, logged-in user, at least one restaurant created
  - Navigate to `/poc/restaurant-os/persons`
  - Verify page loads with "Personas" heading, current restaurant name, "Agregar Persona" button, and empty state
  - Click "Agregar Persona", verify form dialog with fields: Nombre, Rol, Tipo, Correo Electrónico, WhatsApp
  - Test form validation: submit empty form, verify "Nombre" and "Rol" required errors
  - Fill form: name "Carlos García", role "Chef", type "Empleado", email "carlos@test.com", whatsapp "+573001234567"
  - Submit and verify person appears in table with correct data
  - Create a second person: name "María López", role "Mesera", type "Empleado"
  - Test search: type "Carlos" in search field, verify only Carlos appears
  - Test filter: select "Empleado" from type filter, verify both persons show
  - Test edit: click edit on Carlos, verify form pre-populated, change role to "Chef Principal", submit, verify updated in table
  - Test delete: click delete on María, verify confirmation dialog "¿Está seguro que desea eliminar esta persona?", confirm, verify removed from table
  - Success criteria: all CRUD operations work, Spanish labels displayed, search and filter functional, console shows INFO logs

### Step 2: Read Conditional Documentation
- Read `app_docs/feature-14633eae-person-entity-crud-backend.md` for backend API details
- Read `app_docs/feature-342b3948-restaurant-selector-multitenant-navigation.md` for RestaurantContext patterns

### Step 3: Create Person Types
- Create `apps/Client/src/types/person.ts` with:
  - `PersonType` union type: `'employee' | 'supplier' | 'owner'`
  - `Person` interface: `id` (string), `restaurant_id` (string), `name` (string), `role` (string), `email` (string | null, optional), `whatsapp` (string | null, optional), `type` (PersonType), `created_at` (string), `updated_at` (string | null, optional)
  - `PersonCreate` interface: `restaurant_id` (string), `name` (string), `role` (string), `email` (string, optional), `whatsapp` (string, optional), `type` (PersonType, optional)
  - `PersonUpdate` interface: `name` (string, optional), `role` (string, optional), `email` (string, optional), `whatsapp` (string, optional), `type` (PersonType, optional)
  - `PersonFilters` interface: `type` (PersonType, optional)
- Update `apps/Client/src/types/index.ts` to re-export person types: `export type { Person, PersonType, PersonCreate, PersonUpdate, PersonFilters } from './person'`

### Step 4: Create Person Service
- Read `apps/Client/src/services/restaurantService.ts` for the service pattern
- Create `apps/Client/src/services/personService.ts` following the restaurantService pattern:
  - Import `apiClient` from `@/api/clients`
  - Import person types from `@/types/person`
  - `getAll(restaurantId: string, type?: PersonType): Promise<Person[]>` — GET `/persons?restaurant_id={restaurantId}&type={type}`, with console.log INFO/ERROR
  - `create(data: PersonCreate): Promise<Person>` — POST `/persons`
  - `update(id: string, data: PersonUpdate): Promise<Person>` — PUT `/persons/{id}`
  - `delete(id: string): Promise<void>` — DELETE `/persons/{id}`
  - All methods wrapped in try/catch with `console.log('INFO [PersonService]: ...')` and `console.error('ERROR [PersonService]: ...')`
  - Export as `personService` object and `default`

### Step 5: Create usePersons Hook
- Read `apps/Client/src/hooks/useProspects.ts` for the hook pattern
- Create `apps/Client/src/hooks/usePersons.ts`:
  - Accept `restaurantId: string | null` parameter
  - State: `persons` (Person[]), `isLoading` (boolean), `error` (string | null), `filters` (PersonFilters)
  - `fetchPersons` — useCallback, guards on `!restaurantId`, calls `personService.getAll(restaurantId, filters.type)`, with INFO/ERROR logging
  - `createPerson(data: PersonCreate)` — useCallback, calls `personService.create(data)`, then `fetchPersons()` to refresh
  - `updatePerson(id: string, data: PersonUpdate)` — useCallback, calls `personService.update(id, data)`, then `fetchPersons()` to refresh
  - `deletePerson(id: string)` — useCallback, calls `personService.delete(id)`, then `fetchPersons()` to refresh
  - `setFilters` — to update type filter
  - useEffect to auto-fetch when `restaurantId` or `filters` change
  - Return `UsePersonsResult` interface with all state and methods
  - Export as named `usePersons` and default

### Step 6: Create TRPersonForm Component
- Read `apps/Client/src/components/forms/TRProspectForm.tsx` for the form pattern
- Create `apps/Client/src/components/forms/TRPersonForm.tsx`:
  - Props interface `TRPersonFormProps`: `onSubmit` (async function), `initialData` (Person, optional for edit mode), `restaurantId` (string), `onCancel` (function), `isSubmitting` (boolean, optional)
  - Use `useForm` with `defaultValues` from `initialData` or empty strings
  - Use `useEffect` to `reset` form when `initialData` changes
  - Fields (all Spanish labels):
    - `name`: TextField, required, max 255, label "Nombre", register with `{ required: 'El nombre es obligatorio', maxLength: { value: 255, message: 'Máximo 255 caracteres' } }`
    - `role`: TextField, required, label "Rol", register with `{ required: 'El rol es obligatorio' }`
    - `type`: Controller + Select, required, label "Tipo", options: `employee` → "Empleado", `supplier` → "Proveedor", `owner` → "Dueño", default "employee"
    - `email`: TextField, optional, label "Correo Electrónico", register with email pattern validation `{ pattern: { value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/, message: 'Formato de correo inválido' } }`
    - `whatsapp`: TextField, optional, label "WhatsApp"
  - Submit handler: builds PersonCreate (with `restaurant_id`) or PersonUpdate based on `isEditMode`
  - Buttons: "Cancelar" (outlined, type button) and "Agregar Persona" / "Actualizar Persona" (contained, type submit)
  - Loading state: disable fields and show CircularProgress in submit button when `isSubmitting`
  - Console.log on submit: `INFO [TRPersonForm]: Submitting person form`

### Step 7: Build RestaurantOSPersonsPage
- Read `apps/Client/src/pages/TransactionsPage.tsx` for the table-based CRUD page pattern
- Read `apps/Client/src/pages/restaurantos/RestaurantOSPersonsPage.tsx` (current placeholder)
- Replace the placeholder with a full CRUD page:
  - Use `useRestaurant()` for `currentRestaurant`, `restaurants`, `isLoading`
  - Use `usePersons(currentRestaurant?.id ?? null)` for person data and operations
  - State: `isAddDialogOpen`, `isEditDialogOpen`, `isDeleteDialogOpen`, `selectedPerson`, `isSubmitting`, `searchQuery` (string)
  - Guards:
    - Loading: show `CircularProgress` with "Cargando..."
    - No restaurants: show `<TRNoRestaurantPrompt />`
  - Header: "Personas" (h4), current restaurant name (h6), "Agregar Persona" button (contained, PersonAdd icon)
  - Error display: `<Alert severity="error">` when `error` is set
  - Filters row:
    - Search TextField with label "Buscar por nombre", value bound to `searchQuery` state, onChange updates `searchQuery`
    - Type filter: Select with label "Filtrar por tipo", options: "Todos" (empty value), "Empleado" (employee), "Proveedor" (supplier), "Dueño" (owner), onChange calls `setFilters({ type: value || undefined })`
  - Data table (`<Table>` / `<TableContainer>`):
    - Headers: Nombre, Rol, Tipo, Correo Electrónico, WhatsApp, Acciones
    - Rows: filtered by `searchQuery` (case-insensitive name match), display person data
    - Type display: map `employee` → "Empleado", `supplier` → "Proveedor", `owner` → "Dueño"
    - Actions column: Edit (IconButton with EditIcon) and Delete (IconButton with DeleteIcon)
  - Empty state: "No se encontraron personas" when filtered list is empty
  - Add Dialog: MUI Dialog with title "Agregar Persona", `<TRPersonForm>` with `restaurantId`, `onSubmit` calls `createPerson` then closes dialog
  - Edit Dialog: MUI Dialog with title "Editar Persona", `<TRPersonForm>` with `initialData={selectedPerson}`, `onSubmit` calls `updatePerson` then closes dialog
  - Delete Dialog: MUI Dialog with title "Eliminar Persona", body text "¿Está seguro que desea eliminar esta persona?", "Cancelar" and "Eliminar" buttons, confirm calls `deletePerson(selectedPerson.id)` then closes
  - Console.log on all operations: `INFO [RestaurantOSPersonsPage]: ...`

### Step 8: Run Validation Commands
- Run `cd apps/Client && npx tsc --noEmit` to validate TypeScript compilation with zero errors
- Run `cd apps/Client && npm run build` to validate production build succeeds
- Run `cd apps/Server && python -m pytest tests/ -x` to verify no backend regressions
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_person_management.md` E2E test to validate the feature end-to-end

## Testing Strategy
### Unit Tests
No dedicated unit test files are required for this feature — the existing codebase convention for frontend CRUD pages relies on E2E tests for validation rather than unit tests. The TypeScript compiler (`tsc --noEmit`) validates type correctness across all new files.

### Edge Cases
- No restaurant selected: page shows `TRNoRestaurantPrompt`
- Empty persons list: page shows "No se encontraron personas" message
- Search with no results: filtered table shows empty state
- Email validation: invalid email format shows "Formato de correo inválido"
- Required fields empty: submitting without name/role shows required error messages
- API error on CRUD operations: error state shown via Alert component
- Long person names: max 255 chars enforced by form validation
- Delete confirmation: cancel should not delete, confirm should remove and refresh

## Acceptance Criteria
- Person Management page loads at `/poc/restaurant-os/persons` with "Personas" heading
- Page shows current restaurant name from RestaurantContext
- No-restaurant state shows `TRNoRestaurantPrompt` component
- Data table displays persons with columns: Nombre, Rol, Tipo, Correo Electrónico, WhatsApp, Acciones
- "Agregar Persona" button opens a dialog with TRPersonForm
- Form fields: Nombre (required), Rol (required), Tipo (select: Empleado/Proveedor/Dueño), Correo Electrónico (optional, email validated), WhatsApp (optional)
- Form validation prevents submission with missing required fields
- Creating a person adds it to the table
- Edit button opens form pre-populated with person data
- Updating a person reflects changes in the table
- Delete button shows confirmation dialog with "¿Está seguro que desea eliminar esta persona?"
- Confirming delete removes person from table
- Search by name filters the table (case-insensitive)
- Type filter dropdown filters by Todos/Empleado/Proveedor/Dueño
- All UI labels are in Spanish (Colombian)
- Console shows INFO log messages for all operations
- TypeScript compiles with zero errors
- Production build succeeds

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Client && npx tsc --noEmit` — Run Client type check to validate zero TypeScript errors
- `cd apps/Client && npm run build` — Run Client production build to validate the feature compiles correctly
- `cd apps/Server && python -m pytest tests/ -x` — Run Server tests to validate no backend regressions
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_person_management.md` E2E test to validate this functionality works end-to-end

## Notes
- The backend Person API is fully implemented (ROS-002). All 6 endpoints are operational: POST/GET/GET(search)/GET(by-id)/PUT/DELETE on `/api/persons`.
- The route `/poc/restaurant-os/persons` is already registered in `App.tsx` with the import for `RestaurantOSPersonsPage`. No routing changes are needed.
- The `TRNoRestaurantPrompt` component already exists and is imported in the current placeholder page.
- Person type values stored in the database are lowercase English (`employee`, `supplier`, `owner`) but displayed in Spanish on the frontend (`Empleado`, `Proveedor`, `Dueño`).
- The search functionality is implemented client-side by filtering the persons array. For large datasets, the backend search endpoint (`GET /persons/search?query=`) could be used instead, but client-side filtering is sufficient for typical restaurant staff sizes.
- This feature runs in parallel with ROS-009, ROS-011, ROS-012, ROS-013. No conflicts expected since each page is in its own file.
