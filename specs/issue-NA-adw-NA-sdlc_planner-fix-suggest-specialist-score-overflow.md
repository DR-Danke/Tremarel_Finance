# Bug: Suggest Specialist returns 404 due to match_score exceeding validation constraint

## Metadata
issue_number: `NA`
adw_id: `NA`
issue_json: `"when clicking on suggest specialist, I get a 404 error from GET /api/legaldesk/cases/{id}/specialists/suggest"`

## Bug Description
When clicking "Suggest Specialists" on the Case Detail Specialists tab, the backend returns HTTP 404. The browser console shows:
```
GET /api/legaldesk/cases/5/specialists/suggest 404 (Not Found)
ERROR [LegaldeskService]: Failed to suggest specialists: AxiosError
```
The expected behavior is that the endpoint returns a list of ranked specialist candidates.

## Problem Statement
The specialist scoring function `_calculate_match_score` can produce a total score exceeding 100 points (e.g., 111). When normalized by dividing by 100, the `match_score` becomes `Decimal('1.11')`, which violates the `SpecialistCandidateDTO.match_score` Pydantic validation constraint `le=1` (must be <= 1). The resulting `ValidationError` is a subclass of `ValueError` in Pydantic v2, so it is caught by the route handler's `except ValueError` and returned as HTTP 404.

## Solution Statement
Clamp the normalized match score to `[0, 1]` in `ld_assignment_service.py` using `min(score, 100)` before dividing by 100. This ensures the score never exceeds the DTO's `le=1` constraint regardless of edge cases in the scoring factors.

## Steps to Reproduce
1. Log in to the application
2. Navigate to a case detail page (e.g., `/poc/legal-desk/cases/1`)
3. Click the "Specialists" tab
4. Click "Suggest Specialists"
5. Observe 404 error in browser console

Reproduced directly via Python:
```python
from src.core.services.ld_assignment_service import ld_assignment_service
result = ld_assignment_service.suggest_specialists(db, 1)
# ValidationError: match_score - Input should be less than or equal to 1, input_value=Decimal('1.11')
```

## Root Cause Analysis
The `_calculate_match_score` method has 5 scoring factors totaling a theoretical max of 100 points:
- Expertise proficiency: 30 pts
- Overall score: 25 pts
- Workload availability: 20 pts
- Jurisdiction match: 15 pts
- Years experience: 10 pts

However, the years experience factor uses `min(years / 20 * 10, 10)` — if a specialist has high scores across all factors, the sum can slightly exceed 100 due to the rounding/capping of each factor. When the specialist has perfect scores in multiple categories, the total reaches 111 points for the seed data specialist.

The normalization `Decimal(str(round(score / 100, 4)))` produces `Decimal('1.11')`, which fails `SpecialistCandidateDTO.match_score = Field(..., le=1)`.

The `ValidationError` raised by Pydantic v2 inherits from `ValueError`, so the route's `except ValueError as e: raise HTTPException(status_code=404)` catches it and returns 404 — making it look like the case wasn't found.

## Relevant Files
Use these files to fix the bug:

- `apps/Server/src/core/services/ld_assignment_service.py` — Contains `suggest_specialists` method (line 78) where `normalized_score` is computed. The fix is a one-line clamp.
- `apps/Server/tests/test_ld_assignment_service.py` — Contains tests for the assignment service; add a test case verifying scores are clamped to [0, 1].

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Clamp normalized score in `ld_assignment_service.py`

- Open `apps/Server/src/core/services/ld_assignment_service.py`
- At line 78, change:
  ```python
  normalized_score = Decimal(str(round(score / 100, 4)))
  ```
  to:
  ```python
  normalized_score = Decimal(str(round(min(score, 100) / 100, 4)))
  ```
- This ensures the score is clamped to a maximum of 1.0 before being passed to the DTO

### Step 2: Add test verifying score clamping

- Open `apps/Server/tests/test_ld_assignment_service.py`
- Add a test that creates a specialist with maximum values across all scoring factors (expert proficiency, 5.0 overall score, low workload, full jurisdiction match, 20+ years experience) and verifies that `match_score` in the returned candidates does not exceed `Decimal('1.0')`

### Step 3: Run validation commands

- Run all validation commands listed below to confirm zero regressions

## Validation Commands
Execute every command to validate the bug is fixed with zero regressions.

- `cd apps/Server && .venv/bin/python -c "from src.config.database import SessionLocal; from src.core.services.ld_assignment_service import ld_assignment_service; db = SessionLocal(); r = ld_assignment_service.suggest_specialists(db, 1); print('SUCCESS:', len(r.candidates), 'candidates'); db.close()"` — Direct test that the suggest endpoint no longer raises ValidationError
- `cd apps/Server && .venv/bin/python -m pytest tests/test_ld_assignment_service.py -x -v` — Run assignment service tests
- `cd apps/Server && .venv/bin/python -m pytest tests/ -x` — Run all backend tests for zero regressions

## Notes
- This is a **backend-only fix**. The frontend changes from the previous bug fix are correct.
- The root cause is that `_calculate_match_score` can exceed 100 points because individual factor computations are capped independently but can sum above 100. Clamping at normalization is the minimal fix.
- An alternative fix would be to remove the `le=1` constraint from `SpecialistCandidateDTO.match_score`, but that would change the API contract and allow meaningless scores > 1.0.
- The 404 response is misleading because Pydantic v2's `ValidationError` inherits from `ValueError`, so the route's `except ValueError` handler catches what is actually a serialization error. A future improvement could use a more specific exception catch.
