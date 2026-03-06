# Meeting Summary: Service Desk WhatsApp Integration - Cardona Call

**Date:** 2026-03-04
**ADW ID:** f0132ffd

## Summary

The team reviewed the current state of the Service Desk WhatsApp integration built on Chatbase. The AI assistant already supports ticket creation and status checking via WhatsApp using Meta Business Manager. Key gaps were identified: technician responses from the web app do not flow back to WhatsApp users, documentation generation from tickets needs refinement, and additional Chatbase custom actions require a paid upgrade. The team agreed to deliver the current MVP and propose an expanded feature set at an additional recurring monthly cost.

## Participants

- Speaker 1 (Cardona) (Technical Lead / WhatsApp Integration Owner)
- Speaker 2 (Daniel) (Developer / Platform Owner)

## Prospect

- **Contact:** Cardona

## Discussion Points

### WhatsApp Service Desk Assistant - Current Capabilities
The Chatbase-powered assistant currently supports: get ticket details, get user tickets, get ticket status, search knowledge base, add comment to ticket, escalate to human, and create ticket. These actions call backend API endpoints and return information to users via WhatsApp.

### One-Way Communication Gap
Critical gap identified: when a technician responds or updates a ticket through the web application, the update does not flow back to the end user on WhatsApp. The current flow only supports user-to-system communication, not system-to-user notifications. Outbound webhooks via Chatbase are needed to close this loop.

### Meta Business Manager & WhatsApp Setup
WhatsApp integration requires a Meta Business Manager account (free/freemium) and a dedicated phone number purchased from a provider. The number is registered in WhatsApp Manager within Meta Business Suite, with two-step verification and Facebook policy-compliant naming.

### User Management & Onboarding
There is no self-service sign-up flow. Users are assigned by administrators. IT sends an email notifying users about the new Service Desk. End users creating tickets via WhatsApp only see their own tickets and ticket queue in the 'My Panel' view.

### Documentation Generation from Tickets
Debate on whether documentation should be generated per-ticket or per-problem. Generating per-ticket would create excessive documentation. The recommendation is to generate documentation at the service category/problem level, using ticket logs as data inputs organized by service categories.

### Missing Custom Actions
Additional actions needed: get ticket comments (currently only add comment exists), change ticket status. Custom actions in Chatbase require the paid plan. Each action is configured with API endpoint, HTTP method, headers, inputs, and JSON body.

### Ticket Detail Improvements
Several UI fixes needed: display technician name instead of ID, assign service category for WhatsApp-originated tickets, collect user location via system prompt to create tags, and fix classification data not being set for WhatsApp tickets.

### Pricing & Commercial Strategy
Current pricing: $10/month for 12 technicians. Proposed strategy: deliver the MVP with 2 core actions (create ticket, check status), then offer expanded features (all custom actions, more integrations) at $20/month recurring. Additional Chatbase costs need to be factored in.

### Chatbase Conversation Data
Chatbase conversations can be pulled via API, providing analytics on which users write most, what types of problems occur, which assets and locations are involved. This data feeds into resolution insights.

### Product Showcase Potential
The current implementation is polished enough to serve as a product demo/showcase on the website, demonstrating AI-powered workflow management for enterprises.

## Action Items

- [ ] Pay for Chatbase premium to enable all custom actions (Owner: Cardona)
- [ ] Refine the WhatsApp assistant system prompt to be more conversational (Owner: Cardona)
- [ ] Add user location collection to the system prompt and create location tags (Owner: Cardona)
- [ ] Create 'get ticket comments' custom action in Chatbase (Owner: Cardona)
- [ ] Implement outbound webhook so technician responses flow back to WhatsApp users (Owner: Cardona)
- [ ] Fix ticket detail view to display technician name instead of ID (Owner: Daniel)
- [ ] Auto-assign service category for tickets originating from WhatsApp (Owner: Daniel)
- [ ] Fix documentation generation to properly save when resolving tickets (Owner: Daniel)
- [ ] Remove duplicate sections (activity history vs audit history) in ticket detail (Owner: Daniel)
- [ ] Determine Chatbase subscription cost and finalize client pricing model (Owner: Cardona) [Due: Before next client meeting]
- [ ] Prepare delivery presentation showing MVP and upsell opportunities (Owner: Both) [Due: Next client meeting]

## Decisions

- No self-service sign-up flow — users will be assigned by administrators via email notification
- MVP WhatsApp channels: WhatsApp and email are the two supported input channels for ticket creation
- MVP includes two core Chatbase actions: create ticket and check ticket status
- Documentation should be generated at the problem/service category level, not per individual ticket
- Deliver current MVP first, then propose expanded features at an additional recurring monthly cost
- Current pricing stays at $10/month for 12 technicians; expanded features to be offered at $20/month
- The finished product can be used as a website showcase/demo for the company's AI capabilities

## Next Steps

- Finalize and deliver the MVP with WhatsApp ticket creation and status checking
- Determine Chatbase premium costs and calculate margin for client billing
- Prepare a proposal for the next client meeting: show delivered MVP, present expanded feature options with recurring costs
- Implement outbound webhook to enable two-way communication (technician responses back to WhatsApp)
- Add missing Chatbase custom actions (get comments, change status) after upgrading plan
- Set up the product as a website showcase demonstrating AI-powered service desk workflows
