# Meeting Summary: Farú Legal — Discovery Call & Proof of Concept Scoping

**Date:** 2026-02-24
**ADW ID:** 151661c9

## Summary

Discovery call with Carlos, co-founder of Farú Legal, a global legal services platform that operates as a 'legal cloud' — connecting enterprise clients with a curated ecosystem of 400–500 specialist lawyers across multiple jurisdictions and practice areas. The meeting mapped out the full operational flow: commercial funnel, AI-assisted specialist assignment, pricing engine, case management, and billing. The team agreed to build a proof of concept starting with 1–2 case types (e.g., trademark registration) and 3–4 specialists, with a follow-up meeting scheduled for Friday February 28 at 4:00 PM.

## Participants

- Daniel Restrepo (Tremarel / Danke Apps — Business Lead)
- Carlos (Farú Legal — Co-Founder / CEO)
- Daniel Cardona (Tremarel / Danke Apps — Technical Lead)

## Prospect

- **Company:** Farú Legal
- **Contact:** Carlos

## Discussion Points

### Platform Architecture & Operational Flow
Mapped the end-to-end flow: leads enter through multiple channels → discovery call → system extracts requirements → assignment engine proposes specialists → pricing negotiation → client receives quote → upon acceptance, operational tickets are created → case management with task tracking, deliverables, and billing. Three distinct data layers: commercial database, operations database, and specialist database.

### Specialist Assignment Engine (Core Need)
The main bottleneck today is manual specialist assignment. Carlos has an undocumented heuristic in his head for matching cases to specialists based on specialty, jurisdiction, past performance score, workload capacity, and collaboration ability. This logic needs to be documented and automated, potentially with AI for complex cases and deterministic code for simpler ones.

### Pricing Engine
Each assignment requires a pricing negotiation: the system should suggest price ranges based on historical data with specialists, allow Farú Legal to add their margin, and generate a client-facing quote. Specialists are paid within 1–2 days of client payment.

### Farú Legal Business Model — 'Legal Uber'
Carlos founded Farú Legal after 3 years as corporate team manager at Brigard (major law firm). The platform addresses a market gap: clients need cross-jurisdictional, multi-specialty legal services but struggle to coordinate independent lawyers across countries. Farú Legal's 'Concilieri' methodology organizes the right specialists into coordinated teams for each case.

### Specialist Ecosystem
400–500 lawyers in the ecosystem, including individual practitioners and boutique/mid-size firms. Originally individual-only, but boutique firms proved excellent due to their infrastructure + deep specialization. Minimum 8 years experience required. Specialists earn a performance score based on quality, timeliness, and teamwork.

### Current Tooling & Pain Points
Operations managed in Notion (case tracking, lawyer assignments, tasks, billing status, Google Drive links). Started with Go High Level for CRM but abandoned it to avoid maintaining two disconnected databases. Everything is still largely manual — WhatsApp, email, manual follow-ups. Daniel Restrepo recommended keeping Go High Level for the commercial funnel only.

### Two Operational Models — Products vs. Projects
Simple, repeatable services (e.g., trademark registration) consume disproportionate management energy and should be fully automated. Complex projects (e.g., cross-border corporate structuring) require the Concilieri's strategic involvement. Both must be served because small cases often lead to major client relationships.

### AI & Agent Opportunities
Carlos envisions the specialist community evolving into a hybrid of human lawyers and AI agents. Potential AI applications include: processing discovery call transcripts to extract requirements, automatic specialist matching, automated alerts and follow-ups, and full automation of standardized products like trademark registration.

## Action Items

- [ ] Design and build a proof of concept for the specialist assignment and pricing engine, scoped to 1–2 case types and 3–4 specialists (Owner: Daniel Cardona (Tremarel)) [Due: Present progress at Friday follow-up (2026-02-28)]
- [ ] Document the specialist assignment heuristic (criteria, decision tree, scoring factors) (Owner: Carlos (Farú Legal)) [Due: Before Friday follow-up]
- [ ] Provide consolidated specialist database for the POC pilot group (Owner: Carlos (Farú Legal))
- [ ] Update the commercial proposal and send to the Tremarel team (Owner: Carlos (Farú Legal)) [Due: Same day (2026-02-24)]
- [ ] Provide current Notion licensing costs (Owner: Carlos (Farú Legal))

## Decisions

- Proceed with a phased proof-of-concept approach rather than building the full system at once
- POC will focus on the specialist assignment engine with 1–2 case types (e.g., trademark registration) and 3–4 specialists
- Drop Go High Level as standalone CRM to avoid dual-database management; consider keeping it for commercial funnel only
- The platform will be designed as a service desk connected to CRM channels with embedded AI for assignment and classification

## Next Steps

- Follow-up meeting scheduled for Friday, February 28, 2026 at 4:00 PM
- Carlos to send updated proposal immediately after this call
- Tremarel team to process meeting input and design the POC architecture
- Carlos available to support with investor-related needs if required
