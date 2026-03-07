# Standardize Delete Endpoint RBAC Enforcement

**ADW ID:** 957bac6a
**Date:** 2026-03-07
**Specification:** specs/patch/patch-adw-957bac6a-standardize-delete-rbac-enforcement.md

## Overview

Standardized RBAC enforcement on delete endpoints across four route files (person, recipe, resource, restaurant) by replacing `get_current_user` with `require_roles(["admin", "manager"])`. This resolves inconsistency where these endpoints relied solely on service-layer PermissionError checks while all other delete endpoints enforced role gating at the route level.

## What Was Built

- Route-level RBAC enforcement on delete endpoints for person, recipe, resource, and restaurant routes
- Updated docstrings to document the admin/manager role requirement
- Updated test mocks to use `role="admin"` for delete test cases

## Technical Implementation

### Files Modified

- `apps/Server/src/adapter/rest/person_routes.py`: Added `require_roles` import; replaced `get_current_user` with `require_roles(["admin", "manager"])` on `delete_person` endpoint
- `apps/Server/src/adapter/rest/recipe_routes.py`: Same change on `delete_recipe` endpoint
- `apps/Server/src/adapter/rest/resource_routes.py`: Same change on `delete_resource` endpoint
- `apps/Server/src/adapter/rest/restaurant_routes.py`: Same change on `delete_restaurant` endpoint
- `apps/Server/tests/test_person_api.py`: Updated `test_delete_person_success` mock user to `role="admin"`
- `apps/Server/tests/test_recipe_api.py`: Updated `test_delete_recipe_success` and `test_delete_recipe_not_found` mock users to `role="admin"`
- `apps/Server/tests/test_resource_api.py`: Updated `test_delete_resource_success` mock user to `role="admin"`
- `apps/Server/tests/test_restaurant_api.py`: Updated `test_delete_restaurant_success` mock user to `role="admin"`

### Key Changes

- `require_roles(["admin", "manager"])` internally calls `get_current_user`, so service-layer checks remain as defense-in-depth
- Only delete endpoints were changed; create, list, get, and update endpoints retain `get_current_user`
- This is a purely restrictive change -- it tightens access control, never loosens it
- All four route files now match the pattern used by transaction, budget, recurring_template, meeting_record, prospect, and pipeline_stage delete endpoints

## How to Use

1. Delete requests to `/api/persons/{id}`, `/api/recipes/{id}`, `/api/resources/{id}`, and `/api/restaurants/{id}` now require the authenticated user to have `admin` or `manager` role
2. Users with `user` or `viewer` roles will receive a 403 Forbidden response when attempting to delete these resources
3. No frontend changes are needed -- the existing RoleProtectedRoute guards already restrict UI delete actions to admin/manager roles

## Configuration

No new configuration required. The `require_roles` dependency is imported from `src.adapter.rest.rbac_dependencies`, which already exists in the codebase.

## Testing

- All backend tests pass with the updated mock users using `role="admin"`
- Existing service-layer authorization tests remain valid as defense-in-depth

## Notes

- This patch addresses Issue #192 (Inconsistent RBAC enforcement on delete endpoints)
- The `require_roles` dependency returns the current user dict, so no downstream code changes were needed beyond the dependency swap
