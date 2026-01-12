# E2E Test: Email Webhook Integration

Test the email-to-ticket webhook functionality for the ServiceDesk module.

## User Story

As a support team
I want emails sent to our support address to automatically create tickets
So that users can submit support requests via email

## Prerequisites

- Backend server running on `http://localhost:8000`
- Database accessible and seeded with test data
- No SMTP configuration required (webhook receives, doesn't send in test)

## Test Steps

### Part 1: Health Check

1. Send GET request to `/api/servicedesk/webhooks/health`
2. **Verify** response status is 200
3. **Verify** response contains:
   - `status` field equals "healthy"
   - `smtp_configured` field (boolean)
   - `classification_enabled` field (boolean)

### Part 2: New Ticket Creation from Email

4. Send POST request to `/api/servicedesk/webhooks/email` with payload:
   ```json
   {
     "from_email": "testuser@example.com",
     "from_name": "Test User",
     "to_email": "support@system0.com",
     "subject": "Cannot access my account - urgent",
     "body_plain": "Hello, I've been trying to log in to my account but keep getting an error message. I've tried resetting my password but it still doesn't work. Please help!",
     "body_html": null,
     "message_id": "<test-e2e-001@example.com>",
     "in_reply_to": null,
     "references": null,
     "date": "{{CURRENT_ISO_DATETIME}}",
     "attachments": null
   }
   ```
5. **Verify** response status is 200
6. **Verify** response contains:
   - `success` equals `true`
   - `ticket_number` matches pattern `TKT-\d{4}-\d{5}`
   - `is_reply` equals `false`
   - `ticket_id` is a valid UUID

### Part 3: Verify Ticket Created

7. Extract `ticket_number` from previous response
8. Send GET request to `/api/servicedesk/tickets?search_query={{ticket_number}}`
9. **Verify** ticket exists with:
   - `title` equals "Cannot access my account - urgent"
   - `channel` equals "email"
   - `requester_email` equals "testuser@example.com"
   - `status` equals "new"

### Part 4: Reply to Existing Ticket

10. Using the `ticket_number` from Part 2, send POST to `/api/servicedesk/webhooks/email`:
    ```json
    {
      "from_email": "testuser@example.com",
      "from_name": "Test User",
      "to_email": "support@system0.com",
      "subject": "Re: [{{TICKET_NUMBER}}] Cannot access my account - urgent",
      "body_plain": "I tried what you suggested but it still doesn't work. Here's the error I see: 'Authentication failed'",
      "body_html": null,
      "message_id": "<test-e2e-002@example.com>",
      "in_reply_to": "<test-e2e-001@example.com>",
      "references": "<test-e2e-001@example.com>",
      "date": "{{CURRENT_ISO_DATETIME}}",
      "attachments": null
    }
    ```
11. **Verify** response status is 200
12. **Verify** response contains:
    - `success` equals `true`
    - `ticket_number` equals the original ticket number
    - `is_reply` equals `true`

### Part 5: Verify Reply Added as Message

13. Send GET request to `/api/servicedesk/tickets/{{TICKET_ID}}?include_messages=true`
14. **Verify** ticket details include:
    - `messages` array has at least 1 message
    - Most recent message contains "Authentication failed"
    - Message `sender_type` equals "customer"

### Part 6: Email with Attachment

15. Send POST to `/api/servicedesk/webhooks/email` with attachment:
    ```json
    {
      "from_email": "newuser@example.com",
      "from_name": "New User",
      "to_email": "support@system0.com",
      "subject": "Error screenshot attached",
      "body_plain": "Please see the attached screenshot of my error.",
      "body_html": null,
      "message_id": "<test-e2e-003@example.com>",
      "in_reply_to": null,
      "references": null,
      "date": "{{CURRENT_ISO_DATETIME}}",
      "attachments": [
        {
          "filename": "error.png",
          "content_type": "image/png",
          "content_base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
          "size": 68
        }
      ]
    }
    ```
16. **Verify** response status is 200
17. **Verify** response `success` equals `true`
18. Extract new ticket ID
19. Send GET request to `/api/servicedesk/tickets/{{NEW_TICKET_ID}}`
20. **Verify** ticket has attachments (check attachments array or count)

### Part 7: Invalid Email Handling

21. Send POST to `/api/servicedesk/webhooks/email` with empty body:
    ```json
    {
      "from_email": "invalid@example.com",
      "to_email": "support@system0.com",
      "subject": "Empty email",
      "body_plain": "",
      "body_html": "",
      "message_id": "<test-e2e-004@example.com>",
      "date": "{{CURRENT_ISO_DATETIME}}"
    }
    ```
22. **Verify** response status is 400
23. **Verify** response contains error about empty body

### Part 8: Missing Required Fields

24. Send POST to `/api/servicedesk/webhooks/email` with missing fields:
    ```json
    {
      "from_email": "partial@example.com"
    }
    ```
25. **Verify** response status is 422 (validation error)

## Success Criteria

- Health check endpoint returns service status
- New emails create new tickets with correct metadata
- Reply emails add messages to existing tickets (not new tickets)
- Attachments are processed and stored
- Invalid emails are rejected with appropriate error messages
- All required field validations work correctly

## Test Data Notes

- Use unique `message_id` values for each test email
- Use ISO 8601 format for dates: `2026-01-06T10:30:00Z`
- Base64 attachment in Part 6 is a valid 1x1 PNG pixel image
