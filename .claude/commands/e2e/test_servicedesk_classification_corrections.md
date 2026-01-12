# E2E Test: ServiceDesk Classification Corrections

Test the ServiceDesk classification corrections feature to validate that when a technician changes the category or priority of an AI-classified ticket, the correction is recorded and tracked for accuracy metrics.

## User Story

As a ServiceDesk administrator
I want the system to record when technicians correct AI-suggested classifications
So that I can track AI classification accuracy and the system can learn from corrections to improve future classifications

## Test Steps

1. Navigate to the `Application URL` and login with admin/manager credentials
2. Navigate to the ServiceDesk dashboard at `/servicedesk`
3. Take a screenshot of the ServiceDesk dashboard
4. Create a new ticket with AI classification:
   - Click on the "Nuevo Ticket" (New Ticket) tab
   - Fill in the form with:
     - Subject/Title: "Mi computadora no enciende"
     - Description: "Desde ayer mi PC de escritorio no enciende. La luz de power no prende. Ya verifique que el cable esta conectado. Necesito trabajar urgentemente."
     - Category: Select "hardware"
     - Priority: Select "high"
     - Requester email: "testuser@example.com"
   - Submit the form
   - Take a screenshot of the success message with ticket number
5. Navigate to the ticket detail view by clicking on the newly created ticket
6. Take a screenshot showing the initial ticket with AI classification
7. **Verify** that the ticket shows AI classification information (category, priority, confidence)
8. Edit the ticket to change the classification:
   - Click on the edit button or category/priority field
   - Change the category from the AI-suggested value to a different one (e.g., from "hardware" to "software")
   - Save the changes
9. Take a screenshot after the edit showing the changed category
10. **Verify** that a system message appears in the ticket history indicating the AI correction was recorded
11. **Verify** that the system message contains text like "Clasificacion IA corregida" or similar
12. Navigate to the Analytics dashboard at `/servicedesk` → Analytics tab
13. Look for classification accuracy metrics section
14. Take a screenshot of the analytics dashboard showing accuracy metrics (if displayed)
15. **Verify** that accuracy metrics include:
    - Total classifications count
    - Total corrections count
    - Accuracy rate percentage
    - Optional: breakdown by category

## Success Criteria

- Ticket creation with AI classification succeeds
- Ticket detail page shows AI classification data
- Editing ticket category/priority successfully saves the change
- System message is added to ticket history when classification is corrected
- System message mentions the AI correction (original vs new values)
- No errors occur during the update process
- Optional: Analytics dashboard displays accuracy metrics
- 5+ screenshots are taken documenting the flow

## Test Data

- Test User: Admin or manager role
- Subject: "Mi computadora no enciende"
- Description: "Desde ayer mi PC de escritorio no enciende. La luz de power no prende. Ya verifique que el cable esta conectado. Necesito trabajar urgentemente."
- Original Category: "hardware" (expected AI classification)
- Changed Category: "software" (manual correction by technician)
- Priority: "high"

## Expected Behavior

### AI Classification

Based on the test ticket content, the AI should classify:
- Category: `technical` (with subcategory `hardware`)
- Priority: `high` (user mentions urgent need)
- Impact: `individual`
- Confidence: Should be high (>0.7) given clear hardware issue description

### Correction Recording

When the technician changes the category:
1. The system compares original AI classification with new values
2. If different, `ClassificationService.record_correction()` is called
3. A system message is added to ticket history with content like:
   "Clasificacion IA corregida: hardware/high → software/high"
4. Correction is stored in `sd_ticket_patterns` table

### Accuracy Metrics (Optional)

If frontend displays accuracy metrics:
- Total Classifications: Number of tickets classified by AI
- Total Corrections: Number of times technicians changed AI classification
- Accuracy Rate: (1 - corrections/total) as percentage

## API Validation (Alternative)

If UI components are not fully implemented, verify via API:

### 1. Check ticket history for system message

```
GET /api/servicedesk/tickets/{ticket_id}
```

Look for a message with:
- `sender_type`: "system"
- `content`: Contains "Clasificacion IA corregida" or correction details
- `metadata.action`: "classification_correction"

### 2. Check accuracy endpoint

```
GET /api/servicedesk/analytics/classification-accuracy?days=30
```

Expected response:
```json
{
  "total_classifications": 100,
  "total_corrections": 5,
  "accuracy_rate": 0.95,
  "by_category": {
    "technical": 0.92,
    "billing": 0.98
  }
}
```

## Edge Cases to Consider

1. **No AI classification**: If ticket doesn't have AI classification, changing category should NOT record a correction
2. **Same values**: If technician selects the same category/priority as AI, no correction should be recorded
3. **Partial change**: If only category OR only priority changes, correction should still be recorded
4. **Multiple edits**: Each edit that changes classification should record a new correction

## Notes

- The correction detection happens in `ticket_service.update_ticket()`
- System messages use `MessageSenderType.SYSTEM`
- Corrections are stored in `sd_ticket_patterns` table with `pattern_type='classification'`
- Accuracy metrics are estimates since not all classifications are tracked
