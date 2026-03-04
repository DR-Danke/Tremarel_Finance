# Meeting Summary: Tendery System - First Delivery Feedback Session

**Date:** 2026-03-03
**ADW ID:** 2aa2b9e2

## Summary

First delivery review of the Tendery quotation system for a logistics/transportation company. The team demoed the full quotation workflow including client selection from Odoo CRM, route configuration, pricing engine (CICETAC + RNDC + historical data), profitability/utility validation, PDF generation, email delivery, QR-based client approval, and quotation cloning. Key feedback centered on changing the pricing UI so users edit the final client price instead of margins, adding default minimum profitability per vehicle type, classifying routes as urban/national/container-return, and implementing an amendment feature for approved quotations. A 2-week user acceptance testing phase was agreed upon with a follow-up meeting in 8 days.

## Participants

- Manuel (Software Developer / Technical Lead)
- Kelly (Commercial Team)
- Daniel (System Presenter / Developer)
- Carlos Cardona (Commercial Manager / Decision Maker)
- Paola (Pau) (Commercial Team)
- Marcela (Marce) (Operations / Commercial)
- Juan David (Operations Manager)
- Speaker 8 (Operations / Stakeholder)

## Prospect

- **Company:** Hay Huevos (temporary name - AI software company)
- **Contact:** Carlos Cardona

## Discussion Points

### Pricing Engine & Margin Validation Logic
Extensive discussion on how profitability (%) and utility (absolute value) interact. Current system takes the nominally higher of the two, but both must be met or the quotation goes to approval. Team agreed to change UX: user should edit the final client price, and the system should auto-calculate and validate both margin checks (utility and profitability). If both pass, proceed; if either fails, require approval.

### Vehicle Type Configuration
Vehicle types need corrections: remove weight labels to avoid confusion between sub-types (Minimula S2/S3, Tractomula variants). Missing vehicle type 'Poderosa' (intermediate between Minimula and Tractomula). Weight capacities need correction (NHR: 2t not 3.5t, Turbo: 4.5t, Sencillo: 5-8.5t). The invalid 'MULA' type in the Excel template needs to be fixed.

### Route Classification (Urban/National/Container Return)
System needs a route type field to distinguish between urban, national, and container return operations. Urban routes don't have CICETAC regulation. This classification affects which cost sources are available and which profitability policies apply per vehicle type.

### Cost Data Sources & Update Frequency
Three cost sources: CICETAC (regulated floor), RNDC (market data via statistical analysis/Gaussian curve), and Historical data. RNDC currently uses month-old data from January Excel. Goal is daily updates. Buenaventura route (80% of quotations) is most volatile and may need manual handling initially. Debate on using first standard deviation above vs. below the mean (85th percentile of dispatch volume recommended).

### Quotation Amendment Functionality
Most structurally significant change requested. Need ability to modify accepted quotations when operational conditions change (e.g., container return location changes from express to consolidated). Amendments should be permission-controlled. Applies especially to spot quotations where client instructions change after approval.

### Client Approval Workflow
Quotations sent via email with PDF attachment and QR code. Client can accept, reject, or request advisor. Discussion on needing WhatsApp delivery and email-based one-click approval buttons since clients often approve informally via WhatsApp. Internal approval queue managed by Carlos and Juan David.

### Multi-Delivery & Container Return Scenarios
Complex scenarios like Buenaventura-Bogota with container return to Tocancipa or port consolidation. Resolved via SAT (additional services) for extra deliveries/returns. Container returns for different shipping lines (Evergreen, CMA) have different costs. ITR operations handled as SATs, not routes.

### Price Rounding to Superior Multiples
Client-facing prices must be rounded up to the next multiple of 10,000 COP. Currently not implemented - system shows exact calculated values instead of commercially rounded figures.

### Integration with Postar (TMS) - Phase 2
Future phase: approved quotations and tariffs should sync to Postar TMS so operations can create service orders and manifests directly. Currently, the quotation module operates independently. Service order creation from approved quotations is the next development phase.

### Quotation Cloning Feature
Demonstrated ability to clone existing quotations for new clients. Clone brings routes but missing some configuration details. Need to fix clone button to carry full configuration. Useful for repeat quotations (e.g., same routes for different clients).

### Quotation Vigency/Validity Period
Current default is 15 days. Discussion on appropriate validity periods - weekly for volatile routes (Buenaventura) vs. annual for established tariff clients (like Textiles). Vigency periods should be configurable per quotation.

### Email Domain & Branding
Current emails sent from 'huevos' domain which is unprofessional for client-facing communications. Need to configure proper company domain. Also need letterhead/branding on PDF quotations and user-specific email signatures.

## Action Items

- [ ] Change pricing UI: user edits final client price, system auto-calculates and validates both profitability (%) and utility (absolute value) with visual check indicators (Owner: Manuel / Daniel (Development team)) [Due: Before next meeting (within 8 days)]
- [ ] Add default minimum profitability and utility values per vehicle type that auto-populate but remain editable (Owner: Manuel / Daniel (Development team)) [Due: Before next meeting (within 8 days)]
- [ ] Remove weight labels from vehicle type selector to avoid confusion between sub-types (Owner: Manuel / Daniel (Development team)) [Due: Before next meeting (within 8 days)]
- [ ] Add route classification field: urban, national, container return (Owner: Manuel / Daniel (Development team)) [Due: Before next meeting (within 8 days)]
- [ ] Implement price rounding to next superior multiple of 10,000 COP (Owner: Manuel / Daniel (Development team)) [Due: Before next meeting (within 8 days)]
- [ ] Re-enable profitability policy alerts per vehicle type (temporarily disabled) (Owner: Manuel / Daniel (Development team)) [Due: Before next meeting (within 8 days)]
- [ ] Send SAT (additional services) list with costs to development team (Owner: Carlos Cardona)
- [ ] Implement quotation amendment/modification functionality for approved quotations with permission control (Owner: Manuel / Daniel (Development team))
- [ ] Change email sending domain from temporary 'huevos' domain to proper company domain (Owner: Manuel / Daniel (Development team))
- [ ] Add mobile-friendly approval via email link (one-click approve button in email) (Owner: Manuel / Daniel (Development team))
- [ ] Fix quotation cloning to carry full route configuration (Owner: Manuel / Daniel (Development team))
- [ ] Configure approval users: Carlos Cardona and Juan David as quotation approvers (Owner: Manuel / Daniel (Development team)) [Due: Before testing phase begins]
- [ ] Enable Excel upload for historical cost data until automated integration is available (Owner: Manuel / Daniel (Development team))
- [ ] Contact Ministry for updated RNDC data feed (Owner: Carlos Cardona)
- [ ] Commercial team to test the Tendery system during 2-week UAT phase and document observations (Owner: Kelly / Paola / Marcela (Commercial team)) [Due: 2 weeks from meeting date]
- [ ] Add letterhead/branding to PDF quotation documents (Owner: Manuel / Daniel (Development team))
- [ ] Add user-specific email signature to outgoing quotation emails (Owner: Manuel / Daniel (Development team))

## Decisions

- Follow-up meeting scheduled in 8 days (March 11, 2026) at the same time
- 2-week User Acceptance Testing (UAT) phase starts immediately - all commercial team members will test the system
- Carlos Cardona and Juan David will be configured as quotation approvers
- Pricing UI will be redesigned: user edits final client price, system validates both profitability and utility checks
- Multi-delivery and container return scenarios will be handled via SAT (additional services), not as separate routes
- Buenaventura route pricing will be managed manually initially until automated data feed is established
- RNDC historical data will be updated monthly via Excel upload as baseline, with daily updates as the goal
- Route classification (urban/national/container return) will be added as a field in route configuration
- Default minimum margins should auto-populate per vehicle type but remain editable by commercial users
- Quotation validity periods should be configurable (not fixed at 15 days) to support both spot and annual tariff clients
- Amendment functionality for approved quotations is approved as a feature requirement (most structural change)
- Phase 1 focuses on quotation module only; Phase 2 will integrate with Postar TMS for service orders

## Next Steps

- Development team applies immediate UI adjustments (pricing input change, vehicle weights, route classification, rounding) before next meeting
- Carlos sends SAT list with costs and contacts Ministry for RNDC data
- Commercial team (Kelly, Paola, Marcela) begins testing the Tendery system this week
- All approvals routed to Carlos Cardona during testing phase
- Team reconvenes in 8 days with compiled observations and change requests
- After quotation module is validated, begin Phase 2 planning: Postar TMS integration and service order creation
