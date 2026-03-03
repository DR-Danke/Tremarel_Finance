# Tendery v2 - ADW Implementation Prompts

## Overview

This plan contains GitHub issue prompts for implementing Tendery v2 improvements using `adw_sdlc_iso.py`. Each prompt will trigger the `/feature` command which handles technical planning.

**Source:** Business process meeting 2026-01-22 with Finkargo/Confie team.
**Requirements Doc:** `ai_docs/tendery-meeting-requirements-20260122.md` (Sections 3-10)

**Project Goal:** Evolve Tendery from quotation-only to full dispatch lifecycle. Key additions: Service Requests (SS), cargo type classification, visibility controls, enhanced driver scoring, dual-mode dispatch, real pricing data sources, and compliance automation.

**Key New Concepts:**
1. **Solicitud de Servicio (SS)** - Bridge between approved quote and dispatch (1 quote → N SS)
2. **Flete vs Tarifa** - Cost to driver vs Price to client (dispatcher NEVER sees tarifa)
3. **Turno** - Driver availability declaration (priority in scoring)
4. **Dual-Mode Dispatch** - Tender (automated) vs Direct (manual by dispatcher)
5. **Re-Offer** - Escalate freight price if no driver accepts

**Execution**: `uv run adw_sdlc_iso.py <issue-number>`

**Parallelization**: Issues within the same wave can run simultaneously in separate worktrees (up to 15 concurrent).

**Naming Conventions:**
- Component prefix: `TY` (TYQuotationForm, TYServiceRequestList)
- Database table prefix: `ty_` (ty_service_requests, ty_driver_turnos)
- Route prefix: `/tendery/*` (frontend), `/api/tendery/*` (backend)

**Terminology:**
- **Flete** = Cost paid to vehicle owner/driver
- **Tarifa** = Price charged to client (Flete + Margin + Services)
- **SS** = Solicitud de Servicio (Service Request)
- **Turno** = Driver availability declaration in a city
- **Rentabilidad** = Profit margin % (e.g., min 12% for mulas)
- **Utilidad** = Absolute profit $ (e.g., min $500K COP per tractomula)

---

## Wave 9: Quick Wins (Run in Parallel)

These four issues enhance existing functionality and can run simultaneously since they touch different areas.

### TD-022: Cargo Type & Description on Quote

**Title:** `[Tendery] Wave 9: Cargo Type Classification on Quote`

**Body:**
```markdown
## Context
**Project:** Tendery v2 - Transport Quotation System improvements based on business process meeting
**Overview:** Add cargo type classification to quotation form. Different cargo types trigger different vehicle requirements, surcharges, and mandatory additional services. Types: General, Refrigerada, Peligrosa (MATPEL), Alimentos, Liquidos, Electronica/Alta Valor, Maquinaria/Sobredimensionada.

**Current Wave:** Wave 9 of 13 - Quick Wins
**Current Issue:** TD-022 (Issue 22 of 39)
**Parallel Execution:** YES - This issue runs in parallel with TD-023, TD-024, TD-025.

**Dependencies:** None (extends existing quote form and DTOs).
**What comes next:** Wave 10 uses cargo_type in Service Request creation.

## Request
Add cargo type classification and description fields to the quotation form and backend.

### 1. Backend DTO Updates
Update `apps/Server/app/models/tendery/quote_dto.py`:
```python
from enum import Enum

class CargoType(str, Enum):
    GENERAL = "general"
    REFRIGERADA = "refrigerada"
    PELIGROSA = "peligrosa"  # MATPEL
    ALIMENTOS = "alimentos"
    LIQUIDOS = "liquidos"
    ELECTRONICA = "electronica"  # Alta valor
    MAQUINARIA = "maquinaria"  # Sobredimensionada

class QuoteCreateDTO(BaseModel):
    # ... existing fields ...
    cargo_type: CargoType = CargoType.GENERAL
    cargo_description: Optional[str] = Field(None, max_length=500)
```

### 2. Quote Service Update
In `apps/Server/app/services/tendery/quote_service.py`, pass `cargo_type` and `cargo_description` through to the repository layer. Include in the quote_data dict that gets persisted.

### 3. Frontend Types
Update `apps/Client/src/types/tendery/quote.ts`:
```typescript
export type CargoType = 'general' | 'refrigerada' | 'peligrosa' | 'alimentos' | 'liquidos' | 'electronica' | 'maquinaria';

export interface QuotationFormData {
  // ... existing fields ...
  cargo_type: CargoType;
  cargo_description?: string;
}
```

### 4. Transport Section UI
Update `apps/Client/src/components/tendery/TYTransportSection.tsx`:
- Add a `Select` dropdown for cargo_type after vehicle type selector
- Add a `TextField` multiline for cargo_description (optional)
- Labels in Spanish:
  - "Tipo de Carga" for the dropdown
  - Options: "General", "Refrigerada", "Peligrosa (MATPEL)", "Alimentos", "Líquidos", "Electrónica/Alto Valor", "Maquinaria/Sobredimensionada"
  - "Descripción de Mercancía" for the textarea

### 5. Form Data Transform
Update `transformFormData()` in `apps/Client/src/components/tendery/TYQuotationForm.tsx` to include `cargo_type` and `cargo_description` in the API payload.

### 6. Auto-Suggest Services (Future Hook)
Add a comment/TODO in TYTransportSection for future implementation:
```typescript
// TODO TD-036: When cargo_type changes, call security rules engine
// to auto-suggest mandatory additional services for this cargo+route combination
```

**UI Language:** Spanish (Colombian)
**Validation:** cargo_type is required (default: "general"), cargo_description is optional.
```

---

### TD-023: Tariff Visibility Controls

**Title:** `[Tendery] Wave 9: Tariff Visibility Controls for Dispatcher`

**Body:**
```markdown
## Context
**Project:** Tendery v2 - Transport Quotation System improvements
**Overview:** Dispatchers should NEVER see the tariff (client price) or margin breakdown. They only need to see the flete (cost to pay driver), route, vehicle type, and cargo details. This prevents freight inflation when dispatchers see wide margins. The system separates "what to pay" from "what to charge."

**Business Rule:**
- Commercial role sees: Tarifa + Flete + Margen (full pricing breakdown)
- Despachador/Operations role sees: ONLY Flete + route + vehicle + cargo (no tariff, no margins)

**Current Wave:** Wave 9 of 13 - Quick Wins
**Current Issue:** TD-023 (Issue 23 of 39)
**Parallel Execution:** YES - This issue runs in parallel with TD-022, TD-024, TD-025.

**Dependencies:** None.
**What comes next:** Wave 10 SS module uses these visibility controls.

## Request
Implement role-based field visibility on quote/SS API responses.

### 1. Operational Response DTO
Create a restricted DTO in `apps/Server/app/models/tendery/quote_dto.py`:
```python
class QuoteOperationalDTO(BaseModel):
    """Response DTO for operations/dispatcher - hides tariff and margins"""
    id: int
    reference_number: str
    client_name: str
    origin_city: str
    destination_city: str
    vehicle_type: str
    cargo_type: Optional[str] = None
    cargo_description: Optional[str] = None
    weight_tons: Optional[Decimal] = None
    # ONLY the flete (what to pay driver)
    flete_cop: Decimal  # This is base_cost_cop (driver payment)
    additional_services_cop: Decimal
    # NO tarifa, NO margin_cop, NO total_price_cop, NO margin_type
    status: str
    created_at: datetime
```

### 2. Route Handler Update
In `apps/Server/app/api/tendery/quote_routes.py`:
```python
from app.api.dependencies import get_current_user

@router.get("/quotes/{quote_id}")
async def get_quote(quote_id: int, current_user: dict = Depends(get_current_user)):
    quote = await quote_service.get_quote(quote_id)
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")

    user_role = current_user.get("role", "user")

    # Operations/dispatcher only sees flete, not tariff
    if user_role in ["dispatcher", "operations", "tower"]:
        print(f"INFO [QuoteRoutes]: Returning operational view for role={user_role}")
        return QuoteOperationalDTO(
            flete_cop=quote["base_cost_cop"],
            # ... map other allowed fields
        )

    # Commercial/admin sees everything
    return QuoteResponseDTO(**quote)
```

### 3. List Endpoint
Apply same logic to `GET /api/tendery/quotes` list endpoint - filter response fields based on role.

### 4. Frontend Conditional Rendering
In quote detail components, check user role before showing pricing breakdown:
```typescript
const { user } = useAuth();
const isCommercial = ['admin', 'manager', 'commercial'].includes(user?.role || '');

// Only show margin breakdown for commercial users
{isCommercial && (
  <TYPricingBreakdown pricing={quote.pricing} />
)}

// Operations always sees flete
<Typography>Flete: ${formatCurrency(quote.flete_cop)}</Typography>
```

### 5. Logging
```python
print(f"INFO [QuoteRoutes]: Role-based visibility applied: role={user_role}, showing={'full' if is_commercial else 'operational'}")
```

**Critical Rule:** This is a SECURITY control. The tariff (client price) and margin breakdown MUST NOT leak to operations roles under any circumstance.
```

---

### TD-024: Seller Quote Acceptance

**Title:** `[Tendery] Wave 9: Seller Marks Quote as Accepted`

**Body:**
```markdown
## Context
**Project:** Tendery v2 - Transport Quotation System improvements
**Overview:** Clients will NOT approve quotes via email or web links (attempted 30,000+ times, never works in Colombian transport industry). Clients approve via WhatsApp or phone call. The SELLER (commercial) is responsible for marking the quote as accepted in the system after receiving verbal/WA confirmation.

**Business Rule:** Only the seller who created the quote OR an admin can mark it as accepted. This triggers the quote into "active" state where Service Requests can be generated from it.

**Current Wave:** Wave 9 of 13 - Quick Wins
**Current Issue:** TD-024 (Issue 24 of 39)
**Parallel Execution:** YES - This issue runs in parallel with TD-022, TD-023, TD-025.

**Dependencies:** None.
**What comes next:** Wave 10 SS creation requires quotes to be in "accepted" status.

## Request
Add seller acceptance endpoint and UI action.

### 1. New Endpoint
Add to `apps/Server/app/api/tendery/quote_routes.py`:
```python
@router.put("/quotes/{quote_id}/accept")
async def accept_quote(quote_id: int, current_user: dict = Depends(get_current_user)):
    """Seller marks quote as accepted after client confirms via phone/WhatsApp"""
    print(f"INFO [QuoteRoutes]: Seller {current_user['id']} accepting quote {quote_id}")

    quote = await quote_service.get_quote(quote_id)
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")

    # Only seller who created it or admin can accept
    user_role = current_user.get("role", "user")
    if user_role not in ["admin", "manager"] and quote.get("seller_id") != current_user["id"]:
        raise HTTPException(status_code=403, detail="Only the quote creator or admin can accept")

    # Status validation
    if quote["status"] not in ["draft", "sent", "negotiating"]:
        raise HTTPException(status_code=400, detail=f"Cannot accept quote in status: {quote['status']}")

    result = await quote_service.accept_quote(quote_id, current_user["id"])
    return result
```

### 2. Service Method
Add to `apps/Server/app/services/tendery/quote_service.py`:
```python
async def accept_quote(self, quote_id: int, accepted_by_id: str) -> dict:
    """Mark quote as accepted by seller"""
    print(f"INFO [QuoteService]: Accepting quote {quote_id} by user {accepted_by_id}")

    updated = await self.quote_repository.update_status(
        quote_id,
        status="accepted",
        accepted_at=datetime.utcnow(),
        accepted_by_id=accepted_by_id
    )

    print(f"INFO [QuoteService]: Quote {quote_id} accepted successfully")
    return updated
```

### 3. Repository Update
Add to `apps/Server/app/repository/tendery/quote_repository.py`:
- `update_status(quote_id, status, accepted_at, accepted_by_id)` method
- Updates `status`, `accepted_at`, `accepted_by_id` fields

### 4. Database Column
Add `accepted_by_id VARCHAR(100)` column to `ty_quotes` table (accepted_at already exists).

### 5. Frontend Action Button
Add acceptance button to quote detail/list views for commercial users:
```typescript
// In quote detail component
const handleAcceptQuote = async () => {
  if (window.confirm('¿Confirmar que el cliente aceptó esta cotización?')) {
    await quoteService.acceptQuote(quote.id);
    // Refresh quote data
  }
};

// Only show for commercial users on quotes in valid states
{isCommercial && ['draft', 'sent', 'negotiating'].includes(quote.status) && (
  <Button
    variant="contained"
    color="success"
    onClick={handleAcceptQuote}
  >
    Marcar como Aceptada
  </Button>
)}
```

### 6. Quote Status Type Update
Update `apps/Client/src/types/tendery/quote.ts`:
```typescript
export type QuoteStatus = 'draft' | 'sent' | 'negotiating' | 'accepted' | 'active' | 'rejected' | 'expired';
```

**UI Language:** Spanish (Colombian). Button text: "Marcar como Aceptada". Confirmation: "¿Confirmar que el cliente aceptó esta cotización?"
```

---

### TD-025: Enhanced Kiosco Scoring

**Title:** `[Tendery] Wave 9: Enhanced Kiosco Scoring with Fidelization`

**Body:**
```markdown
## Context
**Project:** Tendery v2 - Transport Quotation System improvements
**Overview:** The Kiosco scoring algorithm needs two new factors from the business meeting:
1. **Fidelization**: Drivers with more trips completed for the company should score higher
2. **Client Familiarity**: Drivers who have previously delivered to the same client should score higher (client satisfaction increases when they see familiar drivers)

**Scoring Priority (from meeting):** Turno > Fidelization > Client Familiarity > Proximity > Rating > Route Experience

**Current Wave:** Wave 9 of 13 - Quick Wins
**Current Issue:** TD-025 (Issue 25 of 39)
**Parallel Execution:** YES - This issue runs in parallel with TD-022, TD-023, TD-024.

**Dependencies:** None (modifies existing kiosco_service.py).
**What comes next:** Wave 11 adds turno system which becomes highest-priority factor.

## Request
Enhance the Kiosco scoring algorithm with fidelization and client familiarity factors.

### 1. Updated Score Calculation
Update `_calculate_score()` in `apps/Server/app/services/tendery/kiosco_service.py`:
```python
def _calculate_score(self, driver: dict, quote_data: dict, fidelization_count: int, client_familiarity_count: int) -> float:
    """Calculate composite driver score for assignment ranking"""
    score = 0.0

    # Rating (0-50 pts) - existing
    rating = driver.get("rating", 3.0)
    score += rating * 10

    # Distance penalty (0 to -25 pts) - existing
    distance_km = driver.get("distance_km", 0)
    score -= min(distance_km / 4, 25)

    # Experience bonus - existing
    total_trips = driver.get("total_trips", 0)
    if total_trips > 100:
        score += 10
    elif total_trips > 50:
        score += 5

    # NEW: Fidelization bonus (0-20 pts)
    # Drivers who have completed more trips with the company
    if fidelization_count > 50:
        score += 20
    elif fidelization_count > 20:
        score += 15
    elif fidelization_count > 10:
        score += 10
    elif fidelization_count > 5:
        score += 5

    # NEW: Client familiarity bonus (0-15 pts)
    # Drivers who have previously served THIS specific client
    if client_familiarity_count > 10:
        score += 15
    elif client_familiarity_count > 5:
        score += 10
    elif client_familiarity_count > 0:
        score += 5

    print(f"INFO [KioscoService]: Driver {driver['id']} score={score:.1f} "
          f"(rating={rating}, dist={distance_km}km, trips={total_trips}, "
          f"fidelization={fidelization_count}, client_familiarity={client_familiarity_count})")

    return score
```

### 2. Repository Queries
Add to `apps/Server/app/repository/tendery/kiosco_repository.py`:
```python
async def get_driver_fidelization_count(self, driver_id: int) -> int:
    """Count total completed trips for this driver with our company"""
    # Query ty_cost_orders WHERE driver_id = X AND status = 'completed'
    query = """
        SELECT COUNT(*) as count FROM ty_cost_orders
        WHERE driver_id = %s AND status = 'delivered'
    """
    # Return count

async def get_driver_client_trips(self, driver_id: int, client_nit: str) -> int:
    """Count trips this driver has done for this specific client"""
    query = """
        SELECT COUNT(*) as count FROM ty_cost_orders co
        JOIN ty_quotes q ON co.quote_id = q.id
        WHERE co.driver_id = %s AND q.client_nit = %s AND co.status = 'delivered'
    """
    # Return count
```

### 3. Service Integration
Update `_find_candidates()` in kiosco_service.py to:
1. Extract `client_nit` from the quote data
2. For each candidate driver, fetch fidelization_count and client_familiarity_count
3. Pass these into `_calculate_score()`

### 4. Logging
```python
print(f"INFO [KioscoService]: Enhanced scoring - driver {driver_id}: "
      f"fidelization={fidelization_count} trips, client_familiarity={client_trips} trips")
```

**Note:** The turno system (highest priority factor) will be added in TD-031. For now, fidelization and client familiarity are the new additions.
```

---

## Wave 10: Service Request (SS) Module (Run Sequentially)

These four issues build the SS module incrementally. Each depends on the previous.

### TD-026: Service Request Data Model

**Title:** `[Tendery] Wave 10: Service Request Data Model & Repository`

**Body:**
```markdown
## Context
**Project:** Tendery v2 - Transport Quotation System improvements
**Overview:** The Service Request (Solicitud de Servicio / SS) is the bridge between an approved quote and an actual dispatch. One quote can generate hundreds of SS over months (e.g., a distribution client with 300 routes dispatches daily for a year from one quote). The SS contains the operational data needed for dispatch while hiding the commercial tariff from operations.

**Key Concept:** Quote = commercial agreement with client. SS = individual dispatch order derived from that agreement.

**Current Wave:** Wave 10 of 13 - Service Request Module
**Current Issue:** TD-026 (Issue 26 of 39)
**Parallel Execution:** NO - Must complete before TD-027.

**Dependencies:** Requires Wave 9 completion (cargo_type field from TD-022).
**What comes next:** TD-027 implements the SS creation endpoint.

## Request
Create the Service Request data model, database table, DTOs, repository, and TypeScript types.

### 1. Database Table
Create migration or SQL for `ty_service_requests`:
```sql
CREATE TABLE IF NOT EXISTS ty_service_requests (
    id SERIAL PRIMARY KEY,
    ss_number VARCHAR(50) NOT NULL UNIQUE,  -- SS-2026-000001

    -- Parent quote reference
    quote_id INTEGER NOT NULL REFERENCES ty_quotes(id),

    -- Route & transport (copied from quote at creation time)
    route_id INTEGER,
    origin_city_id INTEGER,
    destination_city_id INTEGER,
    origin_city VARCHAR(100) NOT NULL,
    destination_city VARCHAR(100) NOT NULL,
    vehicle_type_id INTEGER,
    vehicle_type_name VARCHAR(100),

    -- Cargo details
    cargo_type VARCHAR(50),
    cargo_description VARCHAR(500),
    weight_tons DECIMAL(10, 2),
    cargo_value_cop DECIMAL(15, 2),

    -- Pricing (CRITICAL: dispatcher only sees flete_cop)
    tariff_cop DECIMAL(15, 2),         -- client price (HIDDEN from dispatcher)
    flete_cop DECIMAL(15, 2),          -- what to pay driver
    additional_services_cop DECIMAL(15, 2) DEFAULT 0,
    margin_cop DECIMAL(15, 2),         -- profit (HIDDEN from dispatcher)

    -- Dispatch configuration
    dispatch_mode VARCHAR(20) DEFAULT 'tender',  -- 'tender' or 'direct'

    -- Status lifecycle
    status VARCHAR(30) DEFAULT 'pending',
    -- pending -> dispatching -> assigned -> in_progress -> completed | cancelled

    -- Schedule
    pickup_date DATE,
    pickup_time TIME,
    delivery_date DATE,

    -- Additional services (array of service IDs)
    additional_service_ids INTEGER[],

    -- Notes
    notes TEXT,

    -- Assignments (filled during dispatch)
    assigned_driver_id INTEGER REFERENCES ty_drivers(id),
    assigned_vehicle_plate VARCHAR(20),
    cost_order_id INTEGER REFERENCES ty_cost_orders(id),

    -- Audit
    created_by_id VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ty_ss_quote ON ty_service_requests(quote_id);
CREATE INDEX IF NOT EXISTS idx_ty_ss_status ON ty_service_requests(status);
CREATE INDEX IF NOT EXISTS idx_ty_ss_origin ON ty_service_requests(origin_city_id);
CREATE INDEX IF NOT EXISTS idx_ty_ss_created ON ty_service_requests(created_at);
CREATE INDEX IF NOT EXISTS idx_ty_ss_number ON ty_service_requests(ss_number);
```

### 2. Pydantic DTOs
Create `apps/Server/app/models/tendery/service_request_dto.py`:
```python
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, time, datetime
from decimal import Decimal

class ServiceRequestCreateDTO(BaseModel):
    quote_id: int
    route_id: Optional[int] = None
    origin_city: str
    destination_city: str
    vehicle_type_id: Optional[int] = None
    pickup_date: Optional[date] = None
    pickup_time: Optional[time] = None
    delivery_date: Optional[date] = None
    dispatch_mode: str = "tender"  # tender | direct
    additional_service_ids: List[int] = []
    notes: Optional[str] = None

class ServiceRequestResponseDTO(BaseModel):
    id: int
    ss_number: str
    quote_id: int
    origin_city: str
    destination_city: str
    vehicle_type_name: Optional[str] = None
    cargo_type: Optional[str] = None
    weight_tons: Optional[Decimal] = None
    flete_cop: Optional[Decimal] = None
    additional_services_cop: Decimal = Decimal("0")
    dispatch_mode: str
    status: str
    pickup_date: Optional[date] = None
    delivery_date: Optional[date] = None
    assigned_driver_id: Optional[int] = None
    assigned_vehicle_plate: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime

class ServiceRequestFullDTO(ServiceRequestResponseDTO):
    """Full DTO for commercial users - includes tariff and margin"""
    tariff_cop: Optional[Decimal] = None
    margin_cop: Optional[Decimal] = None
    cargo_description: Optional[str] = None
    cost_order_id: Optional[int] = None

class ServiceRequestListItemDTO(BaseModel):
    id: int
    ss_number: str
    origin_city: str
    destination_city: str
    vehicle_type_name: Optional[str] = None
    flete_cop: Optional[Decimal] = None
    status: str
    dispatch_mode: str
    pickup_date: Optional[date] = None
    created_at: datetime
```

### 3. Repository
Create `apps/Server/app/repository/tendery/service_request_repository.py`:
```python
class ServiceRequestRepository:
    def __init__(self, db_connection):
        self.db = db_connection

    async def create(self, ss_data: dict) -> dict:
        """Insert new service request"""

    async def get_by_id(self, ss_id: int) -> Optional[dict]:
        """Get SS by ID"""

    async def list_by_quote(self, quote_id: int) -> List[dict]:
        """Get all SS for a quote"""

    async def list_all(self, filters: dict = None, limit: int = 50, offset: int = 0) -> List[dict]:
        """List SS with optional filters (status, origin, date range)"""

    async def update_status(self, ss_id: int, status: str, **kwargs) -> dict:
        """Update SS status and optional fields (assigned_driver_id, cost_order_id)"""

    async def get_next_ss_number(self) -> str:
        """Generate next SS number: SS-{YEAR}-{6-digit-sequence}"""

    async def count_by_status(self) -> dict:
        """Count SS grouped by status for dashboard"""
```

### 4. TypeScript Types
Create `apps/Client/src/types/tendery/serviceRequest.ts`:
```typescript
export type SSStatus = 'pending' | 'dispatching' | 'assigned' | 'in_progress' | 'completed' | 'cancelled';
export type DispatchMode = 'tender' | 'direct';

export interface ServiceRequest {
  id: number;
  ss_number: string;
  quote_id: number;
  origin_city: string;
  destination_city: string;
  vehicle_type_name?: string;
  cargo_type?: string;
  cargo_description?: string;
  weight_tons?: number;
  flete_cop?: number;
  tariff_cop?: number;  // Only visible to commercial roles
  margin_cop?: number;  // Only visible to commercial roles
  additional_services_cop: number;
  dispatch_mode: DispatchMode;
  status: SSStatus;
  pickup_date?: string;
  pickup_time?: string;
  delivery_date?: string;
  assigned_driver_id?: number;
  assigned_vehicle_plate?: string;
  cost_order_id?: number;
  notes?: string;
  created_at: string;
}

export interface ServiceRequestCreateData {
  quote_id: number;
  origin_city: string;
  destination_city: string;
  vehicle_type_id?: number;
  pickup_date?: string;
  pickup_time?: string;
  delivery_date?: string;
  dispatch_mode: DispatchMode;
  additional_service_ids: number[];
  notes?: string;
}
```

**UI Language:** Spanish (Colombian)
```

---

### TD-027: SS Creation from Approved Quote

**Title:** `[Tendery] Wave 10: Service Request Creation from Quote`

**Body:**
```markdown
## Context
**Project:** Tendery v2 - Transport Quotation System improvements
**Overview:** When a quote is accepted and a client requests a dispatch (via phone/WhatsApp), the seller creates a Service Request (SS) from the approved quote. The SS auto-populates transport details from the parent quote. A single quote can generate thousands of SS over its lifetime.

**Current Wave:** Wave 10 of 13 - Service Request Module
**Current Issue:** TD-027 (Issue 27 of 39)
**Parallel Execution:** NO - Requires TD-026 (data model).

**Dependencies:** TD-026 (SS data model and repository).
**What comes next:** TD-028 implements the SS list dashboard UI.

## Request
Implement the service for creating SS records from approved quotes.

### 1. Service
Create `apps/Server/app/services/tendery/service_request_service.py`:
```python
class ServiceRequestService:
    def __init__(self, ss_repository, quote_repository, route_repository):
        self.ss_repository = ss_repository
        self.quote_repository = quote_repository
        self.route_repository = route_repository

    async def create_from_quote(self, quote_id: int, ss_data: ServiceRequestCreateDTO, created_by_id: str) -> dict:
        """Create a Service Request from an accepted quote"""
        print(f"INFO [SSService]: Creating SS from quote {quote_id}")

        # 1. Validate quote exists and is accepted
        quote = await self.quote_repository.get_by_id(quote_id)
        if not quote:
            raise ValueError(f"Quote {quote_id} not found")
        if quote["status"] not in ["accepted", "active"]:
            raise ValueError(f"Quote must be accepted/active. Current: {quote['status']}")

        # 2. Generate SS number
        ss_number = await self.ss_repository.get_next_ss_number()

        # 3. Auto-populate from parent quote
        ss_record = {
            "ss_number": ss_number,
            "quote_id": quote_id,
            "origin_city": ss_data.origin_city or quote["origin_city"],
            "destination_city": ss_data.destination_city or quote["destination_city"],
            "origin_city_id": quote.get("origin_city_id"),
            "destination_city_id": quote.get("destination_city_id"),
            "route_id": ss_data.route_id or quote.get("route_id"),
            "vehicle_type_id": ss_data.vehicle_type_id or quote.get("vehicle_type_id"),
            "vehicle_type_name": quote.get("vehicle_type_name"),
            "cargo_type": quote.get("cargo_type"),
            "cargo_description": quote.get("cargo_description"),
            "weight_tons": quote.get("weight_tons"),
            "cargo_value_cop": quote.get("cargo_value_cop"),
            # Pricing from quote
            "tariff_cop": quote.get("total_price_cop"),
            "flete_cop": quote.get("base_cost_cop"),
            "additional_services_cop": quote.get("additional_services_cop", 0),
            "margin_cop": quote.get("margin_cop"),
            # SS-specific data
            "dispatch_mode": ss_data.dispatch_mode,
            "pickup_date": ss_data.pickup_date,
            "pickup_time": ss_data.pickup_time,
            "delivery_date": ss_data.delivery_date,
            "additional_service_ids": ss_data.additional_service_ids,
            "notes": ss_data.notes,
            "created_by_id": created_by_id,
            "status": "pending",
        }

        # 4. Persist
        result = await self.ss_repository.create(ss_record)

        # 5. Update quote status to "active" if first SS
        if quote["status"] == "accepted":
            await self.quote_repository.update_status(quote_id, "active")

        print(f"INFO [SSService]: SS {ss_number} created from quote {quote_id}")
        return result
```

### 2. API Routes
Create `apps/Server/app/api/tendery/service_request_routes.py`:
```python
from fastapi import APIRouter, Depends, HTTPException

router = APIRouter(prefix="/tendery/service-requests", tags=["Tendery SS"])

@router.post("")
async def create_service_request(dto: ServiceRequestCreateDTO, current_user = Depends(get_current_user)):
    """Create SS from an accepted quote"""
    result = await ss_service.create_from_quote(dto.quote_id, dto, current_user["id"])
    return result

@router.get("")
async def list_service_requests(
    status: Optional[str] = None,
    quote_id: Optional[int] = None,
    limit: int = 50,
    offset: int = 0,
    current_user = Depends(get_current_user)
):
    """List SS with filters"""
    filters = {"status": status, "quote_id": quote_id}
    return await ss_service.list_all(filters, limit, offset, current_user)

@router.get("/{ss_id}")
async def get_service_request(ss_id: int, current_user = Depends(get_current_user)):
    """Get SS detail - applies visibility controls based on role"""
    ss = await ss_service.get_by_id(ss_id, current_user)
    if not ss:
        raise HTTPException(status_code=404, detail="Service Request not found")
    return ss
```

### 3. Register Router
Update `apps/Server/main.py` to include the new router:
```python
from app.api.tendery.service_request_routes import router as tendery_ss_router
app.include_router(tendery_ss_router, prefix="/api")
```

### 4. Frontend Hook
Create `apps/Client/src/hooks/tendery/useServiceRequests.ts`:
```typescript
export function useServiceRequests() {
  const [serviceRequests, setServiceRequests] = useState<ServiceRequest[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchServiceRequests = async (filters?: SSFilters) => { ... };
  const createServiceRequest = async (data: ServiceRequestCreateData) => { ... };

  return { serviceRequests, loading, fetchServiceRequests, createServiceRequest };
}
```

### 5. Frontend Service
Create `apps/Client/src/services/tendery/serviceRequestService.ts`:
- `createSS(data)` - POST /api/tendery/service-requests
- `listSS(filters)` - GET /api/tendery/service-requests
- `getSS(id)` - GET /api/tendery/service-requests/:id

**UI Language:** Spanish (Colombian)
```

---

### TD-028: SS List Dashboard UI

**Title:** `[Tendery] Wave 10: Service Request Dashboard & List UI`

**Body:**
```markdown
## Context
**Project:** Tendery v2 - Transport Quotation System improvements
**Overview:** Operations needs a dedicated dashboard to see all pending Service Requests, filter by status/route/date, and initiate dispatch. This is the primary work view for dispatchers.

**Current Wave:** Wave 10 of 13 - Service Request Module
**Current Issue:** TD-028 (Issue 28 of 39)
**Parallel Execution:** NO - Requires TD-027 (creation endpoint).

**Dependencies:** TD-027 (SS creation service and API).
**What comes next:** TD-029 links SS to Kiosco dispatch.

## Request
Create the Service Request operations dashboard.

### 1. Page Component
Create `apps/Client/src/pages/tendery/TenderyServiceRequestsPage.tsx`:
- Page title: "Solicitudes de Servicio"
- Status summary cards at top: Pendientes, En Despacho, Asignadas, Completadas
- Filterable table below with columns: SS#, Origen, Destino, Vehiculo, Flete, Estado, Fecha
- Click row to expand/navigate to detail

### 2. List Component
Create `apps/Client/src/components/tendery/TYServiceRequestList.tsx`:
```typescript
interface TYServiceRequestListProps {
  serviceRequests: ServiceRequest[];
  onSelect: (ss: ServiceRequest) => void;
  onDispatch: (ss: ServiceRequest) => void;
}
```
- MUI DataGrid or Table with sorting/pagination
- Status chip with color coding:
  - pending: warning (yellow)
  - dispatching: info (blue)
  - assigned: primary (teal)
  - in_progress: secondary (purple)
  - completed: success (green)
  - cancelled: error (red)
- "Despachar" action button for pending SS

### 3. Filters Component
Create `apps/Client/src/components/tendery/TYServiceRequestFilters.tsx`:
- Status dropdown (multi-select)
- Origin/Destination city autocomplete
- Date range picker (pickup_date)
- Dispatch mode filter (Tender/Directo/Todos)

### 4. Detail Component
Create `apps/Client/src/components/tendery/TYServiceRequestDetail.tsx`:
- Full SS information display
- Parent quote reference (link to quote)
- Pricing: show flete_cop always, show tariff/margin ONLY for commercial roles
- Dispatch actions section (placeholder for TD-029)
- Assignment info (driver, vehicle) when assigned
- Timeline of status changes

### 5. Route Registration
Add to React Router:
```typescript
<Route path="/tendery/solicitudes" element={
  <RoleProtectedRoute allowedRoles={['admin', 'manager', 'user', 'dispatcher']}>
    <TenderyServiceRequestsPage />
  </RoleProtectedRoute>
} />
```

### 6. Navigation
Add "Solicitudes" menu item to the Tendery sidebar section.

### 7. Create SS from Quote Detail
Add "Crear Solicitud de Servicio" button on accepted/active quote detail view. Opens a dialog with:
- Pre-filled origin/destination/vehicle from quote
- Date pickers for pickup and delivery
- Dispatch mode selector (Tender/Directo)
- Notes field
- Submit creates the SS

**UI Language:** Spanish (Colombian)
- Page title: "Solicitudes de Servicio"
- Button: "Crear Solicitud"
- Filter labels: "Estado", "Origen", "Destino", "Fecha de Cargue", "Modo de Despacho"
- Action: "Despachar"
```

---

### TD-029: SS to Kiosco Dispatch Link

**Title:** `[Tendery] Wave 10: Link Service Request to Kiosco Dispatch`

**Body:**
```markdown
## Context
**Project:** Tendery v2 - Transport Quotation System improvements
**Overview:** When an SS is ready for dispatch, it triggers the Kiosco assignment engine (for Tender mode) or allows manual driver selection (for Direct mode). The SS provides all necessary data for driver matching: route, vehicle type, cargo qualification, flete amount.

**Current Wave:** Wave 10 of 13 - Service Request Module
**Current Issue:** TD-029 (Issue 29 of 39)
**Parallel Execution:** NO - Requires TD-028 (UI) and TD-026 (model).

**Dependencies:** TD-026, TD-027, TD-028.
**What comes next:** Wave 11 - Enhanced Dispatch (dual-mode, turno, re-offer).

## Request
Connect the SS dispatch action to the Kiosco assignment engine.

### 1. Dispatch Endpoint
Add to `apps/Server/app/api/tendery/service_request_routes.py`:
```python
@router.post("/{ss_id}/dispatch")
async def dispatch_service_request(ss_id: int, current_user = Depends(get_current_user)):
    """Initiate dispatch for a service request"""
    print(f"INFO [SSRoutes]: Dispatching SS {ss_id} by user {current_user['id']}")
    result = await ss_service.dispatch(ss_id, current_user)
    return result
```

### 2. Service Dispatch Method
Add to `apps/Server/app/services/tendery/service_request_service.py`:
```python
async def dispatch(self, ss_id: int, current_user: dict) -> dict:
    """Dispatch an SS - triggers Kiosco or allows direct assignment"""
    ss = await self.ss_repository.get_by_id(ss_id)
    if not ss:
        raise ValueError(f"SS {ss_id} not found")
    if ss["status"] != "pending":
        raise ValueError(f"SS must be pending to dispatch. Current: {ss['status']}")

    # Update status to dispatching
    await self.ss_repository.update_status(ss_id, "dispatching")

    if ss["dispatch_mode"] == "tender":
        # Automated: trigger Kiosco assignment
        print(f"INFO [SSService]: Tender mode - initiating Kiosco for SS {ss_id}")
        assignment_result = await self.kiosco_service.initiate_assignment_from_ss(ss_id)
        return {"mode": "tender", "ss_id": ss_id, "assignment": assignment_result}
    else:
        # Direct: return SS data for manual driver selection
        print(f"INFO [SSService]: Direct mode - awaiting manual assignment for SS {ss_id}")
        return {"mode": "direct", "ss_id": ss_id, "status": "awaiting_manual_assignment"}
```

### 3. Kiosco Service Update
Update `apps/Server/app/services/tendery/kiosco_service.py`:
```python
async def initiate_assignment_from_ss(self, ss_id: int) -> dict:
    """Initiate driver assignment from a Service Request"""
    print(f"INFO [KioscoService]: Starting assignment for SS {ss_id}")

    # Get SS data
    ss = await self.ss_repository.get_by_id(ss_id)

    # Get parent quote for client info (needed for client familiarity scoring)
    quote = await self.quote_repository.get_by_id(ss["quote_id"])

    # Build assignment context from SS
    assignment_data = {
        "service_request_id": ss_id,
        "quote_id": ss["quote_id"],
        "origin_city_id": ss["origin_city_id"],
        "destination_city_id": ss["destination_city_id"],
        "vehicle_type_id": ss["vehicle_type_id"],
        "cargo_type": ss.get("cargo_type"),
        "offered_price_cop": ss["flete_cop"],
        "client_nit": quote.get("client_nit"),
    }

    # Find candidates and create offers (existing logic)
    candidates = await self._find_candidates(assignment_data)
    # ... existing offer creation logic
```

### 4. Status Sync
When a cost order is created from the Kiosco assignment:
- Update SS `assigned_driver_id`, `assigned_vehicle_plate`, `cost_order_id`
- Update SS status to `assigned`

### 5. Frontend Dispatch Dialog
In `apps/Client/src/components/tendery/TYServiceRequestDetail.tsx`:
```typescript
const handleDispatch = async () => {
  const confirmed = window.confirm(
    ss.dispatch_mode === 'tender'
      ? '¿Iniciar búsqueda automática de conductor (Tender)?'
      : '¿Iniciar asignación manual de conductor?'
  );
  if (confirmed) {
    await serviceRequestService.dispatch(ss.id);
    // Refresh SS data
  }
};
```

### 6. Load Offers Table Update
Add `service_request_id` column to `ty_load_offers` table (nullable, for backwards compatibility). When offers are created from SS, link them.

**UI Language:** Spanish (Colombian)
```

---

## Wave 11: Enhanced Dispatch (Run Sequentially)

These three issues build on each other to complete the advanced dispatch capabilities.

### TD-030: Dual-Mode Dispatch

**Title:** `[Tendery] Wave 11: Dual-Mode Dispatch (Tender vs Direct)`

**Body:**
```markdown
## Context
**Project:** Tendery v2 - Transport Quotation System improvements
**Overview:** Operations can dispatch via two modes:
1. **Tender (Automated)**: System scores drivers, sends WhatsApp offers, first-accept-wins
2. **Direct (Manual)**: Dispatcher selects a specific driver they know/trust, bypasses scoring

Both modes should coexist. The system tracks outcomes of both for comparative analytics.

**Business Rule:** The dispatcher decision between modes is per-SS. Some loads are routine (use Tender), others need a specific relationship driver (use Direct).

**Current Wave:** Wave 11 of 13 - Enhanced Dispatch
**Current Issue:** TD-030 (Issue 30 of 39)
**Parallel Execution:** NO - Must complete before TD-031.

**Dependencies:** Requires Wave 10 completion (SS module).
**What comes next:** TD-031 implements driver turno system.

## Request
Implement dual-mode dispatch with direct assignment capability.

### 1. Direct Assignment DTO
Add to `apps/Server/app/models/tendery/kiosco_dto.py`:
```python
class DirectAssignmentDTO(BaseModel):
    service_request_id: int
    driver_id: int
    agreed_flete_cop: Optional[Decimal] = None  # Override flete if different
    notes: Optional[str] = None
```

### 2. Direct Assignment Service
Add to `apps/Server/app/services/tendery/kiosco_service.py`:
```python
async def direct_assignment(self, dto: DirectAssignmentDTO, assigned_by: str) -> dict:
    """Direct mode: dispatcher manually assigns a specific driver"""
    print(f"INFO [KioscoService]: Direct assignment - SS {dto.service_request_id} to driver {dto.driver_id}")

    # Validate driver exists and is available
    driver = await self.driver_repository.get_by_id(dto.driver_id)
    if not driver:
        raise ValueError(f"Driver {dto.driver_id} not found")
    if not driver.get("is_available", False):
        raise ValueError(f"Driver {dto.driver_id} is not available")

    # Get SS
    ss = await self.ss_repository.get_by_id(dto.service_request_id)
    if not ss:
        raise ValueError(f"SS {dto.service_request_id} not found")

    # Create cost order directly (skip offer/response cycle)
    flete = dto.agreed_flete_cop or ss["flete_cop"]
    cost_order = await self._create_cost_order(ss, driver, flete, assigned_by, mode="direct")

    # Update SS
    await self.ss_repository.update_status(
        dto.service_request_id,
        status="assigned",
        assigned_driver_id=dto.driver_id,
        assigned_vehicle_plate=driver.get("plate"),
        cost_order_id=cost_order["id"]
    )

    return cost_order
```

### 3. Endpoint
Add to `apps/Server/app/api/tendery/kiosco_routes.py`:
```python
@router.post("/assignments/direct")
async def direct_assign(dto: DirectAssignmentDTO, current_user = Depends(get_current_user)):
    """Manually assign a driver to an SS (Direct mode)"""
    result = await kiosco_service.direct_assignment(dto, current_user["id"])
    return result
```

### 4. Frontend: Dispatch Mode Toggle
Create `apps/Client/src/components/tendery/TYDispatchModeSelector.tsx`:
- Toggle switch: "Automático (Tender)" vs "Manual (Directo)"
- When Direct: show driver search dropdown
- When Tender: show "Iniciar búsqueda automática" button

### 5. Cost Order Mode Tracking
Add `dispatch_mode VARCHAR(20)` column to `ty_cost_orders` table to track which mode was used.

### 6. Analytics Foundation
Add logging that tracks: mode used, time to assignment, final flete vs original flete.
```python
print(f"INFO [KioscoService]: Assignment complete - mode={mode}, "
      f"ss={ss_id}, driver={driver_id}, flete={flete}, time_to_assign={elapsed}")
```

**UI Language:** Spanish (Colombian)
- Toggle labels: "Automático (Tender)" / "Manual (Directo)"
- Direct mode label: "Seleccionar Conductor"
```

---

### TD-031: Driver Turno System

**Title:** `[Tendery] Wave 11: Driver Turno (Availability Declaration) System`

**Body:**
```markdown
## Context
**Project:** Tendery v2 - Transport Quotation System improvements
**Overview:** Drivers call or send a WhatsApp when they arrive at a city: "Estoy disponible en Bogotá". This creates a "turno" (queue position). Drivers with active turnos should be prioritized in Kiosco scoring - they've made themselves known as available and should be served first.

**Business Rule:** Turno is the HIGHEST priority factor in scoring. A driver who declared availability in the origin city should be offered loads before any other driver, regardless of other scoring factors.

**Current Wave:** Wave 11 of 13 - Enhanced Dispatch
**Current Issue:** TD-031 (Issue 31 of 39)
**Parallel Execution:** NO - Requires TD-030.

**Dependencies:** TD-030 (dual-mode dispatch).
**What comes next:** TD-032 implements re-offer mechanism.

## Request
Implement driver turno declaration and integrate with Kiosco scoring.

### 1. Database Table
```sql
CREATE TABLE IF NOT EXISTS ty_driver_turnos (
    id SERIAL PRIMARY KEY,
    driver_id INTEGER NOT NULL REFERENCES ty_drivers(id),
    city_id INTEGER NOT NULL REFERENCES ty_cities(id),
    city_name VARCHAR(100) NOT NULL,
    available_from TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    available_until TIMESTAMPTZ,  -- NULL = until cancelled
    vehicle_type_id INTEGER REFERENCES ty_vehicle_types(id),
    preferred_destinations TEXT[],  -- optional: preferred routes
    status VARCHAR(20) DEFAULT 'active',  -- active, expired, cancelled, assigned
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_ty_turnos_city ON ty_driver_turnos(city_id, status);
CREATE INDEX IF NOT EXISTS idx_ty_turnos_driver ON ty_driver_turnos(driver_id, status);
```

### 2. DTOs
Create `apps/Server/app/models/tendery/turno_dto.py`:
```python
class TurnoCreateDTO(BaseModel):
    driver_id: int
    city_id: int
    city_name: str
    vehicle_type_id: Optional[int] = None
    available_until: Optional[datetime] = None
    preferred_destinations: List[str] = []
    notes: Optional[str] = None

class TurnoResponseDTO(BaseModel):
    id: int
    driver_id: int
    driver_name: str
    city_name: str
    available_from: datetime
    available_until: Optional[datetime]
    status: str
    created_at: datetime
```

### 3. Repository
Create `apps/Server/app/repository/tendery/turno_repository.py`:
- `create(turno_data)` - Register new turno
- `get_active_turnos(city_id)` - Get all active turnos for a city
- `get_driver_active_turno(driver_id)` - Get driver's current turno
- `cancel(turno_id)` - Cancel a turno
- `expire_old_turnos()` - Batch expire turnos past available_until

### 4. Service
Create `apps/Server/app/services/tendery/turno_service.py`:
- `declare_availability(dto)` - Creates turno, expires previous for same driver
- `get_available_in_city(city_id)` - Returns drivers with active turnos
- `cancel_turno(turno_id, driver_id)` - Cancel specific turno

### 5. Kiosco Integration
Update `_calculate_score()` in `apps/Server/app/services/tendery/kiosco_service.py`:
```python
# NEW: Turno bonus (HIGHEST PRIORITY - 30 pts)
# A driver who declared availability in the origin city gets maximum priority
has_turno = await self.turno_repository.get_driver_active_turno_in_city(
    driver["id"], origin_city_id
)
if has_turno:
    score += 30  # Highest bonus - turno priority
    print(f"INFO [KioscoService]: Driver {driver['id']} has active turno in origin city (+30)")
```

### 6. API Endpoints
```python
# In a new turno_routes.py or added to driver routes
@router.post("/drivers/{driver_id}/turno")
async def declare_turno(driver_id: int, dto: TurnoCreateDTO): ...

@router.get("/drivers/available/{city_id}")
async def get_available_drivers(city_id: int): ...

@router.delete("/drivers/{driver_id}/turno")
async def cancel_turno(driver_id: int): ...
```

### 7. Frontend
Create `apps/Client/src/components/tendery/TYDriverTurnoList.tsx`:
- List of active turnos with city, driver name, time since declaration
- "Cancelar" action button
- Shows on the Kiosco page as "Conductores Enturnados"

**UI Language:** Spanish (Colombian)
- Section title: "Conductores Enturnados"
- Button: "Registrar Turno"
- Status: "Disponible en {ciudad} desde {hora}"
```

---

### TD-032: Re-Offer Mechanism

**Title:** `[Tendery] Wave 11: Re-Offer Mechanism with Price Escalation`

**Body:**
```markdown
## Context
**Project:** Tendery v2 - Transport Quotation System improvements
**Overview:** When no driver accepts an offer within the timeout, the system can escalate the freight price and re-send offers. This continues until a driver accepts OR the price ceiling is reached (minimum margin threshold). If the ceiling is hit and no one accepts, the SS escalates to manual dispatch.

**Business Rules:**
- Escalation increment: configurable per round (default +$50K COP or +5%)
- Maximum rounds: configurable (default 3)
- Price ceiling: Cannot exceed the flete that would bring margin below minimum commercial policy
- After ceiling hit: escalate to Direct (manual) mode

**Current Wave:** Wave 11 of 13 - Enhanced Dispatch
**Current Issue:** TD-032 (Issue 32 of 39)
**Parallel Execution:** NO - Requires TD-030 and TD-031.

**Dependencies:** TD-030, TD-031.
**What comes next:** Wave 12 - Real Data Sources.

## Request
Implement automatic re-offer with price escalation and ceiling enforcement.

### 1. Re-Offer Configuration
Add to `apps/Server/app/models/tendery/kiosco_dto.py`:
```python
class ReofferConfigDTO(BaseModel):
    escalation_type: str = "fixed"  # "fixed" ($COP) or "percentage" (%)
    escalation_amount: Decimal = Decimal("50000")  # +$50K per round
    max_rounds: int = 3
    timeout_minutes: int = 30  # per round

class ReofferRequestDTO(BaseModel):
    service_request_id: int
    override_price: Optional[Decimal] = None  # Manual price override
```

### 2. Service Method
Add to `apps/Server/app/services/tendery/kiosco_service.py`:
```python
async def reoffer(self, ss_id: int, config: ReofferConfigDTO = None) -> dict:
    """Escalate offer price and re-send to candidates"""
    if config is None:
        config = ReofferConfigDTO()

    ss = await self.ss_repository.get_by_id(ss_id)
    if not ss:
        raise ValueError(f"SS {ss_id} not found")

    # Get current offer round
    existing_offers = await self.offer_repository.get_offers_for_ss(ss_id)
    current_round = self._get_current_round(existing_offers)

    if current_round >= config.max_rounds:
        print(f"INFO [KioscoService]: Max rounds reached for SS {ss_id}. Escalating to manual.")
        await self.ss_repository.update_status(ss_id, "pending", dispatch_mode="direct")
        return {"status": "escalated_to_manual", "rounds_attempted": current_round}

    # Calculate new price
    last_price = self._get_last_offered_price(existing_offers) or ss["flete_cop"]
    if config.escalation_type == "fixed":
        new_price = last_price + config.escalation_amount
    else:
        new_price = last_price * (1 + config.escalation_amount / 100)

    # Check ceiling (minimum margin enforcement)
    tariff = ss["tariff_cop"]
    min_margin = await self._get_minimum_margin(ss["vehicle_type_id"])
    price_ceiling = tariff * (1 - min_margin / 100)  # Max flete before margin breaks

    if new_price > price_ceiling:
        print(f"INFO [KioscoService]: Price ceiling reached for SS {ss_id}. "
              f"New price {new_price} > ceiling {price_ceiling}. Escalating to manual.")
        await self.ss_repository.update_status(ss_id, "pending", dispatch_mode="direct")
        return {"status": "ceiling_reached", "ceiling": price_ceiling}

    # Create new round of offers
    print(f"INFO [KioscoService]: Re-offering SS {ss_id} round {current_round + 1} "
          f"at {new_price} COP (was {last_price})")

    candidates = await self._find_candidates({...ss, "offered_price_cop": new_price})
    offers = await self._create_offers(candidates, ss_id, new_price, round=current_round + 1)

    return {"status": "reoffered", "round": current_round + 1, "price": new_price, "offers": len(offers)}
```

### 3. Endpoint
Add to `apps/Server/app/api/tendery/kiosco_routes.py`:
```python
@router.post("/assignments/{ss_id}/reoffer")
async def reoffer(ss_id: int, config: Optional[ReofferConfigDTO] = None):
    """Manually trigger re-offer with optional config override"""
    result = await kiosco_service.reoffer(ss_id, config)
    return result
```

### 4. Auto-Trigger (Timer-Based)
Add a check in the offer expiry handler:
```python
# When all offers for a round expire/reject, automatically trigger reoffer
async def handle_offer_expiry(self, offer_id: int):
    offer = await self.offer_repository.get_by_id(offer_id)
    ss_id = offer["service_request_id"]

    # Check if all offers for this SS are expired/rejected
    active_offers = await self.offer_repository.count_active(ss_id)
    if active_offers == 0:
        print(f"INFO [KioscoService]: All offers expired for SS {ss_id}. Auto re-offering.")
        await self.reoffer(ss_id)
```

### 5. Frontend Status Display
Create `apps/Client/src/components/tendery/TYReofferStatus.tsx`:
- Shows current round: "Ronda 2/3"
- Shows current offered price: "$1,650,000 COP"
- Shows price ceiling: "Techo: $1,800,000 COP"
- Action button: "Re-ofertar Manualmente" for immediate trigger
- Status indicator: spinner while waiting for responses

### 6. Offer History
Show offer history per SS: rounds, prices, driver responses (accepted/rejected/expired).

**UI Language:** Spanish (Colombian)
- Labels: "Ronda", "Precio Ofertado", "Techo de Precio", "Re-ofertar"
- Status: "Esperando respuesta...", "Sin respuesta - escalando precio", "Techo alcanzado - asignar manualmente"
```

---

## Wave 12: Real Data Sources (Run in Parallel)

These three issues implement real data source integrations and can run simultaneously.

### TD-033: SICE-TAC Scraping

**Title:** `[Tendery] Wave 12: SICE-TAC Web Scraping with Playwright`

**Body:**
```markdown
## Context
**Project:** Tendery v2 - Transport Quotation System improvements
**Overview:** SICE-TAC (government minimum freight tariffs) has NO API. The only way to get tariffs is to fill a web form and extract the result. Currently we use mock data. This issue replaces the mock with actual Playwright-based web scraping.

**Form Fields Required:**
1. Tipo de vehiculo (dropdown)
2. Estado: Cargado/Vacio (radio)
3. Tipo de carroceria (dropdown)
4. Tipo de carga (dropdown)
5. Municipio origen (autocomplete)
6. Municipio destino (autocomplete)
7. Ruta (select from results)
8. Horas logisticas: Espera cargue (2h), Cargue (2h), Espera descargue (2h), Descargue (2h)

**Result:** Minimum legal freight in COP.
**Scale:** One quote with 10 routes × 4 vehicle types = 40 SICE-TAC queries. Must handle concurrency limits.

**Current Wave:** Wave 12 of 13 - Real Data Sources
**Current Issue:** TD-033 (Issue 33 of 39)
**Parallel Execution:** YES - Can run alongside TD-034, TD-035.

**Dependencies:** Requires Wave 11 completion.
**What comes next:** Wave 13 - Advanced Features.

## Request
Replace mock SICE-TAC service with Playwright web scraping.

### 1. Scraper Module
Create `apps/Server/app/services/tendery/sicetac_scraper.py`:
```python
import asyncio
from playwright.async_api import async_playwright

class SicetacScraper:
    """Scrapes SICE-TAC government website for minimum freight tariffs"""

    SICETAC_URL = "https://www.sicetac.gov.co/..."  # Actual URL
    _semaphore = asyncio.Semaphore(1)  # Only 1 concurrent scrape

    async def get_tariff(
        self,
        vehicle_type_code: str,
        cargo_type: str,
        origin_city_code: str,
        destination_city_code: str,
        body_type: str = "general",
    ) -> dict:
        """Scrape SICE-TAC for minimum tariff"""
        async with self._semaphore:
            print(f"INFO [SicetacScraper]: Scraping tariff for "
                  f"{origin_city_code} -> {destination_city_code}, vehicle={vehicle_type_code}")

            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()

                try:
                    await page.goto(self.SICETAC_URL)

                    # Fill form fields
                    await self._select_vehicle_type(page, vehicle_type_code)
                    await self._select_loaded(page)
                    await self._select_body_type(page, body_type)
                    await self._select_cargo_type(page, cargo_type)
                    await self._fill_origin(page, origin_city_code)
                    await self._fill_destination(page, destination_city_code)
                    await self._set_logistic_hours(page)

                    # Submit and extract result
                    await page.click('button[type="submit"]')
                    await page.wait_for_selector('.result-tariff')

                    tariff_text = await page.text_content('.result-tariff')
                    tariff_cop = self._parse_cop_value(tariff_text)

                    print(f"INFO [SicetacScraper]: Result: ${tariff_cop:,.0f} COP")
                    return {"min_tariff_cop": tariff_cop, "source": "scraping"}

                except Exception as e:
                    print(f"ERROR [SicetacScraper]: Scraping failed: {str(e)}")
                    return None
                finally:
                    await browser.close()
```

### 2. Cache Layer
Create/update `apps/Server/app/repository/tendery/sicetac_repository.py`:
```python
async def get_cached_tariff(self, route_id: int, vehicle_type_id: int, max_age_hours: int = 24):
    """Get cached SICE-TAC tariff if still valid"""

async def cache_tariff(self, route_id: int, vehicle_type_id: int, tariff_cop: Decimal):
    """Store scraped tariff in cache table"""
```

### 3. Service Integration
Update `apps/Server/app/services/tendery/sicetac_service.py`:
```python
async def get_tariff(self, route_id, vehicle_type_id, cargo_type=None):
    # 1. Check cache
    cached = await self.repository.get_cached_tariff(route_id, vehicle_type_id)
    if cached:
        return cached

    # 2. If USE_MOCK_APIS=True, return mock
    if self.use_mock:
        return self._mock_tariff(route_id, vehicle_type_id)

    # 3. Scrape real value
    result = await self.scraper.get_tariff(vehicle_type_code, cargo_type, origin_code, dest_code)
    if result:
        await self.repository.cache_tariff(route_id, vehicle_type_id, result["min_tariff_cop"])
        return result

    # 4. Fallback to mock if scraping fails
    print(f"WARN [SicetacService]: Scraping failed, falling back to mock")
    return self._mock_tariff(route_id, vehicle_type_id)
```

### 4. Dependencies
Add to `apps/Server/requirements.txt`:
```
playwright==1.40.0
```

### 5. Deployment Note
Add Playwright browser installation to deployment:
```bash
playwright install chromium
```

### 6. Rate Limiting
- Semaphore limits to 1 concurrent scrape
- Between requests: 2-second delay
- Max retries: 3 per query
- Timeout: 30 seconds per scrape

**Note:** The actual SICE-TAC URL and form selectors need to be confirmed with the team. Use environment variable `SICETAC_URL` for configurability.
```

---

### TD-034: RNDC Excel Processing

**Title:** `[Tendery] Wave 12: RNDC Excel Processing Pipeline`

**Body:**
```markdown
## Context
**Project:** Tendery v2 - Transport Quotation System improvements
**Overview:** RNDC (Registro Nacional de Despachos de Carga) provides monthly Excel downloads with all national dispatches. Files contain 55K-200K+ rows. The data needs cleaning (remove $0 fleet-owned), grouping by corridor+vehicle+cargo, and Gaussian analysis to find optimal pricing percentiles.

**Data Cleaning Rules:**
1. Remove rows with freight = $0 (fleet-owned vehicles, not subject to SICE-TAC)
2. Remove rows below P10 (suspected dumping or internal transfers)
3. Only values ABOVE SICE-TAC floor are relevant for market analysis
4. Group by: origin_city + destination_city + vehicle_type (+ optionally cargo_type)

**Current Wave:** Wave 12 of 13 - Real Data Sources
**Current Issue:** TD-034 (Issue 34 of 39)
**Parallel Execution:** YES - Can run alongside TD-033, TD-035.

**Dependencies:** Requires Wave 11 completion.
**What comes next:** Wave 13 - Advanced Features.

## Request
Implement RNDC Excel upload, processing, and Gaussian analysis pipeline.

### 1. Upload Endpoint
Add to `apps/Server/app/api/tendery/rndc_routes.py`:
```python
from fastapi import APIRouter, UploadFile, File

router = APIRouter(prefix="/tendery/rndc", tags=["Tendery RNDC"])

@router.post("/upload")
async def upload_rndc_excel(file: UploadFile = File(...), current_user = Depends(get_current_user)):
    """Upload monthly RNDC Excel file for processing"""
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(400, "File must be Excel format (.xlsx or .xls)")

    print(f"INFO [RndcRoutes]: Uploading RNDC file: {file.filename}")
    result = await rndc_service.process_upload(file)
    return result

@router.get("/analysis")
async def get_rndc_analysis(
    route_id: Optional[int] = None,
    vehicle_type_id: Optional[int] = None,
):
    """Get processed RNDC analysis data"""
    return await rndc_service.get_analysis(route_id, vehicle_type_id)
```

### 2. Processing Service
Update `apps/Server/app/services/tendery/rndc_service.py`:
```python
import pandas as pd
import numpy as np
from scipy import stats

class RndcService:
    async def process_upload(self, file: UploadFile) -> dict:
        """Process RNDC Excel file: clean, group, analyze"""
        print(f"INFO [RndcService]: Processing RNDC file...")

        # 1. Read Excel
        df = pd.read_excel(file.file)
        total_rows = len(df)
        print(f"INFO [RndcService]: Read {total_rows} rows")

        # 2. Clean: remove $0 values (fleet-owned)
        df = df[df['valor_flete'] > 0]
        print(f"INFO [RndcService]: After removing $0: {len(df)} rows")

        # 3. Remove outliers below P10
        df = df.groupby(['origen', 'destino', 'tipo_vehiculo']).apply(
            lambda x: x[x['valor_flete'] >= x['valor_flete'].quantile(0.10)]
        ).reset_index(drop=True)
        print(f"INFO [RndcService]: After removing < P10: {len(df)} rows")

        # 4. Group and analyze
        groups = df.groupby(['origen', 'destino', 'tipo_vehiculo'])
        results = []

        for (origin, dest, vehicle), group in groups:
            values = group['valor_flete'].values
            if len(values) < 5:
                continue  # Skip groups with too few samples

            analysis = {
                'origin_city': origin,
                'destination_city': dest,
                'vehicle_type': vehicle,
                'sample_count': len(values),
                'min_cop': float(np.min(values)),
                'max_cop': float(np.max(values)),
                'mean_cop': float(np.mean(values)),
                'median_cop': float(np.median(values)),
                'std_dev_cop': float(np.std(values)),
                'p25_cop': float(np.percentile(values, 25)),
                'p50_cop': float(np.percentile(values, 50)),
                'p55_cop': float(np.percentile(values, 55)),
                'p60_cop': float(np.percentile(values, 60)),
                'p75_cop': float(np.percentile(values, 75)),
                'p90_cop': float(np.percentile(values, 90)),
            }
            results.append(analysis)

        # 5. Store in database
        stored = await self.repository.bulk_store_analysis(results)

        print(f"INFO [RndcService]: Processed {len(results)} corridor-vehicle combinations")
        return {"total_rows": total_rows, "analyzed_groups": len(results), "stored": stored}
```

### 3. Repository
Update `apps/Server/app/repository/tendery/rndc_repository.py`:
```python
async def bulk_store_analysis(self, results: List[dict]) -> int:
    """Store analysis results, replacing existing for same corridors"""

async def get_analysis(self, route_id=None, vehicle_type_id=None) -> List[dict]:
    """Get stored analysis filtered by route and/or vehicle type"""

async def get_optimal_price(self, origin_city: str, dest_city: str, vehicle_type: str) -> Optional[dict]:
    """Get P55-P60 optimal price for a corridor"""
```

### 4. Dependencies
Add to `apps/Server/requirements.txt`:
```
pandas==2.1.0
numpy==1.26.0
openpyxl==3.1.2
scipy==1.11.0
```

### 5. Frontend Upload UI
Create `apps/Client/src/components/tendery/TYRndcUpload.tsx`:
- File upload dropzone
- Progress bar during processing
- Results summary: rows processed, corridors analyzed
- Table preview of top results

### 6. Integration with Pricing
Update `pricing_calculator_service.py` to use real RNDC data when available:
```python
# Check for real RNDC analysis first
rndc_data = await self.rndc_repository.get_optimal_price(origin, dest, vehicle)
if rndc_data:
    rndc_price = rndc_data["p60_cop"]  # P60 = optimal target
else:
    rndc_price = self._mock_rndc_price(...)
```

**UI Language:** Spanish (Colombian)
- Button: "Cargar Excel RNDC"
- Status: "Procesando...", "Completado: X corredores analizados"
```

---

### TD-035: Market Rate Input

**Title:** `[Tendery] Wave 12: Market Rate Input for Dispatchers`

**Body:**
```markdown
## Context
**Project:** Tendery v2 - Transport Quotation System improvements
**Overview:** Real-time market rates from dispatcher knowledge are the most volatile pricing source. When a ship arrives at port, prices spike instantly. When there's low demand, prices drop. This information lives in dispatcher phone calls and WhatsApp groups. We need a way for dispatchers to log these observations so the pricing engine can incorporate them.

**Current Wave:** Wave 12 of 13 - Real Data Sources
**Current Issue:** TD-035 (Issue 35 of 39)
**Parallel Execution:** YES - Can run alongside TD-033, TD-034.

**Dependencies:** Requires Wave 11 completion.
**What comes next:** Wave 13 - Advanced Features.

## Request
Create market rate input mechanism and integrate with pricing engine.

### 1. Database Table
```sql
CREATE TABLE IF NOT EXISTS ty_market_rates (
    id SERIAL PRIMARY KEY,
    route_id INTEGER REFERENCES ty_routes(id),
    origin_city VARCHAR(100) NOT NULL,
    destination_city VARCHAR(100) NOT NULL,
    vehicle_type_id INTEGER REFERENCES ty_vehicle_types(id),
    vehicle_type_name VARCHAR(100),
    reported_price_cop DECIMAL(15, 2) NOT NULL,
    source VARCHAR(50) NOT NULL,  -- 'phone_call', 'whatsapp', 'driver_offer', 'competitor', 'port_update'
    reporter_id VARCHAR(100),
    reporter_name VARCHAR(200),
    driver_id INTEGER REFERENCES ty_drivers(id),  -- optional
    notes TEXT,
    reported_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMPTZ  -- market rates expire quickly (24-48h)
);
CREATE INDEX IF NOT EXISTS idx_ty_market_route ON ty_market_rates(route_id, reported_at);
CREATE INDEX IF NOT EXISTS idx_ty_market_vehicle ON ty_market_rates(vehicle_type_id);
```

### 2. DTOs
Create in `apps/Server/app/models/tendery/market_rate_dto.py`:
```python
class MarketRateCreateDTO(BaseModel):
    origin_city: str
    destination_city: str
    vehicle_type_id: int
    reported_price_cop: Decimal
    source: str  # phone_call, whatsapp, driver_offer, competitor, port_update
    driver_id: Optional[int] = None
    notes: Optional[str] = None

class MarketRateResponseDTO(BaseModel):
    id: int
    origin_city: str
    destination_city: str
    vehicle_type_name: Optional[str]
    reported_price_cop: Decimal
    source: str
    reporter_name: Optional[str]
    reported_at: datetime
```

### 3. Repository
Create `apps/Server/app/repository/tendery/market_rate_repository.py`:
```python
class MarketRateRepository:
    async def create(self, rate_data: dict) -> dict: ...

    async def get_recent_average(
        self, origin_city: str, dest_city: str, vehicle_type_id: int, days_back: int = 7
    ) -> Optional[Decimal]:
        """Average of recent market rates for this corridor"""

    async def get_recent_rates(self, limit: int = 20) -> List[dict]:
        """Recent market rate observations for dashboard"""
```

### 4. Endpoints
Create `apps/Server/app/api/tendery/market_rate_routes.py`:
```python
router = APIRouter(prefix="/tendery/market-rates", tags=["Tendery Market"])

@router.post("")
async def log_market_rate(dto: MarketRateCreateDTO, current_user = Depends(get_current_user)):
    """Log a market rate observation"""
    ...

@router.get("")
async def get_recent_rates(limit: int = 20):
    """Get recent market rate observations"""
    ...

@router.get("/average")
async def get_market_average(origin: str, destination: str, vehicle_type_id: int, days: int = 7):
    """Get average market rate for a corridor"""
    ...
```

### 5. Pricing Integration
Update `apps/Server/app/services/tendery/pricing_calculator_service.py`:
```python
# Add market rate as 4th pricing source
market_rate = await self.market_rate_repository.get_recent_average(
    origin_city, dest_city, vehicle_type_id, days_back=7
)

# Updated formula: weighted combination
if market_rate:
    optimal_flete = max(
        sicetac_min,  # Floor - cannot go below
        (rndc_optimal * 0.50) + (historical * 0.25) + (market_rate * 0.25)
    )
else:
    optimal_flete = max(sicetac_min, (rndc_optimal * 0.60) + (historical * 0.40))
```

### 6. Frontend Quick-Entry Form
Create `apps/Client/src/components/tendery/TYMarketRateInput.tsx`:
- Compact form: Route selector + Price input + Source dropdown + Notes
- Sources: "Llamada telefónica", "WhatsApp", "Oferta de conductor", "Competencia", "Actualización de puerto"
- Submit adds rate to the system
- Place in dispatch/operations dashboard

### 7. Dashboard Widget
Create `apps/Client/src/components/tendery/TYMarketRateWidget.tsx`:
- Shows last 5-10 market rates logged
- Mini-table: Ruta, Vehículo, Precio, Fuente, Hace X minutos

**UI Language:** Spanish (Colombian)
- Form title: "Registrar Precio de Mercado"
- Source labels: "Llamada", "WhatsApp", "Oferta Conductor", "Competencia", "Puerto"
- Button: "Registrar"
```

---

## Wave 13: Advanced Features (Mixed Parallelization)

TD-036, TD-037, TD-038 can run in parallel. TD-039 requires TD-036 and TD-038.

### TD-036: Route Security Rules Engine

**Title:** `[Tendery] Wave 13: Route-Specific Security Rules Engine`

**Body:**
```markdown
## Context
**Project:** Tendery v2 - Transport Quotation System improvements
**Overview:** Certain cargo+route combinations require mandatory security services (escorts, satellite locks, additional insurance). For example: tires from Cartagena to Bogotá always require an escort. Electronics above $100M COP require satellite lock. These rules come from operational experience and are currently undocumented "tribal knowledge."

**Current Wave:** Wave 13 of 13 - Advanced Features
**Current Issue:** TD-036 (Issue 36 of 39)
**Parallel Execution:** YES - Can run alongside TD-037, TD-038.

**Dependencies:** Requires Wave 12 completion and TD-022 (cargo_type field).
**What comes next:** TD-039 uses rules for compliance validation.

## Request
Build a rules engine that evaluates cargo type + route to determine mandatory additional services.

### 1. Database Table
```sql
CREATE TABLE IF NOT EXISTS ty_security_rules (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    cargo_type VARCHAR(50),  -- NULL = applies to all cargo types
    origin_city_id INTEGER REFERENCES ty_cities(id),  -- NULL = any origin
    destination_city_id INTEGER REFERENCES ty_cities(id),  -- NULL = any destination
    route_pattern VARCHAR(200),  -- e.g., "Cartagena->*" or "*->Bogota"
    min_cargo_value_cop DECIMAL(15, 2),  -- NULL = no minimum
    required_service_ids INTEGER[] NOT NULL,  -- services that MUST be included
    risk_level VARCHAR(20) DEFAULT 'medium',  -- low, medium, high, critical
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
```

### 2. Service
Create `apps/Server/app/services/tendery/security_rules_service.py`:
```python
class SecurityRulesService:
    async def evaluate(self, cargo_type: str, origin_city_id: int,
                       destination_city_id: int, cargo_value_cop: Decimal = None) -> dict:
        """Evaluate security rules for a cargo+route combination"""
        print(f"INFO [SecurityRules]: Evaluating rules for cargo={cargo_type}, "
              f"origin={origin_city_id}, dest={destination_city_id}")

        rules = await self.repository.find_matching_rules(
            cargo_type, origin_city_id, destination_city_id, cargo_value_cop
        )

        mandatory_service_ids = set()
        applied_rules = []
        max_risk = "low"

        for rule in rules:
            mandatory_service_ids.update(rule["required_service_ids"])
            applied_rules.append(rule["name"])
            if self._risk_level_value(rule["risk_level"]) > self._risk_level_value(max_risk):
                max_risk = rule["risk_level"]

        result = {
            "mandatory_service_ids": list(mandatory_service_ids),
            "applied_rules": applied_rules,
            "risk_level": max_risk,
            "has_mandatory_services": len(mandatory_service_ids) > 0
        }

        print(f"INFO [SecurityRules]: Found {len(applied_rules)} matching rules, "
              f"{len(mandatory_service_ids)} mandatory services, risk={max_risk}")
        return result
```

### 3. Pricing Integration
In `pricing_calculator_service.py`, call security rules before calculating:
```python
# Auto-add mandatory services based on security rules
security = await self.security_rules_service.evaluate(
    cargo_type, origin_city_id, destination_city_id, cargo_value_cop
)
all_service_ids = list(set(additional_service_ids + security["mandatory_service_ids"]))
```

### 4. Frontend Warning
When user selects cargo_type + route in the quotation form, display a warning:
```typescript
// In TYTransportSection or TYReviewSection
{securityRules.has_mandatory_services && (
  <Alert severity="warning">
    <AlertTitle>Servicios de Seguridad Obligatorios</AlertTitle>
    Esta ruta requiere: {securityRules.applied_rules.join(', ')}
  </Alert>
)}
```

### 5. Admin CRUD
Create `apps/Client/src/components/tendery/TYSecurityRulesAdmin.tsx`:
- List of active rules with filters
- Create/Edit form: cargo type, origin, destination, value threshold, required services
- Toggle active/inactive

### 6. Seed Data
```sql
INSERT INTO ty_security_rules (name, cargo_type, route_pattern, required_service_ids, risk_level, description) VALUES
    ('Electrónica Cartagena-Bogotá', 'electronica', 'Cartagena->Bogota', ARRAY[1, 8], 'high', 'Electrónica en corredor Caribe requiere escolta y candado'),
    ('Valores altos > $100M', NULL, NULL, ARRAY[1, 5], 'critical', 'Carga > $100M requiere escolta y póliza adicional'),
    ('MATPEL cualquier ruta', 'peligrosa', NULL, ARRAY[6], 'high', 'MATPEL requiere acompañamiento especializado'),
    ('Llantas desde Cartagena', 'general', 'Cartagena->*', ARRAY[1], 'medium', 'Llantas desde puertos requieren escolta por alto robo');
```

**UI Language:** Spanish (Colombian)
```

---

### TD-037: Client Categorization & Scoring

**Title:** `[Tendery] Wave 13: Client Categorization and Scoring System`

**Body:**
```markdown
## Context
**Project:** Tendery v2 - Transport Quotation System improvements
**Overview:** Clients fall into two main categories with different pricing dynamics:
1. **Distribution**: Small/medium vehicles (turbos, sencillos), stable tariffs, long-term relationships (up to 1 year per quote)
2. **Ports/Containers**: Large vehicles (tractomulas), volatile tariffs (change daily with ship arrivals), spot pricing

Client scoring helps prioritize commercial effort and adjust pricing strategies.

**Current Wave:** Wave 13 of 13 - Advanced Features
**Current Issue:** TD-037 (Issue 37 of 39)
**Parallel Execution:** YES - Can run alongside TD-036, TD-038.

**Dependencies:** Requires Wave 12 completion.
**What comes next:** TD-039 (compliance) completes the system.

## Request
Implement client categorization and scoring.

### 1. Database Table
```sql
CREATE TABLE IF NOT EXISTS ty_clients (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    nit VARCHAR(20) UNIQUE,
    category VARCHAR(30) DEFAULT 'general',  -- distribution, ports, general
    scoring DECIMAL(5, 2) DEFAULT 50.00,  -- 0-100 score
    credit_status VARCHAR(30) DEFAULT 'pending',  -- pending, approved, rejected, cash_only
    credit_amount_cop DECIMAL(15, 2),
    credit_days INTEGER,
    total_quotes INTEGER DEFAULT 0,
    total_accepted INTEGER DEFAULT 0,
    total_dispatches INTEGER DEFAULT 0,
    total_revenue_cop DECIMAL(15, 2) DEFAULT 0,
    avg_margin_pct DECIMAL(5, 2) DEFAULT 0,
    primary_routes TEXT[],
    last_dispatch_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_ty_clients_nit ON ty_clients(nit);
CREATE INDEX IF NOT EXISTS idx_ty_clients_category ON ty_clients(category);
```

### 2. Service
Create `apps/Server/app/services/tendery/client_service.py`:
```python
class ClientService:
    async def get_or_create_by_nit(self, nit: str, name: str) -> dict:
        """Get existing client or create new one"""

    async def update_scoring(self, client_id: int) -> float:
        """Recalculate client score based on activity"""
        # Factors: acceptance_rate, volume, recurrence, avg_margin, payment_history

    async def categorize(self, client_id: int, category: str) -> dict:
        """Set client category (distribution/ports/general)"""

    async def get_pricing_strategy(self, client_id: int) -> dict:
        """Returns pricing strategy based on category"""
        # Distribution: trust SICE-TAC more, stable margins
        # Ports: trust market intelligence more, higher margins for volatility
```

### 3. Quote Integration
When creating a quote, look up client by NIT:
- If existing: apply category-specific pricing strategy
- If new: create client record, default to "general" category

### 4. Frontend Components
- `TYClientBadge.tsx`: Shows category icon + score next to client name
- `TYClientProfile.tsx`: Full client info in quote detail view
- Update `TYQuotationForm.tsx`: After NIT entry, show client info if found

### 5. Scoring Formula
```python
def _calculate_score(self, client: dict) -> float:
    score = 50.0  # Base

    # Acceptance rate bonus (0-20)
    if client["total_quotes"] > 0:
        rate = client["total_accepted"] / client["total_quotes"]
        score += rate * 20

    # Volume bonus (0-15)
    if client["total_dispatches"] > 100:
        score += 15
    elif client["total_dispatches"] > 50:
        score += 10

    # Margin quality (0-15)
    if client["avg_margin_pct"] > 20:
        score += 15
    elif client["avg_margin_pct"] > 12:
        score += 10

    return min(score, 100.0)
```

**UI Language:** Spanish (Colombian)
- Categories: "Distribución", "Puertos/Contenedores", "General"
- Labels: "Puntuación del Cliente", "Categoría"
```

---

### TD-038: Auto-Proforma per Service Request

**Title:** `[Tendery] Wave 13: Automatic Proforma Generation per SS`

**Body:**
```markdown
## Context
**Project:** Tendery v2 - Transport Quotation System improvements
**Overview:** Insurance policies require a formal offer (proforma) for every dispatch to cover potential cargo claims. Currently proformas are manual. Each SS should auto-generate a proforma that includes all compliance info (insurance coverage, security services, terms).

**Business Rule:** Every dispatch MUST have a formal proforma (oferta). Without it, insurance may not cover cargo losses.

**Current Wave:** Wave 13 of 13 - Advanced Features
**Current Issue:** TD-038 (Issue 38 of 39)
**Parallel Execution:** YES - Can run alongside TD-036, TD-037.

**Dependencies:** Requires Wave 10 (SS module) completion.
**What comes next:** TD-039 (compliance validation) uses proforma status.

## Request
Auto-generate proforma documents when Service Requests are created.

### 1. Database Extension
Add `service_request_id` to existing proforma table or create:
```sql
CREATE TABLE IF NOT EXISTS ty_proformas (
    id SERIAL PRIMARY KEY,
    proforma_number VARCHAR(50) NOT NULL UNIQUE,
    service_request_id INTEGER REFERENCES ty_service_requests(id),
    quote_id INTEGER REFERENCES ty_quotes(id),
    -- Client info
    client_name VARCHAR(200),
    client_nit VARCHAR(20),
    -- Transport details
    origin_city VARCHAR(100),
    destination_city VARCHAR(100),
    vehicle_type VARCHAR(100),
    cargo_type VARCHAR(50),
    cargo_description VARCHAR(500),
    weight_tons DECIMAL(10, 2),
    cargo_value_cop DECIMAL(15, 2),
    -- Pricing
    tariff_cop DECIMAL(15, 2),
    additional_services_cop DECIMAL(15, 2),
    total_cop DECIMAL(15, 2),
    -- Compliance
    insurance_coverage_cop DECIMAL(15, 2),
    security_services TEXT[],
    terms TEXT,
    -- Validity
    valid_until TIMESTAMPTZ,
    -- Status
    status VARCHAR(20) DEFAULT 'generated',  -- generated, sent, accepted
    generated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
```

### 2. Auto-Generation Trigger
In `apps/Server/app/services/tendery/service_request_service.py`, after creating SS:
```python
# Auto-generate proforma for insurance compliance
proforma = await self.proforma_service.generate_for_ss(result["id"])
print(f"INFO [SSService]: Auto-generated proforma {proforma['proforma_number']} for SS {result['ss_number']}")
```

### 3. Proforma Service Update
Update `apps/Server/app/services/tendery/proforma_service.py`:
```python
async def generate_for_ss(self, ss_id: int) -> dict:
    """Auto-generate proforma from Service Request data"""
    ss = await self.ss_repository.get_by_id(ss_id)
    quote = await self.quote_repository.get_by_id(ss["quote_id"])

    proforma_data = {
        "proforma_number": await self._generate_number(),
        "service_request_id": ss_id,
        "quote_id": ss["quote_id"],
        "client_name": quote["client_name"],
        "client_nit": quote.get("client_nit"),
        "origin_city": ss["origin_city"],
        "destination_city": ss["destination_city"],
        "vehicle_type": ss.get("vehicle_type_name"),
        "cargo_type": ss.get("cargo_type"),
        "cargo_description": ss.get("cargo_description"),
        "weight_tons": ss.get("weight_tons"),
        "cargo_value_cop": ss.get("cargo_value_cop"),
        "tariff_cop": ss["tariff_cop"],
        "additional_services_cop": ss.get("additional_services_cop", 0),
        "total_cop": ss["tariff_cop"] + ss.get("additional_services_cop", 0),
        "insurance_coverage_cop": ss.get("cargo_value_cop", 0),
        "valid_until": datetime.utcnow() + timedelta(days=7),
        "terms": self._get_standard_terms(),
    }

    return await self.proforma_repository.create(proforma_data)
```

### 4. Frontend
Add "Ver Proforma" button to SS detail view:
```typescript
{ss.proforma_id && (
  <Button onClick={() => window.open(`/api/tendery/proformas/${ss.proforma_id}/pdf`)}>
    Ver Proforma
  </Button>
)}
```

**UI Language:** Spanish (Colombian)
- Button: "Ver Proforma"
- Status: "Proforma generada automáticamente"
```

---

### TD-039: Insurance Compliance Validation

**Title:** `[Tendery] Wave 13: Dispatch Compliance Validation`

**Body:**
```markdown
## Context
**Project:** Tendery v2 - Transport Quotation System improvements
**Overview:** Before a vehicle can be dispatched, several compliance checks must pass: driver documentation, vehicle certifications, cargo insurance coverage, and mandatory security services. This blocks dispatch if any requirement is missing, preventing uninsured shipments.

**Current Wave:** Wave 13 of 13 - Advanced Features
**Current Issue:** TD-039 (Issue 39 of 39)
**Parallel Execution:** NO - Requires TD-036 (security rules) and TD-038 (proforma).

**Dependencies:** TD-036, TD-038.
**What comes next:** This completes Tendery v2 implementation.

## Request
Implement pre-dispatch compliance validation.

### 1. Service
Create `apps/Server/app/services/tendery/compliance_service.py`:
```python
class ComplianceService:
    async def validate_dispatch_readiness(self, ss_id: int, driver_id: int) -> dict:
        """Validate all compliance requirements before dispatch"""
        print(f"INFO [ComplianceService]: Validating dispatch readiness for SS {ss_id}, driver {driver_id}")

        checks = []
        all_passed = True

        # 1. Proforma exists
        proforma = await self.proforma_repository.get_by_ss(ss_id)
        checks.append({
            "name": "Proforma/Oferta Formal",
            "passed": proforma is not None,
            "detail": f"Proforma {proforma['proforma_number']}" if proforma else "No generada"
        })

        # 2. Driver documentation valid
        driver = await self.driver_repository.get_by_id(driver_id)
        has_docs = driver.get("documents_valid", False)
        checks.append({
            "name": "Documentación del Conductor",
            "passed": has_docs,
            "detail": "Cédula, licencia, SOAT vigentes" if has_docs else "Documentos pendientes"
        })

        # 3. Vehicle certification
        has_cert = driver.get("vehicle_certified", False)
        checks.append({
            "name": "Revisión Tecnomecánica",
            "passed": has_cert,
            "detail": "Vigente" if has_cert else "Vencida o no registrada"
        })

        # 4. Cargo insurance coverage
        ss = await self.ss_repository.get_by_id(ss_id)
        cargo_value = ss.get("cargo_value_cop", 0)
        has_insurance = cargo_value <= 200_000_000  # Basic policy covers up to $200M
        checks.append({
            "name": "Cobertura de Seguro",
            "passed": has_insurance,
            "detail": f"Valor carga: ${cargo_value:,.0f}" if has_insurance else "Requiere póliza adicional"
        })

        # 5. Security services confirmed (from rules engine)
        security = await self.security_rules_service.evaluate(
            ss.get("cargo_type"), ss.get("origin_city_id"), ss.get("destination_city_id"), cargo_value
        )
        if security["has_mandatory_services"]:
            # Check all mandatory services are in the SS
            ss_services = set(ss.get("additional_service_ids", []))
            mandatory = set(security["mandatory_service_ids"])
            services_ok = mandatory.issubset(ss_services)
            checks.append({
                "name": "Servicios de Seguridad",
                "passed": services_ok,
                "detail": "Todos los servicios obligatorios incluidos" if services_ok else f"Faltan: {mandatory - ss_services}"
            })
            if not services_ok:
                all_passed = False

        # 6. Driver cargo qualification
        if ss.get("cargo_type"):
            qualifications = driver.get("cargo_qualifications", [])
            qualified = ss["cargo_type"] in qualifications or ss["cargo_type"] == "general"
            checks.append({
                "name": "Calificación de Carga",
                "passed": qualified,
                "detail": f"Conductor calificado para {ss['cargo_type']}" if qualified else "Conductor no calificado para este tipo de carga"
            })

        for check in checks:
            if not check["passed"]:
                all_passed = False

        result = {
            "ss_id": ss_id,
            "driver_id": driver_id,
            "all_passed": all_passed,
            "checks": checks,
            "can_dispatch": all_passed,
            "blocking_issues": [c for c in checks if not c["passed"]]
        }

        print(f"INFO [ComplianceService]: Validation result: {'PASSED' if all_passed else 'BLOCKED'} "
              f"({sum(1 for c in checks if c['passed'])}/{len(checks)} checks passed)")

        return result
```

### 2. Endpoint
Add to SS routes:
```python
@router.get("/{ss_id}/compliance/{driver_id}")
async def check_compliance(ss_id: int, driver_id: int):
    """Check dispatch compliance for SS + driver combination"""
    return await compliance_service.validate_dispatch_readiness(ss_id, driver_id)
```

### 3. Integration with Dispatch
Before creating cost order, validate compliance:
```python
# In kiosco_service or dispatch logic
compliance = await self.compliance_service.validate_dispatch_readiness(ss_id, driver_id)
if not compliance["can_dispatch"]:
    raise ValueError(f"Dispatch blocked: {[c['name'] for c in compliance['blocking_issues']]}")
```

### 4. Frontend Checklist
Create `apps/Client/src/components/tendery/TYComplianceChecklist.tsx`:
```typescript
interface TYComplianceChecklistProps {
  checks: ComplianceCheck[];
  canDispatch: boolean;
}
```
- Green checkmarks for passed items
- Red X for failed items with detail text
- "Despachar" button only enabled when all checks pass
- Warning banner if any check fails

### 5. Dashboard Alert
Show count of SS with compliance issues in the operations dashboard:
```typescript
<Paper sx={{ p: 2, borderLeft: '4px solid red' }}>
  <Typography variant="h6">Con Problemas de Cumplimiento</Typography>
  <Typography variant="h3" color="error">{complianceIssueCount}</Typography>
</Paper>
```

**UI Language:** Spanish (Colombian)
- Title: "Validación de Cumplimiento"
- Checks: "Proforma", "Documentación", "Revisión Tecnomecánica", "Seguro", "Servicios de Seguridad", "Calificación"
- Passed: "Cumple" / Failed: "No cumple"
- Button: "Despachar" (disabled if blocked)
```

---

## Dependency Graph

```
WAVE 9 (Quick Wins) - ALL PARALLEL:
  TD-022 (Cargo Type) ─┐
  TD-023 (Visibility)  ─┤── 4 worktrees simultaneous
  TD-024 (Acceptance)  ─┤
  TD-025 (Scoring)     ─┘

WAVE 10 (SS Module) - SEQUENTIAL:
  TD-026 (Data Model) → TD-027 (Creation) → TD-028 (Dashboard) → TD-029 (Kiosco Link)

WAVE 11 (Enhanced Dispatch) - SEQUENTIAL:
  TD-030 (Dual-Mode) → TD-031 (Turno) → TD-032 (Re-Offer)

WAVE 12 (Real Data Sources) - ALL PARALLEL:
  TD-033 (SICE-TAC Scraping) ─┐
  TD-034 (RNDC Excel)         ─┤── 3 worktrees simultaneous
  TD-035 (Market Rates)       ─┘

WAVE 13 (Advanced Features) - MIXED:
  TD-036 (Security Rules)  ─┐
  TD-037 (Client Scoring)  ─┤── 3 worktrees simultaneous
  TD-038 (Auto-Proforma)  ─┘
  TD-039 (Compliance) ────── Sequential after TD-036 + TD-038
```

**Inter-wave dependencies:**
- Wave 10 requires Wave 9 completion (uses cargo_type from TD-022)
- Wave 11 requires Wave 10 completion (uses SS module)
- Wave 12 requires Wave 11 completion
- Wave 13 requires Wave 12 completion AND Wave 10

---

## Execution Summary

| Wave | Issues | Mode | Worktrees | Description |
|------|--------|------|-----------|-------------|
| 9 | TD-022 to TD-025 | Parallel | 4 | Quick wins on existing features |
| 10 | TD-026 to TD-029 | Sequential | 1 | Service Request module (new) |
| 11 | TD-030 to TD-032 | Sequential | 1 | Enhanced dispatch capabilities |
| 12 | TD-033 to TD-035 | Parallel | 3 | Real data source integrations |
| 13 | TD-036 to TD-039 | Mixed | 3+1 | Advanced features & compliance |

**Total: 18 issues across 5 waves**
