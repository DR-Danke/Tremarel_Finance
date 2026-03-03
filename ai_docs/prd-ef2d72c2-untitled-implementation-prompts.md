The implementation prompts document has been generated at `ai_docs/restaurant_os_implementation_prompts.md`.

**Summary:**
- **22 prompts** across **7 waves** for the Restaurant Operating System
- ID prefix: `ROS-001` through `ROS-022`

**Wave breakdown:**

| Wave | Name | Issues | Parallel |
|------|------|--------|----------|
| 1 | Foundation Core Entities | ROS-001 (Restaurant), ROS-002 (Person), ROS-003 (Resource) | 3 in parallel |
| 2 | Foundation Extended Entities | ROS-004 (Document), ROS-005 (Event), ROS-006 (Inventory Movement) | 3 in parallel |
| 3 | Task Engine & Frontend Shell | ROS-007 (Task Assignment), ROS-008 (Restaurant Selector) | 2 in parallel |
| 4 | Daily Tasks & Frontend Pages | ROS-009 (Daily Summary), ROS-010 (Persons Page), ROS-011 (Documents Page), ROS-012 (Events Page), ROS-013 (Resources Page) | 5 in parallel |
| 5 | Notifications & Recipe Model | ROS-014 (WhatsApp), ROS-015 (Email), ROS-016 (Recipe CRUD) | 3 in parallel |
| 6 | Alerts, OCR & Recipe Features | ROS-017 (Expiration Alerts), ROS-018 (Invoice OCR), ROS-019 (Recipe Deduction), ROS-020 (Recipe Frontend) | 4 in parallel |
| 7 | Cost Intelligence & Compliance | ROS-021 (Auto Recalculation), ROS-022 (Permit Presets) | 2 in parallel |

The PRD's original 4 waves were split into 7 to respect the **no intra-wave dependencies** rule. All prompts are self-contained with explicit file paths, code snippets, and Spanish (Colombian) UI language where applicable.