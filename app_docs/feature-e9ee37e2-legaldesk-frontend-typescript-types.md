# Legal Desk Frontend TypeScript Types & Maps

**ADW ID:** e9ee37e2
**Date:** 2026-03-04
**Specification:** specs/issue-142-adw-e9ee37e2-sdlc_planner-legaldesk-frontend-typescript-types-maps.md

## Overview

Comprehensive TypeScript type definitions for the Legal Desk module frontend. Defines 14 string literal union types matching all database enums, ~25 interfaces matching the 11 `ld_*` database tables, CRUD operation interfaces, and label/color constant maps for UI rendering. This is a pure foundation/types layer with no runtime logic.

## What Was Built

- 14 string literal union types covering all Legal Desk database enums (CaseStatus, CaseType, LegalDomain, CaseComplexity, CasePriority, etc.)
- 11 entity interfaces matching `ld_*` database tables (LdClient, LdSpecialist, LdCase, LdCaseSpecialist, LdCaseDeliverable, LdCaseMessage, LdCaseDocument, LdPricingHistory, LdSpecialistScore, LdSpecialistExpertise, LdSpecialistJurisdiction)
- 2 detail/extended interfaces (LdCaseDetail, LdSpecialistDetail) with nested relations
- 16 create/update interfaces for CRUD operations
- 3 filter interfaces and 3 list response interfaces
- 2 dashboard/specialized interfaces (LdDashboardStats, LdSpecialistCandidate)
- 19 label and color constant maps for UI rendering (status badges, priority chips, domain labels)
- Central re-export from `types/index.ts`

## Technical Implementation

### Files Modified

- `apps/Client/src/types/legaldesk.ts` (new, 601 lines): Complete Legal Desk types file with all unions, interfaces, and constant maps
- `apps/Client/src/types/index.ts` (+77 lines): Re-exports all Legal Desk types and constants using `export type {}` for types and `export {}` for constants

### Key Changes

- All entity interfaces use `number` for IDs (matching PostgreSQL SERIAL primary keys), not UUID strings — this differs from the core Finance Tracker entities
- SQL column names are matched exactly (e.g., `budget` not `client_budget`, `margin_percentage` not `faroo_margin_pct`)
- `case_type` on LdCase is optional (`?:`) since it is not a column in the SQL table but included for forward compatibility
- `ai_classification` uses `Record<string, unknown> | null` instead of `any` to maintain type safety for the JSONB field
- All Ld-prefixed names avoid collision with existing Finance Tracker types
- Color maps use MUI-palette-inspired hex codes with semantic meaning (green for success, red for urgent/critical, grey for inactive/archived)

## How to Use

1. **Import types** from the central index or directly from `legaldesk.ts`:
   ```typescript
   import type { LdCase, LdCaseCreate, CaseStatus } from '@/types';
   import { CASE_STATUS_LABELS, CASE_STATUS_COLORS } from '@/types';
   ```

2. **Use union types** for type-safe status/domain/priority values:
   ```typescript
   const status: CaseStatus = 'active';
   const domain: LegalDomain = 'corporate';
   ```

3. **Use label/color maps** for UI rendering:
   ```typescript
   <Chip label={CASE_STATUS_LABELS[case.status]} sx={{ bgcolor: CASE_STATUS_COLORS[case.status] }} />
   <Chip label={LEGAL_DOMAIN_LABELS[case.legal_domain]} sx={{ bgcolor: LEGAL_DOMAIN_COLORS[case.legal_domain] }} />
   ```

4. **Use create/update interfaces** for form data and API payloads:
   ```typescript
   const newCase: LdCaseCreate = { title: 'IP Review', client_id: 1, legal_domain: 'ip' };
   const updates: LdCaseUpdate = { status: 'active', priority: 'high' };
   ```

5. **Use filter interfaces** for query parameters:
   ```typescript
   const filters: LdCaseFilters = { status: 'active', legal_domain: 'corporate' };
   ```

## Configuration

No configuration required. This is a pure TypeScript types/constants file with no runtime dependencies.

## Testing

- Run `cd apps/Client && npx tsc --noEmit` to validate all types compile with zero errors
- Run `cd apps/Client && npm run build` to verify no build regressions
- TypeScript's `Record` type enforces that all label/color maps cover every member of their respective union type at compile time

## Notes

- This is a foundational layer for the Legal Desk module. Wave 5 (services/hooks) and Wave 6 (UI components) will consume these types.
- No runtime code, API calls, or UI components are included — validation is purely compile-time.
- The `LdCaseDetail` and `LdSpecialistDetail` interfaces use `extends` for clean composition with nested arrays of related entities.
- All 19 constant maps are typed with `Record<UnionType, string>` ensuring compile-time completeness checks.
