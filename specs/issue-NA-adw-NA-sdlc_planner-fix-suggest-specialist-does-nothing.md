# Bug: Suggest Specialist button does nothing after creating a case

## Metadata
issue_number: `NA`
adw_id: `NA`
issue_json: `"after creating a case, when I click on Suggest Specialist, nothing happens"`

## Bug Description
After creating a new Legal Desk case and navigating to the Case Detail page's "Specialists" tab, clicking the "Suggest Specialists" button produces no visible result. No candidates appear, no error message is shown, and the UI appears completely unresponsive to the click. The expected behavior is that a list of ranked specialist candidates should appear in a "Suggested Candidates" table below the assigned specialists section.

## Problem Statement
There is a two-layer mismatch between the frontend and backend for the specialist suggestion endpoint:

1. **Response envelope mismatch**: The frontend service (`legaldeskService.suggestSpecialists`) expects the API to return a flat array of `LdSpecialistCandidate[]`, but the backend returns a `SuggestionResponseDTO` object with structure `{ case_id, legal_domain, candidates: [...], generated_at }`. The frontend receives the wrapper object and tries to use it as an array.

2. **Candidate schema mismatch**: The frontend type `LdSpecialistCandidate` expects `{ specialist: LdSpecialist, expertise_match: LdSpecialistExpertise | null, availability_score: number, overall_score: number }`, but the backend `SpecialistCandidateDTO` returns `{ specialist_id, full_name, email, match_score, hourly_rate, currency, current_workload, max_concurrent_cases, expertise_match: string[], jurisdiction_match: string[], match_reasons: string[] }`. Every field name and type is different.

Because the response is not an array, `response.data.length` (line 141 of legaldeskService.ts) succeeds since the object has properties, but `setCandidates(results)` sets a non-array value. The rendering code (`candidates.length > 0`) then evaluates to false (or the `.map()` on line 438 of LegalDeskCaseDetailPage.tsx fails silently), so no candidates ever display. If an error is thrown, it's caught by the hook's try/catch and sets `error` state, but the error message is generic and easy to miss in the UI.

## Solution Statement
Fix the frontend to correctly consume the backend's actual response shape. This is the minimal-change approach:

1. **Frontend service**: Extract `response.data.candidates` from the `SuggestionResponseDTO` wrapper instead of treating the whole response as the array.
2. **Frontend type**: Replace the `LdSpecialistCandidate` interface with fields matching the backend's `SpecialistCandidateDTO` schema.
3. **Frontend page**: Update the candidates table rendering in `LegalDeskCaseDetailPage.tsx` to use the correct field names from the updated type (`specialist_id`, `full_name`, `match_score` instead of `c.specialist.id`, `c.specialist.full_name`, `c.overall_score`).
4. **Frontend page**: Update the "Assign" button to pass `c.specialist_id` directly instead of `c.specialist.id`.

## Steps to Reproduce
1. Log in to the application
2. Navigate to `/poc/legal-desk/cases/new`
3. Fill in the form (title, client, legal domain = "corporate", etc.) and submit
4. After redirect to case detail page, click the "Specialists" tab (tab index 1)
5. Click the "Suggest Specialists" button
6. Observe: nothing happens (no candidate table appears, no error feedback)
7. Open browser console: may see errors about accessing properties on undefined, or the response object shape mismatch

## Root Cause Analysis
The backend endpoint `GET /api/legaldesk/cases/{case_id}/specialists/suggest` was implemented returning `SuggestionResponseDTO` (a wrapper object containing metadata + candidates array). The frontend was implemented expecting a flat `LdSpecialistCandidate[]` array with a completely different field schema. These two layers were built in parallel by separate ADW agents (Wave 3 backend services vs Wave 5/6 frontend) and the contract was never reconciled.

Specifically:
- **Backend** (`legaldesk_routes.py:247`): `response_model=SuggestionResponseDTO` returns `{ case_id, legal_domain, candidates: [SpecialistCandidateDTO...], generated_at }`
- **Frontend** (`legaldeskService.ts:140`): `apiClient.get<LdSpecialistCandidate[]>(...)` expects a flat array
- **Frontend type** (`legaldesk.ts:434`): `LdSpecialistCandidate` has `specialist: LdSpecialist` (nested object) but backend returns `specialist_id: number` (flat ID)
- **Frontend render** (`LegalDeskCaseDetailPage.tsx:439`): `c.specialist.id` crashes because `c.specialist` doesn't exist in the backend response

The chain of failure: API call succeeds -> response shape doesn't match expected type -> setCandidates gets wrong data -> candidates table either doesn't render or throws silently.

## Relevant Files
Use these files to fix the bug:

- `apps/Client/src/types/legaldesk.ts` — Contains `LdSpecialistCandidate` interface (line 434) that must be updated to match the backend's `SpecialistCandidateDTO` schema
- `apps/Client/src/types/index.ts` — Re-exports `LdSpecialistCandidate`; may need to export new/renamed types
- `apps/Client/src/services/legaldeskService.ts` — Contains `suggestSpecialists` method (line 137) that must extract `candidates` from the response envelope
- `apps/Client/src/hooks/useLegaldeskCaseDetail.ts` — Contains `suggestSpecialists` callback (line 136) that calls the service and sets candidates state; no changes needed if service returns correct type
- `apps/Client/src/pages/legaldesk/LegalDeskCaseDetailPage.tsx` — Contains candidates table rendering (lines 423-465) that references `c.specialist.id`, `c.specialist.full_name`, `c.overall_score`, `c.availability_score`, `c.expertise_match?.proficiency_level` which must be updated to use correct field names
- `apps/Server/src/adapter/rest/legaldesk_routes.py` — Backend suggest endpoint (line 247) for reference; no changes needed
- `apps/Server/src/interface/legaldesk_dto.py` — Backend `SpecialistCandidateDTO` (line 657) and `SuggestionResponseDTO` (line 677) for reference; no changes needed
- `apps/Server/src/core/services/ld_assignment_service.py` — Backend assignment service for reference; no changes needed
- `app_docs/feature-e9ee37e2-legaldesk-frontend-typescript-types.md` — Documentation for Legal Desk TypeScript types
- `app_docs/feature-7febcc45-legaldesk-all-pages.md` — Documentation for Legal Desk pages
- `app_docs/feature-e846c4b4-legaldesk-ui-components-forms.md` — Documentation for Legal Desk UI components
- Read `.claude/commands/test_e2e.md` and `.claude/commands/e2e/test_basic_query.md` to understand how to create an E2E test file

### New Files
- `.claude/commands/e2e/test_legaldesk_suggest_specialist.md` — E2E test validating the suggest specialist flow works end-to-end

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Update `LdSpecialistCandidate` type to match backend DTO

- Open `apps/Client/src/types/legaldesk.ts`
- Replace the `LdSpecialistCandidate` interface (line 434) with fields matching the backend's `SpecialistCandidateDTO`:
  ```typescript
  export interface LdSpecialistCandidate {
    specialist_id: number
    full_name: string
    email: string
    match_score: number
    hourly_rate: number | null
    currency: string
    current_workload: number
    max_concurrent_cases: number
    expertise_match: string[]
    jurisdiction_match: string[]
    match_reasons: string[]
  }
  ```
- Verify `apps/Client/src/types/index.ts` still re-exports `LdSpecialistCandidate` correctly (the name is the same so no changes needed there)

### Step 2: Update `legaldeskService.suggestSpecialists` to extract candidates from response envelope

- Open `apps/Client/src/services/legaldeskService.ts`
- Add a local interface for the API response shape at the top or inline:
  ```typescript
  interface SuggestionResponse {
    case_id: number
    legal_domain: string
    candidates: LdSpecialistCandidate[]
    generated_at: string
  }
  ```
- Update the `suggestSpecialists` method (line 137-147) to:
  - Type the API call as `apiClient.get<SuggestionResponse>(...)`
  - Return `response.data.candidates` instead of `response.data`
  - Log `response.data.candidates.length` instead of `response.data.length`

### Step 3: Update candidates table rendering in `LegalDeskCaseDetailPage.tsx`

- Open `apps/Client/src/pages/legaldesk/LegalDeskCaseDetailPage.tsx`
- Update the candidates table header columns (lines 429-434) to match the new fields:
  - "Name" (full_name)
  - "Match Score" (match_score)
  - "Workload" (current_workload / max_concurrent_cases)
  - "Expertise" (expertise_match joined)
  - "Action" (assign button)
- Update the candidates `.map()` rendering (lines 438-460):
  - Change `key={c.specialist.id}` to `key={c.specialist_id}`
  - Change `c.specialist.full_name` to `c.full_name`
  - Change `c.overall_score.toFixed(1)` to `(c.match_score * 100).toFixed(0) + '%'` or similar display
  - Change `c.availability_score.toFixed(1)` to `${c.current_workload}/${c.max_concurrent_cases}`
  - Change `c.expertise_match?.proficiency_level || 'N/A'` to `c.expertise_match.join(', ')` (it's now a string array)
  - Change `specialist_id: c.specialist.id` in the Assign button onClick to `specialist_id: c.specialist_id`

### Step 4: Create E2E test specification

- Read `.claude/commands/e2e/test_basic_query.md` and `.claude/commands/e2e/test_legaldesk_pages.md`
- Create a new E2E test file at `.claude/commands/e2e/test_legaldesk_suggest_specialist.md` that validates:
  1. Navigate to `/poc/legal-desk/cases/new` (authenticated)
  2. Fill and submit the case form (title, client, legal_domain="corporate", complexity, priority)
  3. Verify redirect to case detail page
  4. Click the "Specialists" tab
  5. Click the "Suggest Specialists" button
  6. Verify the "Suggested Candidates" section appears with at least one row
  7. Verify candidate rows show name, match score, workload, expertise columns
  8. Take a screenshot of the suggested candidates table
  9. Click the "Assign" button on the first candidate
  10. Verify the assigned specialists table updates with the new assignment
  11. Take a screenshot of the final state
- Note: This test requires seed data with specialists that have "corporate" domain expertise

### Step 5: Run validation commands

- Run all validation commands listed below to confirm zero regressions

## Validation Commands
Execute every command to validate the bug is fixed with zero regressions.

- `cd apps/Client && npx tsc --noEmit` — TypeScript type check: ensures updated types are consistent across all consumers (hooks, services, pages)
- `cd apps/Client && npm run build` — Production build: ensures no runtime import or JSX compilation errors
- `cd apps/Server && .venv/bin/python -m pytest tests/ -x` — Backend tests: ensures no regressions in Legal Desk backend (backend is not modified but run for confidence)
- Read `.claude/commands/test_e2e.md`, then read and execute the new E2E `.claude/commands/e2e/test_legaldesk_suggest_specialist.md` test file to validate this functionality works

## Notes
- This is a **frontend-only fix**. The backend endpoint and service work correctly; the issue is that the frontend was built against an assumed API contract that doesn't match the actual backend implementation.
- No new libraries are needed.
- The `LdSpecialistCandidate` type name is preserved (not renamed) so that all existing imports throughout hooks, pages, and the type index continue to work without changes.
- The backend returns `match_score` as a Decimal 0-1 value (e.g., 0.85). The frontend should display it as a percentage (e.g., "85%") for user-friendliness.
- Seed data must include specialists with matching expertise domains for the suggestion engine to return results. The `seed_legaldesk_data.sql` file already provides this data for the "corporate" domain.
- The `suggestSpecialists` callback in the hook catches errors and sets `error` state. After this fix, if the API genuinely fails, the error banner will display. Previously, the type mismatch could cause a JavaScript runtime error that was caught as a generic failure.
