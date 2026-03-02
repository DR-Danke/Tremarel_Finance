# Meeting Summary: Faroo Legal - Platform Discovery & Proof of Concept Scoping

**Date:** 2026-02-24
**ADW ID:** f40cfdf4

## Summary

Carlos, founder of Faroo Legal, presented his vision for a global legal services platform — an 'Uber for Legal' — that connects clients with a curated ecosystem of 400-500 specialist lawyers across multiple geographies and legal domains. The team identified the core bottleneck as the manual assignment and operations workflow (currently run via WhatsApp, email, and Notion) and agreed to build a phased proof of concept starting with the specialist assignment engine and pricing engine. A follow-up meeting was scheduled for Friday, February 28, 2026 at 4:00 PM to review the POC design and Carlos's updated commercial proposal.

## Participants

- Daniel Restrepo (Tremarel / Marketing & Commercial Strategy)
- Carlos (Founder & Consigliere, Faroo Legal)
- Daniel Cardona (Tremarel / Technical Architecture & Systems)

## Prospect

- **Company:** Faroo Legal
- **Contact:** Carlos

## Discussion Points

### Faroo Legal Business Model — 'Uber for Legal'
Carlos described Faroo Legal as a global legal services platform that acts as a 'Consigliere' — orchestrating the right specialists for each client need. The platform addresses the fragmentation problem where clients must independently coordinate lawyers across countries and specialties. Faroo curates and assigns specialists from its 400-500 member ecosystem based on expertise, performance score, and availability.

### Specialist Assignment & Routing Engine
The primary bottleneck identified is the manual specialist assignment process. The team discussed building an intelligent routing engine that processes client requirements (potentially using AI to extract needs from discovery calls), matches them against the specialist database (skills, certifications, experience, score, current workload), and proposes candidate specialists for approval. This is the top priority for the POC.

### Pricing Engine
A pricing motor is needed that determines specialist cost vs. client billing rate. After the platform pre-selects specialists, there is a negotiation phase with the specialist on fees, then Faroo adds its margin and presents a unified quote to the client. Historical pricing data should inform suggested ranges.

### Operations Pipeline & Case Management
Once a client accepts an offer, operational tickets are created per case. Each case tracks assigned specialists, pending tasks, deliverables, deadlines, billing status, and document uploads (currently via Google Drive linked to Notion). Automated alerts for upcoming deadlines and overdue deliverables were identified as critical needs.

### Commercial Funnel & CRM Integration
The commercial pipeline flows from multi-channel lead acquisition through discovery calls to proposal generation. Speaker 1 (Daniel Restrepo) recommended keeping Go High Level as the CRM for the commercial funnel, with backend integrations to pull data into the operations platform. Currently considering consolidating to avoid dual-database management between Go High Level and Notion.

### Specialist Database & Scoring System
Specialists include both individual lawyers (personas naturales) and law firms/boutiques (personas juridicas), each with minimum 8 years of experience. A scoring system rates specialists based on service quality, client satisfaction, teamwork ability, delivery timeliness, and recurrence. This database already exists but is managed manually, leading to human bias and forgotten specialists.

### Two Operational Models — Automatable Products vs. Complex Projects
Carlos identified two distinct case types: standardized products (e.g., trademark registration) that should be almost fully automated, and complex projects (e.g., corporate restructuring, transfer pricing) requiring deep specialist involvement and the Consigliere methodology. Small standardized cases consume disproportionate management energy relative to their value.

### Dual Case Origination Channels
Cases arrive through two paths: (1) directly from clients via Faroo's commercial funnel, where Faroo invoices the client, and (2) through specialist referrals, where a member specialist brings a case outside their expertise, effectively becoming a client for that project. Both channels feed into the same operational pipeline.

### AI & Hybrid Human-Agent Ecosystem Vision
Carlos expressed a forward-looking vision where the specialist community becomes hybrid — combining human lawyers with AI agents. This aligns with Tremarel's capabilities in AI/agent systems and represents a future evolution opportunity for the platform.

## Action Items

- [ ] Design and build a proof of concept for the specialist assignment engine and pricing engine, starting with a limited pilot (e.g., trademark registration case + one other case type, with 3-4 specialists) (Owner: Daniel Cardona (Tremarel)) [Due: Initial design by Friday 2026-02-28]
- [ ] Document the specialist assignment heuristics and criteria (currently exists only in Carlos's head) (Owner: Carlos (Faroo Legal)) [Due: Before Friday 2026-02-28 follow-up]
- [ ] Update and send the revised commercial proposal (Owner: Carlos (Faroo Legal)) [Due: Same day (2026-02-24)]
- [ ] Provide Notion licensing cost information (Owner: Carlos (Faroo Legal))
- [ ] Consolidate the specialist database for the pilot (select 3-4 specialists, define data schema for skills, certifications, experience, score) (Owner: Carlos (Faroo Legal) + Tremarel)
- [ ] Schedule and send calendar invite for Friday follow-up meeting at 4:00 PM (Owner: Daniel Cardona (Tremarel)) [Due: 2026-02-24]

## Decisions

- Pursue a phased approach — start with a proof of concept before building the full platform
- POC will focus on the specialist assignment engine and pricing engine as the two core components
- Pilot will use specific case types (trademark registration + one other) with 3-4 specialists to validate the concept
- Keep Go High Level for the commercial CRM funnel; integrate it with the operations platform via backend connectors
- Follow-up meeting scheduled for Friday, February 28, 2026 at 4:00 PM
- Carlos offered to support Tremarel with investor-facing materials if needed

## Next Steps

- Follow-up meeting on Friday, February 28, 2026 at 4:00 PM to review the POC design and Carlos's updated proposal
- Carlos to send updated commercial proposal immediately
- Tremarel to process meeting input and design the POC architecture
- Carlos to document assignment criteria and provide specialist data for the pilot
- Carlos to confirm Notion licensing costs with his partner
