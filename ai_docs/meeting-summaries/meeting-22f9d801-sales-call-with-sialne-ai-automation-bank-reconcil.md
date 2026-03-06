# Meeting Summary: Sales Call with SIALNE — AI Automation & Bank Reconciliation

**Date:** 2026-03-03
**ADW ID:** 22f9d801

## Summary

Initial sales call with Ignacio Guerra, Financial Director at SIALNE (a poultry company in Brazil, part of the Carnero family group). The team presented their three-phase AI automation approach (Augment, Automate, Agentize) and demonstrated a live bank reconciliation tool achieving ~90% automatic matching with 35 rules. Ignacio expressed strong interest in starting with bank reconciliation as a quick-win pilot project. Additional opportunities discussed included legal document management with role-based access controls and SAP security governance.

## Participants

- Daniel (Co-founder / Former VP of Product at Fincargo (Back Office & Processes))
- Ignacio Guerra (Financial Director at SIALNE (Prospect))
- Dani (Co-founder / Growth & Marketing)

## Prospect

- **Company:** SIALNE
- **Contact:** Ignacio Guerra

## Discussion Points

### Bank Reconciliation Automation
Live demo of the bank reconciliation tool was shown. The system uploads bank statements and ERP ledger entries (5,800+ records), applies ~35 matching rules in order of confidence (exact match on ID/amount/date, then fuzzy matches with date/amount tolerance), achieving ~90% automatic reconciliation. Currently outputs to Excel but can be integrated further. The prospect's team currently spends 2-3 days with 1-2 people on this monthly process.

### Three-Phase AI Implementation Approach
The team presented their methodology: (1) Augment — point automations to help existing staff do more; (2) Automate — full process automation with API integrations replacing manual Excel workflows; (3) Agentize — deploy autonomous AI agents so staff shift from operators to supervisors. Emphasized that jumping directly to agents often fails due to organizational readiness and token costs.

### SIALNE Organizational Structure & IT Governance
SIALNE is the anchor company of the Carnero family group (poultry), with a smaller dairy subsidiary. Ignacio oversees Finance, IT (~15 people), Legal, Utilities, and Facilities. IT governance follows an annual planning process: business area directors present tech needs in their business plans, IT allocates internal resources, and overflow projects are outsourced with the requesting area paying from its own budget. IT acts as PMO for third-party projects.

### Legal Document Management & Access Control
Ignacio's legal team wants to build a contract management system accessible via WhatsApp where users can query contract information. The critical challenge is role-based access control — determining which users can see which contracts and which fields (e.g., one user sees contract duration but not pricing). The team presented their existing Legal Hub solution with contract templates, approval workflows, and queryable contract database.

### SAP Security & Access Governance
SIALNE recently upgraded to SAP S/4HANA but lacks formal access governance. Currently, access requests are granted informally based on manager approval. As the company grows (from 4 trusted users to 1,000), they need proper profile definitions per role/process, access review routines, and usage monitoring. Ignacio asked for vendor recommendations in Colombia.

### Organizational Diagnostic Offering
The team presented their diagnostic service that maps the entire organization through WhatsApp conversations and interviews. Deliverables include: departmental digital maturity assessment, economic opportunity analysis, macro-process documentation, knowledge gap identification, system criticality prioritization, technical debt assessment, and ROI-driven implementation recommendations.

### Pricing & Commercial Terms
Bank reconciliation: $4,000 one-time implementation fee + $200/month maintenance (unlimited bank accounts). Services exported from Colombia are VAT-exempt, so quoted prices are final. Implementation timeline: 1-2 weeks from kickoff to functional platform. Proof of concept available with NDA.

### WhatsApp Integration for Business Processes
Discussion about routing IT service requests and invoice processing through WhatsApp instead of the current intranet-based ticketing system. Example: photo an invoice via WhatsApp, system auto-identifies it, routes to SAP for processing — reducing the need for users to be at a computer.

### Competitive Landscape
Ignacio mentioned they had spoken with Celonis that same morning about similar automation and AI agent services. SIALNE is evaluating multiple vendors to find the best fit for each specific need in terms of quality, cost, and speed.

## Action Items

- [ ] Send a brief company presentation and an initial proposal specifically for bank reconciliation automation (Owner: Tremarel team (Daniel & Dani))
- [ ] Talk to the accounting team internally to validate whether bank/account reconciliation is a real pain point and understand the specific details of the process (Owner: Ignacio Guerra)
- [ ] Research and recommend a vendor for SAP security and access governance (profile definitions, access review routines) (Owner: Tremarel team (Daniel & Dani))
- [ ] Schedule a follow-up meeting if there is alignment after internal validation and proposal review (Owner: Ignacio Guerra)
- [ ] Potentially connect Ignacio's accounting team directly with the Tremarel team for detailed technical discussions (in Portuguese) (Owner: Ignacio Guerra)

## Decisions

- Bank reconciliation automation will be the first pilot project (quick win) if validated internally
- Ignacio will validate the reconciliation use case with his accounting team before proceeding
- An NDA can be signed for a proof of concept if needed
- Legal document management and SAP access governance are secondary priorities to explore after the initial pilot
- Communication can proceed in Portuguese with Ignacio's team

## Next Steps

- Tremarel team sends company presentation and bank reconciliation proposal to Ignacio
- Ignacio validates reconciliation pain points with his accounting team
- Tremarel team researches SAP security/access governance vendor recommendations
- If there is a match, schedule a follow-up call (potentially including accounting team members)
- If proceeding, sign NDA and provide bank statement + ledger data for proof of concept
