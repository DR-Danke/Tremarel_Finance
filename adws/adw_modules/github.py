#!/usr/bin/env -S uv run
# /// script
# dependencies = ["python-dotenv", "pydantic"]
# ///

"""
GitHub Operations Module - AI Developer Workflow (ADW)

This module contains all GitHub-related operations including:
- Issue fetching and manipulation
- Comment posting
- Repository path extraction
- Issue status management
"""

import subprocess
import sys
import os
import json
import time
from typing import Dict, List, Optional
from .data_types import GitHubIssue, GitHubIssueListItem, GitHubComment

# Bot identifier to prevent webhook loops and filter bot comments
ADW_BOT_IDENTIFIER = "[ADW-AGENTS]"


def get_github_env() -> Optional[dict]:
    """Get environment with GitHub token set up. Returns None if no GITHUB_PAT.
    
    Subprocess env behavior:
    - env=None → Inherits parent's environment (default)
    - env={} → Empty environment (no variables)
    - env=custom_dict → Only uses specified variables
    
    So this will work with gh authentication:
    # These are equivalent:
    result = subprocess.run(cmd, capture_output=True, text=True)
    result = subprocess.run(cmd, capture_output=True, text=True, env=None)
    
    But this will NOT work (no PATH, no auth):
    result = subprocess.run(cmd, capture_output=True, text=True, env={})
    """
    github_pat = os.getenv("GITHUB_PAT")
    if not github_pat:
        return None
    
    # Only create minimal env with GitHub token
    env = {
        "GH_TOKEN": github_pat,
        "PATH": os.environ.get("PATH", ""),
    }
    return env


def get_repo_url() -> str:
    """Get GitHub repository URL from git remote."""
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        raise ValueError(
            "No git remote 'origin' found. Please ensure you're in a git repository with a remote."
        )
    except FileNotFoundError:
        raise ValueError("git command not found. Please ensure git is installed.")


def extract_repo_path(github_url: str) -> str:
    """Extract owner/repo from GitHub URL."""
    # Handle both https://github.com/owner/repo and https://github.com/owner/repo.git
    return github_url.replace("https://github.com/", "").replace(".git", "")


def fetch_issue(issue_number: str, repo_path: str, max_retries: int = 3) -> GitHubIssue:
    """Fetch GitHub issue using gh CLI and return typed model.

    Retries on network failures with exponential backoff.
    """
    # Use JSON output for structured data
    cmd = [
        "gh",
        "issue",
        "view",
        issue_number,
        "-R",
        repo_path,
        "--json",
        "number,title,body,state,author,assignees,labels,milestone,comments,createdAt,updatedAt,closedAt,url",
    ]

    # Set up environment with GitHub token if available
    env = get_github_env()

    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, env=env, timeout=30
            )

            if result.returncode == 0:
                # Parse JSON response into Pydantic model
                issue_data = json.loads(result.stdout)
                issue = GitHubIssue(**issue_data)
                return issue
            else:
                last_error = result.stderr
                # Retry on network errors
                if any(kw in last_error.lower() for kw in ["timeout", "i/o", "dial tcp"]):
                    if attempt < max_retries:
                        wait = 2 ** attempt
                        print(f"Network error fetching issue (attempt {attempt}/{max_retries}), retrying in {wait}s: {last_error.strip()}", file=sys.stderr)
                        time.sleep(wait)
                        continue
                print(result.stderr, file=sys.stderr)
                sys.exit(result.returncode)
        except subprocess.TimeoutExpired:
            last_error = "subprocess timed out after 30s"
            if attempt < max_retries:
                wait = 2 ** attempt
                print(f"gh command timed out (attempt {attempt}/{max_retries}), retrying in {wait}s", file=sys.stderr)
                time.sleep(wait)
                continue
        except FileNotFoundError:
            print("Error: GitHub CLI (gh) is not installed.", file=sys.stderr)
            print("\nTo install gh:", file=sys.stderr)
            print("  - macOS: brew install gh", file=sys.stderr)
            print(
                "  - Linux: See https://github.com/cli/cli#installation",
                file=sys.stderr,
            )
            print(
                "  - Windows: See https://github.com/cli/cli#installation", file=sys.stderr
            )
            print("\nAfter installation, authenticate with: gh auth login", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            last_error = str(e)
            if attempt < max_retries:
                wait = 2 ** attempt
                print(f"Error fetching issue (attempt {attempt}/{max_retries}), retrying in {wait}s: {e}", file=sys.stderr)
                time.sleep(wait)
                continue

    # All retries exhausted
    print(f"Failed to fetch issue after {max_retries} attempts: {last_error}", file=sys.stderr)
    sys.exit(1)


def make_issue_comment(issue_id: str, comment: str, max_retries: int = 3) -> None:
    """Post a comment to a GitHub issue using gh CLI.

    Retries up to max_retries times with exponential backoff on network failures
    (common in WSL2 environments with intermittent DNS/connectivity issues).
    """
    # Get repo information from git remote
    github_repo_url = get_repo_url()
    repo_path = extract_repo_path(github_repo_url)

    # Ensure comment has ADW_BOT_IDENTIFIER to prevent webhook loops
    if not comment.startswith(ADW_BOT_IDENTIFIER):
        comment = f"{ADW_BOT_IDENTIFIER} {comment}"

    # Build command
    cmd = [
        "gh",
        "issue",
        "comment",
        issue_id,
        "-R",
        repo_path,
        "--body",
        comment,
    ]

    # Set up environment with GitHub token if available
    env = get_github_env()

    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, env=env, timeout=30
            )

            if result.returncode == 0:
                print(f"Successfully posted comment to issue #{issue_id}")
                return
            else:
                last_error = result.stderr
                # Check if this is a network/timeout error worth retrying
                if "timeout" in last_error.lower() or "i/o" in last_error.lower() or "dial tcp" in last_error.lower():
                    if attempt < max_retries:
                        wait = 2 ** attempt  # 2s, 4s, 8s
                        print(f"Network error posting comment (attempt {attempt}/{max_retries}), retrying in {wait}s: {last_error.strip()}", file=sys.stderr)
                        time.sleep(wait)
                        continue
                # Non-network error, fail immediately
                print(f"Error posting comment: {last_error}", file=sys.stderr)
                raise RuntimeError(f"Failed to post comment: {last_error}")
        except subprocess.TimeoutExpired:
            last_error = "subprocess timed out after 30s"
            if attempt < max_retries:
                wait = 2 ** attempt
                print(f"gh command timed out (attempt {attempt}/{max_retries}), retrying in {wait}s", file=sys.stderr)
                time.sleep(wait)
                continue
        except RuntimeError:
            raise
        except Exception as e:
            last_error = str(e)
            if attempt < max_retries:
                wait = 2 ** attempt
                print(f"Error posting comment (attempt {attempt}/{max_retries}), retrying in {wait}s: {e}", file=sys.stderr)
                time.sleep(wait)
                continue

    # All retries exhausted
    print(f"Failed to post comment after {max_retries} attempts: {last_error}", file=sys.stderr)
    raise RuntimeError(f"Failed to post comment after {max_retries} retries: {last_error}")


def mark_issue_in_progress(issue_id: str) -> None:
    """Mark issue as in progress by adding label and comment."""
    # Get repo information from git remote
    github_repo_url = get_repo_url()
    repo_path = extract_repo_path(github_repo_url)

    # Add "in_progress" label
    cmd = [
        "gh",
        "issue",
        "edit",
        issue_id,
        "-R",
        repo_path,
        "--add-label",
        "in_progress",
    ]

    # Set up environment with GitHub token if available
    env = get_github_env()

    # Try to add label (may fail if label doesn't exist)
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=30)
        if result.returncode != 0:
            print(f"Note: Could not add 'in_progress' label: {result.stderr}")
    except subprocess.TimeoutExpired:
        print("Note: Timed out adding 'in_progress' label")

    # Post comment indicating work has started
    # make_issue_comment(issue_id, "🚧 ADW is working on this issue...")

    # Assign to self (optional)
    cmd = [
        "gh",
        "issue",
        "edit",
        issue_id,
        "-R",
        repo_path,
        "--add-assignee",
        "@me",
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=30)
        if result.returncode == 0:
            print(f"Assigned issue #{issue_id} to self")
    except subprocess.TimeoutExpired:
        print("Note: Timed out assigning issue to self")


def fetch_open_issues(repo_path: str) -> List[GitHubIssueListItem]:
    """Fetch all open issues from the GitHub repository."""
    try:
        cmd = [
            "gh",
            "issue",
            "list",
            "--repo",
            repo_path,
            "--state",
            "open",
            "--json",
            "number,title,body,labels,createdAt,updatedAt",
            "--limit",
            "1000",
        ]

        # Set up environment with GitHub token if available
        env = get_github_env()

        # DEBUG level - not printing command
        result = subprocess.run(
            cmd, capture_output=True, text=True, check=True, env=env, timeout=30
        )

        issues_data = json.loads(result.stdout)
        issues = [GitHubIssueListItem(**issue_data) for issue_data in issues_data]
        print(f"Fetched {len(issues)} open issues")
        return issues

    except subprocess.TimeoutExpired:
        print("ERROR: Timed out fetching open issues", file=sys.stderr)
        return []
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to fetch issues: {e.stderr}", file=sys.stderr)
        return []
    except json.JSONDecodeError as e:
        print(f"ERROR: Failed to parse issues JSON: {e}", file=sys.stderr)
        return []


def fetch_issue_comments(repo_path: str, issue_number: int) -> List[Dict]:
    """Fetch all comments for a specific issue."""
    try:
        cmd = [
            "gh",
            "issue",
            "view",
            str(issue_number),
            "--repo",
            repo_path,
            "--json",
            "comments",
        ]

        # Set up environment with GitHub token if available
        env = get_github_env()

        result = subprocess.run(
            cmd, capture_output=True, text=True, check=True, env=env, timeout=30
        )
        data = json.loads(result.stdout)
        comments = data.get("comments", [])

        # Sort comments by creation time
        comments.sort(key=lambda c: c.get("createdAt", ""))

        # DEBUG level - not printing
        return comments

    except subprocess.TimeoutExpired:
        print(
            f"ERROR: Timed out fetching comments for issue #{issue_number}",
            file=sys.stderr,
        )
        return []
    except subprocess.CalledProcessError as e:
        print(
            f"ERROR: Failed to fetch comments for issue #{issue_number}: {e.stderr}",
            file=sys.stderr,
        )
        return []
    except json.JSONDecodeError as e:
        print(
            f"ERROR: Failed to parse comments JSON for issue #{issue_number}: {e}",
            file=sys.stderr,
        )
        return []


def find_keyword_from_comment(keyword: str, issue: GitHubIssue) -> Optional[GitHubComment]:
    """Find the latest comment containing a specific keyword.

    Args:
        keyword: The keyword to search for in comments
        issue: The GitHub issue containing comments

    Returns:
        The latest GitHubComment containing the keyword, or None if not found
    """
    # Sort comments by created_at date (newest first)
    sorted_comments = sorted(issue.comments, key=lambda c: c.created_at, reverse=True)

    # Search through sorted comments (newest first)
    for comment in sorted_comments:
        # Skip ADW bot comments to prevent loops
        if ADW_BOT_IDENTIFIER in comment.body:
            continue

        if keyword in comment.body:
            return comment

    return None


# GitHub comment size limit (leaving some buffer for formatting)
GITHUB_COMMENT_MAX_SIZE = 65000


def upload_file_as_comment(
    issue_number: str,
    file_path: str,
    adw_id: str,
    file_type: str,
    worktree_path: Optional[str] = None,
) -> bool:
    """Upload a file's content as a GitHub issue comment.

    The content is wrapped in a collapsible <details> section for better readability.
    If the file content exceeds GitHub's comment size limit, it will be truncated
    with a note indicating truncation.

    Args:
        issue_number: GitHub issue number
        file_path: Path to the file (relative or absolute)
        adw_id: ADW workflow ID for tracking
        file_type: Type of file ('plan' or 'documentation')
        worktree_path: Optional worktree path to resolve relative paths

    Returns:
        True if upload succeeded, False otherwise
    """
    # Resolve the full path
    if worktree_path and not os.path.isabs(file_path):
        full_path = os.path.join(worktree_path, file_path)
    else:
        full_path = file_path

    # Read the file content
    try:
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"ERROR: File not found for upload: {full_path}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"ERROR: Failed to read file {full_path}: {e}", file=sys.stderr)
        return False

    # Determine the emoji and title based on file type
    if file_type == "plan":
        emoji = "📋"
        title = "Implementation Plan"
    elif file_type == "documentation":
        emoji = "📚"
        title = "Generated Documentation"
    else:
        emoji = "📄"
        title = f"File: {file_type}"

    # Check if content needs truncation
    truncated = False
    if len(content) > GITHUB_COMMENT_MAX_SIZE:
        content = content[:GITHUB_COMMENT_MAX_SIZE]
        truncated = True

    # Build the comment with collapsible section
    truncation_note = "\n\n---\n⚠️ *Content truncated due to GitHub comment size limit. See full file in repository.*" if truncated else ""

    comment = (
        f"{adw_id}_ops: {emoji} **{title}**\n\n"
        f"<details>\n"
        f"<summary>Click to expand {file_type} content ({os.path.basename(file_path)})</summary>\n\n"
        f"```markdown\n{content}\n```{truncation_note}\n"
        f"</details>"
    )

    # Post the comment
    try:
        make_issue_comment(issue_number, comment)
        print(f"Successfully uploaded {file_type} to issue #{issue_number}")
        return True
    except Exception as e:
        print(f"ERROR: Failed to upload {file_type} as comment: {e}", file=sys.stderr)
        return False
