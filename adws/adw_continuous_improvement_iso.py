#!/usr/bin/env -S uv run
# /// script
# dependencies = ["python-dotenv", "pydantic"]
# ///

"""
ADW Continuous Improvement Scanner - Scan codebase zones and create improvement issues

Usage:
  uv run adw_continuous_improvement_iso.py                          # Auto-rotate to next zone
  uv run adw_continuous_improvement_iso.py --zone backend-routes    # Scan specific zone
  uv run adw_continuous_improvement_iso.py --dry-run                # Skip GitHub issue creation
  uv run adw_continuous_improvement_iso.py --category technical     # Only scan technical zones
  uv run adw_continuous_improvement_iso.py --category ux-business   # Only scan UX zones

Workflow:
1. Load coverage_state.json to determine which zone to scan next
2. Select least-recently-scanned zone (rotation algorithm)
3. Discover zone files via glob patterns
4. Execute /scan_continuous_improvement via execute_template()
5. Parse structured JSON findings
6. Deduplicate against previously created issues (finding_hash)
7. Create GitHub issues (labeled: continuous-improvement + category)
8. Update coverage_state.json

This workflow reads from main branch directly — no worktree needed (read-only on codebase).
"""

import sys
import os
import json
import hashlib
import argparse
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

from adw_modules.github import (
    check_gh_authenticated,
    create_issue,
    ensure_labels_exist,
    get_repo_url,
    extract_repo_path,
)
from adw_modules.utils import setup_logger, check_env_vars, make_adw_id
from adw_modules.data_types import (
    AgentTemplateRequest,
    ScanZone,
    ScanFinding,
    ScanResult,
    CoverageEntry,
    CoverageState,
)
from adw_modules.agent import execute_template

# Load environment variables
load_dotenv()

# Project root (parent of adws/)
PROJECT_ROOT = Path(__file__).parent.parent

# Coverage state file location
COVERAGE_STATE_FILE = PROJECT_ROOT / "agents" / "continuous_improvement" / "coverage_state.json"

# Agent name for this workflow
AGENT_NAME = "ci_scanner"

# --- Scan Zone Definitions (14 zones) ---

SCAN_ZONES: list[ScanZone] = [
    # Technical Zones (7)
    ScanZone(
        zone_id="backend-routes",
        description="FastAPI route handlers and REST API endpoints",
        category="technical",
        glob_patterns=["apps/Server/src/adapter/rest/*.py"],
    ),
    ScanZone(
        zone_id="backend-services",
        description="Backend business logic and service layer",
        category="technical",
        glob_patterns=["apps/Server/src/core/services/*.py"],
    ),
    ScanZone(
        zone_id="backend-data",
        description="Data access layer: repositories, models, DTOs, and SQL schemas",
        category="technical",
        glob_patterns=[
            "apps/Server/src/repository/*.py",
            "apps/Server/src/models/*.py",
            "apps/Server/src/interface/*.py",
            "apps/Server/database/*.sql",
        ],
    ),
    ScanZone(
        zone_id="backend-config-auth",
        description="Authentication, authorization, configuration, and app bootstrap",
        category="technical",
        glob_patterns=[
            "apps/Server/src/config/*.py",
            "apps/Server/main.py",
            "apps/Server/src/adapter/rest/dependencies.py",
            "apps/Server/src/adapter/rest/auth_routes.py",
            "apps/Server/src/adapter/rest/rbac_dependencies.py",
        ],
    ),
    ScanZone(
        zone_id="frontend-pages",
        description="React page components (top-level route views)",
        category="technical",
        glob_patterns=["apps/Client/src/pages/**/*.tsx"],
    ),
    ScanZone(
        zone_id="frontend-components",
        description="Reusable React UI components (forms, layout, auth, ui)",
        category="technical",
        glob_patterns=["apps/Client/src/components/**/*.tsx"],
    ),
    ScanZone(
        zone_id="frontend-infra",
        description="Frontend infrastructure: API clients, services, hooks, contexts, types, utils",
        category="technical",
        glob_patterns=[
            "apps/Client/src/api/**/*.ts",
            "apps/Client/src/api/**/*.tsx",
            "apps/Client/src/services/**/*.ts",
            "apps/Client/src/hooks/**/*.ts",
            "apps/Client/src/hooks/**/*.tsx",
            "apps/Client/src/contexts/**/*.tsx",
            "apps/Client/src/types/**/*.ts",
            "apps/Client/src/utils/**/*.ts",
        ],
    ),
    # UX/Business Process Zones (7)
    ScanZone(
        zone_id="ux-navigation",
        description="Sidebar navigation, routing configuration, and layout structure",
        category="ux-business",
        glob_patterns=[
            "apps/Client/src/App.tsx",
            "apps/Client/src/components/layout/*.tsx",
        ],
    ),
    ScanZone(
        zone_id="ux-forms",
        description="Form components and form UX patterns (all TR*Form* components)",
        category="ux-business",
        glob_patterns=["apps/Client/src/components/forms/*.tsx"],
    ),
    ScanZone(
        zone_id="ux-data-display",
        description="Dashboards, charts, tables, and data visualization components",
        category="ux-business",
        glob_patterns=[
            "apps/Client/src/pages/dashboard/**/*.tsx",
            "apps/Client/src/components/ui/*.tsx",
        ],
    ),
    ScanZone(
        zone_id="ux-auth-flow",
        description="Login flow, role-based access, protected routes, and auth context",
        category="ux-business",
        glob_patterns=[
            "apps/Client/src/components/auth/*.tsx",
            "apps/Client/src/contexts/AuthContext.tsx",
            "apps/Client/src/pages/auth/**/*.tsx",
            "apps/Client/src/pages/login/**/*.tsx",
        ],
    ),
    ScanZone(
        zone_id="ux-legaldesk",
        description="LegalDesk module: pages, components, services, and types",
        category="ux-business",
        glob_patterns=[
            "apps/Client/src/pages/legaldesk/**/*.tsx",
            "apps/Client/src/components/legaldesk/**/*.tsx",
            "apps/Client/src/services/legaldesk*.ts",
            "apps/Client/src/types/legaldesk*.ts",
        ],
    ),
    ScanZone(
        zone_id="ux-restaurantos",
        description="RestaurantOS module: pages, components, services, and types",
        category="ux-business",
        glob_patterns=[
            "apps/Client/src/pages/restaurantos/**/*.tsx",
            "apps/Client/src/components/restaurantos/**/*.tsx",
            "apps/Client/src/services/restaurantos*.ts",
            "apps/Client/src/types/restaurantos*.ts",
        ],
    ),
    ScanZone(
        zone_id="ux-core-finance",
        description="Core finance UX: transactions, budgets, categories, entities",
        category="ux-business",
        glob_patterns=[
            "apps/Client/src/pages/transactions/**/*.tsx",
            "apps/Client/src/pages/budgets/**/*.tsx",
            "apps/Client/src/pages/categories/**/*.tsx",
            "apps/Client/src/pages/entities/**/*.tsx",
            "apps/Client/src/services/transaction*.ts",
            "apps/Client/src/services/budget*.ts",
            "apps/Client/src/services/category*.ts",
            "apps/Client/src/services/entity*.ts",
        ],
    ),
]


def load_coverage_state() -> CoverageState:
    """Load coverage state from disk. Returns fresh state if file missing or corrupt."""
    try:
        if COVERAGE_STATE_FILE.exists():
            with open(COVERAGE_STATE_FILE, "r") as f:
                data = json.load(f)
            return CoverageState(**data)
    except (json.JSONDecodeError, Exception) as e:
        print(f"WARNING: Could not load coverage state ({e}), starting fresh")
    return CoverageState()


def save_coverage_state(state: CoverageState) -> None:
    """Persist coverage state to disk."""
    COVERAGE_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(COVERAGE_STATE_FILE, "w") as f:
        json.dump(state.model_dump(), f, indent=2)


def discover_zone_files(zone: ScanZone) -> list[str]:
    """Discover files in a zone using glob patterns. Returns relative paths from project root."""
    files: list[str] = []
    for pattern in zone.glob_patterns:
        matched = sorted(PROJECT_ROOT.glob(pattern))
        for filepath in matched:
            rel = str(filepath.relative_to(PROJECT_ROOT))
            if rel not in files:
                files.append(rel)
    return files


def select_next_zone(
    coverage_state: CoverageState,
    scan_zones: list[ScanZone],
    category_filter: Optional[str] = None,
) -> ScanZone:
    """Select the next zone to scan using rotation algorithm.

    Priority:
    1. Zones never scanned (not in coverage state)
    2. Zones scanned longest ago
    3. On tie, zones with more files
    """
    candidates = scan_zones
    if category_filter:
        candidates = [z for z in candidates if z.category == category_filter]

    if not candidates:
        raise ValueError(f"No zones match category filter: {category_filter}")

    def sort_key(zone: ScanZone) -> tuple:
        entry = coverage_state.zones.get(zone.zone_id)
        if entry is None or entry.last_scanned is None:
            # Never scanned — highest priority (sort earliest)
            return (0, "", -len(discover_zone_files(zone)))
        # Scanned before — sort by last_scanned ascending (oldest first)
        return (1, entry.last_scanned, -entry.files_at_scan)

    candidates_sorted = sorted(candidates, key=sort_key)
    return candidates_sorted[0]


def compute_finding_hash(title: str, affected_files: list[str]) -> str:
    """Compute a deduplication hash for a finding."""
    normalized_title = title.strip().lower()
    sorted_files = "|".join(sorted(affected_files))
    content = f"{normalized_title}|{sorted_files}"
    return hashlib.sha256(content.encode()).hexdigest()


def build_issue_body(finding: ScanFinding, zone: ScanZone, adw_id: str, scan_timestamp: str) -> str:
    """Build GitHub issue body from a finding."""
    affected_list = "\n".join(f"- {f}" for f in finding.affected_files)
    finding_hash = compute_finding_hash(finding.title, finding.affected_files)

    return f"""## Continuous Improvement Finding

**Zone:** {zone.zone_id} ({zone.description})
**Category:** {finding.category}
**Severity:** {finding.severity}
**Scanner ADW ID:** {adw_id}

### Description
{finding.description}

### Affected Files
{affected_list}

### Recommendation
{finding.recommendation}

---
<!-- ci-finding: {{"finding_hash":"{finding_hash}","zone_id":"{zone.zone_id}","scan_timestamp":"{scan_timestamp}","adw_id":"{adw_id}"}} -->
"""


def create_improvement_issues(
    findings: list[ScanFinding],
    zone: ScanZone,
    adw_id: str,
    scan_timestamp: str,
    coverage_state: CoverageState,
    repo_path: str,
    dry_run: bool = False,
    logger: Optional[logging.Logger] = None,
) -> list[str]:
    """Create GitHub issues for findings, skipping duplicates. Returns list of created issue numbers."""
    created: list[str] = []

    for finding in findings:
        finding_hash = compute_finding_hash(finding.title, finding.affected_files)

        # Deduplication check
        if finding_hash in coverage_state.created_finding_hashes:
            msg = f"SKIP (duplicate): {finding.title} [hash={finding_hash[:12]}]"
            if logger:
                logger.info(msg)
            else:
                print(f"INFO: {msg}")
            continue

        if dry_run:
            msg = f"DRY-RUN would create issue: {finding.title} [severity={finding.severity}]"
            if logger:
                logger.info(msg)
            else:
                print(f"INFO: {msg}")
            # Still record hash in dry-run to test dedup logic
            coverage_state.created_finding_hashes.append(finding_hash)
            continue

        # Build issue
        title = f"[CI] {finding.title}"
        body = build_issue_body(finding, zone, adw_id, scan_timestamp)
        labels = [
            "continuous-improvement",
            finding.category,
            f"severity-{finding.severity}",
            "adw-generated",
        ]

        issue_number = create_issue(title, body, labels, repo_path)

        if issue_number:
            coverage_state.created_finding_hashes.append(finding_hash)
            created.append(issue_number)
            msg = f"Created issue #{issue_number}: {finding.title}"
            if logger:
                logger.info(msg)
            else:
                print(f"INFO: {msg}")
        else:
            msg = f"FAILED to create issue: {finding.title}"
            if logger:
                logger.error(msg)
            else:
                print(f"ERROR: {msg}")

    return created


def run_scan(
    zone: ScanZone,
    adw_id: str,
    logger: Optional[logging.Logger] = None,
) -> ScanResult:
    """Execute the scan slash command on a zone and parse results."""
    scan_timestamp = datetime.now(timezone.utc).isoformat()

    # Discover files
    files = discover_zone_files(zone)
    if not files:
        msg = f"No files found for zone {zone.zone_id}, skipping scan"
        if logger:
            logger.warning(msg)
        else:
            print(f"WARNING: {msg}")
        return ScanResult(
            zone_id=zone.zone_id,
            findings=[],
            scan_timestamp=scan_timestamp,
            adw_id=adw_id,
        )

    msg = f"Scanning zone '{zone.zone_id}' ({len(files)} files)"
    if logger:
        logger.info(msg)
    else:
        print(f"INFO: {msg}")

    # Build arguments for the slash command
    file_list = "\n".join(f"- {f}" for f in files)
    scan_args = f"""
**Zone ID:** {zone.zone_id}
**Zone Description:** {zone.description}
**Zone Category:** {zone.category}
**Files to analyze ({len(files)}):**
{file_list}
"""

    # Execute via Claude Code template
    request = AgentTemplateRequest(
        agent_name=AGENT_NAME,
        slash_command="/scan_continuous_improvement",
        args=[scan_args],
        adw_id=adw_id,
        working_dir=str(PROJECT_ROOT),
    )

    response = execute_template(request)

    if not response.success:
        msg = f"Scan execution failed: {response.output[:200]}"
        if logger:
            logger.error(msg)
        else:
            print(f"ERROR: {msg}")
        return ScanResult(
            zone_id=zone.zone_id,
            findings=[],
            scan_timestamp=scan_timestamp,
            adw_id=adw_id,
            raw_output=response.output,
        )

    # Parse the findings from the output file written by the slash command
    findings_file = PROJECT_ROOT / "agents" / adw_id / AGENT_NAME / "ci_scan" / "findings.json"

    # Also check if Claude wrote to the working directory
    alt_findings_file = PROJECT_ROOT / "ci_scan" / "findings.json"

    target_file = None
    if findings_file.exists():
        target_file = findings_file
    elif alt_findings_file.exists():
        target_file = alt_findings_file

    if target_file is None:
        msg = f"Findings file not found at {findings_file} or {alt_findings_file}"
        if logger:
            logger.warning(msg)
        else:
            print(f"WARNING: {msg}")
        return ScanResult(
            zone_id=zone.zone_id,
            findings=[],
            scan_timestamp=scan_timestamp,
            adw_id=adw_id,
            raw_output=response.output,
        )

    try:
        with open(target_file, "r") as f:
            data = json.load(f)

        raw_findings = data.get("findings", [])
        findings = [ScanFinding(**f) for f in raw_findings]

        msg = f"Parsed {len(findings)} findings from {target_file}"
        if logger:
            logger.info(msg)
        else:
            print(f"INFO: {msg}")

        return ScanResult(
            zone_id=zone.zone_id,
            findings=findings,
            scan_timestamp=scan_timestamp,
            adw_id=adw_id,
        )
    except (json.JSONDecodeError, Exception) as e:
        msg = f"Failed to parse findings JSON: {e}"
        if logger:
            logger.error(msg)
        else:
            print(f"ERROR: {msg}")
        return ScanResult(
            zone_id=zone.zone_id,
            findings=[],
            scan_timestamp=scan_timestamp,
            adw_id=adw_id,
            raw_output=response.output,
        )


def update_coverage_after_scan(
    coverage_state: CoverageState,
    zone: ScanZone,
    scan_result: ScanResult,
) -> None:
    """Update coverage state after a scan completes."""
    file_count = len(discover_zone_files(zone))
    coverage_state.zones[zone.zone_id] = CoverageEntry(
        zone_id=zone.zone_id,
        last_scanned=scan_result.scan_timestamp,
        scan_count=(coverage_state.zones.get(zone.zone_id, CoverageEntry(zone_id=zone.zone_id)).scan_count + 1),
        last_adw_id=scan_result.adw_id,
        files_at_scan=file_count,
    )

    # Check if all zones have been scanned (full rotation)
    all_zone_ids = {z.zone_id for z in SCAN_ZONES}
    scanned_zone_ids = {
        zid for zid, entry in coverage_state.zones.items()
        if entry.last_scanned is not None
    }
    if all_zone_ids <= scanned_zone_ids:
        coverage_state.last_full_rotation = scan_result.scan_timestamp


def main():
    """Main entry point for the continuous improvement scanner."""
    parser = argparse.ArgumentParser(
        description="Continuous Improvement Scanner - Scan codebase zones and create GitHub issues"
    )
    parser.add_argument(
        "--zone",
        type=str,
        default=None,
        help="Override rotation and scan a specific zone by ID",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Analyze zone but skip GitHub issue creation",
    )
    parser.add_argument(
        "--category",
        type=str,
        choices=["technical", "ux-business"],
        default=None,
        help="Only scan zones of this category",
    )
    parser.add_argument(
        "--adw-id",
        type=str,
        default=None,
        help="Use a specific ADW ID instead of generating one",
    )
    args = parser.parse_args()

    # Generate ADW ID
    adw_id = args.adw_id or make_adw_id()

    # Set up logger
    logger = setup_logger(adw_id, "adw_continuous_improvement")

    logger.info("=" * 60)
    logger.info("  ADW CONTINUOUS IMPROVEMENT SCANNER")
    logger.info("=" * 60)
    logger.info(f"  ADW ID:     {adw_id}")
    logger.info(f"  Zone:       {args.zone or 'auto-rotate'}")
    logger.info(f"  Category:   {args.category or 'all'}")
    logger.info(f"  Dry run:    {args.dry_run}")
    logger.info("=" * 60)

    # Check prerequisites
    check_env_vars(logger)
    if not args.dry_run:
        if not check_gh_authenticated():
            logger.error("GitHub CLI not authenticated. Run 'gh auth login' first.")
            sys.exit(1)

    # Load coverage state
    coverage_state = load_coverage_state()
    logger.info(f"Loaded coverage state: {len(coverage_state.zones)} zones tracked, "
                f"{len(coverage_state.created_finding_hashes)} finding hashes recorded")

    # Select zone
    if args.zone:
        zone_map = {z.zone_id: z for z in SCAN_ZONES}
        if args.zone not in zone_map:
            logger.error(f"Unknown zone '{args.zone}'. Available: {', '.join(zone_map.keys())}")
            sys.exit(1)
        zone = zone_map[args.zone]
        logger.info(f"Zone override: {zone.zone_id}")
    else:
        zone = select_next_zone(coverage_state, SCAN_ZONES, args.category)
        logger.info(f"Auto-selected zone: {zone.zone_id} (category={zone.category})")

    # Ensure labels exist before creating issues
    if not args.dry_run:
        ensure_labels_exist([
            "continuous-improvement",
            "technical",
            "ux-business",
            "severity-low",
            "severity-medium",
            "severity-high",
            "adw-generated",
        ])

    # Get repo path for issue creation
    repo_path = None
    if not args.dry_run:
        try:
            github_repo_url = get_repo_url()
            repo_path = extract_repo_path(github_repo_url)
        except ValueError as e:
            logger.error(f"Cannot determine repository: {e}")
            sys.exit(1)

    # Run the scan
    scan_result = run_scan(zone, adw_id, logger)
    logger.info(f"Scan complete: {len(scan_result.findings)} findings")

    # Create issues for findings
    if scan_result.findings:
        created = create_improvement_issues(
            scan_result.findings,
            zone,
            adw_id,
            scan_result.scan_timestamp,
            coverage_state,
            repo_path,
            dry_run=args.dry_run,
            logger=logger,
        )
        logger.info(f"Issues created: {len(created)}")
    else:
        logger.info("No findings — zone is healthy")

    # Update coverage state
    update_coverage_after_scan(coverage_state, zone, scan_result)
    save_coverage_state(coverage_state)
    logger.info(f"Coverage state saved to {COVERAGE_STATE_FILE}")

    # Clean up findings file if it was written to project root
    alt_findings_file = PROJECT_ROOT / "ci_scan" / "findings.json"
    if alt_findings_file.exists():
        alt_findings_file.unlink()
        ci_scan_dir = PROJECT_ROOT / "ci_scan"
        if ci_scan_dir.exists() and not any(ci_scan_dir.iterdir()):
            ci_scan_dir.rmdir()

    # Summary
    logger.info("=" * 60)
    logger.info(f"  SCAN SUMMARY")
    logger.info(f"  Zone:     {zone.zone_id}")
    logger.info(f"  Files:    {len(discover_zone_files(zone))}")
    logger.info(f"  Findings: {len(scan_result.findings)}")
    logger.info(f"  ADW ID:   {adw_id}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
