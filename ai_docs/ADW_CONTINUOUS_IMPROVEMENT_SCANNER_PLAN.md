# Continuous Improvement Scanner — Implementation Plan

## Context

The Tremarel Finance app is growing in complexity (finance tracker, LegalDesk, RestaurantOS). Currently, improvements happen reactively — when users report issues or developers spot problems. This plan introduces a **proactive, automated continuous improvement loop**: an ADW trigger that runs 2-3 times daily, scans the codebase in rotation, and creates GitHub issues for improvement recommendations. The user reviews and selectively triggers improvements, ensuring the app gets progressively better without removing working functionality.

The user specifically requested **coverage rotation** so the scanner doesn't fixate on one part of the app — it must track what it's already analyzed and move through the entire codebase before revisiting areas.

---

## Architecture Overview

```
trigger_continuous_improvement.py (schedule: 08:00, 14:00, optional 02:00)
    │
    ▼
adw_continuous_improvement_iso.py (pipeline orchestrator)
    │
    ├── Load coverage_state.json → select least-recently-scanned zone
    ├── Discover zone files via glob patterns
    ├── Execute /scan_continuous_improvement slash command (Claude analyzes zone)
    ├── Parse structured JSON findings
    ├── Deduplicate against previously created issues (finding_hash)
    ├── Create GitHub issues (labeled: continuous-improvement + technical|ux-business)
    └── Update coverage_state.json (mark zone scanned, store finding hashes)
```

**Key design decision**: The scanner reads from main branch directly — no worktree needed since it only analyzes code and creates issues (read-only on codebase).

---

## Scan Zones (14 zones, rotated)

The app is divided into non-overlapping zones. Each scan analyzes **one zone** deeply rather than the whole app shallowly.

### Technical Zones (7)
| Zone ID | Scope | Glob Patterns |
|---------|-------|---------------|
| `backend-routes` | REST API endpoints | `apps/Server/src/adapter/rest/*.py` |
| `backend-services` | Business logic | `apps/Server/src/core/services/*.py` |
| `backend-data` | Data layer | `apps/Server/src/repository/*.py`, `src/models/*.py`, `src/interface/*.py`, `database/*.sql` |
| `backend-config-auth` | Auth & config | `apps/Server/src/config/*.py`, `apps/Server/main.py`, specific auth files |
| `frontend-pages` | Page components | `apps/Client/src/pages/**/*.tsx` |
| `frontend-components` | UI components | `apps/Client/src/components/**/*.tsx` |
| `frontend-infra` | Services, hooks, types | `apps/Client/src/api/**`, `services/**`, `hooks/**`, `contexts/**`, `types/**`, `utils/**` |

### UX/Business Process Zones (7)
| Zone ID | Scope | Glob Patterns |
|---------|-------|---------------|
| `ux-navigation` | Sidebar, routing, layout | `App.tsx`, sidebar, layout components, route config |
| `ux-forms` | Form UX | All `TR*Form*.tsx` components |
| `ux-data-display` | Dashboards, charts, tables | Dashboard pages, chart/table components |
| `ux-auth-flow` | Login, role-based access | Auth components, ProtectedRoute, AuthContext |
| `ux-legaldesk` | LegalDesk module UX | All legaldesk pages + components + services + types |
| `ux-restaurantos` | RestaurantOS module UX | All restaurantos pages + components + services + types |
| `ux-core-finance` | Core finance UX | Transaction, budget, category, entity pages/services |

**Rotation algorithm**: Zones never scanned → zones scanned longest ago → on tie, zones with more files. A full rotation is tracked — all 14 zones get covered before any repeats.

---

## Coverage State (`agents/continuous_improvement/coverage_state.json`)

```json
{
  "zones": {
    "backend-routes": {
      "zone_id": "backend-routes",
      "last_scanned": "2026-03-07T08:00:00Z",
      "scan_count": 3,
      "last_adw_id": "a1b2c3d4",
      "files_at_scan": 21
    }
  },
  "created_finding_hashes": ["sha256hash1", "sha256hash2"],
  "last_full_rotation": "2026-03-05T14:00:00Z"
}
```

- **Deduplication**: Each finding gets a `finding_hash = sha256(normalized_title + "|" + sorted_affected_files)`. Before creating an issue, check if hash exists in `created_finding_hashes`.
- **New zones**: When new feature modules are added (e.g., `apps/Mobile/`), new zone entries can be added to `SCAN_ZONES`. Zones not in coverage state are treated as "never scanned" and get priority.
- **Deleted files**: Files are discovered dynamically at scan time via glob — deleted files simply won't appear.

---

## Files to Create/Modify

### New Files (3)

**1. `.claude/commands/scan_continuous_improvement.md`** (~100 lines)
- Slash command prompt template for Claude to analyze a zone
- Accepts: zone_id, zone_description, zone_category, file_list
- Instructs Claude to find 3-7 actionable improvements without removing existing functionality
- Returns structured JSON with findings (title, description, category, severity, affected_files, recommendation)
- Separate criteria for technical vs. ux-business categories

**2. `adws/adw_continuous_improvement_iso.py`** (~400 lines)
- Pipeline orchestrator (follows `adw_meeting_pipeline_iso.py` pattern)
- Key functions:
  - `load_coverage_state() → CoverageState`
  - `save_coverage_state(state)`
  - `discover_zone_files(zone: ScanZone) → List[str]`
  - `select_next_zone(coverage_state, scan_zones, category_filter?) → ScanZone`
  - `compute_finding_hash(title, affected_files) → str`
  - `build_issue_body(finding, zone, adw_id) → str`
  - `create_improvement_issues(findings, zone, adw_id, coverage_state) → List[str]`
  - `run_scan(zone, adw_id) → ScanResult`
  - `main()`
- CLI flags: `--zone <id>` (override rotation), `--dry-run` (skip issue creation), `--category technical|ux-business`
- Uses `execute_template()` from `adw_modules/agent.py` to run the slash command
- Uses `create_issue()`, `ensure_labels_exist()` from `adw_modules/github.py`
- Logs to `agents/continuous_improvement/{adw_id}/`

**3. `adws/adw_triggers/trigger_continuous_improvement.py`** (~200 lines)
- Schedule-based trigger (follows `trigger_meeting_transcript_watch.py` pattern)
- Uses `schedule` library with `.every().day.at("HH:MM")`
- Default: `08:00` (technical scan), `14:00` (ux-business scan)
- Optional night scan at `02:00` via `ADW_CI_SCAN_TIMES` env var
- Alternates category between runs (morning=technical, afternoon=ux-business)
- Launches pipeline via `subprocess.Popen()` (non-blocking)
- Signal handlers for graceful shutdown
- `--once` flag for single scan
- Logs to `agents/continuous_improvement_logs/`

### Modified Files (3, minimal changes)

**4. `adws/adw_modules/data_types.py`**
- Add `"/scan_continuous_improvement"` to `SlashCommand` Literal
- Add `"adw_continuous_improvement_iso"` to `ADWWorkflow` Literal
- Add Pydantic models: `ScanZone`, `ScanFinding`, `ScanResult`, `CoverageEntry`, `CoverageState`

**5. `adws/adw_modules/agent.py`**
- Add 1 line to `SLASH_COMMAND_MODEL_MAP`:
  ```python
  "/scan_continuous_improvement": {"base": "opus", "heavy": "opus"},
  ```

**6. `adws/adw_modules/workflow_ops.py`** (if it has a workflow registry list)
- Add `"adw_continuous_improvement_iso"` to available workflows

---

## GitHub Issue Output Format

Each finding becomes a GitHub issue with these labels:
- `continuous-improvement` — identifies all CI scanner issues
- `technical` or `ux-business` — category
- `severity-low`, `severity-medium`, or `severity-high`
- `adw-generated` — standard ADW tag

Issue body structure:
```markdown
## Continuous Improvement Finding

**Zone:** backend-routes (FastAPI route handlers and REST API endpoints)
**Category:** technical
**Severity:** medium
**Scanner ADW ID:** a1b2c3d4

### Description
[Detailed description with evidence and file:line references]

### Affected Files
- apps/Server/src/adapter/rest/transaction_routes.py
- apps/Server/src/adapter/rest/entity_routes.py

### Recommendation
[Specific, actionable steps to implement the improvement]

---
<!-- ci-finding: {"finding_hash":"abc123","zone_id":"backend-routes","scan_timestamp":"2026-03-07T08:00:00Z","adw_id":"a1b2c3d4"} -->
```

The HTML comment enables future automation to parse metadata from existing issues.

---

## Implementation Phases

### Phase 1: Foundation
1. Add data types to `adws/adw_modules/data_types.py` (ScanZone, ScanFinding, ScanResult, CoverageEntry, CoverageState + Literal entries)
2. Add model mapping to `adws/adw_modules/agent.py`

### Phase 2: Slash Command
3. Create `.claude/commands/scan_continuous_improvement.md`

### Phase 3: Pipeline
4. Create `adws/adw_continuous_improvement_iso.py`

### Phase 4: Trigger
5. Create `adws/adw_triggers/trigger_continuous_improvement.py`

### Phase 5: Smoke Test
6. Run pipeline with `--dry-run --zone backend-routes` to verify zone discovery + Claude analysis
7. Run pipeline on one zone without `--dry-run` to verify GitHub issue creation
8. Verify coverage_state.json was created and populated
9. Run again on same zone to verify deduplication (no duplicate issues)
10. Run without `--zone` to verify rotation selects a different zone

---

## Edge Cases Handled

| Scenario | Behavior |
|----------|----------|
| Claude returns invalid JSON | Log warning, save raw output for debug, mark zone scanned (0 findings), continue rotation |
| Claude returns 0 findings | Normal — zone is healthy, update coverage timestamp |
| Duplicate finding | `finding_hash` match in `created_finding_hashes` → skip issue creation |
| Files deleted since last scan | Glob discovers files dynamically — deleted files simply absent |
| New module added to app | Add zone entry to `SCAN_ZONES` constant; zones not in coverage state get first priority |
| Coverage state file missing/corrupt | Start fresh — all zones treated as never-scanned |
| GitHub API failure | Log error, continue to next finding, pipeline doesn't crash |
| Overlapping scan (previous still running) | Trigger checks for running process, skips if still active |
