# Meeting Summary: Discovery Meeting - Mi Casa al Dia Property Information System

**Date:** Not specified
**ADW ID:** c3185131

## Summary

Discovery meeting with Mi Casa al Dia, a digital real estate company that sells Colombian properties to immigrants in the US. Their core pain point is the extremely manual and time-consuming process of consolidating property information from 25+ construction companies (each with different Excel/PDF formats) to respond to client inquiries. A phased solution was proposed: (1) data consolidation into a PostgreSQL database, (2) an agile update mechanism with drag-and-drop file ingestion, and (3) WhatsApp integration for automated client responses. Next step is signing a confidentiality agreement, sharing sample data, and building a proof of concept by the following week.

## Participants

- Daniel (Technology Consultant)
- Mi Casa al Dia Representative (Operations Lead / Architect at Mi Casa al Dia)
- Ruben (Mutual Contact / Referral (not present))
- Daniel Cardona (Mentioned at start, unclear if joined)

## Prospect

- **Company:** Mi Casa al Dia
- **Contact:** Mi Casa al Dia Representative

## Discussion Points

### Manual Information Consolidation Problem
Mi Casa al Dia manages 250+ real estate projects from 25+ construction companies. Each company sends data in different formats (Excel, PDF). Responding to a single client inquiry requires searching across the website, multiple Excel files, PDF brochures, Google Drive, WhatsApp groups, and email. A simple city-based query can take 5+ minutes and involves consulting 4-5 different sources.

### Proposed Phased Solution Architecture
Three-phase approach agreed upon: Phase 1 - Initial data consolidation into a PostgreSQL database with field mapping rules. Phase 2 - Agile update mechanism via a web app with drag-and-drop file upload that auto-detects fields from varying Excel/PDF formats. Phase 3 - WhatsApp integration for automated message generation and client response.

### Data Schema and Required Fields
Key fields identified for the consolidated database: constructor name, project name, active status, last update date, published status, department, municipality, sector/zone, typology (apartment/house/lot), phase (launch/construction/immediate delivery), area range, number of units, unit types, VIS classification, price range, parking, bedrooms, bathrooms, and project images.

### Current Client Communication Workflow
Clients arrive via WhatsApp integrated with HubSpot, but HubSpot's 24-hour Meta messaging window is restrictive. The team transfers clients to corporate WhatsApp Business lines for continued communication. Responses are manually drafted with project details, links to the website, brochure information, and payment plans.

### Website and Admin Panel Limitations
Mi Casa al Dia has a custom-coded website (not Wix or similar platform) with an admin panel. Updating prices requires manually editing each project and each unit type one by one. Price updates from a single large constructor with 80 projects is extremely time-consuming. Data must be updated in both the admin panel and the internal Excel macro separately.

### Company Background and Constraints
Mi Casa al Dia is part of a large corporate group (1000+ employees) serving immigrants in the US with legal, tax, and insurance services. The parent company enforces strict technology policies and mandates HubSpot as the CRM. The IT department prioritizes immigration operations, leaving smaller subsidiaries like Mi Casa al Dia without tech support but bound by restrictions.

### Scaling Challenges
Mi Casa al Dia currently operates with only 3 people. They want to scale to handle more clients but lack the infrastructure for rapid, informed responses. The immigration political climate in the US has also impacted their target market, pushing them to explore new markets.

### Website-Database Integration Possibility
Discussed the possibility of connecting the new consolidated database to the existing website so that uploading data once automatically updates the public-facing site. This would eliminate the current dual-update process. Feasibility depends on the website's technical architecture, which the client will share.

## Action Items

- [ ] Send or agree on a confidentiality/NDA agreement before sharing proprietary data (Owner: Both parties (Mi Casa al Dia to send theirs, or Daniel's team to provide one)) [Due: Before data sharing - within days]
- [ ] Share sample Excel files from various construction companies (different formats) (Owner: Mi Casa al Dia Representative) [Due: After NDA is signed]
- [ ] Share sample PDF brochures from construction companies (Owner: Mi Casa al Dia Representative) [Due: After NDA is signed]
- [ ] Share the website technical specifications and architecture details (Owner: Mi Casa al Dia Representative) [Due: After NDA is signed]
- [ ] Define the complete field mapping rules (how different constructor formats map to unified schema) (Owner: Mi Casa al Dia Representative)
- [ ] Build proof of concept for data consolidation and recurring update mechanism (Owner: Daniel (Technology Consultant)) [Due: By Monday or Tuesday of the following week]
- [ ] Review NDA options with Cardona and send to Mi Casa al Dia (Owner: Daniel (Technology Consultant))
- [ ] Schedule follow-up meeting to review proof of concept (Owner: Both parties) [Due: Tuesday of the following week]

## Decisions

- Adopt a phased approach: Phase 1 (Data Consolidation), Phase 2 (Update Mechanism), Phase 3 (WhatsApp Integration)
- Start with a proof of concept focused on data consolidation and agile updating before committing to the full solution
- Sign a confidentiality agreement before sharing any proprietary constructor data
- Use WhatsApp for ongoing communication between meetings
- Evaluate the existing website architecture to determine if the new database can be connected to it or if a new frontend is needed

## Next Steps

- Finalize and sign confidentiality agreement (either from Mi Casa al Dia or from Daniel's team)
- Mi Casa al Dia shares sample Excel files, PDFs, and website technical specs
- Daniel builds a proof of concept for data consolidation with sample data
- Follow-up meeting scheduled for Monday or Tuesday of the following week to review the proof of concept
- Based on proof of concept results, define scope and next phases of the project
