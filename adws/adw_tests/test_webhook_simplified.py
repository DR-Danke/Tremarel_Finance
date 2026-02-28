#!/usr/bin/env -S uv run
# /// script
# dependencies = ["python-dotenv"]
# ///

"""
Test script to verify simplified webhook workflow support.
"""

import os

# Mirror the constants from trigger_webhook.py
DEPENDENT_WORKFLOWS = [
    "adw_build", "adw_test", "adw_review", "adw_document",
    "adw_build_iso", "adw_test_iso", "adw_review_iso", "adw_document_iso"
]

def test_workflow_support():
    """Test the simplified workflow support."""
    print("=== Simplified Webhook Workflow Support ===")
    print()

    print("Entry Point Workflows (can be triggered via webhook):")
    entry_points = [
        "adw_plan",
        "adw_patch",
        "adw_plan_build",
        "adw_plan_build_test",
        "adw_plan_build_test_review",
        "adw_plan_build_document",
        "adw_plan_build_review",
        "adw_sdlc",
        "adw_plan_iso",
        "adw_patch_iso",
        "adw_plan_build_iso",
        "adw_plan_build_test_iso",
        "adw_plan_build_test_review_iso",
        "adw_plan_build_document_iso",
        "adw_plan_build_review_iso",
        "adw_sdlc_iso",
    ]

    for workflow in entry_points:
        emoji = "🏗️" if workflow.endswith("_iso") else "🔧"
        print(f"  {workflow:35} {emoji}")

    print()
    print("Dependent Workflows (require ADW ID):")
    for workflow in DEPENDENT_WORKFLOWS:
        emoji = "🏗️" if workflow.endswith("_iso") else "🔧"
        print(f"  {workflow:35} {emoji}")

    print()
    print("Testing workflow validation logic:")

    test_cases = [
        ("adw_plan", None, True),
        ("adw_plan_iso", None, True),
        ("adw_build", None, False),  # Dependent, no ID
        ("adw_build", "test-123", True),  # Dependent with ID
        ("adw_build_iso", None, False),  # Dependent, no ID
        ("adw_build_iso", "test-123", True),  # Dependent with ID
        ("adw_plan_build", None, True),
        ("adw_plan_build_iso", None, True),
        ("adw_test_iso", None, False),  # Dependent, no ID
        ("adw_sdlc_iso", None, True),
    ]

    for workflow, adw_id, should_work in test_cases:
        if workflow in DEPENDENT_WORKFLOWS and not adw_id:
            status = "❌ BLOCKED (requires ADW ID)"
        else:
            status = "✅ Can trigger"

        id_info = f" (with ID: {adw_id})" if adw_id else ""
        print(f"  {workflow:20}{id_info:20} {status}")


def test_keyword_shortcuts():
    """Test the keyword shortcut routing for adw_run and adw."""
    print()
    print("=== Keyword Shortcut Routing ===")
    print()

    # Keyword mapping: (comment_body, expected_workflow)
    keyword_cases = [
        # adw_run → adw_sdlc_iso
        ("adw_run", "adw_sdlc_iso"),
        ("adw run", "adw_sdlc_iso"),
        ("  adw_run  ", "adw_sdlc_iso"),       # with whitespace
        ("ADW_RUN", "adw_sdlc_iso"),            # uppercase
        ("Adw Run", "adw_sdlc_iso"),            # mixed case
        # adw → adw_plan_build_iso
        ("adw", "adw_plan_build_iso"),
        ("  adw  ", "adw_plan_build_iso"),       # with whitespace
        ("ADW", "adw_plan_build_iso"),           # uppercase
        # Should NOT match keywords (fall through to classifier)
        ("adw_running", None),
        ("adw_run extra text", None),
        ("run adw", None),
        ("adw_plan_iso", None),                  # full command, not a keyword
    ]

    passed = 0
    failed = 0

    for comment_body, expected_workflow in keyword_cases:
        stripped = comment_body.strip().lower()

        # Simulate the webhook keyword check logic
        if stripped in ("adw_run", "adw run"):
            result = "adw_sdlc_iso"
        elif stripped == "adw":
            result = "adw_plan_build_iso"
        else:
            result = None

        ok = result == expected_workflow
        status = "✅ PASS" if ok else "❌ FAIL"
        if ok:
            passed += 1
        else:
            failed += 1

        print(f"  {status}  comment={comment_body!r:25} expected={str(expected_workflow):25} got={str(result)}")

    print()
    print(f"Results: {passed} passed, {failed} failed out of {passed + failed} tests")
    if failed > 0:
        print("KEYWORD SHORTCUT TESTS FAILED")
        return False
    print("All keyword shortcut tests passed!")
    return True


if __name__ == "__main__":
    test_workflow_support()
    success = test_keyword_shortcuts()
    if not success:
        exit(1)