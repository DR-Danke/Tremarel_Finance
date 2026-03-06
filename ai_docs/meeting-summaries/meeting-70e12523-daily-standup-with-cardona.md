# Meeting Summary: Daily Standup with Cardona

**Date:** 2026-03-05
**ADW ID:** 70e12523

## Summary

Daily standup covering progress on the guest name matching/cross-referencing system, bank reconciliation closing, and Service Desk QA strategy. Key outcomes include a decision to use Chatbase for WhatsApp demo numbers for the Faru Legal POC, a plan to reset user passwords in Supabase (except admin), and alignment on preparing a comprehensive commercial deliverable summarizing development hours and contract value for upcoming negotiations.

## Participants

- Speaker 1 (Business / Commercial Lead)
- Daniel Cardona (Dani) (Technical Lead / Developer)

## Prospect

- **Company:** Tremarel

## Discussion Points

### Guest Name Matching & Cross-Referencing System
Discussed issues with name matching in the cross-reference file: asterisks prepended to names and 'Señor/Señora' suffixes are interfering with matches. Name normalization is already implemented. The system correctly filters out Bolivian nationals (report targets foreigners). Explored switching data source from Excel to API/XML for better integration.

### Faru Legal POC - WhatsApp Integration & Ticket Assignment
The Faru Legal proof of concept is built but barebones. Missing WhatsApp integration for ticket creation. Need a demo phone number — agreed to use Chatbase for free US numbers. Core flow: WhatsApp message creates a ticket, then an assignment routine allocates it to a lawyer by expertise. Ticket lifecycle stages: creation, assignment, work.

### Service Desk QA & Testing Strategy
Debated whether to test internally first or hand off to stakeholders immediately. Agreed to do internal testing first, then deliver to the internal stakeholder with specific test flows and request structured feedback. Authentication layout broke, requiring a user password reset.

### Bank Reconciliation & Financial Closing
Five banks have been set up; closing expected this week. Frontend not yet delivered. Need to provision another database ($10). Waiting for confirmation that everything is ready before investing in frontend. Previous reconciliation achieved 75% automatic match rate.

### Commercial Pipeline & Deliverable Preparation
Speaker 1 will compile all sent proposals and pending commercial items into a complete deliverable showing development hours invested, contract value, and cost reductions — to be used as a negotiation tool.

### Upcoming Meetings & Legal Matters
Meeting with Tomás: listen to his position on valuation, prepare counterarguments. Meeting with María: discuss document scope, ask about Liganoa and Faru Legal contacts. Possible meeting with Faru Legal tomorrow. Meeting with Caiceo also planned.

## Action Items

- [ ] Finish the guest name matching/cross-referencing system (Owner: Daniel Cardona (Dani)) [Due: 2026-03-05]
- [ ] Review API endpoint and download XML to evaluate as alternative data source (Owner: Speaker 1)
- [ ] Reset passwords for all Supabase users except admin (Owner: Speaker 1)
- [ ] Advance Service Desk development and verify stakeholder-reported flows (Owner: Daniel Cardona (Dani))
- [ ] Obtain a WhatsApp demo phone number via Chatbase (Owner: Speaker 1)
- [ ] Investigate Chatbase webhook integration for ticket reception and user notifications (Owner: Speaker 1)
- [ ] Prepare complete commercial deliverable (development hours, costs, contract details, proposals) (Owner: Speaker 1)
- [ ] Attend meeting with Tomás — listen to his position and prepare counterarguments (Owner: Daniel Cardona (Dani)) [Due: 2026-03-05]
- [ ] Attend lunch meeting with María — discuss document scope and ask about Liganoa/Faru Legal contacts (Owner: Daniel Cardona (Dani)) [Due: 2026-03-05]
- [ ] Attend meeting with Caiceo (Owner: Daniel Cardona (Dani))
- [ ] Schedule meeting with Faru Legal (possibly tomorrow) (Owner: Daniel Cardona (Dani)) [Due: 2026-03-06]

## Decisions

- Do internal testing of Service Desk before releasing to stakeholders
- Reset all Supabase user passwords except admin to fix authentication issues
- Use Chatbase to obtain free US phone numbers for WhatsApp demos
- Data format (XML vs Excel) is not critical right now — use whatever works with existing libraries on Render
- Ticket assignment should be a separate routine that runs after ticket creation, not part of the creation step itself
- Deliver a partial solution with tips if the full cross-referencing system cannot be completed today

## Next Steps

- Finish cross-referencing system and evaluate API/XML data source
- Reset Supabase user passwords and re-enable stakeholder access to Service Desk
- Set up Chatbase WhatsApp number and integrate webhooks for Faru Legal POC demo
- Meeting with Tomás to discuss valuation and negotiation position
- Lunch meeting with María to discuss legal document scope
- Meeting with Caiceo
- Possible meeting with Faru Legal tomorrow
- Compile commercial pipeline deliverable with all proposals and values for negotiation
