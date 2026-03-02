# Process Meeting Transcript

Parse the raw meeting transcript below and produce two output files: a structured JSON summary and a professionally styled HTML document.

## CRITICAL: Output Method

You MUST save your output by writing TWO files using the Write tool:

1. `meetings/summary.json` — The structured JSON (schema below)
2. `meetings/summary.html` — The styled HTML document

Do NOT just print the JSON. You MUST use the Write tool to create both files. After writing the files, confirm with a short message listing the file paths.

## Input

The full meeting transcript text is provided below:

$ARGUMENTS

## Processing Instructions

Analyze the transcript and extract the following structured information:

1. **Meeting Metadata** — Extract the meeting title/topic, date (if mentioned), and duration (if mentioned).

2. **Participants** — Identify all participants by name and role/title if available. If specific names are not clear, use speaker labels (e.g., "Speaker 1", "Speaker 2").

3. **Company/Prospect Identification** — Identify the company or prospect being discussed. Extract company name, primary contact name, and contact email if mentioned.

4. **Executive Summary** — Write a concise 2-4 sentence summary of the meeting's key outcomes and decisions.

5. **Discussion Points** — Extract the main topics discussed, each with a brief description. Order by importance.

6. **Action Items** — Extract all action items with:
   - Description of the action
   - Owner (who is responsible), if mentioned
   - Deadline, if mentioned

7. **Decisions Made** — List all explicit decisions reached during the meeting.

8. **Next Steps** — List agreed-upon next steps and follow-up activities.

9. **Technical Architecture Diagrams (IMPORTANT)** — You MUST generate Mermaid diagrams whenever the transcript mentions ANY of the following: software platforms, APIs, data pipelines, system integrations, automation engines, databases, matching/routing algorithms, pricing logic, workflows, CRM systems, case management, or any other technical/software concept.

   **When to generate:** If someone in the meeting describes how a system works, what components it has, how data flows, or what needs to be built — that REQUIRES a diagram. Err on the side of generating diagrams. Most business meetings about software or technology WILL need at least 2-3 diagrams.

   **What to generate:**
   - **Flowcharts** (`flowchart TD`) for processes, pipelines, and decision flows
   - **Sequence diagrams** (`sequenceDiagram`) for multi-party interactions and API integrations
   - **Architecture diagrams** (`flowchart LR`) for system components and their connections
   - Generate **multiple diagrams** — one per major technical concept discussed

   **Only skip diagrams** for purely non-technical meetings (e.g., budget reviews with no software discussion, HR meetings, social calls).

   Each diagram must have a `title` and `mermaid_code` field. Return as an array of objects.

10. **HTML Output** — Generate a professionally styled HTML document with inline CSS that:
   - Uses a clean, modern design suitable for business communication
   - Includes a header with the meeting title and date
   - Organizes all extracted information in clearly labeled sections
   - Uses a professional color scheme (blues/grays)
   - Is self-contained with no external CSS dependencies
   - Is suitable for emailing to prospects/customers as a meeting summary
   - If technical diagrams were generated, include them in the HTML inside a "Technical Architecture" section. Embed Mermaid diagrams using `<pre class="mermaid">` tags and include the Mermaid JS library via CDN: `<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>` with `<script>mermaid.initialize({startOnLoad:true});</script>` at the end of the body

## Quality Rules

- Output MUST be in English even if the transcript is in Spanish or another language.
- Action items MUST include an owner if one is identifiable from context.
- If a field cannot be determined from the transcript, use `null` for that field.
- Do NOT fabricate information — only extract what is present in the transcript.
- The HTML output MUST use only inline CSS styles (no external stylesheets), except for the Mermaid CDN script.
- Discussion points should be ordered by importance/relevance, not chronological order.
- If the transcript contains no clear meeting content, return minimal JSON with null fields and a note in the summary.
- The `diagrams` array should ONLY be empty (`[]`) for meetings with zero technical or software content (rare). If any system, platform, engine, workflow, or technical concept is discussed, you MUST generate at least one diagram.
- Mermaid syntax MUST be valid — verify that node IDs don't contain special characters, arrows use correct syntax (`-->`, `-->`), and labels are properly quoted if they contain spaces.
- Diagrams should visualize what was actually discussed — the proposed architecture, data flows, system components, or process steps that were described in the meeting.

## JSON Schema for meetings/summary.json

```json
{
  "title": "Meeting title or topic",
  "meeting_date": "YYYY-MM-DD or null if not mentioned",
  "participants": [
    {"name": "Person Name", "role": "Their role/title or null"}
  ],
  "company_name": "Company or prospect name, or null",
  "contact_name": "Primary contact name, or null",
  "contact_email": "Contact email, or null",
  "summary": "2-4 sentence executive summary of the meeting",
  "discussion_points": [
    {"topic": "Topic title", "description": "Brief description of what was discussed"}
  ],
  "action_items": [
    {"description": "What needs to be done", "owner": "Who is responsible or null", "deadline": "When it's due or null"}
  ],
  "decisions": [
    "Decision 1 that was made",
    "Decision 2 that was made"
  ],
  "next_steps": [
    "Next step 1",
    "Next step 2"
  ],
  "diagrams": [
    {"title": "System Architecture", "mermaid_code": "flowchart TD\n  A[Client] --> B[API Gateway]\n  B --> C[Service]"}
  ],
  "html_output": "<html>full HTML document here</html>"
}
```

## Reminder

Do NOT respond with the JSON in your message. Use the Write tool to save `meetings/summary.json` and `meetings/summary.html`, then confirm the file paths.
