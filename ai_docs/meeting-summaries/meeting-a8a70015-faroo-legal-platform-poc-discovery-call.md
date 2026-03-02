# Meeting Summary: Faroo Legal - Platform POC Discovery Call

**Date:** 2026-02-24
**ADW ID:** a8a70015

## Summary

Discovery call with Carlos, founder of Faroo Legal, a global legal services platform operating as a 'Legal Uber' that connects clients with specialized lawyers across geographies and legal specialties. The platform currently manages 400-500 lawyers in its ecosystem but operates largely manually using Notion for case management and WhatsApp/email for coordination. The team agreed to build a proof of concept focused on the specialist assignment engine and pricing engine, starting with specific use cases like trademark registration. A follow-up meeting was scheduled for Friday at 4 PM.

## Participants

- Daniel Restrepo (Business/Marketing Lead (Tremarel/Danke))
- Carlos (Founder/Co-founder (Faroo Legal))
- Daniel Cardona (Technical Lead (Tremarel/Danke))

## Prospect

- **Company:** Faroo Legal
- **Contact:** Carlos

## Discussion Points

### Faroo Legal Business Model
Carlos explained Faroo Legal as a global legal services platform ("Legal Uber" / "Legal Cloud") that acts as a "Concilieri" — an orchestrator connecting clients with curated specialist lawyers (400-500 in the ecosystem, min. 8 years experience). The model emerged from pain points Carlos identified while managing corporate teams at Movistar and Brigard law firm.

### Client Pain Points and Market Opportunity
Legal clients face growing complexity across multiple geographies (Colombia, Mexico, USA, Bolivia) and increasing specialization (tax, corporate, labor, IP). Clients struggle to find, hire, and coordinate multiple independent lawyers. Traditional law firms have internal conflicts between teams that degrade client experience.

### Operational Workflow and Bottlenecks
The current flow: client request → intake/categorization → specialist pre-selection → pricing negotiation → client proposal → case management with task tracking and deliverables. The main bottleneck is the manual assignment process, which introduces bias (forgetting specialists) and consumes excessive time. Case tracking in Notion is functional but entirely manual.

### Specialist Ecosystem Management
Specialists include both individual lawyers (natural persons) and boutique/medium law firms (legal entities). They are scored based on service quality, teamwork, client satisfaction, and delivery track record. Originally onboarded via paid lifetime membership; specialists get paid within 1-2 days of client payment.

### Two Operational Models — Products vs. Projects
Faroo Legal identified two types of work: automatable products (e.g., trademark registration) that should require minimal manual intervention, and complex projects requiring hands-on concilieri involvement. Small products consume disproportionate energy but serve as entry points for larger client relationships.

### Technology Stack and Tool Decisions
Currently using Notion for operations/case management (linked to Google Drive for document storage). Explored Go High Level for CRM but decided against it to avoid managing two disconnected databases. Daniel Restrepo recommended keeping Go High Level for the commercial funnel while building a unified operational platform.

### AI and Hybrid Human-Agent Vision
Carlos envisions the specialist community evolving into a hybrid model of human experts and AI agents. Meeting transcripts could be automatically processed to extract requirements and route them to appropriate specialists, reducing manual categorization and assignment.

## Action Items

- [ ] Design and build a proof of concept for the specialist assignment and pricing engine (Owner: Daniel Cardona (Tremarel/Danke)) [Due: Friday follow-up (2026-02-28)]
- [ ] Update and send the commercial proposal (Owner: Carlos (Faroo Legal)) [Due: Same day (2026-02-24)]
- [ ] Find out and share Notion licensing costs (Owner: Carlos (Faroo Legal))
- [ ] Document specialist assignment criteria/heuristics (currently only in Carlos's head) (Owner: Carlos (Faroo Legal))
- [ ] Consolidate specialist database (natural persons and legal entities with skills, experience, certifications) (Owner: Carlos (Faroo Legal) / Tremarel team)
- [ ] Share email address via chat for meeting invite (Owner: Carlos (Faroo Legal)) [Due: Same day (2026-02-24)]

## Decisions

- Start with a proof of concept (POC) rather than building the full platform at once
- POC will focus on the specialist assignment engine and pricing engine as the core value proposition
- Use specific test cases for the pilot: trademark registration and one additional case type, with 3-4 specialists
- Keep Go High Level for the commercial/CRM funnel; build custom solution for operations
- Adopt a phased approach to platform development
- Carlos offered to support investor-related activities if needed

## Next Steps

- Follow-up meeting scheduled for Friday 2026-02-28 at 4:00 PM to review POC progress
- Daniel Cardona to process meeting input and design the proof of concept architecture
- Carlos to update and send the commercial proposal immediately
- Both parties to prepare their deliverables: Tremarel for the POC design, Carlos for specialist data and assignment criteria
