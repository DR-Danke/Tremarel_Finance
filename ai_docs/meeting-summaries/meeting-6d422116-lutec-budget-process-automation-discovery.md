# Meeting Summary: Lutec - Budget Process Automation Discovery

**Date:** 2026-03-04
**ADW ID:** 6d422116

## Summary

Discovery meeting between Daniel Cardona and Oscar Pinzón (Budget Director at Lutec) to explore automation opportunities in Lutec's construction budgeting process. Lutec is an electrical construction subcontractor with a 6-person team producing 10-12 budgets per week, where the main bottleneck is manually matching client-provided Excel activity lists against their internal APU (Unit Price Analysis) database of materials, labor, and suppliers. The proposed automation would use similarity matching to automatically suggest the closest APU codes for each client activity, allowing the team to focus on higher-value work like BIM analysis, anomaly detection, and cost projection rather than repetitive Excel lookups.

## Participants

- Daniel Cardona (Automation Consultant)
- Oscar Pinzón (Budget Director at Lutec)

## Prospect

- **Company:** Lutec
- **Contact:** Oscar Pinzón

## Discussion Points

### Core Pain Point: Manual APU Matching Process
The budgeting team spends excessive time manually searching their internal APU (Unit Price Analysis) database to match client-requested construction activities. Each activity must be coded with the correct APU that contains the associated materials, labor, and supplier information. This manual matching process can take up to 3 days per budget and is highly repetitive.

### Client Excel Format Constraints
Each construction client sends their own custom Excel spreadsheet with a quantity sheet ('sábana de cantidades'). Lutec cannot modify the client's file format. Different clients have different Excel structures and levels of specification detail, adding complexity to the matching process.

### APU Database Structure and Categorization
Lutec maintains an internal database of APUs organized by product families (tubing, cables, boxes, plates, etc.) with sub-categories for type, installation method (e.g., suspended), diameter, number of ducts, etc. Each APU contains the required materials/supplies, quantities per unit, labor costs, waste percentages, and supplier mappings.

### Proposed Automation: Similarity-Based Code Matching
The proposed solution would automatically analyze client Excel items and match them against Lutec's APU database using similarity analysis. The system would suggest the closest matching APU for each activity, and Oscar's team would only need to review, validate, and handle exceptions for unmatched items — drastically reducing manual lookup time.

### BIM Integration for Specification Verification
Lutec has a dedicated BIM specialist who reviews 3D construction models to verify specifications, quantities, and identify anomalies (e.g., unknown installation heights for luminaires). BIM analysis is critical for accurate costing but is currently deprioritized because the team spends too much time on manual Excel work.

### End-to-End Budget Workflow
The full workflow includes: (1) receiving client Excel, (2) matching activities to APU codes, (3) associating materials/supplies/labor, (4) identifying missing products, (5) sourcing suppliers and base pricing, (6) passing supplier info to Purchasing for negotiation, (7) applying margin/profitability calculations, (8) returning the completed quotation in the client's original Excel format.

### Post-Quotation Cost Control
After quotation approval, Lutec generates a supply 'bag' (bolsa de insumos) for the project — a consolidated list of everything needed for the construction work. This becomes the cost control baseline, where deviations and incidents impact margin and profitability.

### Team Size and Volume
The budgeting department has 6 people working full-time, producing 10-12 budgets per week. One team member is dedicated exclusively to BIM analysis.

## Action Items

- [ ] Send sample client Excel files (quantity sheets from different clients) to Daniel for analysis (Owner: Oscar Pinzón)
- [ ] Send the internal APU database with codes, materials, and supplier mappings (Owner: Oscar Pinzón)
- [ ] Send the APU template with formulas (material/labor separation, waste percentage calculations) (Owner: Oscar Pinzón)
- [ ] Analyze received files and propose an automation solution for APU matching (Owner: Daniel Cardona)

## Decisions

- The primary automation target is the APU code matching process — automatically suggesting the closest matching APU for client-requested activities using similarity analysis
- Oscar will send sample client Excel files and the internal APU database to Daniel for analysis
- The quotation must always be returned in the client's original Excel format — no format modifications allowed
- The automation should handle the lookup/matching while humans focus on review, BIM analysis, and exception handling

## Next Steps

- Oscar sends sample client Excel files (from multiple clients) to Daniel
- Oscar sends the internal APU database/codes with associated materials and supplier data
- Oscar sends the APU template with formulas for material/labor separation and calculations
- Daniel analyzes the data to design the automated matching solution
- Follow-up meeting once Daniel has reviewed the files and has a proposed approach
