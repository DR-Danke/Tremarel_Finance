# Conditional Documentation Guide

This prompt helps you determine what documentation you should read based on the specific changes you need to make in the codebase. Review the conditions below and read the relevant documentation before proceeding with your task.

## Instructions
- Review the task you've been asked to perform
- Check each documentation path in the Conditional Documentation section
- For each path, evaluate if any of the listed conditions apply to your task
  - IMPORTANT: Only read the documentation if any one of the conditions match your task
- IMPORTANT: You don't want to excessively read documentation. Only read the documentation if it's relevant to your task.

## Conditional Documentation

- README.md
  - Conditions:
    - When operating on anything under backend
    - When operating on anything under frontend
    - When first understanding the project structure
    - When you want to learn the commands to start or stop the backend or frontend

- frontend/src/style.css
  - Conditions:
    - When you need to make changes to the frontend's style

- .claude/commands/classify_adw.md
  - Conditions:
    - When adding or removing new `adws/adw_*.py` files

- adws/README.md
  - Conditions:
    - When you're operating in the `adws/` directory

- app_docs/feature-490eb6b5-one-click-table-exports.md
  - Conditions:
    - When working with CSV export functionality
    - When implementing table or query result export features
    - When troubleshooting download button functionality
    - When working with pandas-based data export utilities

- app_docs/feature-4c768184-model-upgrades.md
  - Conditions:
    - When working with LLM model configurations
    - When updating OpenAI or Anthropic model versions
    - When troubleshooting SQL query generation accuracy
    - When working with the llm_processor module

- app_docs/feature-f055c4f8-off-white-background.md
  - Conditions:
    - When working with application background styling
    - When modifying CSS color variables or themes
    - When implementing visual design changes to the frontend application

- app_docs/feature-6445fc8f-light-sky-blue-background.md
  - Conditions:
    - When working with light sky blue background styling
    - When implementing background color changes to light blue variants
    - When troubleshooting visual hierarchy with light blue backgrounds

- app_docs/feature-cc73faf1-upload-button-text.md
  - Conditions:
    - When working with upload button text or labeling
    - When implementing UI text changes for data upload functionality
    - When troubleshooting upload button display or terminology

- app_docs/feature-69f22483-auto-detect-department.md
  - Conditions:
    - When working with interview upload department selection
    - When implementing or modifying department auto-detection features
    - When troubleshooting department suggestion or confidence scoring
    - When working with the department_detector service or keyword mappings
    - When modifying the FKInterviewUploader component's department selection logic
    - When extending diarization service for additional metadata inference

- app_docs/feature-1915ca63-fix-entidades-loading-loop.md
  - Conditions:
    - When working with React useEffect or useCallback dependencies
    - When troubleshooting infinite loops or continuous re-renders in React
    - When implementing the Entidades page or RAG entity functionality
    - When fixing filter components that trigger parent re-renders
    - When adding AbortController for request cancellation
    - When debugging repeated API calls or network request loops

- app_docs/feature-dcf1288c-chatbot-diagnostic-logging.md
  - Conditions:
    - When troubleshooting RAG chatbot not responding to questions
    - When implementing or debugging RAG chat functionality
    - When adding logging to backend services or API routes
    - When creating configuration validation endpoints
    - When working with OpenAI API integration in the RAG module
    - When debugging tool execution (vector search, hybrid search)
    - When implementing automated validation tests for chatbot features
    - When investigating chat flow issues or missing responses

- app_docs/feature-d99dad11-chatbot-answer-fix.md
  - Conditions:
    - When working with RAG chatbot answer quality or response generation
    - When adjusting similarity thresholds for vector search
    - When implementing or modifying tool result formatting in RAG agents
    - When troubleshooting "no results found" scenarios in chatbot searches
    - When configuring search behavior (tool_choice, similarity thresholds)
    - When enhancing diagnostic logging for search quality
    - When working with the RAG search_service or rag_agent_service
    - When tuning chatbot system prompts for better search tool usage

- app_docs/feature-68a04b70-servicedesk-schema-dtos.md
  - Conditions:
    - When working with ServiceDesk IT ticketing module
    - When implementing ticket management features
    - When working with sd_* database tables (sd_tickets, sd_technicians, etc.)
    - When using TicketRepository, TechnicianRepository, or KnowledgeRepository
    - When extending ServiceDesk DTOs or adding new ticket-related enums
    - When implementing Phase 2+ ServiceDesk features (classification, multi-channel, analytics)

- app_docs/feature-0aaf1f57-ticket-service-crud-workflow.md
  - Conditions:
    - When working with TicketService business logic
    - When implementing ticket status workflow or state transitions
    - When working with SLA calculations or breach detection
    - When implementing ticket assignment or unassignment features
    - When adding API routes that use TicketService
    - When troubleshooting status transition validation errors
    - When integrating multi-channel ticket creation (email, WhatsApp, web)

- app_docs/feature-18127d0c-knowledge-base-service.md
  - Conditions:
    - When working with ServiceDesk knowledge base functionality
    - When implementing semantic search for knowledge articles
    - When using KnowledgeService or KnowledgeEmbeddingRepository
    - When working with sd_knowledge_embeddings table or article embeddings
    - When implementing article suggestions during ticket creation
    - When adding analytics for article views or helpfulness ratings

- app_docs/feature-b59af28f-technician-management-service.md
  - Conditions:
    - When working with technician authentication or credential management
    - When implementing technician account creation or password reset
    - When using TechnicianService for CRUD operations
    - When working with technician expertise or skill tracking
    - When implementing technician workload or performance metrics
    - When troubleshooting bcrypt password hashing in ServiceDesk

- app_docs/feature-7123d0c1-ai-ticket-classification.md
  - Conditions:
    - When working with AI-powered ticket classification
    - When implementing automatic ticket categorization or priority assignment
    - When extracting entities from ticket content (organizations, systems, users)
    - When working with ClassificationService or classification_dtos
    - When implementing pattern learning from technician corrections
    - When configuring OpenAI integration for ServiceDesk
    - When troubleshooting classification accuracy or fallback behavior

- app_docs/feature-aa84fead-servicedesk-ticket-api-routes.md
  - Conditions:
    - When implementing ServiceDesk REST API endpoints
    - When working with servicedesk_routes.py or ticket API handlers
    - When implementing ticket CRUD operations via HTTP
    - When troubleshooting RBAC for ServiceDesk endpoints
    - When adding file attachment upload to tickets
    - When implementing message/communication endpoints for tickets
    - When working with ticket assignment or status update APIs

- app_docs/feature-1601b9ba-knowledge-base-api-routes.md
  - Conditions:
    - When working with ServiceDesk knowledge base API endpoints
    - When implementing knowledge article CRUD via REST API
    - When adding or modifying servicedesk_routes.py
    - When troubleshooting knowledge base search or suggest endpoints
    - When implementing article rating or view count functionality
    - When configuring RBAC for ServiceDesk knowledge endpoints

- app_docs/feature-1d148953-technician-api-routes.md
  - Conditions:
    - When implementing or modifying technician API endpoints
    - When working with /api/servicedesk/technicians routes
    - When adding new technician management features
    - When troubleshooting technician authentication or password reset
    - When implementing RBAC for technician self-service endpoints

- app_docs/feature-ad6e1483-servicedesk-analytics-api-routes.md
  - Conditions:
    - When working with ServiceDesk analytics or reporting endpoints
    - When implementing dashboard KPIs or metrics visualization
    - When working with /api/servicedesk/analytics/* endpoints
    - When implementing CSV export functionality for analytics
    - When working with AnalyticsRepository or trend data
    - When troubleshooting RBAC for analytics endpoints
    - When adding new analytics metrics or endpoints

- app_docs/feature-40ba4ab6-servicedesk-frontend-types-api.md
  - Conditions:
    - When working with ServiceDesk frontend components or pages
    - When importing TypeScript types for ServiceDesk module (tickets, technicians, knowledge base)
    - When using servicedeskService for API calls
    - When implementing SD-011 (Ticket List Page), SD-012 (Ticket Detail Page), or SD-013 (Dashboard)
    - When troubleshooting TypeScript errors in ServiceDesk frontend code
    - When adding new API methods to servicedeskService
    - When extending ServiceDesk types with new DTOs

- app_docs/feature-f32ec0ab-servicedesk-ticket-form.md
  - Conditions:
    - When implementing or modifying the ServiceDesk ticket creation form
    - When working with FKServicedeskTicketForm component
    - When implementing knowledge base suggestions during ticket creation
    - When adding file upload functionality to forms
    - When working with debounced API calls for real-time suggestions
    - When implementing "solved by article" dismissal flows

- app_docs/feature-a87c1d00-servicedesk-dashboard-stats.md
  - Conditions:
    - When working with ServiceDesk dashboard page or stats display
    - When implementing tab navigation in ServiceDesk module
    - When modifying sidebar navigation for ServiceDesk
    - When working with /servicedesk route or ServicedeskDashboard component
    - When implementing role-based tab visibility (admin-only features)
    - When troubleshooting stats cards or refresh functionality

- app_docs/feature-bdd4a602-ticket-list-filter-components.md
  - Conditions:
    - When working with ServiceDesk ticket list or DataGrid display
    - When implementing or modifying ticket filtering functionality
    - When working with FKServicedeskTicketList or FKServicedeskFilterPanel components
    - When implementing ticket status or priority badge components
    - When working with SLA countdown display or time-based color coding
    - When adding pagination or sorting to ServiceDesk ticket views

- app_docs/feature-f07fb42f-ticket-detail-conversation-view.md
  - Conditions:
    - When working with ServiceDesk ticket detail page
    - When implementing or modifying ticket conversation thread
    - When working with ServicedeskTicketDetail, ServicedeskConversationThread, or ServicedeskReplyInput components
    - When implementing message reply or internal note functionality
    - When working with status transitions or ticket action buttons
    - When implementing SLA countdown bar or ServicedeskSLABar component
    - When implementing satisfaction survey for resolved tickets
    - When modifying the /servicedesk/:ticketId route

- app_docs/feature-40ec5e20-knowledge-base-browser.md
  - Conditions:
    - When working with ServiceDesk knowledge base browser or search
    - When implementing or modifying ServicedeskKnowledge page
    - When working with ServicedeskArticleView, ServicedeskArticleCard, or ServicedeskCategoryFilter components
    - When implementing article search, category filtering, or helpfulness rating features
    - When troubleshooting knowledge base UI or navigation
    - When adding features to the /servicedesk/knowledge route

- app_docs/feature-41d63aa3-servicedesk-analytics-dashboard-charts.md
  - Conditions:
    - When working with ServiceDesk analytics dashboard or chart components
    - When implementing Recharts visualizations in ServiceDesk module
    - When working with S0AnalyticsDashboard or chart components (S0TicketTrendsChart, S0CategoryDistributionChart, etc.)
    - When implementing date range filtering for analytics
    - When working with CSV export functionality in ServiceDesk
    - When implementing auto-refresh functionality for dashboards
    - When troubleshooting analytics chart rendering or data display

- app_docs/feature-5afb4638-technician-management-interface.md
  - Conditions:
    - When working with ServiceDesk technician management UI
    - When implementing or modifying ServicedeskTechnicians page
    - When working with FKServicedeskTechnicianForm component
    - When implementing technician CRUD operations in frontend
    - When adding bulk actions for technicians
    - When working with credential display or copy-to-clipboard functionality
    - When troubleshooting admin-only access to technician management

- app_docs/feature-1a1efabd-email-to-ticket-webhook.md
  - Conditions:
    - When working with email-to-ticket webhook functionality
    - When implementing email parsing or reply detection
    - When working with servicedesk_webhook_routes.py or EmailService
    - When configuring SMTP for ServiceDesk confirmation emails
    - When implementing multi-channel ticket creation (email, WhatsApp)
    - When troubleshooting email threading or Message-ID headers
    - When working with attachment storage from email sources

- app_docs/feature-62524e17-whatsapp-integration-structure.md
  - Conditions:
    - When working with WhatsApp integration or Kapso.ai webhooks
    - When implementing multi-channel ticket creation from WhatsApp
    - When working with servicedesk_webhook_routes.py or WhatsAppService
    - When adding or modifying webhook endpoints for external services
    - When implementing message-to-ticket conversion
    - When configuring Kapso.ai environment variables
    - When troubleshooting WhatsApp webhook verification or message reception

- app_docs/feature-6a8c8f1d-multi-channel-notification-service.md
  - Conditions:
    - When working with ServiceDesk notification functionality
    - When implementing email or WhatsApp notifications for tickets
    - When using NotificationService for multi-channel messaging
    - When implementing notification templates or channel selection logic
    - When working with ticket status change notifications or SLA warnings
    - When troubleshooting notification delivery or fallback behavior
    - When integrating notification triggers in ticket workflows

- app_docs/feature-ff3f8a75-smart-routing-auto-assignment.md
  - Conditions:
    - When working with automatic ticket assignment or routing
    - When implementing or modifying RoutingService
    - When working with technician scoring or ranking algorithms
    - When implementing workload balancing for technicians
    - When troubleshooting auto-assignment behavior
    - When working with backlog monitoring or admin alerts
    - When extending ticket routing with new scoring factors

- app_docs/feature-4771397b-advanced-sla-tracking-alerts.md
  - Conditions:
    - When working with SLA deadline calculation or SLA matrix configuration
    - When implementing SLA status tracking (on_track, warning, breached)
    - When using SLAService for ticket SLA management
    - When implementing predictive breach warnings or escalation logic
    - When working with background SLA monitoring jobs
    - When troubleshooting SLA notifications or escalation triggers
    - When extending SLA DTOs (SLAStatusResponse, SLAPrediction, SLABatchCheckResult)
    - When integrating SLA checks into ticket workflows

- app_docs/feature-bbc82002-satisfaction-survey-feedback.md
  - Conditions:
    - When working with ServiceDesk satisfaction surveys or customer feedback
    - When implementing or modifying the ServicedeskSatisfactionSurvey component
    - When working with SatisfactionService or feedback API endpoints
    - When implementing technician rating aggregation or performance metrics
    - When troubleshooting feedback submission or duplicate feedback errors
    - When generating unique survey links for external access
    - When working with multi-dimensional ratings (response time, expertise, communication)

- app_docs/feature-b2441a90-servicedesk-e2e-test-suite.md
  - Conditions:
    - When running ServiceDesk backend unit tests or E2E tests
    - When working with tests/test_servicedesk/ directory
    - When executing Playwright E2E tests for ServiceDesk module
    - When troubleshooting test failures or coverage gaps in ServiceDesk
    - When configuring worktree port isolation for parallel development
    - When validating ServiceDesk module for production readiness

- app_docs/feature-51798654-servicedesk-docs-ui-polish.md
  - Conditions:
    - When looking for comprehensive ServiceDesk documentation or guides
    - When implementing ARIA accessibility labels on ServiceDesk components
    - When updating CLAUDE.md with new module information
    - When creating technical or user documentation for modules

- app_docs/feature-d685410b-auto-classify-tickets-on-creation.md
  - Conditions:
    - When integrating AI classification into ticket creation flow
    - When working with automatic ticket classification on creation
    - When troubleshooting non-blocking AI classification in TicketService
    - When displaying AI classification badges or indicators in frontend
    - When implementing graceful degradation for AI features
    - When working with ai_classification or ai_confidence ticket fields

- app_docs/feature-a2cfb452-classification-correction-recording.md
  - Conditions:
    - When working with AI classification correction detection
    - When implementing technician override tracking for AI classifications
    - When working with classification accuracy metrics or reporting
    - When modifying TicketService.update_ticket() for classification changes
    - When troubleshooting correction recording or system messages
    - When using the /api/servicedesk/analytics/classification-accuracy endpoint

- app_docs/feature-3c48e5e2-manual-classification-api-endpoint.md
  - Conditions:
    - When implementing manual ticket classification or re-classification features
    - When working with POST /api/servicedesk/tickets/{ticket_id}/classify endpoint
    - When mapping AI classification categories to ticket categories
    - When troubleshooting on-demand AI classification for tickets
    - When implementing entity extraction from ticket content
    - When working with classification metadata (tokens, cost, model used)

- app_docs/feature-e7fda4c9-smart-article-suggestions-self-resolution.md
  - Conditions:
    - When working with smart article suggestions during ticket creation
    - When implementing or modifying self-resolution (ticket deflection) tracking
    - When working with sd_self_resolutions table or SelfResolutionRepository
    - When implementing deflection rate analytics or knowledge base effectiveness metrics
    - When modifying FKServicedeskTicketForm "Esto resolvió mi problema" functionality
    - When working with POST /api/servicedesk/knowledge/self-resolved endpoint
    - When implementing GET /api/servicedesk/analytics/deflection endpoint
    - When troubleshooting article suggestion tracking or deflection stats

- app_docs/feature-bc9023b0-knowledge-base-seed-articles.md
  - Conditions:
    - When seeding or populating ServiceDesk knowledge base articles
    - When running seed_knowledge_articles.sql or seed_knowledge_articles.py scripts
    - When adding new knowledge articles for AI recommendations
    - When troubleshooting missing article suggestions during ticket creation
    - When verifying knowledge base embeddings or semantic search functionality

- app_docs/feature-15fb1ab2-article-view-fix.md
  - Conditions:
    - When working with "Ver Articulo" links on ticket creation suggestions
    - When troubleshooting 422 errors on article view navigation
    - When modifying FKServicedeskTicketForm suggestion panel links
    - When working with knowledge article URL patterns (slug vs article_id)

- app_docs/feature-2a0579e1-frontend-react-vite-setup.md
  - Conditions:
    - When setting up or modifying the Client folder structure
    - When working with Vite configuration or path aliases
    - When configuring Material-UI theming for the application
    - When troubleshooting axios interceptor or JWT token handling
    - When deploying the frontend to Vercel
    - When adding new React dependencies or updating package.json
