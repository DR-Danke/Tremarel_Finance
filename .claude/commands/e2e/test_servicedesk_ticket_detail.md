# E2E Test: ServiceDesk Ticket Detail View

## Test Objective
Validate the ServiceDesk ticket detail view displays all sections correctly and allows ticket management actions.

## Prerequisites
- Application running locally (frontend on port 5173, backend on port 8000)
- User logged in with admin or operations role
- At least one ticket exists in the system

## Test Steps

### 1. Navigation to Ticket Detail
1. Navigate to `/servicedesk`
2. Click on a ticket in the list (or navigate directly to `/servicedesk/{ticketId}`)
3. **Expected**: Page loads with ticket detail view

### 2. Ticket Header Display
1. Verify ticket header shows:
   - Ticket number (e.g., "# TKT-001")
   - Ticket subject/title
   - Status badge with appropriate color
2. **Expected**: All header elements visible and correctly formatted

### 3. SLA Countdown Bar
1. Locate the SLA progress bar below the header
2. Verify it displays:
   - Time remaining or "Vencido" if breached
   - Color coding (green > 4h, yellow 1-4h, orange < 1h, red breached)
3. **Expected**: SLA bar shows correct countdown with appropriate color

### 4. Requester Info Card
1. Locate the requester information card
2. Verify it displays:
   - Requester name
   - Email address
   - Phone number (if available)
   - Organization (if available)
3. **Expected**: Requester info card shows all available information

### 5. Conversation Thread
1. Locate the conversation thread section
2. Verify messages display with correct styling:
   - Customer messages: Left-aligned, light gray background
   - Technician messages: Right-aligned, primary color background
   - System messages: Center-aligned, gray italic text
   - Internal notes: Right-aligned, yellow background (tech only)
3. Verify each message shows sender name and timestamp
4. **Expected**: Messages display correctly differentiated by sender type

### 6. Reply Input
1. Locate the reply input section at the bottom
2. Test toggle between "Comentario Publico" and "Nota Interna"
3. Type a test message in the text field
4. Verify attachment upload button is present
5. Click Submit and verify message appears in thread
6. **Expected**: Reply input works with toggle and creates messages

### 7. Status Transition Buttons (Right Sidebar)
1. Locate status action buttons in right sidebar
2. Based on current status, verify appropriate buttons appear:
   - "Iniciar Trabajo" (when new/open)
   - "Marcar Esperando" (when in_progress)
   - "Resolver" (when in_progress)
3. Click a status button and verify status changes
4. **Expected**: Status transitions work correctly

### 8. Assignment Dropdown
1. Locate assignment dropdown in right sidebar
2. Verify it shows current assignee (or "Sin asignar")
3. Open dropdown and verify technician list appears
4. Verify "Asignar a Mi" button is present
5. Test assignment by selecting a technician
6. **Expected**: Assignment dropdown works and updates ticket

### 9. Priority Selector
1. Locate priority selector in right sidebar
2. Verify current priority is shown
3. Open selector and verify options (Baja, Media, Alta, Critica)
4. Change priority and verify it updates
5. **Expected**: Priority selector works correctly

### 10. Category Selector
1. Locate category selector in right sidebar
2. Verify current category is shown
3. Open selector and verify options (Hardware, Software, Red, etc.)
4. Change category and verify it updates
5. **Expected**: Category selector works correctly

### 11. Attachments List
1. Locate attachments section in right sidebar
2. If ticket has attachments, verify they are listed
3. Verify each attachment shows filename and download link
4. **Expected**: Attachments display correctly with download capability

### 12. Satisfaction Survey (Resolved Tickets Only)
1. Navigate to a ticket with status "resolved" or "closed"
2. Locate satisfaction survey section
3. If no feedback exists, verify input form appears with:
   - Star rating (1-5)
   - Optional comment field
   - Submit button
4. If feedback exists, verify it displays the rating and comment
5. **Expected**: Satisfaction survey appears for resolved tickets

### 13. Error Handling
1. Navigate to `/servicedesk/invalid-uuid`
2. **Expected**: Error or "Ticket no encontrado" message displays
3. Navigate back to a valid ticket
4. **Expected**: Page loads normally

### 14. Loading States
1. Refresh the ticket detail page
2. **Expected**: Loading skeleton/spinner appears briefly
3. **Expected**: Content loads and replaces loading state

## Success Criteria
- [ ] Detail view loads and renders all sections for a valid ticket ID
- [ ] Ticket header displays ticket number, subject, and status badge correctly
- [ ] SLA countdown bar shows remaining time with appropriate color coding
- [ ] Requester info card displays name, email, phone, and organization
- [ ] Conversation thread displays messages with correct styling per sender type
- [ ] Reply input allows toggling between public comment and internal note
- [ ] Reply submission creates a new message in the conversation
- [ ] Status transition buttons are shown based on current ticket status
- [ ] Status updates are applied and reflected immediately
- [ ] Assignment dropdown shows available technicians
- [ ] "Assign to Me" button assigns ticket to current user
- [ ] Priority selector updates ticket priority
- [ ] Category selector updates ticket category
- [ ] Attachments list displays all ticket attachments
- [ ] Satisfaction survey appears when ticket is resolved/closed
- [ ] Loading, error, and not found states are handled gracefully

## Notes
- Internal notes should only be visible to technicians (not customers)
- Status transition buttons change based on the current ticket status
- The satisfaction survey form only appears if no feedback has been submitted
- All text labels should be in Spanish
