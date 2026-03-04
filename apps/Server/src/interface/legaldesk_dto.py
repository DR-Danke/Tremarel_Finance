"""Pydantic DTOs and enums for Legal Desk case management operations."""

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


# ============================================================================
# ENUMS
# ============================================================================


class CaseStatus(str, Enum):
    """Status lifecycle of a legal case."""

    NEW = "new"
    CLASSIFYING = "classifying"
    OPEN = "open"
    ASSIGNING = "assigning"
    ACTIVE = "active"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    NEGOTIATING = "negotiating"
    COMPLETED = "completed"
    CLOSED = "closed"
    ARCHIVED = "archived"


class CaseType(str, Enum):
    """Type of legal case."""

    ADVISORY = "advisory"
    LITIGATION = "litigation"


class LegalDomain(str, Enum):
    """Legal practice domain."""

    CORPORATE = "corporate"
    IP = "ip"
    LABOR = "labor"
    TAX = "tax"
    LITIGATION = "litigation"
    REAL_ESTATE = "real_estate"
    IMMIGRATION = "immigration"
    REGULATORY = "regulatory"
    DATA_PRIVACY = "data_privacy"
    COMMERCIAL = "commercial"


class CaseComplexity(str, Enum):
    """Complexity level of a legal case."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CasePriority(str, Enum):
    """Priority level of a legal case."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class OriginationChannel(str, Enum):
    """How a case was originated."""

    DIRECT = "direct"
    REFERRAL = "referral"


class SpecialistStatus(str, Enum):
    """Status of a legal specialist."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    ON_LEAVE = "on_leave"


class SpecialistType(str, Enum):
    """Type of legal specialist."""

    INDIVIDUAL = "individual"
    BOUTIQUE_FIRM = "boutique_firm"


class ProficiencyLevel(str, Enum):
    """Proficiency level in a legal domain."""

    JUNIOR = "junior"
    INTERMEDIATE = "intermediate"
    EXPERT = "expert"


class AssignmentRole(str, Enum):
    """Role of a specialist in a case assignment."""

    LEAD = "lead"
    SUPPORT = "support"
    REVIEWER = "reviewer"
    CONSULTANT = "consultant"


class AssignmentStatus(str, Enum):
    """Status of a specialist assignment."""

    PROPOSED = "proposed"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    ACTIVE = "active"
    COMPLETED = "completed"


class DeliverableStatus(str, Enum):
    """Status of a case deliverable."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PricingAction(str, Enum):
    """Action type in pricing negotiation."""

    PROPOSAL = "proposal"
    COUNTER = "counter"
    ACCEPT = "accept"
    REJECT = "reject"
    ADJUST = "adjust"
    FINAL = "final"


class ClientType(str, Enum):
    """Type of client entity."""

    COMPANY = "company"
    INDIVIDUAL = "individual"


# ============================================================================
# CASE STATUS TRANSITIONS
# ============================================================================

CASE_STATUS_TRANSITIONS: dict[str, list[str]] = {
    CaseStatus.NEW: [CaseStatus.CLASSIFYING, CaseStatus.OPEN, CaseStatus.CLOSED],
    CaseStatus.CLASSIFYING: [CaseStatus.OPEN, CaseStatus.CLOSED],
    CaseStatus.OPEN: [CaseStatus.ASSIGNING, CaseStatus.CLOSED],
    CaseStatus.ASSIGNING: [CaseStatus.ACTIVE, CaseStatus.OPEN, CaseStatus.CLOSED],
    CaseStatus.ACTIVE: [CaseStatus.IN_PROGRESS, CaseStatus.CLOSED],
    CaseStatus.IN_PROGRESS: [CaseStatus.REVIEW, CaseStatus.ACTIVE, CaseStatus.CLOSED],
    CaseStatus.REVIEW: [CaseStatus.NEGOTIATING, CaseStatus.IN_PROGRESS, CaseStatus.COMPLETED],
    CaseStatus.NEGOTIATING: [CaseStatus.REVIEW, CaseStatus.COMPLETED, CaseStatus.CLOSED],
    CaseStatus.COMPLETED: [CaseStatus.CLOSED, CaseStatus.ARCHIVED],
    CaseStatus.CLOSED: [CaseStatus.ARCHIVED],
    CaseStatus.ARCHIVED: [],
}


# ============================================================================
# CLIENT DTOs
# ============================================================================


class ClientCreateDTO(BaseModel):
    """DTO for creating a new client."""

    name: str = Field(..., min_length=1, max_length=255, description="Client name")
    client_type: ClientType = Field(ClientType.COMPANY, description="Client type")
    contact_email: Optional[str] = Field(None, max_length=255, description="Contact email")
    contact_phone: Optional[str] = Field(None, max_length=100, description="Contact phone")
    country: Optional[str] = Field(None, max_length=100, description="Client country")
    industry: Optional[str] = Field(None, max_length=100, description="Client industry")
    notes: Optional[str] = Field(None, description="Additional notes")


class ClientUpdateDTO(BaseModel):
    """DTO for updating an existing client (partial update)."""

    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Client name")
    client_type: Optional[ClientType] = Field(None, description="Client type")
    contact_email: Optional[str] = Field(None, max_length=255, description="Contact email")
    contact_phone: Optional[str] = Field(None, max_length=100, description="Contact phone")
    country: Optional[str] = Field(None, max_length=100, description="Client country")
    industry: Optional[str] = Field(None, max_length=100, description="Client industry")
    notes: Optional[str] = Field(None, description="Additional notes")
    is_active: Optional[bool] = Field(None, description="Active status")


class ClientResponseDTO(BaseModel):
    """DTO for client response."""

    id: int = Field(..., description="Client unique identifier")
    name: str = Field(..., description="Client name")
    client_type: str = Field(..., description="Client type")
    contact_email: Optional[str] = Field(None, description="Contact email")
    contact_phone: Optional[str] = Field(None, description="Contact phone")
    country: Optional[str] = Field(None, description="Client country")
    industry: Optional[str] = Field(None, description="Client industry")
    notes: Optional[str] = Field(None, description="Additional notes")
    is_active: bool = Field(..., description="Active status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    model_config = {"from_attributes": True}


# ============================================================================
# SPECIALIST DTOs
# ============================================================================


class ExpertiseDTO(BaseModel):
    """DTO for specialist expertise in a legal domain."""

    legal_domain: LegalDomain = Field(..., description="Legal domain")
    proficiency_level: ProficiencyLevel = Field(
        ProficiencyLevel.INTERMEDIATE, description="Proficiency level"
    )
    years_in_domain: int = Field(0, ge=0, description="Years of experience in this domain")


class JurisdictionDTO(BaseModel):
    """DTO for specialist jurisdiction coverage."""

    country: str = Field(..., min_length=1, max_length=100, description="Country")
    region: Optional[str] = Field(None, max_length=100, description="Region within country")
    is_primary: bool = Field(False, description="Whether this is the primary jurisdiction")


class SpecialistCreateDTO(BaseModel):
    """DTO for creating a new specialist."""

    full_name: str = Field(..., min_length=1, max_length=255, description="Specialist full name")
    email: str = Field(..., max_length=255, description="Specialist email")
    phone: Optional[str] = Field(None, max_length=100, description="Phone number")
    years_experience: int = Field(0, ge=0, description="Total years of experience")
    hourly_rate: Optional[Decimal] = Field(None, gt=0, description="Hourly rate")
    currency: str = Field("EUR", max_length=10, description="Currency code")
    max_concurrent_cases: int = Field(5, ge=1, description="Maximum concurrent cases")
    expertise: List[ExpertiseDTO] = Field(default_factory=list, description="Areas of expertise")
    jurisdictions: List[JurisdictionDTO] = Field(
        default_factory=list, description="Jurisdiction coverage"
    )


class SpecialistUpdateDTO(BaseModel):
    """DTO for updating an existing specialist (partial update)."""

    full_name: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Specialist full name"
    )
    email: Optional[str] = Field(None, max_length=255, description="Specialist email")
    phone: Optional[str] = Field(None, max_length=100, description="Phone number")
    years_experience: Optional[int] = Field(None, ge=0, description="Total years of experience")
    hourly_rate: Optional[Decimal] = Field(None, gt=0, description="Hourly rate")
    currency: Optional[str] = Field(None, max_length=10, description="Currency code")
    max_concurrent_cases: Optional[int] = Field(None, ge=1, description="Maximum concurrent cases")
    is_active: Optional[bool] = Field(None, description="Active status")
    expertise: Optional[List[ExpertiseDTO]] = Field(None, description="Areas of expertise")
    jurisdictions: Optional[List[JurisdictionDTO]] = Field(
        None, description="Jurisdiction coverage"
    )


class SpecialistResponseDTO(BaseModel):
    """DTO for specialist response."""

    id: int = Field(..., description="Specialist unique identifier")
    full_name: str = Field(..., description="Specialist full name")
    email: str = Field(..., description="Specialist email")
    phone: Optional[str] = Field(None, description="Phone number")
    years_experience: int = Field(..., description="Total years of experience")
    hourly_rate: Optional[Decimal] = Field(None, description="Hourly rate")
    currency: str = Field(..., description="Currency code")
    max_concurrent_cases: int = Field(..., description="Maximum concurrent cases")
    current_workload: int = Field(..., description="Current number of active cases")
    overall_score: Decimal = Field(..., description="Overall performance score")
    is_active: bool = Field(..., description="Active status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    model_config = {"from_attributes": True}


class SpecialistDetailDTO(BaseModel):
    """DTO for specialist detail with expertise and jurisdictions."""

    id: int = Field(..., description="Specialist unique identifier")
    full_name: str = Field(..., description="Specialist full name")
    email: str = Field(..., description="Specialist email")
    phone: Optional[str] = Field(None, description="Phone number")
    years_experience: int = Field(..., description="Total years of experience")
    hourly_rate: Optional[Decimal] = Field(None, description="Hourly rate")
    currency: str = Field(..., description="Currency code")
    max_concurrent_cases: int = Field(..., description="Maximum concurrent cases")
    current_workload: int = Field(..., description="Current number of active cases")
    overall_score: Decimal = Field(..., description="Overall performance score")
    is_active: bool = Field(..., description="Active status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    expertise: List[ExpertiseDTO] = Field(default_factory=list, description="Areas of expertise")
    jurisdictions: List[JurisdictionDTO] = Field(
        default_factory=list, description="Jurisdiction coverage"
    )

    model_config = {"from_attributes": True}


class SpecialistFilterDTO(BaseModel):
    """DTO for filtering specialists."""

    legal_domain: Optional[LegalDomain] = Field(None, description="Filter by legal domain")
    proficiency_level: Optional[ProficiencyLevel] = Field(
        None, description="Filter by proficiency level"
    )
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    min_experience: Optional[int] = Field(None, ge=0, description="Minimum years of experience")
    max_workload: Optional[int] = Field(None, ge=0, description="Maximum current workload")


# ============================================================================
# ASSIGNMENT DTOs (defined before CaseDetailDTO to avoid forward references)
# ============================================================================


class AssignmentCreateDTO(BaseModel):
    """DTO for creating a case-specialist assignment."""

    case_id: int = Field(..., description="Case identifier")
    specialist_id: int = Field(..., description="Specialist identifier")
    role: AssignmentRole = Field(AssignmentRole.LEAD, description="Assignment role")
    proposed_fee: Optional[Decimal] = Field(None, ge=0, description="Proposed fee")
    fee_currency: str = Field("EUR", max_length=10, description="Fee currency code")


class AssignmentResponseDTO(BaseModel):
    """DTO for assignment response."""

    id: int = Field(..., description="Assignment unique identifier")
    case_id: int = Field(..., description="Case identifier")
    specialist_id: int = Field(..., description="Specialist identifier")
    role: str = Field(..., description="Assignment role")
    status: str = Field(..., description="Assignment status")
    proposed_fee: Optional[Decimal] = Field(None, description="Proposed fee")
    agreed_fee: Optional[Decimal] = Field(None, description="Agreed fee")
    fee_currency: str = Field(..., description="Fee currency code")
    assigned_at: datetime = Field(..., description="Assignment timestamp")
    responded_at: Optional[datetime] = Field(None, description="Response timestamp")

    model_config = {"from_attributes": True}


# ============================================================================
# DELIVERABLE DTOs (defined before CaseDetailDTO to avoid forward references)
# ============================================================================


class DeliverableCreateDTO(BaseModel):
    """DTO for creating a case deliverable."""

    case_id: int = Field(..., description="Case identifier")
    title: str = Field(..., min_length=1, max_length=500, description="Deliverable title")
    specialist_id: Optional[int] = Field(None, description="Assigned specialist identifier")
    description: Optional[str] = Field(None, description="Deliverable description")
    due_date: Optional[date] = Field(None, description="Due date")


class DeliverableUpdateDTO(BaseModel):
    """DTO for updating a deliverable (partial update)."""

    title: Optional[str] = Field(None, min_length=1, max_length=500, description="Deliverable title")
    description: Optional[str] = Field(None, description="Deliverable description")
    status: Optional[DeliverableStatus] = Field(None, description="Deliverable status")
    due_date: Optional[date] = Field(None, description="Due date")
    specialist_id: Optional[int] = Field(None, description="Assigned specialist identifier")


class DeliverableResponseDTO(BaseModel):
    """DTO for deliverable response."""

    id: int = Field(..., description="Deliverable unique identifier")
    case_id: int = Field(..., description="Case identifier")
    specialist_id: Optional[int] = Field(None, description="Assigned specialist identifier")
    title: str = Field(..., description="Deliverable title")
    description: Optional[str] = Field(None, description="Deliverable description")
    status: str = Field(..., description="Deliverable status")
    due_date: Optional[date] = Field(None, description="Due date")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    model_config = {"from_attributes": True}


# ============================================================================
# CASE DTOs
# ============================================================================


class CaseCreateDTO(BaseModel):
    """DTO for creating a new legal case."""

    title: str = Field(..., min_length=1, max_length=500, description="Case title")
    client_id: int = Field(..., description="Client identifier")
    legal_domain: LegalDomain = Field(..., description="Legal domain")
    description: Optional[str] = Field(None, description="Case description")
    case_type: Optional[CaseType] = Field(None, description="Case type")
    complexity: CaseComplexity = Field(CaseComplexity.MEDIUM, description="Case complexity")
    priority: CasePriority = Field(CasePriority.MEDIUM, description="Case priority")
    budget: Optional[Decimal] = Field(None, ge=0, description="Case budget")
    deadline: Optional[date] = Field(None, description="Case deadline")


class CaseUpdateDTO(BaseModel):
    """DTO for updating a case (partial update)."""

    title: Optional[str] = Field(None, min_length=1, max_length=500, description="Case title")
    description: Optional[str] = Field(None, description="Case description")
    legal_domain: Optional[LegalDomain] = Field(None, description="Legal domain")
    case_type: Optional[CaseType] = Field(None, description="Case type")
    complexity: Optional[CaseComplexity] = Field(None, description="Case complexity")
    priority: Optional[CasePriority] = Field(None, description="Case priority")
    status: Optional[CaseStatus] = Field(None, description="Case status")
    budget: Optional[Decimal] = Field(None, ge=0, description="Case budget")
    estimated_cost: Optional[Decimal] = Field(None, ge=0, description="Estimated cost")
    final_quote: Optional[Decimal] = Field(None, ge=0, description="Final quote")
    margin_percentage: Optional[Decimal] = Field(None, description="Margin percentage")
    deadline: Optional[date] = Field(None, description="Case deadline")


class CaseResponseDTO(BaseModel):
    """DTO for case response."""

    id: int = Field(..., description="Case unique identifier")
    case_number: str = Field(..., description="Auto-generated case number")
    title: str = Field(..., description="Case title")
    description: Optional[str] = Field(None, description="Case description")
    client_id: int = Field(..., description="Client identifier")
    legal_domain: str = Field(..., description="Legal domain")
    complexity: str = Field(..., description="Case complexity")
    priority: str = Field(..., description="Case priority")
    status: str = Field(..., description="Case status")
    budget: Optional[Decimal] = Field(None, description="Case budget")
    estimated_cost: Optional[Decimal] = Field(None, description="Estimated cost")
    final_quote: Optional[Decimal] = Field(None, description="Final quote")
    margin_percentage: Optional[Decimal] = Field(None, description="Margin percentage")
    deadline: Optional[date] = Field(None, description="Case deadline")
    ai_classification: Optional[dict] = Field(None, description="AI classification result")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    model_config = {"from_attributes": True}


class CaseDetailDTO(BaseModel):
    """DTO for case detail with related entities."""

    id: int = Field(..., description="Case unique identifier")
    case_number: str = Field(..., description="Auto-generated case number")
    title: str = Field(..., description="Case title")
    description: Optional[str] = Field(None, description="Case description")
    client_id: int = Field(..., description="Client identifier")
    legal_domain: str = Field(..., description="Legal domain")
    complexity: str = Field(..., description="Case complexity")
    priority: str = Field(..., description="Case priority")
    status: str = Field(..., description="Case status")
    budget: Optional[Decimal] = Field(None, description="Case budget")
    estimated_cost: Optional[Decimal] = Field(None, description="Estimated cost")
    final_quote: Optional[Decimal] = Field(None, description="Final quote")
    margin_percentage: Optional[Decimal] = Field(None, description="Margin percentage")
    deadline: Optional[date] = Field(None, description="Case deadline")
    ai_classification: Optional[dict] = Field(None, description="AI classification result")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    client: Optional[ClientResponseDTO] = Field(None, description="Client details")
    specialists: List[AssignmentResponseDTO] = Field(
        default_factory=list, description="Assigned specialists"
    )
    deliverables: List[DeliverableResponseDTO] = Field(
        default_factory=list, description="Case deliverables"
    )

    model_config = {"from_attributes": True}


class CaseFilterDTO(BaseModel):
    """DTO for filtering cases."""

    status: Optional[CaseStatus] = Field(None, description="Filter by status")
    legal_domain: Optional[LegalDomain] = Field(None, description="Filter by legal domain")
    priority: Optional[CasePriority] = Field(None, description="Filter by priority")
    case_type: Optional[CaseType] = Field(None, description="Filter by case type")
    client_id: Optional[int] = Field(None, description="Filter by client")
    complexity: Optional[CaseComplexity] = Field(None, description="Filter by complexity")


class CaseListItemDTO(BaseModel):
    """Lightweight DTO for case list views."""

    id: int = Field(..., description="Case unique identifier")
    case_number: str = Field(..., description="Auto-generated case number")
    title: str = Field(..., description="Case title")
    client_id: int = Field(..., description="Client identifier")
    legal_domain: str = Field(..., description="Legal domain")
    priority: str = Field(..., description="Case priority")
    status: str = Field(..., description="Case status")
    deadline: Optional[date] = Field(None, description="Case deadline")
    created_at: datetime = Field(..., description="Creation timestamp")

    model_config = {"from_attributes": True}


# ============================================================================
# MESSAGE DTOs
# ============================================================================


class MessageCreateDTO(BaseModel):
    """DTO for creating a case message."""

    case_id: int = Field(..., description="Case identifier")
    message: str = Field(..., min_length=1, description="Message content")
    sender_type: str = Field("system", max_length=50, description="Sender type")
    sender_name: Optional[str] = Field(None, max_length=255, description="Sender name")
    is_internal: bool = Field(False, description="Whether this is an internal message")


class MessageResponseDTO(BaseModel):
    """DTO for message response."""

    id: int = Field(..., description="Message unique identifier")
    case_id: int = Field(..., description="Case identifier")
    sender_type: str = Field(..., description="Sender type")
    sender_name: Optional[str] = Field(None, description="Sender name")
    message: str = Field(..., description="Message content")
    is_internal: bool = Field(..., description="Whether this is an internal message")
    created_at: datetime = Field(..., description="Creation timestamp")

    model_config = {"from_attributes": True}


# ============================================================================
# DOCUMENT DTOs
# ============================================================================


class DocumentCreateDTO(BaseModel):
    """DTO for creating a case document."""

    case_id: int = Field(..., description="Case identifier")
    file_name: str = Field(..., min_length=1, max_length=500, description="File name")
    file_url: str = Field(..., min_length=1, max_length=1000, description="File URL")
    file_type: Optional[str] = Field(None, max_length=100, description="File MIME type")
    file_size_bytes: Optional[int] = Field(None, ge=0, description="File size in bytes")
    uploaded_by: Optional[str] = Field(None, max_length=255, description="Uploader identifier")


class DocumentResponseDTO(BaseModel):
    """DTO for document response."""

    id: int = Field(..., description="Document unique identifier")
    case_id: int = Field(..., description="Case identifier")
    file_name: str = Field(..., description="File name")
    file_url: str = Field(..., description="File URL")
    file_type: Optional[str] = Field(None, description="File MIME type")
    file_size_bytes: Optional[int] = Field(None, description="File size in bytes")
    uploaded_by: Optional[str] = Field(None, description="Uploader identifier")
    created_at: datetime = Field(..., description="Creation timestamp")

    model_config = {"from_attributes": True}


# ============================================================================
# PRICING DTOs
# ============================================================================


class PricingProposalDTO(BaseModel):
    """DTO for submitting a pricing action."""

    case_id: int = Field(..., description="Case identifier")
    action: PricingAction = Field(..., description="Pricing action type")
    new_amount: Decimal = Field(..., ge=0, description="New pricing amount")
    previous_amount: Optional[Decimal] = Field(None, ge=0, description="Previous amount")
    currency: str = Field("EUR", max_length=10, description="Currency code")
    changed_by: Optional[str] = Field(None, max_length=255, description="Who made the change")
    notes: Optional[str] = Field(None, description="Pricing notes")


class PricingHistoryResponseDTO(BaseModel):
    """DTO for pricing history response."""

    id: int = Field(..., description="Pricing history unique identifier")
    case_id: int = Field(..., description="Case identifier")
    action: str = Field(..., description="Pricing action type")
    previous_amount: Optional[Decimal] = Field(None, description="Previous amount")
    new_amount: Decimal = Field(..., description="New pricing amount")
    currency: str = Field(..., description="Currency code")
    changed_by: Optional[str] = Field(None, description="Who made the change")
    notes: Optional[str] = Field(None, description="Pricing notes")
    created_at: datetime = Field(..., description="Creation timestamp")

    model_config = {"from_attributes": True}


# ============================================================================
# SCORING DTOs
# ============================================================================


class ScoreSubmitDTO(BaseModel):
    """DTO for submitting specialist performance scores."""

    specialist_id: int = Field(..., description="Specialist identifier")
    case_id: int = Field(..., description="Case identifier")
    quality_score: Optional[Decimal] = Field(None, ge=0, le=5, description="Quality score (0-5)")
    teamwork_score: Optional[Decimal] = Field(None, ge=0, le=5, description="Teamwork score (0-5)")
    delivery_score: Optional[Decimal] = Field(None, ge=0, le=5, description="Delivery score (0-5)")
    satisfaction_score: Optional[Decimal] = Field(
        None, ge=0, le=5, description="Satisfaction score (0-5)"
    )
    overall_score: Optional[Decimal] = Field(None, ge=0, le=5, description="Overall score (0-5)")
    feedback: Optional[str] = Field(None, description="Written feedback")


class ScoreResponseDTO(BaseModel):
    """DTO for score response."""

    id: int = Field(..., description="Score unique identifier")
    specialist_id: int = Field(..., description="Specialist identifier")
    case_id: int = Field(..., description="Case identifier")
    quality_score: Optional[Decimal] = Field(None, description="Quality score")
    teamwork_score: Optional[Decimal] = Field(None, description="Teamwork score")
    delivery_score: Optional[Decimal] = Field(None, description="Delivery score")
    satisfaction_score: Optional[Decimal] = Field(None, description="Satisfaction score")
    overall_score: Optional[Decimal] = Field(None, description="Overall score")
    feedback: Optional[str] = Field(None, description="Written feedback")
    scored_at: datetime = Field(..., description="Scoring timestamp")

    model_config = {"from_attributes": True}


# ============================================================================
# ASSIGNMENT ENGINE DTOs (virtual — not mapped to database tables)
# ============================================================================


class SpecialistCandidateDTO(BaseModel):
    """DTO for assignment engine specialist candidate output."""

    specialist_id: int = Field(..., description="Specialist identifier")
    full_name: str = Field(..., description="Specialist full name")
    email: str = Field(..., description="Specialist email")
    match_score: Decimal = Field(..., ge=0, le=1, description="Match score (0-1)")
    hourly_rate: Optional[Decimal] = Field(None, description="Hourly rate")
    currency: str = Field("EUR", description="Currency code")
    current_workload: int = Field(..., description="Current number of active cases")
    max_concurrent_cases: int = Field(..., description="Maximum concurrent cases")
    expertise_match: List[str] = Field(default_factory=list, description="Matching expertise areas")
    jurisdiction_match: List[str] = Field(
        default_factory=list, description="Matching jurisdictions"
    )
    match_reasons: List[str] = Field(
        default_factory=list, description="Detailed scoring reasons"
    )


class SuggestionResponseDTO(BaseModel):
    """DTO for assignment engine suggestion response."""

    case_id: int = Field(..., description="Case identifier")
    legal_domain: str = Field(..., description="Case legal domain")
    candidates: List[SpecialistCandidateDTO] = Field(
        default_factory=list, description="Ranked specialist candidates"
    )
    generated_at: datetime = Field(..., description="Suggestion generation timestamp")


# ============================================================================
# CLASSIFICATION & ANALYTICS DTOs (virtual — not mapped to database tables)
# ============================================================================


class ClassificationResultDTO(BaseModel):
    """DTO for AI case classification result."""

    legal_domain: LegalDomain = Field(..., description="Classified legal domain")
    complexity: CaseComplexity = Field(..., description="Classified complexity")
    case_type: CaseType = Field(..., description="Classified case type")
    confidence: Decimal = Field(..., ge=0, le=1, description="Classification confidence (0-1)")
    suggested_tags: List[str] = Field(
        default_factory=list, description="AI-suggested tags"
    )


class DashboardStatsDTO(BaseModel):
    """DTO for analytics dashboard statistics."""

    total_cases: int = Field(..., description="Total number of cases")
    active_cases: int = Field(..., description="Number of active cases")
    completed_cases: int = Field(..., description="Number of completed cases")
    total_specialists: int = Field(..., description="Total number of specialists")
    avg_case_duration_days: Optional[Decimal] = Field(
        None, description="Average case duration in days"
    )
    total_revenue: Optional[Decimal] = Field(None, description="Total revenue")
    cases_by_status: dict[str, int] = Field(
        default_factory=dict, description="Case count by status"
    )
    cases_by_domain: dict[str, int] = Field(
        default_factory=dict, description="Case count by legal domain"
    )
    cases_by_priority: dict[str, int] = Field(
        default_factory=dict, description="Case count by priority"
    )
