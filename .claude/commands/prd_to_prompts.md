# PRD to Implementation Prompts

Convert a structured PRD (Product Requirements Document) into an implementation prompts document. Each prompt becomes a self-contained GitHub issue body ready for ADW execution via `adw_sdlc_iso.py`.

## Input

`$ARGUMENTS` contains two parts separated by `---SPLIT---`:
- **Part 1:** Path to the PRD file
- **Part 2:** Path to an example prompts document to use as format reference

Example: `ai_docs/prds/my-feature-prd.md ---SPLIT--- ai_docs/tendery_v2_implementation_prompts.md`

## Processing Instructions

Follow these steps exactly:

### Step 1: Parse Input
- Split `$ARGUMENTS` on `---SPLIT---` to extract two paths.
- Trim whitespace from both paths.
- If `---SPLIT---` is not found, stop and report: "ERROR: Expected two file paths separated by `---SPLIT---`".

### Step 2: Read Source Files
- Read the PRD file at the first path.
- Read the example prompts document at the second path.
- If either file cannot be read, stop and report the error.

### Step 3: Analyze the PRD
Extract the following from the PRD:
- **Project name** (from the title or first heading)
- **Executive summary / overview** (project goal, key concepts)
- **Meeting metadata** (date, participants, source) if present
- **Work streams** with their requirements (REQ IDs, titles, descriptions, acceptance criteria, affected modules, dependencies, priorities)
- **Implementation waves** (grouping and ordering of requirements)
- **Naming conventions** (component prefixes, table prefixes, route prefixes) if present
- **Terminology** (domain-specific terms and definitions) if present
- **Open questions** if present

If the PRD has no explicit "Implementation Waves" section, infer waves from the work streams — group independent requirements into parallel waves and sequence dependent ones.

### Step 4: Analyze the Example Format
Study the example prompts document to learn the exact output structure:
- Overview section (source reference, project goal, execution command, parallelization note, naming conventions, terminology)
- Wave headers (`## Wave N: {Wave Name} (Run in Parallel)`)
- Issue format: ID prefix convention, Title format, Body structure
- Context section fields: Project, Overview, Current Wave, Current Issue, Parallel Execution, Dependencies, What comes next
- Request section structure: numbered sub-tasks with explicit file paths, code snippets, UI language notes, validation rules
- Separator pattern between issues (`---`)

### Step 5: Generate Prompts
For each requirement in the PRD, generate one implementation prompt (issue body):

#### Context Section
```
## Context
**Project:** {Project name} — {one-line project description}
**Overview:** {2-3 sentence description of what this specific prompt implements and why}

**Current Wave:** Wave {N} of {total} — {Wave Name}
**Current Issue:** {ID} (Issue {seq} of {total_issues})
**Parallel Execution:** {YES/NO} — {if YES, list which other issues run in parallel}

**Dependencies:** {List dependency IDs, or "None"}
**What comes next:** {Brief description of what the next wave or dependent issues will do with this work}
```

#### Request Section
```
## Request
{One-sentence summary of what to implement}

### 1. {First Sub-Task (e.g., Backend Models)}
{Description with explicit file paths}
{Code snippet if helpful}

### 2. {Second Sub-Task (e.g., Service Layer)}
{Description with explicit file paths}

### 3. {Third Sub-Task (e.g., Frontend Types)}
{Description with explicit file paths}
{Code snippet if helpful}

...continue as needed...

**UI Language:** {Spanish (Colombian) / English / N/A}
**Validation:** {Key validation rules for this prompt}
```

### Step 6: Assign IDs and Group into Waves
- Use an ID prefix derived from the project name (e.g., "TD" for Tendery, "ADW-PIPE" for ADW Pipeline).
- Assign sequential IDs within each wave: `{PREFIX}-001`, `{PREFIX}-002`, etc.
- Prompts within the same wave MUST NOT depend on each other.
- Order waves so that dependencies are satisfied: if Wave 2 prompts depend on Wave 1 outputs, Wave 1 runs first.

### Step 7: Assemble the Document
Combine everything into the output format below.

## Output Format

Generate a complete markdown document with this exact structure:

```
# {Project Name} - ADW Implementation Prompts

## Overview

This plan contains GitHub issue prompts for implementing {Project Name} using `adw_sdlc_iso.py`. Each prompt will trigger the `/feature` command which handles technical planning.

**Source:** {PRD source reference (meeting date, transcript, etc.)}
**Requirements Doc:** `{PRD file path}`

**Project Goal:** {2-3 sentence project goal from PRD}

**Key Concepts:**
{Numbered list of key domain concepts if present in PRD}

**Execution**: `uv run adw_sdlc_iso.py <issue-number>`

**Parallelization**: Issues within the same wave can run simultaneously in separate worktrees (up to 15 concurrent).

{**Naming Conventions:** section if present in PRD}

{**Terminology:** section if present in PRD}

---

## Wave 1: {Wave Name} (Run in Parallel)

{Brief description of what this wave accomplishes and why these issues can run in parallel.}

### {ID}: {Requirement Title}

**Title:** `[{Project Short Name}] Wave {N}: {Short Title}`

**Body:**
\```markdown
## Context
{Context section as specified above}

## Request
{Request section as specified above}
\```

---

### {ID}: {Next Requirement Title}

**Title:** `[{Project Short Name}] Wave {N}: {Short Title}`

**Body:**
\```markdown
## Context
...
## Request
...
\```

---

## Wave 2: {Wave Name} (Run in Parallel)

{Continue pattern for all waves...}

---
```

## Quality Rules

- **Self-contained:** Each prompt must be self-contained — an agent should be able to implement it without reading other prompts.
- **Explicit file paths:** Include explicit file paths for ALL files that need creation or modification.
- **Dependency references:** Reference dependencies by their prompt ID (e.g., "Depends on TD-001").
- **No intra-wave dependencies:** Prompts in the same wave MUST NOT depend on each other.
- **Parallel execution flag:** Include `**Parallel Execution:** YES/NO` on every prompt.
- **Code snippets:** Include code snippets (Python for backend, TypeScript for frontend) where they clarify intent — especially for DTOs, enums, interfaces, and API signatures.
- **UI language:** If the prompt involves UI text, include `**UI Language:** Spanish (Colombian)` (or the appropriate language).
- **Wave descriptions:** Each wave header should briefly explain what the wave accomplishes and why those issues can run in parallel.
- **Sequential numbering:** Issue IDs must be sequential across the entire document (not reset per wave).

Respond ONLY with the prompts markdown document. No preamble, no commentary.
