# Process Meeting Transcript

Parse the raw meeting transcript below and produce a structured meeting summary with an HTML document suitable for sharing with prospects/customers.

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

9. **HTML Output** — Generate a professionally styled HTML document with inline CSS that:
   - Uses a clean, modern design suitable for business communication
   - Includes a header with the meeting title and date
   - Organizes all extracted information in clearly labeled sections
   - Uses a professional color scheme (blues/grays)
   - Is self-contained (no external CSS/JS dependencies)
   - Is suitable for emailing to prospects/customers as a meeting summary

## Quality Rules

- Output MUST be in English even if the transcript is in Spanish or another language.
- Action items MUST include an owner if one is identifiable from context.
- If a field cannot be determined from the transcript, use `null` for that field.
- Do NOT fabricate information — only extract what is present in the transcript.
- The HTML output MUST use only inline CSS styles (no external stylesheets).
- Discussion points should be ordered by importance/relevance, not chronological order.
- If the transcript contains no clear meeting content, return minimal JSON with null fields and a note in the summary.

## Output Format

Respond ONLY with a JSON object wrapped in a code block. No preamble, no commentary.

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
  "html_output": "<html>...</html>"
}
```
