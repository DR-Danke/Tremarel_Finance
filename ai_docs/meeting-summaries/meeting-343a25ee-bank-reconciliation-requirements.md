# Meeting Summary: Bank Reconciliation Requirements

**Date:** 2026-03-06
**ADW ID:** 343a25ee

## Summary

Speaker 1 outlined the requirements for building a bank reconciliation process in Finkargo. The system must import Excel accounting files and bank statements, apply multiple matching rules (exact match, date variance, one-to-many, many-to-one, and fuzzy name matching), and produce matched and unmatched reports to iteratively refine reconciliation rules.

## Participants

- Speaker 1

## Prospect

- **Company:** Finkargo

## Discussion Points

### Multi-Rule Matching Engine
The reconciliation must support multiple matching strategies: exact match, date-shifted matching (same transaction on different dates), one-to-many (one bank line to multiple accounting entries), many-to-one (multiple bank lines to one accounting entry), and fuzzy name matching when no NIT/RFC/ID reference is available.

### File Import Process
The system needs to receive Excel files from accounting and cross-reference them with bank statements. The workflow is: upload bank statement first, then upload the accounting ledger for the corresponding account.

### Reconciliation Reporting
The system must generate two reports after cross-referencing: a matched items report (successful reconciliation) and an unmatched items report. The unmatched report will be used to evaluate whether additional reconciliation rules can be applied.

### Fuzzy Name Matching
Often there is no structured identifier (NIT/RFC/ID) available. Instead, descriptions contain names that may be exact or approximate matches to the accounting counterparty names, requiring fuzzy string matching capabilities.

## Action Items

- [ ] Build bank statement upload and parsing functionality (Excel import)
- [ ] Build accounting ledger upload for the corresponding bank account
- [ ] Implement multi-rule matching engine (exact, date-shifted, one-to-many, many-to-one, fuzzy name)
- [ ] Build matched items report view
- [ ] Build unmatched items report view for rule evaluation

## Decisions

- The reconciliation process will be built within the Finkargo platform
- Bank statement will be uploaded first, followed by the accounting ledger for the corresponding account
- Multiple matching rules will be used rather than relying on a single exact-match approach
- Unmatched report will be used iteratively to discover and apply additional reconciliation rules

## Next Steps

- Implement bank statement Excel upload and parsing
- Implement accounting ledger Excel upload and parsing
- Build the cross-referencing engine with multiple matching rules
- Create matched and unmatched reconciliation reports
- Evaluate unmatched results to refine and add new reconciliation rules
