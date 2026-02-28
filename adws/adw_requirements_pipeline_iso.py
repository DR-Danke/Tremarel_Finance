#!/usr/bin/env -S uv run
# /// script
# dependencies = ["python-dotenv", "pydantic"]
# ///

"""
ADW Requirements Pipeline Orchestrator - End-to-end transcript to GitHub issues pipeline

Usage:
  uv run adw_requirements_pipeline_iso.py <transcript-path> [adw-id] [--example <path>] [--skip-issues]

Pipeline Stages:
  1. adw_transcript_to_prd_iso.py   — Transcript → PRD
  2. adw_prd_to_prompts_iso.py      — PRD → Implementation Prompts
  3. adw_prompts_to_issues_iso.py   — Prompts → GitHub Issues

This orchestrator chains the three stages via subprocess, parsing each stage's
stdout to extract artifact paths for the next stage. All stages share the same
ADW ID for worktree reuse.

Flags:
  --skip-issues   Stop after Stage 2 (PRD → Prompts), do not create GitHub issues
  --example PATH  Custom example prompts path for Stage 2 (default: ai_docs/tendery_v2_implementation_prompts.md)
"""

import subprocess
import sys
import os
import re

# Add the parent directory to Python path to import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from adw_modules.workflow_ops import ensure_adw_id
from adw_modules.state import ADWState


def parse_success_path(output: str, prefix: str) -> str | None:
    """Extract file path from subprocess stdout using a SUCCESS prefix pattern.

    Looks for lines like: SUCCESS: {prefix} at {path}
    Returns the path or None if not found.
    """
    pattern = rf"SUCCESS:\s*{re.escape(prefix)}\s+at\s+(.+)"
    match = re.search(pattern, output)
    if match:
        return match.group(1).strip()
    return None


def parse_issue_numbers(output: str) -> list[str]:
    """Extract issue numbers (#NNN) from subprocess stdout."""
    return re.findall(r"#(\d+)", output)


def main():
    """Main entry point."""
    # Check for flags
    skip_issues = "--skip-issues" in sys.argv
    example_path = None

    # Extract --example flag
    args = list(sys.argv)
    if "--skip-issues" in args:
        args.remove("--skip-issues")
    if "--example" in args:
        idx = args.index("--example")
        if idx + 1 < len(args):
            example_path = args[idx + 1]
            args.pop(idx + 1)
            args.pop(idx)
        else:
            print("ERROR: --example requires a path argument")
            sys.exit(1)

    if len(args) < 2:
        print("Usage: uv run adw_requirements_pipeline_iso.py <transcript-path> [adw-id] [--example <path>] [--skip-issues]")
        print()
        print("Pipeline Stages:")
        print("  1. Transcript → PRD")
        print("  2. PRD → Implementation Prompts")
        print("  3. Prompts → GitHub Issues")
        print()
        print("Flags:")
        print("  --skip-issues   Stop after Stage 2 (skip GitHub issue creation)")
        print("  --example PATH  Custom example prompts path for Stage 2")
        sys.exit(1)

    transcript_path = args[1]
    adw_id = args[2] if len(args) > 2 else None

    # Validate transcript file exists
    if not os.path.exists(transcript_path):
        print(f"ERROR: Transcript file not found: {transcript_path}")
        sys.exit(1)

    SUPPORTED_EXTENSIONS = (".md", ".pdf")
    if not transcript_path.endswith(SUPPORTED_EXTENSIONS):
        print(f"ERROR: Transcript file must be one of {SUPPORTED_EXTENSIONS}: {transcript_path}")
        sys.exit(1)

    # Make transcript path absolute
    transcript_path = os.path.abspath(transcript_path)

    # Ensure ADW ID exists with initialized state
    adw_id = ensure_adw_id("pipeline", adw_id)
    print(f"Using ADW ID: {adw_id}")

    # Load state
    state = ADWState.load(adw_id)
    if not state.get("adw_id"):
        state.update(adw_id=adw_id)

    # Track workflow
    state.append_adw_id("adw_requirements_pipeline_iso")
    state.save("adw_requirements_pipeline_iso")

    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Create pipeline log directory
    pipeline_log_dir = os.path.join(
        os.path.dirname(script_dir), "agents", adw_id, "pipeline"
    )
    os.makedirs(pipeline_log_dir, exist_ok=True)

    # Pipeline header
    print()
    print("=" * 60)
    print("  ADW REQUIREMENTS PIPELINE ORCHESTRATOR")
    print("=" * 60)
    print(f"  ADW ID:       {adw_id}")
    print(f"  Transcript:   {transcript_path}")
    print(f"  Skip Issues:  {skip_issues}")
    if example_path:
        print(f"  Example:      {example_path}")
    print("=" * 60)
    print()

    # Track pipeline results
    prd_path = None
    prompts_path = None
    created_issues = []

    # =========================================================================
    # STAGE 1: Transcript → PRD
    # =========================================================================
    stage1_cmd = [
        "uv",
        "run",
        os.path.join(script_dir, "adw_transcript_to_prd_iso.py"),
        transcript_path,
        adw_id,
    ]
    print(f"\n=== STAGE 1: Transcript → PRD ===")
    print(f"Running: {' '.join(stage1_cmd)}")

    stage1 = subprocess.run(stage1_cmd, capture_output=True, text=True)

    # Write stage output to log
    with open(os.path.join(pipeline_log_dir, "stage1_stdout.log"), "w") as f:
        f.write(stage1.stdout)
    if stage1.stderr:
        with open(os.path.join(pipeline_log_dir, "stage1_stderr.log"), "w") as f:
            f.write(stage1.stderr)

    if stage1.returncode != 0:
        print(f"\nERROR: Stage 1 (Transcript → PRD) failed with exit code {stage1.returncode}")
        print(f"STDOUT:\n{stage1.stdout}")
        print(f"STDERR:\n{stage1.stderr}")
        state.save("adw_requirements_pipeline_iso")
        sys.exit(1)

    # Parse PRD path from stdout
    prd_path = parse_success_path(stage1.stdout, "PRD generated")
    if not prd_path:
        print(f"\nERROR: Could not parse PRD path from Stage 1 output")
        print(f"STDOUT:\n{stage1.stdout}")
        state.save("adw_requirements_pipeline_iso")
        sys.exit(1)

    print(f"  ✓ PRD generated: {prd_path}")
    state.update(plan_file=prd_path)
    state.save("adw_requirements_pipeline_iso")

    # =========================================================================
    # STAGE 2: PRD → Implementation Prompts
    # =========================================================================
    # Construct the full PRD path inside the worktree
    prd_full_path = os.path.join(
        os.path.dirname(script_dir), "trees", adw_id, prd_path
    )

    stage2_cmd = [
        "uv",
        "run",
        os.path.join(script_dir, "adw_prd_to_prompts_iso.py"),
        prd_full_path,
        adw_id,
    ]
    if example_path:
        stage2_cmd.extend(["--example", example_path])

    print(f"\n=== STAGE 2: PRD → Implementation Prompts ===")
    print(f"Running: {' '.join(stage2_cmd)}")

    stage2 = subprocess.run(stage2_cmd, capture_output=True, text=True)

    # Write stage output to log
    with open(os.path.join(pipeline_log_dir, "stage2_stdout.log"), "w") as f:
        f.write(stage2.stdout)
    if stage2.stderr:
        with open(os.path.join(pipeline_log_dir, "stage2_stderr.log"), "w") as f:
            f.write(stage2.stderr)

    if stage2.returncode != 0:
        print(f"\nERROR: Stage 2 (PRD → Prompts) failed with exit code {stage2.returncode}")
        print(f"STDOUT:\n{stage2.stdout}")
        print(f"STDERR:\n{stage2.stderr}")
        state.save("adw_requirements_pipeline_iso")
        sys.exit(1)

    # Parse prompts path from stdout
    prompts_path = parse_success_path(stage2.stdout, "Prompts document generated")
    if not prompts_path:
        print(f"\nERROR: Could not parse prompts path from Stage 2 output")
        print(f"STDOUT:\n{stage2.stdout}")
        state.save("adw_requirements_pipeline_iso")
        sys.exit(1)

    print(f"  ✓ Prompts generated: {prompts_path}")
    state.update(prompts_file=prompts_path)
    state.save("adw_requirements_pipeline_iso")

    # =========================================================================
    # STAGE 3: Prompts → GitHub Issues (unless --skip-issues)
    # =========================================================================
    if skip_issues:
        print(f"\n=== STAGE 3: SKIPPED (--skip-issues) ===")
    else:
        # Construct the full prompts path inside the worktree
        prompts_full_path = os.path.join(
            os.path.dirname(script_dir), "trees", adw_id, prompts_path
        )

        stage3_cmd = [
            "uv",
            "run",
            os.path.join(script_dir, "adw_prompts_to_issues_iso.py"),
            prompts_full_path,
            adw_id,
        ]

        print(f"\n=== STAGE 3: Prompts → GitHub Issues ===")
        print(f"Running: {' '.join(stage3_cmd)}")

        stage3 = subprocess.run(stage3_cmd, capture_output=True, text=True)

        # Write stage output to log
        with open(os.path.join(pipeline_log_dir, "stage3_stdout.log"), "w") as f:
            f.write(stage3.stdout)
        if stage3.stderr:
            with open(os.path.join(pipeline_log_dir, "stage3_stderr.log"), "w") as f:
                f.write(stage3.stderr)

        if stage3.returncode != 0:
            print(f"\nERROR: Stage 3 (Prompts → Issues) failed with exit code {stage3.returncode}")
            print(f"STDOUT:\n{stage3.stdout}")
            print(f"STDERR:\n{stage3.stderr}")
            state.save("adw_requirements_pipeline_iso")
            sys.exit(1)

        # Parse created issue numbers
        created_issues = parse_issue_numbers(stage3.stdout)
        print(f"  ✓ Created {len(created_issues)} GitHub issues")
        if created_issues:
            print(f"    Issues: {', '.join(f'#{n}' for n in created_issues)}")

        # Store created issues in state
        state.data["created_issues"] = created_issues
        state.save("adw_requirements_pipeline_iso")

    # =========================================================================
    # MERGE TO MAIN
    # =========================================================================
    print(f"\n=== MERGE: Branch → main ===")

    branch_name = state.get("branch_name") or f"transcript-prd-{adw_id}"

    # Get project root (parent of adws directory)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    from adw_modules.git_ops import merge_branch_to_main

    merge_success, merge_error = merge_branch_to_main(branch_name, cwd=project_root)

    if merge_success:
        print(f"  ✓ Merged {branch_name} → main and pushed")
        merge_status = "MERGED"
    else:
        print(f"  ✗ Merge failed: {merge_error}")
        print(f"    Branch {branch_name} is still available for manual merge")
        merge_status = f"FAILED ({merge_error})"

    # =========================================================================
    # SUMMARY
    # =========================================================================
    print()
    print("=" * 60)
    print("  PIPELINE COMPLETE")
    print("=" * 60)
    print(f"  ADW ID:       {adw_id}")
    print(f"  Transcript:   {os.path.basename(transcript_path)}")
    print(f"  PRD:          {prd_path}")
    print(f"  Prompts:      {prompts_path}")
    if skip_issues:
        print(f"  Issues:       SKIPPED (--skip-issues)")
    elif created_issues:
        print(f"  Issues:       {', '.join(f'#{n}' for n in created_issues)}")
    else:
        print(f"  Issues:       0 created")
    print(f"  Merge:        {merge_status}")
    print(f"  Worktree:     trees/{adw_id}/")
    print(f"  Logs:         agents/{adw_id}/pipeline/")
    print("=" * 60)
    print()
    print("Pipeline complete. Comment \"adw_run\" on any issue to begin development.")


if __name__ == "__main__":
    main()
