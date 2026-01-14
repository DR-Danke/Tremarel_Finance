# Bug Fix: WSL2 Backend Binding and Entity Context for Categories

**ADW ID:** NA
**Date:** 2026-01-14
**Specification:** specs/issue-NA-adw-NA-sdlc_planner-fix-wsl2-backend-binding.md

## Overview

This bug fix addresses two issues that caused "Cannot connect to server" errors when creating categories:

1. **WSL2 Backend Binding**: The backend uvicorn server was binding to `127.0.0.1` which is not accessible from Windows host in WSL2 environments
2. **Hardcoded Entity ID**: CategoriesPage was using a hardcoded default entity ID that didn't exist in the database, causing foreign key violations

## What Was Fixed

### Issue 1: WSL2 Backend Network Binding

**Problem:** In WSL2 environments, the backend bound to `localhost:8000` (127.0.0.1) is only accessible from within WSL2. The frontend running on Windows (via WSL interop with Windows Node.js) cannot reach this address.

**Solution:** Start the backend with `--host 0.0.0.0` flag so uvicorn binds to all network interfaces.

**Files Modified:**
- `CLAUDE.md`: Updated backend development command to include `--host 0.0.0.0`
- `.claude/commands/start.md`: Updated /start command to start both frontend and backend with correct host bindings

### Issue 2: Hardcoded Entity ID in CategoriesPage

**Problem:** CategoriesPage used a hardcoded `DEFAULT_ENTITY_ID` that didn't exist in the database, causing `ForeignKeyViolation` errors when creating categories.

**Solution:** Updated CategoriesPage to use EntityContext to get the current user's actual entity.

**Files Modified:**
- `apps/Client/src/pages/CategoriesPage.tsx`:
  - Replaced hardcoded `DEFAULT_ENTITY_ID` with `useEntity()` hook
  - Added loading state while entity context loads
  - Added "No Entity Selected" message with link to create/manage entities
  - Added current entity info banner showing which entity is being managed

## Technical Implementation

### Backend Startup Command

```bash
# Old (WSL2 incompatible)
python -m uvicorn main:app --reload --port 8000

# New (WSL2 compatible)
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### CategoriesPage Entity Integration

```typescript
// Old - Hardcoded entity ID
const DEFAULT_ENTITY_ID = 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'
const { entityId: urlEntityId } = useParams<{ entityId?: string }>()
const entityId = urlEntityId || DEFAULT_ENTITY_ID

// New - Using EntityContext
const { currentEntity, entities, isLoading: entityLoading } = useEntity()
const entityId = currentEntity?.id || null

// Early return if no entity selected
if (!currentEntity) {
  return (
    <Container>
      <Typography>No Entity Selected</Typography>
      <Button component={Link} to="/entities">
        {entities.length === 0 ? 'Create Entity' : 'Manage Entities'}
      </Button>
    </Container>
  )
}
```

## How to Use

### Starting the Application in WSL2

1. Start backend with host binding:
   ```bash
   cd apps/Server && .venv/bin/python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. Start frontend with host binding:
   ```bash
   cd apps/Client && npm run dev -- --host 0.0.0.0
   ```

3. Or use the `/start` command which handles both automatically

### Using Categories Page

1. Log in to the application
2. Ensure you have at least one entity (create one via Entities page if needed)
3. Select an entity from the entity selector
4. Navigate to Categories page
5. The page will show categories for the currently selected entity

## Configuration

No additional configuration required beyond the standard environment variables.

## Testing

### Verify Backend Binding
```bash
# Should show *:8000 (bound to all interfaces)
lsof -i :8000
```

### Verify Category Creation
1. Log in and select an entity
2. Navigate to /categories
3. Click "Add Category"
4. Fill in category details
5. Verify success message and category appears in tree

## Root Cause Analysis

### WSL2 Networking
- WSL2 runs in a lightweight VM with its own network namespace
- `localhost` inside WSL2 resolves to WSL2's loopback, not Windows' loopback
- Services must bind to `0.0.0.0` to be accessible from Windows host

### Entity Context Pattern
- All entity-specific pages should use `useEntity()` hook to get current entity
- Never hardcode entity IDs - they vary per user/environment
- Always handle the "no entity selected" state gracefully

## Notes

- This fix applies to all WSL2 development environments
- Production deployments (Render) are not affected as they use proper host binding
- The pattern of using EntityContext should be followed by all entity-specific pages (Transactions, Budgets, Reports, etc.)
- When debugging "Cannot connect to server" errors, check:
  1. Is the backend running?
  2. Is the backend bound to `0.0.0.0` (not just `127.0.0.1`)?
  3. Is the correct entity ID being used?
