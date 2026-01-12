# E2E Test: ServiceDesk Satisfaction Survey

## Test Objective
Validate the ServiceDesk satisfaction survey system allows customers to submit multi-dimensional feedback for resolved tickets and enforces one submission per ticket.

## User Story
As a customer who has had a support ticket resolved,
I want to provide feedback on the quality of service I received,
So that the IT team can improve their support and recognize high-performing technicians.

## Prerequisites
- Application running locally (frontend on port 5173, backend on port 8000)
- User logged in with admin or operations role
- At least one ticket with status "resolved" or "closed" exists

## Test Steps

### 1. Navigate to Resolved Ticket
1. Navigate to `/servicedesk`
2. Filter tickets by status "resolved" or find a resolved ticket
3. Click on the ticket to open detail view
4. **Expected**: Ticket detail page loads with satisfaction survey section visible in the sidebar

### 2. Survey Form Display
1. Locate the satisfaction survey section in the right sidebar
2. Verify the survey form displays:
   - Title "Encuesta de Satisfaccion"
   - Question text "Como calificarias la atencion recibida?"
   - 5-star rating input with emoji icons
   - "Tiempo de respuesta" rating (1-5 stars)
   - "Conocimiento tecnico" rating (1-5 stars)
   - "Calidad de comunicacion" rating (1-5 stars)
   - Optional comment text field with placeholder "Comentarios adicionales (opcional)..."
   - "Enviar Encuesta" submit button
3. **Expected**: All form elements are visible and styled correctly

### 3. Rating Selection
1. Click on the third star (3) for overall satisfaction
2. Verify star displays selection and label shows "Neutral"
3. Click on the fifth star (5) for overall satisfaction
4. Verify stars update and label shows "Muy satisfecho"
5. Repeat for response time, technical expertise, and communication ratings
6. **Expected**: Star ratings are interactive and show correct labels

### 4. Comment Input
1. Click on the comment text field
2. Type: "El soporte fue excelente, muy rapido y profesional."
3. Verify text appears in the field
4. **Expected**: Comment field accepts text input

### 5. Submit Button State
1. Clear all ratings (if possible) or start with a fresh resolved ticket
2. Verify submit button is disabled when no overall rating is selected
3. Select an overall rating (e.g., 4 stars)
4. Verify submit button becomes enabled
5. **Expected**: Submit button requires at least overall rating

### 6. Successful Submission
1. Ensure overall rating is selected (e.g., 4 stars)
2. Add ratings for response time (4), technical expertise (5), communication (4)
3. Add a comment (optional)
4. Click "Enviar Encuesta" button
5. Verify loading state appears (button shows spinner or "Enviando...")
6. **Expected**: Success message "Gracias por tu opinion" appears
7. **Expected**: Form is replaced with completion confirmation

### 7. Feedback Display After Submission
1. Refresh the ticket detail page
2. Navigate to the satisfaction survey section
3. Verify the submitted feedback displays:
   - Star rating (read-only)
   - Rating label (e.g., "Satisfecho")
   - Comment text (if provided)
   - "Encuesta de Satisfaccion Completada" title
4. **Expected**: Submitted feedback displays correctly, no input form shown

### 8. One Submission Per Ticket Enforcement
1. Navigate to a ticket that already has feedback submitted
2. Verify no input form is shown
3. Verify only the submitted feedback is displayed
4. (API Test) Attempt to POST another feedback for the same ticket via API
5. **Expected**: Second submission is rejected with appropriate error

### 9. Survey Not Shown for Open Tickets
1. Navigate to a ticket with status "open" or "in_progress"
2. Check the right sidebar
3. **Expected**: Satisfaction survey section is NOT visible for non-resolved tickets

### 10. Multi-Dimensional Ratings Storage
1. Navigate to a resolved ticket without feedback
2. Submit feedback with:
   - Overall: 5 stars
   - Response time: 4 stars
   - Technical expertise: 5 stars
   - Communication: 3 stars
   - Comment: "Test multi-dimensional feedback"
3. Refresh the page
4. Verify all individual ratings are stored and displayed correctly
5. **Expected**: All four rating dimensions are preserved

### 11. Error Handling - Network Error
1. Navigate to a resolved ticket without feedback
2. Open browser DevTools, go to Network tab
3. Enable offline mode or block requests to the API
4. Fill in the survey and click submit
5. **Expected**: Error message appears (e.g., "Error al enviar la encuesta. Por favor, intente nuevamente.")
6. Disable offline mode
7. Click submit again
8. **Expected**: Submission succeeds

### 12. Empty Comment Submission
1. Navigate to a resolved ticket without feedback
2. Select overall rating (4 stars)
3. Leave comment field empty
4. Click submit
5. **Expected**: Submission succeeds (comment is optional)
6. Verify feedback displays without comment text

## Success Criteria
- [ ] Survey form renders correctly for resolved/closed tickets only
- [ ] All four rating dimensions are displayed (overall, response time, technical expertise, communication)
- [ ] 5-star emoji rating is interactive with Spanish labels
- [ ] Comment field is optional and accepts free text
- [ ] Submit button is disabled until overall rating is selected
- [ ] Loading state displays during submission
- [ ] Success message "Gracias por tu opinion" appears after submission
- [ ] Submitted feedback displays correctly with star rating and comment
- [ ] One submission per ticket is enforced (form hidden after submission)
- [ ] Survey section is hidden for tickets that are not resolved/closed
- [ ] Multi-dimensional ratings are correctly stored and displayed
- [ ] Error states are handled gracefully with user-friendly messages
- [ ] All text labels are in Spanish

## Screenshot Requirements
1. **Survey form empty state**: Show the survey form before any input
2. **Survey form filled state**: Show the form with all ratings selected and comment filled
3. **Submission success**: Show the "Gracias por tu opinion" confirmation
4. **Feedback display**: Show the completed feedback view with ratings and comment
5. **Open ticket (no survey)**: Show a non-resolved ticket without the survey section

## Notes
- The survey uses emoji icons for ratings (sad face to happy face)
- Rating labels: "Muy insatisfecho", "Insatisfecho", "Neutral", "Satisfecho", "Muy satisfecho"
- The form background color is yellow (#FEF9C3) for input mode
- The completed state background is green (#F0FDF4)
- Response time, technical expertise, and communication ratings are optional
- Only the overall rating is required for submission
