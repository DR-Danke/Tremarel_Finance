# Prompts to GitHub Issues

Parse an ADW implementation prompts document and create one GitHub issue per prompt using the `gh` CLI.

## Input

`$ARGUMENTS` is the path to the implementation prompts markdown file.

## Processing Instructions

Follow these steps exactly:

### Step 1: Read the Prompts File
- Read the file at the path given in `$ARGUMENTS`.
- If the file cannot be read, stop and report: "ERROR: Cannot read prompts file at: $ARGUMENTS"

### Step 2: Parse Issues from the Document

The prompts document has a consistent structure. Extract each issue using these patterns:

Each issue block looks like this:
```
### {ID}: {Description Title}

**Title:** `{issue title text}`

**Body:**
\```markdown
{issue body content — may be many lines, may contain nested code blocks}
\```
```

For each issue block, extract:
1. **ID** — the prompt ID (e.g., `CF-001`, `CFR-003`, `TD-022`)
2. **Title** — the text inside backticks after `**Title:**` (e.g., `[Cumplidos] Wave 1: Document Type Master Catalog`)
3. **Body** — everything between the opening ` ```markdown ` after `**Body:**` and its matching closing ` ``` `

**CRITICAL — Nested code blocks:** The body content itself contains fenced code blocks (` ```sql `, ` ```python `, ` ```typescript `, etc.). You must correctly handle these nested blocks. The body ends at the ` ``` ` that is at the SAME indentation level as the opening ` ```markdown ` — not at any inner code block fence. Use the fact that inner code blocks always have a language identifier (sql, python, typescript, etc.) while the closing fence is a bare ` ``` ` on its own line.

### Step 3: Validate Parsed Issues
- Print: `INFO: Parsed {count} issues from prompts document`
- For each issue, print: `INFO: {ID} — {Title}`
- If 0 issues were parsed, stop and report: "ERROR: No issues found in prompts document. Check the file format."

### Step 4: Determine Labels
- Extract the project short name from the first issue title (the text in square brackets, e.g., `Cumplidos` from `[Cumplidos] Wave 1: ...`)
- Use this as a label. Also add `adw-generated` as a second label.
- Before creating issues, ensure both labels exist in the repo. Use `gh label create` for any that don't exist (use `--force` to avoid errors if they already exist).

### Step 5: Create GitHub Issues
For each parsed issue, create a GitHub issue using the `gh` CLI:

```bash
gh issue create \
  --title "{Title}" \
  --body "{Body}" \
  --label "{project_label}" \
  --label "adw-generated"
```

**IMPORTANT:**
- Use a HEREDOC to pass the body to avoid shell escaping issues with the markdown content.
- Create issues in the order they appear in the document (preserving wave ordering).
- After each issue is created, print: `CREATED: #{issue_number} — {ID} — {Title}`
- If an issue creation fails, print the error but continue with the remaining issues. Do NOT stop on failure.

### Step 6: Print Summary Table

After all issues are created, print a summary:

```
=== ISSUE CREATION SUMMARY ===
Prompts File: {filename}
Total Parsed: {count}
Created:      {created_count}
Failed:       {failed_count}

| # | ID | Title | Issue |
|---|-----|-------|-------|
| 1 | {ID} | {Title} | #{issue_number} |
| 2 | {ID} | {Title} | #{issue_number} |
...
================================
```

## Important Notes

- Do NOT modify the prompts file.
- Do NOT create branches, make commits, or modify any code.
- The ONLY external action is creating GitHub issues via `gh issue create`.
- If `gh` is not authenticated, stop immediately and report: "ERROR: gh CLI is not authenticated. Run 'gh auth login' first."
- Verify `gh auth status` before starting issue creation.

Respond with the summary table at the end. Include every `CREATED: #NNN` line in your output so the calling system can parse issue numbers.
