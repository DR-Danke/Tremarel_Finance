# Meeting Summary: FAROO Proof of Concept Demo - Legal Service Desk & Notion Integration

**Date:** 2026-03-05
**ADW ID:** 2b20cf91

## Summary

A proof-of-concept demo was presented to the FAROO prospect showcasing a legal service desk platform with AI-powered specialist routing (via OpenAI). The client currently operates using Notion for case management, specialist coordination, billing, and CRM — all manually maintained. Two complementary workstreams were identified: commercial/sales process automation and operational process automation. The agreed next step is to identify specific manual Notion workflows that can be automated through agentic flows while preserving the client's existing organizational structure.

## Participants

- Speaker 1 (FAROO Client) (Prospect / Client - Legal Operations Lead)
- Speaker 2 (Daniel) (Sales / Business Consultant)
- Speaker 3 (Daniel - Technical) (Technical Lead / Developer)

## Prospect

- **Company:** FAROO

## Discussion Points

### Legal Service Desk POC Demo
A barebones proof-of-concept was demonstrated featuring specialist management (individuals and boutiques), client management, case creation with legal domains/jurisdictions/budgets, and AI-powered specialist assignment using OpenAI. The system includes Kanban-style dashboards for case tracking and workload visibility (e.g., showing specialists at capacity in red).

### Current Notion-Based Operations
The client showed their existing Notion setup which handles commercial process tracking, operational case management, specialist/lawyer database, document structure, referral commissions, billing/payment tracking, and invoicing. Notion is valued for its flexibility ('lienzo'/canvas) but everything is manual. They pay 57 hours/month and lawyers access as free guests.

### Commercial vs. Operational Process Separation
Two distinct processes were identified: (1) Commercial/Sales — prospect acquisition via LinkedIn, pre-meeting qualification, growth engine, and CRM capabilities that Notion lacks; (2) Operational — case assignment, specialist coordination, case tracking, billing. Both are complementary but require different solutions.

### Automation Pain Points
Key pain points identified: manual data entry in Notion, WhatsApp message tracking (not knowing if messages were answered), manual invoice handling (creating in Alegra, downloading, uploading to Notion), manual case status updates, and lack of prospecting/campaign capabilities.

### WhatsApp and Email Integration
The client expressed strong interest in having WhatsApp and email channels automatically feed information into the system, enabling automated responses for routine queries (e.g., case status updates like 'the appeal has been filed') and flagging items requiring personal attention.

### Notion Integration Strategy
Rather than replacing Notion entirely, the team proposed identifying automation points where the service desk platform can run underneath and feed Notion, or integrate bidirectionally. The client's Notion AI assistant ('el narizon') already generates proposals and connects information, making a hybrid approach attractive.

### Investment Portfolio Analogy for Prioritization
The consulting team proposed prioritizing automation like an investment portfolio: short-term (automate biggest pain points now for immediate ROI), medium-term, and long-term improvements. Start with what causes the most headaches today.

### Agentic Flows for Administrative Tasks
The technical team proposed using agentic workflows to handle administrative/operational tasks like creating cases, assigning specialists, and transferring data — shifting the client's role from 'doing the assignment' to 'reviewing the assignment'.

## Action Items

- [ ] Identify and document specific manual processes in Notion that transfer information to/from other systems (Alegra invoicing, Google Drive, WhatsApp, email) as candidates for automation (Owner: FAROO Client (Speaker 1))
- [ ] Map out the three core processes: sales/commercial process, operational/case management process, and billing/invoicing process (Owner: Speaker 2 (Daniel - Business))
- [ ] Build a more involved proof of concept targeting one specific Notion workflow, demonstrating an agentic flow that automates data transfer between Notion and another system (Owner: Speaker 3 (Daniel - Technical))
- [ ] Review the summary document previously sent via email and confirm pain points are accurately captured (Owner: FAROO Client (Speaker 1))

## Decisions

- The service desk concept is validated as the right operational model for FAROO's legal case management needs
- The project will be split into two workstreams: commercial/sales process and operational process
- Notion will not be immediately replaced; instead, the approach will focus on automating manual processes and integrating with the existing Notion setup
- Prioritization will follow a short-term/medium-term/long-term investment approach, starting with the highest-pain manual processes
- The next POC iteration should target a specific manual Notion workflow for automation via agentic flows

## Next Steps

- Client to walk through a specific manual process (Notion to external system data transfer) so the team can evaluate agentic flow automation potential
- Team to design a more involved POC demonstrating automation of one identified manual Notion workflow
- Map all integration points: Notion, Alegra (invoicing), Google Drive (documents), WhatsApp, and email
- Define automation priorities using the short/medium/long-term investment framework
- Explore WhatsApp and email ingestion as automatic data sources for the service desk platform
