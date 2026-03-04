# Meeting Summary: Budget & Product Catalog Codification

**Date:** 2026-03-04
**ADW ID:** 8382bae3

## Summary

Oscar and a product/inventory manager discussed the codification of APUs (Unit Price Analyses) and the challenge of managing approximately 15,000 products in the database. The key insight is that products can be duplicated because quality tiers vary by client, meaning the same product type (e.g., a tube or duct) may exist at different quality and price levels. Products are categorized by product type, category, and quality, all of which directly impact pricing.

## Participants

- Oscar
- Speaker 2 (Product/Inventory Manager)

## Prospect

- **Contact:** Oscar

## Discussion Points

### Product Catalog Size and Complexity
The inventory contains approximately 15,000 products. This large volume includes duplicates arising from different quality tiers offered to different client segments.

### APU Codification
Discussion about coding/cataloging APUs (Unit Price Analyses) to better organize and manage the product database.

### Quality-Based Product Differentiation
The same product type (tubes, unions, ducts) can exist at multiple quality levels. Lower-budget clients receive more economical options sourced from below-market alternatives, while premium clients receive higher-quality products.

### Pricing Structure
Product pricing is directly affected by three attributes: product type, category, and quality tier. This multi-dimensional pricing model needs to be captured in any codification system.

## Action Items

- [ ] Review and process the file that was shared (referenced at the end of the transcript) (Owner: Oscar)
- [ ] Design a codification system for APUs that accounts for product type, category, and quality tiers

## Decisions

- Products will be categorized along three dimensions: product type, category, and quality tier
- Duplicate product entries are acceptable and necessary to accommodate different quality levels for different client segments

## Next Steps

- Process the shared file containing product/inventory data
- Develop a codification scheme for APUs that supports quality-based differentiation and pricing
