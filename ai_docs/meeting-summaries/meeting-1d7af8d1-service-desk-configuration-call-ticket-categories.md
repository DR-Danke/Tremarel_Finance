# Meeting Summary: Service Desk Configuration Call - Ticket Categories, VIP Assignment & WhatsApp Chatbot

**Date:** 2026-03-03
**ADW ID:** 1d7af8d1

## Summary

The team reviewed the Service Desk ticket system configuration including first-level assignment rules (numbering, location, workload), the finalized 5 ticket categories (Hardware, Software, SAP, Telecommunications, Others), and VIP user assignment logic. The developer confirmed database model changes are complete and API/frontend adjustments will be finished today. Fixed assets data will be delivered next week. The team agreed to begin WhatsApp chatbot testing for tone and communication quality.

## Participants

- Speaker 1 (Rolito) (Project Lead / Client-side Coordinator)
- Speaker 2 (Developer (Database, API & Frontend))
- Speaker 3 (Stakeholder / Manager)
- Nicolás (Team Member (has WhatsApp chatbot link))

## Prospect

- **Contact:** Rolito

## Discussion Points

### Ticket Category Definition
Categories finalized to exactly 5: Hardware, Software, SAP (core system), Telecommunications, and Others. SAP tickets are initially routed via email. The service catalog Level 1 follows these same 5 categories with subcategories underneath.

### Service Catalog Structure
Level 1 catalog aligns with the 5 defined categories. Based on user selection and ticket description, tickets are routed to the appropriate category and subcategory. Software subcategories include Identity & Access Management (user creation, deletion, modifications, password resets).

### First-Level Ticket Assignment
Assignment criteria defined based on three factors: numbering/scale, geographic location, and workload (number of tickets). These determine which support agent handles each incoming ticket.

### VIP User Assignment
VIP users are identified and directed to first-level support for priority handling. Only incident-type requests qualify for VIP treatment. CC notifications are sent based on the user's city to designated personnel.

### Development Progress Update
Database model changes are already complete. API middleware and frontend adjustments are in progress across three development stages, expected to be completed today.

### Fixed Assets Data
Internal teams are working on populating fixed asset information into the provided structure/format. Data delivery expected by next week.

### WhatsApp Chatbot Testing
Request to begin testing the WhatsApp chatbot interface for ticket submission. Focus on evaluating tone, communication style, and response quality. Nicolás has the conversation link.

## Action Items

- [ ] Complete API and frontend adjustments for the new ticket category and assignment model (Owner: Speaker 2 (Developer)) [Due: 2026-03-03 (today)]
- [ ] Deliver fixed assets data in the agreed structure/format (Owner: Speaker 1 (Rolito) / Internal teams) [Due: Next week (~2026-03-10)]
- [ ] Begin WhatsApp chatbot testing for tone and communication evaluation (Owner: Speaker 1 (Rolito) / Nicolás) [Due: Between today and tomorrow (2026-03-03 to 2026-03-04)]
- [ ] Notify the team once all three development stages are complete (Owner: Speaker 2 (Developer))

## Decisions

- Ticket categories are fixed at exactly 5: Hardware, Software, SAP, Telecommunications, and Others
- VIP assignment applies only to incident-type requests
- Service catalog Level 1 will follow the 5 defined categories with subcategories
- Fixed assets data will follow the structure/format already provided
- WhatsApp chatbot testing to begin immediately (today/tomorrow)
- CC notifications for VIP incidents are sent based on the user's city

## Next Steps

- Developer completes API and frontend changes for ticket categories and assignment logic
- Developer notifies team upon completion of all three development stages
- Rolito coordinates with Nicolás to start WhatsApp chatbot testing today/tomorrow
- Internal teams finalize fixed assets data and send it next week
- Team evaluates WhatsApp chatbot responses and provides feedback on tone and communication
