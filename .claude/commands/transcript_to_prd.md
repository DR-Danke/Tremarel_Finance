# Transcript to PRD

Parse the meeting transcript below and produce a structured Product Requirements Document (PRD). The PRD must be structured enough for a downstream agent to convert it into implementation prompts.

## Input

The full meeting transcript text is provided below:

$ARGUMENTS

## Processing Instructions

Analyze the transcript and perform the following steps:

1. **Identify all actionable items** — Extract every distinct feature request, bug report, process change, and architectural decision mentioned in the transcript. Items may appear non-contiguously; group related items even if they are scattered throughout the conversation.

2. **Group into work streams** — Organize related items into logical work streams (e.g., "User Authentication", "Pricing Engine", "UI Improvements"). Each stream should represent a cohesive area of work.

3. **Extract metadata for each requirement** — For every requirement, extract:
   - **REQ ID**: Sequential identifier (REQ-001, REQ-002, etc.)
   - **Title**: Short, descriptive title
   - **Description**: Detailed explanation of what is needed
   - **Type**: One of `feature`, `bug`, `process_change`, `architecture_decision`
   - **Priority**: One of `P0` (critical/blocking), `P1` (high/must-have), `P2` (medium/should-have), `P3` (nice-to-have)
   - **Acceptance Criteria**: At least one measurable criterion per requirement
   - **Affected Modules**: Which parts of the system are impacted
   - **Dependencies**: References to other REQ IDs from this document that must be completed first

4. **Determine implementation waves** — Sequence the work streams into implementation waves based on dependencies and priority. Wave 1 contains foundational work with no dependencies; later waves build on earlier ones.

5. **Flag ambiguity** — If a transcript item is vague, contradictory, or lacks enough detail to define a clear requirement, place it in the "Open Questions" section rather than guessing the intent.

## Quality Rules

- Every requirement MUST have at least one Acceptance Criteria entry.
- Dependencies MUST reference valid REQ IDs from the same document.
- Ambiguous or unclear items MUST go to "Open Questions" — do NOT guess intent.
- Output MUST be in English even if the transcript is in Spanish or another language.
- If the transcript contains no clear actionable items, produce a PRD with empty Work Streams and a note in Open Questions explaining that no actionable items were identified.

## Output Format

Respond ONLY with the PRD markdown document below. No preamble, no commentary.

```
# PRD: {Meeting Topic}

## Meeting Metadata
- **Date**: {extracted or "Not specified"}
- **Participants**: {extracted or "Not specified"}
- **Duration**: {extracted or "Not specified"}
- **Context**: {brief description of the meeting purpose}

## Executive Summary
{2-4 sentence summary of the key decisions, priorities, and scope discussed in the meeting}

## Work Streams

### Stream 1: {Stream Name}
{Brief description of this work stream's scope and goals}

#### Requirements

##### REQ-001: {Title}
- **Type**: {feature | bug | process_change | architecture_decision}
- **Priority**: {P0 | P1 | P2 | P3}
- **Description**: {Detailed description}
- **Affected Modules**: {List of affected modules/files}
- **Dependencies**: {REQ IDs or "None"}
- **Acceptance Criteria**:
  - [ ] {Measurable criterion 1}
  - [ ] {Measurable criterion 2}

{Repeat for each requirement in this stream}

### Stream N: {Stream Name}
{Continue for all identified work streams}

## Implementation Waves

### Wave 1: Foundation
{List REQ IDs and rationale for why these go first — no dependencies, foundational work}

### Wave 2: Core Features
{List REQ IDs that depend on Wave 1 completion}

### Wave N: {Wave Name}
{Continue as needed}

## Cross-Cutting Concerns
{Shared data models, migration needs, breaking changes, or infrastructure requirements that span multiple work streams}

## Open Questions
{List items that were ambiguous, contradictory, or lacked enough detail. Include the original transcript context and what clarification is needed.}

- **Q1**: {Question} — Context: "{relevant transcript excerpt}"
- **Q2**: {Question} — Context: "{relevant transcript excerpt}"
```
