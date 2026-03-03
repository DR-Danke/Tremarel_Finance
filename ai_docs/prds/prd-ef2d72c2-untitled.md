PRD generated and saved to `ai_docs/prds/prd-ef2d72c2-restaurant-operating-system.md`.

**Summary of what was produced:**

- **22 requirements** across **6 work streams**:
  1. **Core Data Model & Universal Entities** (6 reqs) — Person, Document, Event, Resource, Inventory Movement, Restaurant multi-tenancy
  2. **Task Management & Assignment** (2 reqs) — Recurring task creation and daily employee summaries
  3. **Notification System** (3 reqs) — WhatsApp integration, email, and document expiration automation
  4. **Frontend Core Views** (5 reqs) — Management pages for all entities plus restaurant selector
  5. **Recipe & Cost Intelligence** (5 reqs) — Recipes, OCR invoice scanning, auto cost recalculation, profitability alerts
  6. **Permit & Compliance Tracking** (1 req) — Preset permit types with custom alert schedules

- **4 implementation waves**: Foundation → Task Engine & Notifications → Frontend → Recipe & Cost Intelligence

- **8 open questions** flagged for stakeholder clarification (monorepo integration, WhatsApp provider, entity/restaurant relationship, OCR service, scheduler architecture, payroll scope, REST vs GraphQL, margin threshold)