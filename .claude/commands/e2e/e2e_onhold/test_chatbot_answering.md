# E2E Test: Chatbot Answering Questions

Test that the RAG chatbot successfully answers questions about uploaded documents.

## User Story

As a user with admin/analyst/manager role
I want the chatbot to answer questions about uploaded documents
So that I can extract insights from my document library through conversational AI

## Prerequisites

- User must be logged in with admin, analyst, or manager role
- OpenAI API key must be configured in backend environment variables
- At least one test document available for upload (PDF, DOCX, or TXT)

## Test Steps

### Part 1: Upload and Process Document

1. Navigate to the System0 Hub login page
2. Take a screenshot of the login page
3. Log in with admin credentials
4. **Verify** successful login (redirect to home/dashboard)
5. Take a screenshot of the authenticated home page

6. Navigate to Intelligence → Documentos
7. **Verify** the Documentos page loads
8. **Verify** "Subir Documento" button is visible
9. Take a screenshot of the Documentos page

10. Click "Subir Documento" button
11. Upload a test document (e.g., sample contract, invoice, or report PDF)
12. **Verify** upload success message appears
13. Take a screenshot of the uploaded document in the list

14. Wait for document processing to complete (max 60 seconds)
15. **Verify** document status changes to "completed"
16. **Verify** chunk_count > 0
17. Take a screenshot of the completed document with processing details

### Part 2: Create Chat Session and Ask Questions

18. Navigate to Intelligence → Chat
19. **Verify** the Chat page loads
20. **Verify** "Nueva Conversación" button is visible
21. Take a screenshot of the Chat page

22. Click "Nueva Conversación" button
23. Enter session title: "Test - Document Q&A"
24. Click "Crear" to create the session
25. **Verify** new session appears in the session list
26. **Verify** chat interface is displayed
27. Take a screenshot of the new chat session

28. In the chat input, enter a question about the uploaded document:
    - Example: "¿Qué información contiene el documento?"
    - Or: "Resume el contenido principal del documento"
29. Take a screenshot of the question entered
30. Click the send button or press Enter
31. **Verify** the user message appears in the chat

32. Wait for assistant response (max 30 seconds)
33. **CRITICAL VERIFY** Assistant response appears within 30 seconds
34. **CRITICAL VERIFY** Response content is not empty
35. **CRITICAL VERIFY** Response is longer than 50 characters (not a generic error)
36. **Verify** No error messages are displayed
37. Take a screenshot of the assistant's response

38. **Verify** Sources are cited (if applicable - check for source references)
39. Take a screenshot of the complete chat conversation

### Part 3: Test Follow-up Question

40. Ask a follow-up question:
    - Example: "¿Puedes darme más detalles sobre [tema del documento]?"
41. Take a screenshot of the follow-up question
42. **Verify** Assistant responds to follow-up within 30 seconds
43. **Verify** Response maintains conversation context
44. Take a screenshot of the follow-up response

### Part 4: Check Cost Tracking (Optional - Admin Only)

45. If logged in as admin, navigate to the session details
46. **Verify** Token count is displayed
47. **Verify** Cost in USD is displayed
48. Take a screenshot of the cost information

## Success Criteria

✅ Document uploads successfully
✅ Document processing completes (status: "completed")
✅ Embeddings are generated (chunk_count > 0)
✅ Chat session can be created
✅ User can send messages
✅ **CRITICAL**: Assistant responds within 30 seconds
✅ **CRITICAL**: Assistant response is substantive (not empty or error)
✅ **CRITICAL**: Response references document content (uses RAG tools)
✅ No error messages appear during chat
✅ Follow-up questions work correctly
✅ Cost tracking works (admin only)
✅ At least 10 screenshots captured at key steps

## Expected Behavior

- **User message**: Appears immediately in chat interface
- **Assistant response**: Appears within 30 seconds with relevant content from the uploaded document
- **Sources**: May include references to document chunks (chunk IDs, page numbers)
- **No errors**: No 503 Service Unavailable, no 400 Bad Request, no timeout errors

## Known Issues to Avoid

- If OPENAI_API_KEY is not configured, expect HTTP 503 with message about configuration
- If no documents uploaded, assistant should still respond but may indicate no context available
- If budget exhausted, expect error about monthly budget

## Debugging Steps (If Test Fails)

1. Check backend logs for `[RAG_API]`, `[CHAT]`, `[OPENAI]`, and `[TOOL]` prefixes
2. Verify OPENAI_API_KEY is set: `GET /api/rag/admin/config-status`
3. Check document processing status in database
4. Check embeddings exist for the document
5. Review browser console for frontend errors
6. Check network tab for API request/response details

## Screenshots to Capture

1. Login page
2. Authenticated home page
3. Documentos page (before upload)
4. Document uploaded (in list)
5. Document processing completed
6. Chat page (before creating session)
7. New chat session created
8. Question entered in chat
9. Assistant response (CRITICAL - proves bug is fixed)
10. Follow-up question
11. Follow-up response
12. Cost information (optional)

Total: 10-12 screenshots minimum
