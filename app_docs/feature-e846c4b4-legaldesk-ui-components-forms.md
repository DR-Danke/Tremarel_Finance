# Legal Desk UI Components & Forms

**ADW ID:** e846c4b4
**Date:** 2026-03-04
**Specification:** specs/issue-151-adw-e846c4b4-sdlc_planner-ld-ui-components-forms.md

## Overview

Six reusable UI components and three react-hook-form based forms for the Legal Desk module. These are the foundational building blocks used by all Legal Desk pages (LD-015, LD-016), covering status/priority/domain badges, specialist score display, pricing timeline, deliverable checklist, and CRUD forms for cases, specialists, and clients.

## What Was Built

- **TRCaseStatusBadge** — Colored MUI Chip displaying case status label
- **TRCasePriorityBadge** — Colored MUI Chip displaying case priority (low/medium/high/urgent)
- **TRLegalDomainBadge** — Colored MUI Chip displaying legal domain area
- **TRSpecialistScoreDisplay** — MUI Rating (5-star) with optional numeric score
- **TRPricingTimeline** — Vertical MUI Stepper showing pricing negotiation history
- **TRDeliverableChecklist** — MUI List of deliverables with status chips and optional status change dropdown
- **TRLegalCaseForm** — Full case create/edit form with client Autocomplete and domain/type/priority selects
- **TRLegalClientForm** — Client create/edit form with email validation and client type select
- **TRLegalSpecialistForm** — Specialist create/edit form with dynamic expertise and jurisdiction sub-sections via `useFieldArray`
- **E2E test specification** for all components

## Technical Implementation

### Files Modified

- `apps/Client/src/components/ui/TRCaseStatusBadge.tsx`: New — badge for 11 case statuses with color/label lookup
- `apps/Client/src/components/ui/TRCasePriorityBadge.tsx`: New — badge for 4 priority levels with color coding
- `apps/Client/src/components/ui/TRLegalDomainBadge.tsx`: New — badge for 10 legal domains
- `apps/Client/src/components/ui/TRSpecialistScoreDisplay.tsx`: New — read-only 5-star rating with numeric display
- `apps/Client/src/components/ui/TRPricingTimeline.tsx`: New — vertical stepper timeline of pricing history entries
- `apps/Client/src/components/ui/TRDeliverableChecklist.tsx`: New — deliverable list with status chips and optional status change
- `apps/Client/src/components/forms/TRLegalCaseForm.tsx`: New — case CRUD form (347 lines)
- `apps/Client/src/components/forms/TRLegalClientForm.tsx`: New — client CRUD form (216 lines)
- `apps/Client/src/components/forms/TRLegalSpecialistForm.tsx`: New — specialist CRUD form with dynamic arrays (435 lines)
- `apps/Server/src/adapter/rest/legaldesk_routes.py`: Lint fix — removed unnecessary f-string prefixes from 3 log statements, removed unused `DeliverableStatus` import
- `apps/Server/tests/test_ld_classification_service.py`: Lint fix — minor test cleanup
- `.claude/commands/e2e/test_legaldesk_ui_components.md`: New — E2E test specification

### Key Changes

- **Badge pattern**: All three badges follow the same pattern — accept an enum value prop, look up label/color from constant maps in `@/types/legaldesk`, render MUI `Chip` with fallback gray color
- **No new dependencies**: `TRPricingTimeline` uses MUI `Stepper` with `orientation="vertical"` instead of `@mui/lab` Timeline; date fields use native `<TextField type="date">` instead of `@mui/x-date-pickers`
- **Dynamic form arrays**: `TRLegalSpecialistForm` uses `useFieldArray` twice — for expertise entries (domain + proficiency pairs) and jurisdiction entries (country + region + is_primary)
- **Create/edit mode**: All three forms support both modes via `initialData` prop; forms reset on successful creation but not on edit
- **Type safety**: All components use types from `@/types/legaldesk` with no `any` types; all props are typed via interfaces

## How to Use

### Badge Components

```tsx
import { TRCaseStatusBadge } from '@/components/ui/TRCaseStatusBadge';
import { TRCasePriorityBadge } from '@/components/ui/TRCasePriorityBadge';
import { TRLegalDomainBadge } from '@/components/ui/TRLegalDomainBadge';

<TRCaseStatusBadge status="active" size="small" />
<TRCasePriorityBadge priority="urgent" />
<TRLegalDomainBadge domain="corporate" />
```

### Score Display

```tsx
import { TRSpecialistScoreDisplay } from '@/components/ui/TRSpecialistScoreDisplay';

<TRSpecialistScoreDisplay score={4.5} showNumeric={true} />
```

### Pricing Timeline

```tsx
import { TRPricingTimeline } from '@/components/ui/TRPricingTimeline';

<TRPricingTimeline history={pricingHistoryEntries} />
```

### Deliverable Checklist

```tsx
import { TRDeliverableChecklist } from '@/components/ui/TRDeliverableChecklist';

// Read-only mode
<TRDeliverableChecklist deliverables={caseDeliverables} />

// With status change
<TRDeliverableChecklist
  deliverables={caseDeliverables}
  onStatusChange={(id, status) => updateDeliverableStatus(id, status)}
/>
```

### Forms

```tsx
import { TRLegalCaseForm } from '@/components/forms/TRLegalCaseForm';
import { TRLegalClientForm } from '@/components/forms/TRLegalClientForm';
import { TRLegalSpecialistForm } from '@/components/forms/TRLegalSpecialistForm';

// Case form (create mode)
<TRLegalCaseForm
  onSubmit={handleCreateCase}
  clients={clientsList}
  onCancel={handleClose}
  isSubmitting={loading}
/>

// Case form (edit mode)
<TRLegalCaseForm
  onSubmit={handleUpdateCase}
  initialData={existingCase}
  clients={clientsList}
  onCancel={handleClose}
/>

// Client form
<TRLegalClientForm
  onSubmit={handleCreateClient}
  onCancel={handleClose}
/>

// Specialist form (passes expertise + jurisdictions as separate args)
<TRLegalSpecialistForm
  onSubmit={(data, expertise, jurisdictions) => handleCreate(data, expertise, jurisdictions)}
  onCancel={handleClose}
/>
```

## Configuration

No additional configuration required. All components use existing dependencies (MUI, react-hook-form) and types from `@/types/legaldesk`.

## Testing

Run the E2E test specification:

```bash
# Read and execute the E2E test
# .claude/commands/e2e/test_legaldesk_ui_components.md
```

Validation commands:

```bash
cd apps/Client && npx tsc --noEmit       # TypeScript type check
cd apps/Client && npm run build           # Production build
cd apps/Server && python -m pytest tests/ -x  # Backend regression check
```

## Notes

- Badge components use black text for status and white text for priority/domain for contrast
- `TRSpecialistScoreDisplay` is the simplest component (~6 lines JSX), using MUI Rating with 0.5 precision
- The specialist form `city` field is included as UI-only since `LdSpecialistCreate` does not have a `city` field in the backend
- These components are consumed by Legal Desk pages (LD-015, LD-016) built in parallel
- Empty state handling: `TRPricingTimeline` shows "No pricing history", `TRDeliverableChecklist` shows "No deliverables"
