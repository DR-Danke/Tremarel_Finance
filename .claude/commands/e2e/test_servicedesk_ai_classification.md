# E2E Test: ServiceDesk AI Classification

Test the ServiceDesk AI classification feature to validate that tickets are automatically classified by AI when created, with category, priority, and impact suggestions displayed.

## User Story

As an IT support user
I want my tickets to be automatically classified by AI when I create them
So that I don't need to manually select categories and priorities, and technicians can see AI-suggested classifications immediately

## Test Steps

1. Navigate to the `Application URL` and login with test credentials
2. Navigate to the ServiceDesk dashboard at `/servicedesk`
3. Take a screenshot of the ServiceDesk dashboard
4. Click on the "Nuevo Ticket" (New Ticket) tab to open the ticket creation form
5. Take a screenshot of the ticket creation form
6. Fill in the form fields with a descriptive ticket to trigger AI classification:
   - Subject/Title: "Mi impresora HP LaserJet no imprime documentos"
   - Description: "Desde esta mañana mi impresora HP LaserJet del departamento de Finanzas no imprime. La luz esta en rojo y aparece un mensaje de error. Ya intente reiniciarla pero sigue igual. Necesito imprimir reportes urgentes."
   - Category: Select "hardware"
   - Priority: Select "high"
   - Requester email: Use test email (e.g., "testuser@example.com")
7. Take a screenshot of the filled form before submission
8. Submit the form by clicking the submit button
9. **Verify** that a success message appears indicating the ticket was created
10. **Verify** that the success message includes a ticket number in the format `TKT-YYYY-NNNNN`
11. Take a screenshot of the success message with the ticket number
12. Navigate to the ticket list tab or click on the ticket to view details
13. **Verify** that the ticket detail page shows AI classification information
14. **Verify** that AI classification includes one or more of:
    - AI-suggested category (may show as "Clasificación IA" or similar badge)
    - AI confidence indicator (percentage or badge like "Alta confianza")
    - AI reasoning or explanation for the classification
15. Take a screenshot of the ticket detail showing AI classification
16. **Verify** that if AI classification appears, it shows relevant suggestions based on the ticket content (e.g., hardware-related for printer issue)

## Success Criteria

- Ticket creation form loads correctly
- Form can be filled with valid data describing a technical issue
- Form submission succeeds without errors
- Success message displays a ticket number in format `TKT-YYYY-NNNNN`
- Ticket detail page loads and shows ticket information
- AI classification fields are present in the ticket (ai_classification and/or ai_confidence)
- If AI classification is shown in UI, it displays relevant category/priority suggestions
- 5+ screenshots are taken documenting the flow

## Test Data

- Test User: Any authenticated user in the system
- Subject: "Mi impresora HP LaserJet no imprime documentos"
- Description: "Desde esta mañana mi impresora HP LaserJet del departamento de Finanzas no imprime. La luz esta en rojo y aparece un mensaje de error. Ya intente reiniciarla pero sigue igual. Necesito imprimir reportes urgentes."
- Category: "hardware"
- Priority: "high"

## Expected AI Classification

Based on the test ticket content, the AI should classify:
- Category: `technical` (with subcategory `hardware`)
- Priority: `high` or `medium` (printer issue affecting work)
- Impact: `individual` or `department` (mentioned Finance department)
- Confidence: Should be reasonably high (>0.7) given clear hardware issue description

## Notes on AI Classification Display

The AI classification may be displayed in different ways depending on frontend implementation:
1. **Badge/Chip**: A small colored badge showing "IA: Hardware" or similar
2. **Confidence Meter**: A percentage or visual indicator showing AI confidence
3. **Sidebar Section**: A dedicated section in ticket details showing AI suggestions
4. **Tooltip/Popover**: Hover information showing AI reasoning

If AI classification is not visually displayed in the UI but exists in the API response, the test should still pass as long as:
- The ticket was created successfully
- The API response includes `ai_classification` field with valid data
- The `ai_confidence` field has a numeric value

## API Response Validation (Alternative)

If UI components for AI classification are not implemented, verify via browser dev tools or API call that:
```json
{
  "ai_classification": {
    "category": "technical",
    "subcategory": "hardware",
    "priority": "high",
    "impact": "...",
    "confidence_score": 0.XX,
    "reasoning": "..."
  },
  "ai_confidence": 0.XX
}
```
