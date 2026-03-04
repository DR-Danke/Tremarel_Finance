# Meeting Summary: Lutec - Bank Reconciliation & Financial Operations Discovery

**Date:** 2026-03-04
**ADW ID:** 869ef307

## Summary

Discovery meeting at Lutec to map financial operations and identify automation opportunities. The financial team manages 5 bank accounts (2 savings, 1 checking, 2 trust/fiduciary) with entirely manual daily and monthly reconciliation using Excel VLOOKUP/CONCATENATE formulas. Key pain points include: complex fiduciary payment matching (single trust sends payments from multiple unnamed clients), manual DIAN/Radian invoice acceptance for 500+ monthly invoices via one-by-one XML upload, and a fragmented procure-to-pay chain spanning three departments (Logistics, Inventory, Accounting) across World Office ERP and Monday.com. Lutec is migrating to Uranit ERP for better budget control. The consultant will start by automating bank reconciliation using ~30 accounting rules, with February data from Davivienda and Bogota banks as proof of concept.

## Participants

- Daniel Cardona (Technology & Process Automation Consultant)
- Catalina Carranza (Financial Manager (Gerente Financiera) - Lutec)
- Jose (Inventory Manager - Lutec)
- Daniel Giraldo (Business Development / Facilitator)

## Prospect

- **Company:** Lutec
- **Contact:** Catalina Carranza

## Discussion Points

### Bank Reconciliation Process
Treasury downloads daily bank movements (Excel for working, PDF for official records) from 5 accounts and cross-references with World Office accounting auxiliaries. Daily reconciliation tracks entries/exits for cash receipts and disbursements. Monthly full reconciliation uses CONCATENATE and VLOOKUP formulas in Excel. Payroll flat files add complexity as they show lump sums that must be broken down by employee. Monthly close takes ~1 week with reports delivered to management with a one-week delay.

### Procure-to-Pay Workflow
Three departments handle each purchase: Logistics creates Purchase Orders (OC) in World Office and tracks in Monday.com; Inventory receives goods at 47 warehouses, validates against OC, and creates Supplier Receipt (RP) in World Office; Accounting validates the full chain (OC + RP + Invoice) before authorizing Treasury to pay. Missing OCs or RPs cause significant delays. The process also handles advances/prepayments which complicate tracking.

### DIAN/Radian Invoice Acceptance
Over 500 monthly purchase invoices (95%+ domestic) require acceptance or rejection events filed with Colombia's DIAN tax authority through the Radian system. Currently done one-by-one via XML upload. The team recently tested a third-party service for bulk XML download and mass upload, which proved significantly faster. DIAN is the source of truth for received invoices, not email or the ERP.

### Fiduciary Payment Matching (Accounts Receivable)
Many clients pay through trust/fiduciary entities, which send payments aggregating multiple clients without identifying which client paid what amount. The collections coordinator maintains a manual mapping of which trusts typically pay for which clients, but this only resolves ~80% of cases. Clients also apply variable withholding tax percentages inconsistently, adding further reconciliation complexity.

### Inventory Management
47 warehouses across project sites. Inventory receives ~50 purchase orders daily during peak periods (first 1.5 weeks of month). Physical inventory managed by administrative staff with Excel Kardex as backup. Daily reports sent to coordination for World Office data entry. Warehouse staff send receipt documents via email for manual processing.

### ERP Migration: World Office to Uranit
Lutec is migrating from World Office (current ERP) to Uranit (Chilean ERP). Key drivers: World Office cannot link purchase orders to receipts to invoices automatically, and Engineering department cannot control project budgets at APU (Analysis per Unit) detail level. Uranit promises automated document linking and budget alerts. Currently in training phase; full migration not yet started.

### Two Sales Models: Engineering vs Illumination
Engineering sells projects as functional units (bundling labor, supplies, provisioning) and invoices the whole project without requiring inventory detail. Illumination sells products directly, requiring inventory tracking, purchase orders tied to quotes, and item-level invoicing. Both models share the same procurement chain but diverge at the sales/invoicing stage.

### Budget Control Gap
Engineering uses APU (Average Per Unit) budgets for client proposals but World Office cannot track actual costs against these budgets at the required detail level. No alerts exist for over-purchasing or unauthorized cost overruns. Yearly purchase projections were introduced in 2025 and have been helpful but are still manual. Variable project scope and new construction projects make forecasting inherently difficult.

### Monthly Close Delays
Monthly financial close takes approximately one week after month-end. Delays caused by: uncontabilized invoices, pending bank final statements (available after the 5th), and incomplete reconciliations. Weekly reports to management are delivered with a one-week lag and may still contain unreconciled items.

## Action Items

- [ ] Send 6 documents for February: Davivienda (bank statement PDF, bank movements Excel, World Office auxiliary) and Bogota (bank statement PDF, bank movements Excel, World Office auxiliary) (Owner: Catalina Carranza)
- [ ] Analyze February bank reconciliation data from Davivienda and Bogota to prototype automated matching using ~30 accounting rules (Owner: Daniel Cardona)
- [ ] Schedule discovery meeting with Oscar (budget department) to understand budget control processes (Owner: Daniel Giraldo)
- [ ] Sit with Catalina's team to map all reconciliation rules, cross-reference logic, and exception patterns (Owner: Daniel Cardona)

## Decisions

- Bank reconciliation will be the first automation focus area
- Davivienda and Bogota bank accounts will be used as initial proof-of-concept scope
- February 2026 data will be used for the pilot analysis
- ERP migration to Uranit is a confirmed strategic decision (already in training phase)
- Budget process (Oscar's area) identified as second priority automation opportunity

## Next Steps

- Catalina sends 6 February bank documents to Daniel Cardona's email
- Daniel Cardona analyzes reconciliation data and prototypes automated matching
- Follow-up meeting with Oscar to discover budget control processes and pain points
- Working session with Catalina's team to document all ~30 accounting reconciliation rules
- Daniel Giraldo to identify other departments at Lutec that could benefit from process automation
