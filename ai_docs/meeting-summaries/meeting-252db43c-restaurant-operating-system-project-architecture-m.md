# Meeting Summary: Restaurant Operating System - Project Architecture & MVP Planning

**Date:** Not specified
**ADW ID:** 252db43c

## Summary

The meeting presented the complete architecture and phased roadmap for a centralized operational management platform targeting small restaurants. The system is built on four universal entities (Person, Document, Event, Resource) that compose all business functions without rigid modules. MVP Phase 1 covers employee management, task assignment with WhatsApp notifications, document tracking with expiry alerts, and basic inventory. A Phase 2 extension was detailed for recipe standardization, automatic cost calculation via invoice OCR scanning, and profitability alerts.

## Participants

- Speaker 1 (Project Lead / Product Architect)

## Discussion Points

### Core Entity Architecture
The entire system is built on 4 universal entities: Person (employees, suppliers, owners), Document (contracts, permits, invoices), Event (tasks, reminders, payments, shifts, checklists), and Resource (products, assets, services). All business functions are composed from combinations of these entities rather than rigid modules.

### Problem Statement
Small restaurants suffer from operational disorder: unclear task ownership, expired permits and documents, inventory discrepancies, uncontrolled waste, and forgotten payments/taxes. Current tools (WhatsApp, notebooks, memory, disconnected apps) are insufficient. POS systems only handle sales; ERPs are expensive and rigid.

### MVP Phase 1 Scope
Phase 1 delivers: employee directory, task lists with date/frequency assignment, daily WhatsApp task notifications per employee, document upload with expiration dates, automatic pre-expiry alerts, and basic inventory with entry/exit movements (purchase, usage, production, waste).

### Event-Driven System Design
The Event entity serves as the system's nervous system. All key flows pass through Events: documents with expiry dates create Events, Events trigger notifications on their dates, recurring tasks generate daily Events, and inventory changes register movements. Notification channels include email, push, and WhatsApp.

### Recipe & Cost Management Extension
A Phase 2 extension adds Recipe and Recipe_Item entities on top of existing Resource/Document/Event/Inventory_Movement. Recipes define theoretical dish costs by linking resources with quantities. When ingredient costs change (via invoice scanning), all affected recipe costs are automatically recalculated.

### Invoice Scanning & OCR Pipeline
Supplier invoices are photographed and uploaded as Documents. AI/OCR extracts supplier, products, quantities, and unit prices. Each detected item updates the corresponding Resource's latest unit cost and registers an inventory entry movement. Cost changes trigger automatic recipe recalculation.

### Profitability Alerts
Each Recipe tracks current cost, margin percentage, and a profitability flag. When margin drops below a defined minimum (e.g., 60%), the system creates an Event of type 'profitability_alert' notifying the owner via push/WhatsApp with the dish name, cost, sale price, and margin.

### Permit & Compliance Management
Document + Event combinations handle regulatory compliance: food handling permits (30-day advance alert), fire department permits (expiry alert), commerce chamber registration (annual alert), fire extinguisher recharges (recharge alert), and health inspections (inspection alert).

### Module Composition Pattern
Business functions are not rigid modules but entity combinations: Contracts = Person + Document + Event, Permits = Document + Event, Checklists = Event + Person, Inventory = Resource + Event, Payments = Event + Document, Payroll = Person + Event, Purchasing = Resource + Event, Marketing = Event + AI, Production = Resource + Event, Franchises = same model per restaurant.

### Technology Stack
Proposed stack: PostgreSQL via Supabase for database, REST or GraphQL API, React or FlutterFlow for frontend, Email + WhatsApp API for notifications, and DocuSign API for digital signatures in Phase 2.

### Phased Roadmap
Phase 1: CRUD for all 4 entities, notifications, basic inventory. Phase 2: Digital contracts, basic payroll, production/cost centers. Phase 3: AI for prediction, analysis, and autonomous agents.

## Action Items

- [ ] Build CRUD operations for the 4 core entities: Person, Document, Event, Resource [Due: Phase 1]
- [ ] Implement notification system supporting email, push, and WhatsApp channels [Due: Phase 1]
- [ ] Build Inventory_Movement tracking (entries/exits with motives: purchase, usage, production, waste) [Due: Phase 1]
- [ ] Implement event-driven automation: document expiry creates Events, recurring tasks generate daily Events [Due: Phase 1]
- [ ] Design and implement Recipe and Recipe_Item data models for cost management [Due: Phase 2]
- [ ] Build invoice scanning pipeline with OCR for automatic cost extraction and Resource updates [Due: Phase 2]
- [ ] Implement automatic recipe cost recalculation when ingredient prices change [Due: Phase 2]
- [ ] Build profitability alert system with configurable margin thresholds [Due: Phase 2]
- [ ] Optionally convert project overview into architecture diagram and technical backlog

## Decisions

- The system will be built on 4 universal entities (Person, Document, Event, Resource) rather than rigid modules
- Event entity serves as the central nervous system — all workflows pass through Events
- MVP Phase 1 scope: employee management, task assignment with WhatsApp notifications, document tracking with expiry alerts, and basic inventory
- Recipe and cost management is explicitly deferred to Phase 2 as it depends on established inventory, defined recipes, digitized invoices, and minimum operational discipline
- No sub-inventories or complex cost centers in Phase 1 — kept deliberately simple
- Technology stack: PostgreSQL (Supabase), REST/GraphQL API, React/FlutterFlow frontend, WhatsApp + Email notifications
- The platform is positioned as a 'daily operating system for small restaurants' — not a POS or ERP
- Design principle: 'We don't design functions. We design a system that enables functions.'

## Next Steps

- Set up PostgreSQL database on Supabase with the 4 core entity schemas plus Inventory_Movement
- Build Phase 1 MVP with CRUD, notifications, and basic inventory
- Convert project overview into a formal architecture diagram
- Create a technical development backlog from the phased roadmap
- Validate Phase 1 with real small restaurant operations before proceeding to Phase 2
