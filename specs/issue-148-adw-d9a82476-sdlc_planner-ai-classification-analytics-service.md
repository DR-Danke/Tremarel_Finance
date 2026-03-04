# Feature: Legal Desk AI Classification & Analytics Service

## Metadata
issue_number: `148`
adw_id: `d9a82476`
issue_json: `{"number":148,"title":"[Legal Desk] Wave 3: AI Classification & Analytics Service","body":"..."}`

## Feature Description
Implement two backend services for the Legal Desk module:

1. **AI Classification Service** (`ld_classification_service.py`): Classifies legal cases by domain, type, complexity, and confidence using OpenAI GPT-4o-mini. When the OpenAI API key is unavailable or an API error occurs, the service falls back to a keyword-based classification approach. Classification results are stored in the case's `ai_classification` JSONB field.

2. **Analytics Service** (`ld_analytics_service.py`): Aggregates dashboard statistics including case counts by status/domain, revenue pipeline summary, specialist performance rankings, recent cases, and average case duration. Delegates to the existing `LdAnalyticsRepository` for database queries and composes results into a `DashboardStatsDTO`.

Both services follow the established Clean Architecture pattern: service layer orchestrates business logic, calls repositories for data access, and returns typed DTOs.

## User Story
As a legal desk administrator
I want cases to be automatically classified by AI and view aggregated dashboard analytics
So that I can quickly understand case distributions, specialist workload, and revenue without manual categorization

## Problem Statement
Legal cases currently lack automated classification — domain, complexity, and type must be set manually. There is also no aggregated analytics view for dashboard statistics. These two capabilities are foundational for Wave 4 API routes (`POST /cases/{id}/classify` and `GET /analytics/dashboard`).

## Solution Statement
Create two service classes following existing singleton patterns:
- `LdClassificationService` with `classify_case(db, case_id)` that uses OpenAI GPT-4o-mini with keyword fallback
- `LdAnalyticsService` with `get_dashboard_stats(db)` that aggregates repository data into `DashboardStatsDTO`

Add `OPENAI_API_KEY` as an optional setting. Write comprehensive unit tests with mocked dependencies.

## Relevant Files
Use these files to implement the feature:

### Existing Files to Read
- `apps/Server/src/interface/legaldesk_dto.py` — Contains `ClassificationResultDTO` (line 690) and `DashboardStatsDTO` (line 702), plus all enums (`LegalDomain`, `CaseComplexity`, `CaseType`, `CaseStatus`)
- `apps/Server/src/repository/ld_case_repository.py` — `LdCaseRepository` with `get_by_id()` and `update()` methods needed by classification service
- `apps/Server/src/repository/ld_analytics_repository.py` — `LdAnalyticsRepository` with `count_cases_by_status()`, `count_cases_by_domain()`, `revenue_pipeline()`, `specialist_performance_rankings()`, `avg_case_duration()` methods
- `apps/Server/src/models/ld_case.py` — `LdCase` model with `ai_classification` JSONB column (line 41), `title`, `description` fields
- `apps/Server/src/models/ld_specialist.py` — `LdSpecialist` model for specialist count queries
- `apps/Server/src/config/settings.py` — `Settings` class where `OPENAI_API_KEY` will be added
- `apps/Server/src/core/services/dashboard_service.py` — Reference pattern for service class structure (singleton, logging, method signatures)
- `apps/Server/src/core/services/__init__.py` — Service exports (no LD services yet)
- `apps/Server/tests/test_ld_analytics_repository.py` — Reference for LD test patterns (pytest fixtures, MagicMock, class-based test groups)
- `apps/Server/tests/test_ld_case_repository.py` — Reference for case-related test mocking patterns
- `apps/Server/requirements.txt` — Dependencies file (openai not yet present)
- `app_docs/feature-cbc09752-legaldesk-pydantic-dtos-enums.md` — LD DTOs and enums documentation
- `app_docs/feature-444abca2-legaldesk-core-repositories.md` — Core repositories documentation
- `app_docs/feature-601d0350-legaldesk-supporting-repositories-wave2.md` — Supporting repositories documentation (includes analytics repo)

### New Files
- `apps/Server/src/core/services/ld_classification_service.py` — AI classification service with OpenAI + keyword fallback
- `apps/Server/src/core/services/ld_analytics_service.py` — Analytics dashboard aggregation service
- `apps/Server/tests/test_ld_classification_service.py` — Unit tests for classification service
- `apps/Server/tests/test_ld_analytics_service.py` — Unit tests for analytics service

## Implementation Plan
### Phase 1: Foundation
Add `OPENAI_API_KEY` as an optional environment variable to `Settings` class. Add `openai` to `requirements.txt`. These are the shared prerequisites for the classification service.

### Phase 2: Core Implementation
1. **Classification Service**: Build `LdClassificationService` with:
   - OpenAI GPT-4o-mini integration for case classification
   - Keyword-based fallback for when API key is missing or API fails
   - Case lookup via `ld_case_repository.get_by_id()`
   - Store results via `ld_case_repository.update()` on the `ai_classification` JSONB field
   - Return `ClassificationResultDTO`

2. **Analytics Service**: Build `LdAnalyticsService` with:
   - Delegate to `ld_analytics_repository` for all database queries
   - Query specialist count from `LdSpecialist` model
   - Query recent 10 cases from `LdCase` model
   - Compose all data into `DashboardStatsDTO`

### Phase 3: Integration
- Write comprehensive unit tests for both services using mocked repositories and OpenAI client
- Verify all tests pass alongside existing LD tests
- Ensure no regressions across the test suite

## Step by Step Tasks

### Step 1: Add OPENAI_API_KEY to Settings
- Open `apps/Server/src/config/settings.py`
- Add `OPENAI_API_KEY: str = ""` field to the `Settings` class (optional, defaults to empty string)
- This follows the same pattern as other optional API keys like `WHATSAPP_API_KEY`

### Step 2: Add openai to requirements.txt
- Open `apps/Server/requirements.txt`
- Add `openai>=1.0.0` under a new `# AI Classification` section
- Place it after the Utilities section

### Step 3: Create the Classification Service
- Create `apps/Server/src/core/services/ld_classification_service.py`
- Implement `LdClassificationService` class with:

**`classify_case(self, db: Session, case_id: int) -> ClassificationResultDTO`:**
1. Fetch case using `ld_case_repository.get_by_id(db, case_id)`
2. Raise `ValueError` if case not found
3. Build classification text from `case.title` and `case.description`
4. Check `OPENAI_API_KEY` from settings — if present, call `_classify_with_openai(text)`
5. On OpenAI error or missing key, call `_classify_with_keywords(text)`
6. Store result dict in `case.ai_classification` via `ld_case_repository.update(db, case_id, {"ai_classification": result_dict})`
7. Return `ClassificationResultDTO`

**`_classify_with_openai(self, text: str) -> ClassificationResultDTO`:**
1. Initialize OpenAI client with API key from settings
2. Send chat completion request to `gpt-4o-mini` with system prompt:
   - Request JSON response with fields: `legal_domain`, `case_type`, `complexity`, `confidence`, `reasoning`
   - Provide valid enum values in the prompt for legal_domain, case_type, complexity
3. Parse JSON response
4. Map parsed values to `ClassificationResultDTO` (use `reasoning` as a suggested tag)
5. Wrap in try/except to catch any OpenAI errors → re-raise or fall back

**`_classify_with_keywords(self, text: str) -> ClassificationResultDTO`:**
1. Define `DOMAIN_KEYWORDS` dict mapping domain strings to keyword lists:
   - `corporate`: merger, acquisition, shareholder, board, incorporation, corporate
   - `ip`: patent, trademark, copyright, intellectual property, brand
   - `labor`: employment, worker, termination, labor, harassment, wage
   - `tax`: tax, fiscal, irs, deduction, filing
   - `litigation`: lawsuit, court, dispute, damages, trial
   - `real_estate`: property, lease, tenant, landlord, zoning
   - `immigration`: visa, immigration, citizenship, deportation, asylum
   - `regulatory`: compliance, regulation, license, permit, inspection
   - `data_privacy`: privacy, gdpr, data protection, breach, consent
   - `commercial`: contract, agreement, vendor, procurement, negotiation
2. Lowercase the text and count keyword matches per domain
3. Select domain with most matches (default to `commercial` if no matches)
4. Determine `case_type`: if domain is `litigation` → `litigation`, else `advisory`
5. Set `complexity` to `medium` and `confidence` to `Decimal("0.5")` (keyword-based has lower confidence)
6. Return `ClassificationResultDTO`

- Export singleton: `ld_classification_service = LdClassificationService()`
- Add comprehensive logging at each step with `print(f"INFO [LdClassificationService]: ...")`

### Step 4: Create the Analytics Service
- Create `apps/Server/src/core/services/ld_analytics_service.py`
- Implement `LdAnalyticsService` class with:

**`get_dashboard_stats(self, db: Session) -> DashboardStatsDTO`:**
1. Call `ld_analytics_repository.count_cases_by_status(db)` → `cases_by_status`
2. Call `ld_analytics_repository.count_cases_by_domain(db)` → `cases_by_domain`
3. Call `ld_analytics_repository.revenue_pipeline(db)` → `revenue_data`
4. Call `ld_analytics_repository.specialist_performance_rankings(db)` → `rankings`
5. Call `ld_analytics_repository.avg_case_duration(db)` → `avg_duration`
6. Compute `total_cases` = sum of all `cases_by_status` values
7. Compute `active_cases` = sum counts for statuses: `active`, `in_progress`, `review`, `negotiating`
8. Compute `completed_cases` = count for status `completed`
9. Query `total_specialists` = `db.query(func.count(LdSpecialist.id)).scalar()`
10. Compute `total_revenue` = `revenue_data["total_final_quote"]`
11. Compute `cases_by_priority` by querying `db.query(LdCase.priority, func.count(LdCase.id)).group_by(LdCase.priority).all()`
12. Assemble and return `DashboardStatsDTO`

- Export singleton: `ld_analytics_service = LdAnalyticsService()`
- Add comprehensive logging at each step

### Step 5: Write Classification Service Tests
- Create `apps/Server/tests/test_ld_classification_service.py`
- Follow existing test patterns (pytest, MagicMock, class-based groups)
- Test classes:

**`TestClassifyCase`:**
- `test_classify_case_with_openai_success` — mock OpenAI response, verify DTO returned, verify case updated with ai_classification
- `test_classify_case_falls_back_on_missing_api_key` — settings with empty OPENAI_API_KEY, verify keyword classification used
- `test_classify_case_falls_back_on_openai_error` — mock OpenAI to raise exception, verify keyword fallback
- `test_classify_case_not_found` — mock repository returns None, verify ValueError raised

**`TestClassifyWithKeywords`:**
- `test_corporate_domain_detected` — text with "merger" and "shareholder" → legal_domain=corporate
- `test_litigation_domain_detected` — text with "lawsuit" and "court" → legal_domain=litigation, case_type=litigation
- `test_default_domain_when_no_keywords_match` — generic text → legal_domain=commercial
- `test_confidence_is_half_for_keywords` — verify confidence = 0.5
- `test_case_type_advisory_for_non_litigation` — verify non-litigation domains get case_type=advisory

**`TestClassifyWithOpenai`:**
- `test_successful_openai_classification` — mock OpenAI client, verify JSON parsed correctly
- `test_openai_returns_invalid_json` — mock malformed response, verify exception raised

### Step 6: Write Analytics Service Tests
- Create `apps/Server/tests/test_ld_analytics_service.py`
- Test classes:

**`TestGetDashboardStats`:**
- `test_dashboard_stats_with_data` — mock all repository methods with sample data, verify DTO fields computed correctly (total_cases, active_cases, completed_cases, total_specialists, avg_case_duration_days, total_revenue, cases_by_status, cases_by_domain, cases_by_priority)
- `test_dashboard_stats_empty_database` — mock all repository methods returning empty/zero, verify DTO with zero/empty values
- `test_active_cases_counted_correctly` — verify only active, in_progress, review, negotiating statuses counted
- `test_total_revenue_from_pipeline` — verify total_revenue comes from revenue_pipeline total_final_quote

### Step 7: Run Validation Commands
- Run all Server tests to verify zero regressions
- Run Client type check and build to ensure no cross-impact

## Testing Strategy
### Unit Tests
- **Classification Service**: Mock `ld_case_repository`, `openai.OpenAI` client, and `get_settings()` to test all paths (OpenAI success, OpenAI failure, missing API key, case not found, keyword matching for each domain)
- **Analytics Service**: Mock `ld_analytics_repository` methods and database queries to test aggregation logic and DTO composition
- All tests use `unittest.mock.patch` and `MagicMock` consistent with existing LD test patterns

### Edge Cases
- Case not found for classification (ValueError)
- OpenAI returns malformed JSON (fallback to keywords)
- OpenAI API timeout or network error (fallback to keywords)
- Empty OPENAI_API_KEY (fallback to keywords)
- Text with no keyword matches (defaults to `commercial` domain)
- Text with equal keyword matches across multiple domains (first match wins)
- Empty database for analytics (all zeros/empty dicts)
- No completed cases (avg_case_duration_days = None)
- No active specialists (total_specialists = 0)

## Acceptance Criteria
- `LdClassificationService.classify_case()` returns a valid `ClassificationResultDTO` for any case
- OpenAI classification sends proper prompt with enum values and parses JSON response
- Keyword fallback activates when `OPENAI_API_KEY` is empty or OpenAI call fails
- Keyword fallback correctly maps domains based on keyword frequency in case text
- Classification result is persisted to the case's `ai_classification` JSONB field
- `LdAnalyticsService.get_dashboard_stats()` returns a valid `DashboardStatsDTO`
- `total_cases` equals sum of all status counts
- `active_cases` counts only active/in_progress/review/negotiating statuses
- `completed_cases` counts only completed status
- `total_revenue` derives from revenue pipeline data
- All unit tests pass with `pytest`
- No regressions in existing test suite
- `OPENAI_API_KEY` is optional (empty string default) — app starts without it

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && pip install -r requirements.txt` — Install new openai dependency
- `cd apps/Server && python -m pytest tests/test_ld_classification_service.py -v` — Run classification service tests
- `cd apps/Server && python -m pytest tests/test_ld_analytics_service.py -v` — Run analytics service tests
- `cd apps/Server && python -m pytest tests/ -v` — Run all Server tests to validate zero regressions
- `cd apps/Client && npx tsc --noEmit` — Run Client type check (no frontend changes expected but verify)
- `cd apps/Client && npm run build` — Run Client build to validate no regressions

## Notes
- **New dependency**: `openai>=1.0.0` must be added to `requirements.txt`. Install with `pip install -r requirements.txt`.
- **No REST routes in this issue**: Wave 4 will expose `POST /cases/{id}/classify` and `GET /analytics/dashboard` — this issue only creates the service layer.
- **No UI changes**: This is purely backend (Wave 3 — Backend Business Logic). No E2E tests needed.
- **Parallel execution**: This issue (LD-011) runs in parallel with LD-008, LD-009, LD-010. No merge conflicts expected since this creates new files only, with minimal edits to shared files (`settings.py`, `requirements.txt`).
- **DashboardStatsDTO gap**: The issue mentions `specialist_performance`, `recent_cases`, and `revenue_summary` fields, but the existing `DashboardStatsDTO` doesn't have those fields. The implementation should populate the fields that exist in the DTO (`total_cases`, `active_cases`, `completed_cases`, `total_specialists`, `avg_case_duration_days`, `total_revenue`, `cases_by_status`, `cases_by_domain`, `cases_by_priority`). The specialist performance and recent cases data from repositories can be computed but not returned unless the DTO is extended — stick with the existing DTO shape.
