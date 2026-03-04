"""Legal Desk API endpoint routes (~33 endpoints).

Covers cases, assignments, deliverables, messages, documents,
pricing negotiation, specialists, clients, and analytics dashboard.
All endpoints require JWT authentication.
"""

from decimal import Decimal
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.adapter.rest.dependencies import get_current_user, get_db
from src.core.services.ld_analytics_service import ld_analytics_service
from src.core.services.ld_assignment_service import ld_assignment_service
from src.core.services.ld_case_service import ld_case_service
from src.core.services.ld_classification_service import ld_classification_service
from src.core.services.ld_client_service import ld_client_service
from src.core.services.ld_pricing_service import ld_pricing_service
from src.core.services.ld_specialist_service import ld_specialist_service
from src.interface.legaldesk_dto import (
    AssignmentCreateDTO,
    AssignmentResponseDTO,
    CaseComplexity,
    CaseCreateDTO,
    CaseDetailDTO,
    CaseFilterDTO,
    CasePriority,
    CaseResponseDTO,
    CaseStatus,
    CaseType,
    CaseUpdateDTO,
    ClassificationResultDTO,
    ClientCreateDTO,
    ClientResponseDTO,
    ClientUpdateDTO,
    DashboardStatsDTO,
    DeliverableCreateDTO,
    DeliverableResponseDTO,
    DeliverableUpdateDTO,
    DocumentCreateDTO,
    DocumentResponseDTO,
    ExpertiseDTO,
    JurisdictionDTO,
    LegalDomain,
    MessageCreateDTO,
    MessageResponseDTO,
    PricingHistoryResponseDTO,
    ScoreResponseDTO,
    ScoreSubmitDTO,
    SpecialistCreateDTO,
    SpecialistDetailDTO,
    SpecialistResponseDTO,
    SpecialistUpdateDTO,
    SuggestionResponseDTO,
)
from src.repository.ld_deliverable_repository import ld_deliverable_repository
from src.repository.ld_document_repository import ld_document_repository
from src.repository.ld_message_repository import ld_message_repository

router = APIRouter(prefix="/api/legaldesk", tags=["Legal Desk"])


# ============================================================================
# Inline request bodies for endpoints that don't match existing DTOs directly
# ============================================================================


class StatusUpdateBody(BaseModel):
    """Body for status update endpoints."""
    status: str = Field(..., description="New status value")


class PricingProposeBody(BaseModel):
    """Body for pricing proposal."""
    specialist_cost: Decimal = Field(..., ge=0, description="Specialist cost")
    client_price: Decimal = Field(..., gt=0, description="Client-facing price")
    notes: Optional[str] = Field(None, description="Notes")


class PricingCounterBody(BaseModel):
    """Body for pricing counter-offer."""
    specialist_cost: Decimal = Field(..., ge=0, description="Revised specialist cost")
    client_price: Decimal = Field(..., gt=0, description="Revised client price")
    notes: Optional[str] = Field(None, description="Notes")


class PricingRejectBody(BaseModel):
    """Body for pricing rejection."""
    notes: Optional[str] = Field(None, description="Rejection reason")


class ExpertiseAddBody(BaseModel):
    """Body for adding expertise to a specialist."""
    legal_domain: str = Field(..., description="Legal domain")
    proficiency_level: str = Field("intermediate", description="Proficiency level")


class JurisdictionAddBody(BaseModel):
    """Body for adding jurisdiction to a specialist."""
    country: str = Field(..., description="Country")
    region: Optional[str] = Field(None, description="Region")
    is_primary: bool = Field(False, description="Primary jurisdiction flag")


# ============================================================================
# CASE ENDPOINTS (6)
# ============================================================================


@router.post("/cases", response_model=CaseResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_case(
    data: CaseCreateDTO,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CaseResponseDTO:
    """Create a new legal case."""
    print(f"INFO [LegalDeskRoutes]: Create case request from user {current_user['id']}")
    case = ld_case_service.create_case(db, data, current_user)
    print(f"INFO [LegalDeskRoutes]: Case {case.id} created")
    return CaseResponseDTO.model_validate(case)


@router.get("/cases", response_model=List[CaseResponseDTO])
async def list_cases(
    status_filter: Optional[CaseStatus] = Query(None, alias="status", description="Filter by status"),
    legal_domain: Optional[LegalDomain] = Query(None, description="Filter by legal domain"),
    priority: Optional[CasePriority] = Query(None, description="Filter by priority"),
    case_type: Optional[CaseType] = Query(None, description="Filter by case type"),
    client_id: Optional[int] = Query(None, description="Filter by client"),
    complexity: Optional[CaseComplexity] = Query(None, description="Filter by complexity"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[CaseResponseDTO]:
    """List cases with optional filters."""
    print(f"INFO [LegalDeskRoutes]: List cases request from user {current_user['id']}")
    filters = CaseFilterDTO(
        status=status_filter,
        legal_domain=legal_domain,
        priority=priority,
        case_type=case_type,
        client_id=client_id,
        complexity=complexity,
    )
    cases = ld_case_service.list_cases(db, filters)
    return [CaseResponseDTO.model_validate(c) for c in cases]


@router.get("/cases/{case_id}", response_model=CaseDetailDTO)
async def get_case_detail(
    case_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CaseDetailDTO:
    """Get case detail with related entities."""
    print(f"INFO [LegalDeskRoutes]: Get case {case_id} detail")
    case = ld_case_service.get_case_with_details(db, case_id)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    return CaseDetailDTO.model_validate(case)


@router.put("/cases/{case_id}", response_model=CaseResponseDTO)
async def update_case(
    case_id: int,
    data: CaseUpdateDTO,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CaseResponseDTO:
    """Update case fields."""
    print(f"INFO [LegalDeskRoutes]: Update case {case_id}")
    case = ld_case_service.update_case(db, case_id, data)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    return CaseResponseDTO.model_validate(case)


@router.patch("/cases/{case_id}/status", response_model=CaseResponseDTO)
async def update_case_status(
    case_id: int,
    body: StatusUpdateBody,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CaseResponseDTO:
    """Update case status with transition validation."""
    print(f"INFO [LegalDeskRoutes]: Update case {case_id} status to '{body.status}'")
    try:
        case = ld_case_service.update_case_status(db, case_id, body.status)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    return CaseResponseDTO.model_validate(case)


@router.post("/cases/{case_id}/classify", response_model=ClassificationResultDTO)
async def classify_case(
    case_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ClassificationResultDTO:
    """AI classify a case by domain, type, and complexity."""
    print(f"INFO [LegalDeskRoutes]: Classify case {case_id}")
    try:
        result = ld_classification_service.classify_case(db, case_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return result


# ============================================================================
# ASSIGNMENT ENDPOINTS (4)
# ============================================================================


@router.get("/cases/{case_id}/specialists", response_model=List[AssignmentResponseDTO])
async def get_case_specialists(
    case_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[AssignmentResponseDTO]:
    """Get all specialist assignments for a case."""
    print(f"INFO [LegalDeskRoutes]: Get specialists for case {case_id}")
    assignments = ld_assignment_service.get_case_specialists(db, case_id)
    return [AssignmentResponseDTO.model_validate(a) for a in assignments]


@router.post("/cases/{case_id}/specialists", response_model=AssignmentResponseDTO, status_code=status.HTTP_201_CREATED)
async def assign_specialist(
    case_id: int,
    data: AssignmentCreateDTO,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AssignmentResponseDTO:
    """Assign a specialist to a case."""
    print(f"INFO [LegalDeskRoutes]: Assign specialist to case {case_id}")
    data.case_id = case_id
    try:
        assignment = ld_assignment_service.assign_specialist(db, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return AssignmentResponseDTO.model_validate(assignment)


@router.get("/cases/{case_id}/specialists/suggest", response_model=SuggestionResponseDTO)
async def suggest_specialists(
    case_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SuggestionResponseDTO:
    """Suggest specialists for a case using the assignment engine."""
    print(f"INFO [LegalDeskRoutes]: Suggest specialists for case {case_id}")
    try:
        suggestions = ld_assignment_service.suggest_specialists(db, case_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return suggestions


@router.patch("/cases/{case_id}/specialists/{assignment_id}/status", response_model=AssignmentResponseDTO)
async def update_assignment_status(
    case_id: int,
    assignment_id: int,
    body: StatusUpdateBody,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AssignmentResponseDTO:
    """Update assignment status (e.g., accepted, rejected, completed)."""
    print(f"INFO [LegalDeskRoutes]: Update assignment {assignment_id} status to '{body.status}'")
    try:
        assignment = ld_assignment_service.update_assignment_status(db, assignment_id, body.status)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return AssignmentResponseDTO.model_validate(assignment)


# ============================================================================
# DELIVERABLE ENDPOINTS (4)
# ============================================================================


@router.get("/cases/{case_id}/deliverables", response_model=List[DeliverableResponseDTO])
async def list_deliverables(
    case_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[DeliverableResponseDTO]:
    """List deliverables for a case."""
    print(f"INFO [LegalDeskRoutes]: List deliverables for case {case_id}")
    deliverables = ld_deliverable_repository.get_by_case(db, case_id)
    return [DeliverableResponseDTO.model_validate(d) for d in deliverables]


@router.post("/cases/{case_id}/deliverables", response_model=DeliverableResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_deliverable(
    case_id: int,
    data: DeliverableCreateDTO,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DeliverableResponseDTO:
    """Create a deliverable for a case."""
    print(f"INFO [LegalDeskRoutes]: Create deliverable for case {case_id}")
    data.case_id = case_id
    deliverable = ld_deliverable_repository.create(db, data.model_dump())
    return DeliverableResponseDTO.model_validate(deliverable)


@router.put("/cases/{case_id}/deliverables/{deliverable_id}", response_model=DeliverableResponseDTO)
async def update_deliverable(
    case_id: int,
    deliverable_id: int,
    data: DeliverableUpdateDTO,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DeliverableResponseDTO:
    """Update a deliverable."""
    print(f"INFO [LegalDeskRoutes]: Update deliverable {deliverable_id} for case {case_id}")
    updated = ld_deliverable_repository.update(db, deliverable_id, data.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deliverable not found")
    return DeliverableResponseDTO.model_validate(updated)


@router.patch("/cases/{case_id}/deliverables/{deliverable_id}/status", response_model=DeliverableResponseDTO)
async def update_deliverable_status(
    case_id: int,
    deliverable_id: int,
    body: StatusUpdateBody,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DeliverableResponseDTO:
    """Update deliverable status."""
    print(f"INFO [LegalDeskRoutes]: Update deliverable {deliverable_id} status to '{body.status}'")
    updated = ld_deliverable_repository.update_status(db, deliverable_id, body.status)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deliverable not found")
    return DeliverableResponseDTO.model_validate(updated)


# ============================================================================
# MESSAGE ENDPOINTS (2)
# ============================================================================


@router.get("/cases/{case_id}/messages", response_model=List[MessageResponseDTO])
async def get_messages(
    case_id: int,
    include_internal: bool = Query(False, description="Include internal messages"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[MessageResponseDTO]:
    """Get messages for a case."""
    print(f"INFO [LegalDeskRoutes]: Get messages for case {case_id}, include_internal={include_internal}")
    messages = ld_message_repository.get_by_case(db, case_id, include_internal=include_internal)
    return [MessageResponseDTO.model_validate(m) for m in messages]


@router.post("/cases/{case_id}/messages", response_model=MessageResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_message(
    case_id: int,
    data: MessageCreateDTO,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MessageResponseDTO:
    """Create a message on a case."""
    print(f"INFO [LegalDeskRoutes]: Create message for case {case_id}")
    msg_data = data.model_dump()
    msg_data["case_id"] = case_id
    message = ld_message_repository.create(db, msg_data)
    return MessageResponseDTO.model_validate(message)


# ============================================================================
# DOCUMENT ENDPOINTS (2)
# ============================================================================


@router.get("/cases/{case_id}/documents", response_model=List[DocumentResponseDTO])
async def list_documents(
    case_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[DocumentResponseDTO]:
    """List documents for a case."""
    print(f"INFO [LegalDeskRoutes]: List documents for case {case_id}")
    documents = ld_document_repository.get_by_case(db, case_id)
    return [DocumentResponseDTO.model_validate(d) for d in documents]


@router.post("/cases/{case_id}/documents", response_model=DocumentResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_document(
    case_id: int,
    data: DocumentCreateDTO,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DocumentResponseDTO:
    """Add document metadata to a case."""
    print(f"INFO [LegalDeskRoutes]: Add document to case {case_id}")
    doc_data = data.model_dump()
    doc_data["case_id"] = case_id
    document = ld_document_repository.create(db, doc_data)
    return DocumentResponseDTO.model_validate(document)


# ============================================================================
# PRICING ENDPOINTS (5)
# ============================================================================


@router.get("/cases/{case_id}/pricing", response_model=List[PricingHistoryResponseDTO])
async def get_pricing_history(
    case_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[PricingHistoryResponseDTO]:
    """Get pricing history for a case."""
    print(f"INFO [LegalDeskRoutes]: Get pricing history for case {case_id}")
    return ld_pricing_service.get_pricing_history(db, case_id)


@router.post("/cases/{case_id}/pricing/propose", response_model=PricingHistoryResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_pricing_proposal(
    case_id: int,
    body: PricingProposeBody,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PricingHistoryResponseDTO:
    """Create a pricing proposal for a case."""
    print(f"INFO [LegalDeskRoutes]: Create pricing proposal for case {case_id}")
    try:
        entry = ld_pricing_service.create_proposal(
            db, case_id, body.specialist_cost, body.client_price,
            notes=body.notes, created_by=current_user.get("email"),
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return PricingHistoryResponseDTO.model_validate(entry)


@router.post("/cases/{case_id}/pricing/counter", response_model=PricingHistoryResponseDTO, status_code=status.HTTP_201_CREATED)
async def submit_counter_offer(
    case_id: int,
    body: PricingCounterBody,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PricingHistoryResponseDTO:
    """Submit a counter-offer for a case."""
    print(f"INFO [LegalDeskRoutes]: Submit counter-offer for case {case_id}")
    try:
        entry = ld_pricing_service.submit_counter(
            db, case_id, body.specialist_cost, body.client_price,
            notes=body.notes, created_by=current_user.get("email"),
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return PricingHistoryResponseDTO.model_validate(entry)


@router.post("/cases/{case_id}/pricing/accept", response_model=PricingHistoryResponseDTO)
async def accept_pricing(
    case_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PricingHistoryResponseDTO:
    """Accept current pricing for a case."""
    print(f"INFO [LegalDeskRoutes]: Accept pricing for case {case_id}")
    try:
        entry = ld_pricing_service.accept_pricing(
            db, case_id, created_by=current_user.get("email"),
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return PricingHistoryResponseDTO.model_validate(entry)


@router.post("/cases/{case_id}/pricing/reject", response_model=PricingHistoryResponseDTO)
async def reject_pricing(
    case_id: int,
    body: PricingRejectBody,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PricingHistoryResponseDTO:
    """Reject pricing for a case."""
    print(f"INFO [LegalDeskRoutes]: Reject pricing for case {case_id}")
    try:
        entry = ld_pricing_service.reject_pricing(
            db, case_id, notes=body.notes, created_by=current_user.get("email"),
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return PricingHistoryResponseDTO.model_validate(entry)


# ============================================================================
# SPECIALIST ENDPOINTS (7)
# ============================================================================


@router.get("/specialists", response_model=List[SpecialistResponseDTO])
async def list_specialists(
    legal_domain: Optional[str] = Query(None, description="Filter by legal domain"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    min_experience: Optional[int] = Query(None, ge=0, description="Minimum years of experience"),
    max_workload: Optional[int] = Query(None, ge=0, description="Maximum current workload"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[SpecialistResponseDTO]:
    """List all specialists with optional filters."""
    print("INFO [LegalDeskRoutes]: List specialists")
    filters: Optional[dict] = None
    filter_params = {
        "legal_domain": legal_domain,
        "is_active": is_active,
        "min_experience": min_experience,
        "max_workload": max_workload,
    }
    active_filters = {k: v for k, v in filter_params.items() if v is not None}
    if active_filters:
        filters = active_filters
    specialists = ld_specialist_service.list_all(db, filters)
    return [SpecialistResponseDTO.model_validate(s) for s in specialists]


@router.post("/specialists", response_model=SpecialistResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_specialist(
    data: SpecialistCreateDTO,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SpecialistResponseDTO:
    """Create a new specialist."""
    print(f"INFO [LegalDeskRoutes]: Create specialist '{data.full_name}'")
    specialist = ld_specialist_service.create(db, data)
    return SpecialistResponseDTO.model_validate(specialist)


@router.get("/specialists/{specialist_id}", response_model=SpecialistDetailDTO)
async def get_specialist_detail(
    specialist_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SpecialistDetailDTO:
    """Get specialist detail with expertise and jurisdictions."""
    print(f"INFO [LegalDeskRoutes]: Get specialist {specialist_id} detail")
    specialist = ld_specialist_service.get_specialist_detail(db, specialist_id)
    if not specialist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Specialist not found")
    return SpecialistDetailDTO.model_validate(specialist)


@router.put("/specialists/{specialist_id}", response_model=SpecialistResponseDTO)
async def update_specialist(
    specialist_id: int,
    data: SpecialistUpdateDTO,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SpecialistResponseDTO:
    """Update specialist fields."""
    print(f"INFO [LegalDeskRoutes]: Update specialist {specialist_id}")
    specialist = ld_specialist_service.update(db, specialist_id, data)
    if not specialist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Specialist not found")
    return SpecialistResponseDTO.model_validate(specialist)


@router.post("/specialists/{specialist_id}/expertise", response_model=ExpertiseDTO, status_code=status.HTTP_201_CREATED)
async def add_expertise(
    specialist_id: int,
    body: ExpertiseAddBody,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ExpertiseDTO:
    """Add expertise to a specialist."""
    print(f"INFO [LegalDeskRoutes]: Add expertise '{body.legal_domain}' to specialist {specialist_id}")
    expertise = ld_specialist_service.add_expertise(
        db, specialist_id, body.legal_domain, body.proficiency_level,
    )
    return ExpertiseDTO(
        legal_domain=expertise.legal_domain,
        proficiency_level=expertise.proficiency_level,
        years_in_domain=expertise.years_in_domain or 0,
    )


@router.post("/specialists/{specialist_id}/jurisdictions", response_model=JurisdictionDTO, status_code=status.HTTP_201_CREATED)
async def add_jurisdiction(
    specialist_id: int,
    body: JurisdictionAddBody,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> JurisdictionDTO:
    """Add jurisdiction to a specialist."""
    print(f"INFO [LegalDeskRoutes]: Add jurisdiction '{body.country}' to specialist {specialist_id}")
    jurisdiction = ld_specialist_service.add_jurisdiction(
        db, specialist_id, body.country, body.region, body.is_primary,
    )
    return JurisdictionDTO(
        country=jurisdiction.country,
        region=jurisdiction.region,
        is_primary=jurisdiction.is_primary,
    )


@router.post("/specialists/{specialist_id}/scores", response_model=ScoreResponseDTO, status_code=status.HTTP_201_CREATED)
async def submit_score(
    specialist_id: int,
    data: ScoreSubmitDTO,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ScoreResponseDTO:
    """Submit performance score for a specialist on a case."""
    print(f"INFO [LegalDeskRoutes]: Submit score for specialist {specialist_id}")
    data.specialist_id = specialist_id
    score = ld_specialist_service.submit_score(db, specialist_id, data.case_id, data)
    return ScoreResponseDTO.model_validate(score)


# ============================================================================
# CLIENT ENDPOINTS (4)
# ============================================================================


@router.get("/clients", response_model=List[ClientResponseDTO])
async def list_clients(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[ClientResponseDTO]:
    """List all clients."""
    print("INFO [LegalDeskRoutes]: List clients")
    clients = ld_client_service.list_all(db)
    return [ClientResponseDTO.model_validate(c) for c in clients]


@router.post("/clients", response_model=ClientResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_client(
    data: ClientCreateDTO,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ClientResponseDTO:
    """Create a new client."""
    print(f"INFO [LegalDeskRoutes]: Create client '{data.name}'")
    client = ld_client_service.create(db, data)
    return ClientResponseDTO.model_validate(client)


@router.get("/clients/{client_id}", response_model=ClientResponseDTO)
async def get_client(
    client_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ClientResponseDTO:
    """Get client by ID."""
    print(f"INFO [LegalDeskRoutes]: Get client {client_id}")
    client = ld_client_service.get(db, client_id)
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    return ClientResponseDTO.model_validate(client)


@router.put("/clients/{client_id}", response_model=ClientResponseDTO)
async def update_client(
    client_id: int,
    data: ClientUpdateDTO,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ClientResponseDTO:
    """Update client fields."""
    print(f"INFO [LegalDeskRoutes]: Update client {client_id}")
    client = ld_client_service.update(db, client_id, data)
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    return ClientResponseDTO.model_validate(client)


# ============================================================================
# ANALYTICS ENDPOINT (1)
# ============================================================================


@router.get("/analytics/dashboard", response_model=DashboardStatsDTO)
async def get_dashboard_stats(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DashboardStatsDTO:
    """Get dashboard analytics statistics."""
    print("INFO [LegalDeskRoutes]: Get dashboard stats")
    return ld_analytics_service.get_dashboard_stats(db)
