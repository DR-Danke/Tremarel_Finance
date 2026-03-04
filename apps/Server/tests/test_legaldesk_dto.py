"""Tests for Legal Desk DTOs and enums."""

from datetime import date, datetime
from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError

from src.interface.legaldesk_dto import (
    CASE_STATUS_TRANSITIONS,
    AssignmentCreateDTO,
    AssignmentResponseDTO,
    AssignmentRole,
    AssignmentStatus,
    CaseComplexity,
    CaseCreateDTO,
    CaseDetailDTO,
    CaseFilterDTO,
    CaseListItemDTO,
    CasePriority,
    CaseResponseDTO,
    CaseStatus,
    CaseType,
    CaseUpdateDTO,
    ClassificationResultDTO,
    ClientCreateDTO,
    ClientResponseDTO,
    ClientType,
    ClientUpdateDTO,
    DashboardStatsDTO,
    DeliverableCreateDTO,
    DeliverableResponseDTO,
    DeliverableStatus,
    DeliverableUpdateDTO,
    DocumentCreateDTO,
    DocumentResponseDTO,
    ExpertiseDTO,
    JurisdictionDTO,
    LegalDomain,
    MessageCreateDTO,
    MessageResponseDTO,
    OriginationChannel,
    PricingAction,
    PricingHistoryResponseDTO,
    PricingProposalDTO,
    ProficiencyLevel,
    ScoreResponseDTO,
    ScoreSubmitDTO,
    SpecialistCandidateDTO,
    SpecialistCreateDTO,
    SpecialistDetailDTO,
    SpecialistFilterDTO,
    SpecialistResponseDTO,
    SpecialistStatus,
    SpecialistType,
    SpecialistUpdateDTO,
    SuggestionResponseDTO,
)


# ============================================================================
# Enum Tests
# ============================================================================


class TestCaseStatusEnum:
    """Tests for CaseStatus enum."""

    def test_member_count(self) -> None:
        assert len(CaseStatus) == 11
        print("INFO [TestLegalDeskDTO]: CaseStatus member count - PASSED")

    def test_values(self) -> None:
        assert CaseStatus.NEW == "new"
        assert CaseStatus.CLASSIFYING == "classifying"
        assert CaseStatus.OPEN == "open"
        assert CaseStatus.ASSIGNING == "assigning"
        assert CaseStatus.ACTIVE == "active"
        assert CaseStatus.IN_PROGRESS == "in_progress"
        assert CaseStatus.REVIEW == "review"
        assert CaseStatus.NEGOTIATING == "negotiating"
        assert CaseStatus.COMPLETED == "completed"
        assert CaseStatus.CLOSED == "closed"
        assert CaseStatus.ARCHIVED == "archived"
        print("INFO [TestLegalDeskDTO]: CaseStatus values - PASSED")

    def test_str_inheritance(self) -> None:
        assert isinstance(CaseStatus.NEW, str)
        print("INFO [TestLegalDeskDTO]: CaseStatus str inheritance - PASSED")


class TestCaseTypeEnum:
    def test_member_count(self) -> None:
        assert len(CaseType) == 2

    def test_values(self) -> None:
        assert CaseType.ADVISORY == "advisory"
        assert CaseType.LITIGATION == "litigation"


class TestLegalDomainEnum:
    def test_member_count(self) -> None:
        assert len(LegalDomain) == 10

    def test_values(self) -> None:
        assert LegalDomain.CORPORATE == "corporate"
        assert LegalDomain.IP == "ip"
        assert LegalDomain.LABOR == "labor"
        assert LegalDomain.TAX == "tax"
        assert LegalDomain.LITIGATION == "litigation"
        assert LegalDomain.REAL_ESTATE == "real_estate"
        assert LegalDomain.IMMIGRATION == "immigration"
        assert LegalDomain.REGULATORY == "regulatory"
        assert LegalDomain.DATA_PRIVACY == "data_privacy"
        assert LegalDomain.COMMERCIAL == "commercial"


class TestCaseComplexityEnum:
    def test_member_count(self) -> None:
        assert len(CaseComplexity) == 4

    def test_values(self) -> None:
        assert CaseComplexity.LOW == "low"
        assert CaseComplexity.MEDIUM == "medium"
        assert CaseComplexity.HIGH == "high"
        assert CaseComplexity.CRITICAL == "critical"


class TestCasePriorityEnum:
    def test_member_count(self) -> None:
        assert len(CasePriority) == 4

    def test_values(self) -> None:
        assert CasePriority.LOW == "low"
        assert CasePriority.MEDIUM == "medium"
        assert CasePriority.HIGH == "high"
        assert CasePriority.URGENT == "urgent"


class TestOriginationChannelEnum:
    def test_member_count(self) -> None:
        assert len(OriginationChannel) == 2

    def test_values(self) -> None:
        assert OriginationChannel.DIRECT == "direct"
        assert OriginationChannel.REFERRAL == "referral"


class TestSpecialistStatusEnum:
    def test_member_count(self) -> None:
        assert len(SpecialistStatus) == 3

    def test_values(self) -> None:
        assert SpecialistStatus.ACTIVE == "active"
        assert SpecialistStatus.INACTIVE == "inactive"
        assert SpecialistStatus.ON_LEAVE == "on_leave"


class TestSpecialistTypeEnum:
    def test_member_count(self) -> None:
        assert len(SpecialistType) == 2

    def test_values(self) -> None:
        assert SpecialistType.INDIVIDUAL == "individual"
        assert SpecialistType.BOUTIQUE_FIRM == "boutique_firm"


class TestProficiencyLevelEnum:
    def test_member_count(self) -> None:
        assert len(ProficiencyLevel) == 3

    def test_values(self) -> None:
        assert ProficiencyLevel.JUNIOR == "junior"
        assert ProficiencyLevel.INTERMEDIATE == "intermediate"
        assert ProficiencyLevel.EXPERT == "expert"


class TestAssignmentRoleEnum:
    def test_member_count(self) -> None:
        assert len(AssignmentRole) == 4

    def test_values(self) -> None:
        assert AssignmentRole.LEAD == "lead"
        assert AssignmentRole.SUPPORT == "support"
        assert AssignmentRole.REVIEWER == "reviewer"
        assert AssignmentRole.CONSULTANT == "consultant"


class TestAssignmentStatusEnum:
    def test_member_count(self) -> None:
        assert len(AssignmentStatus) == 5

    def test_values(self) -> None:
        assert AssignmentStatus.PROPOSED == "proposed"
        assert AssignmentStatus.ACCEPTED == "accepted"
        assert AssignmentStatus.REJECTED == "rejected"
        assert AssignmentStatus.ACTIVE == "active"
        assert AssignmentStatus.COMPLETED == "completed"


class TestDeliverableStatusEnum:
    def test_member_count(self) -> None:
        assert len(DeliverableStatus) == 5

    def test_values(self) -> None:
        assert DeliverableStatus.PENDING == "pending"
        assert DeliverableStatus.IN_PROGRESS == "in_progress"
        assert DeliverableStatus.REVIEW == "review"
        assert DeliverableStatus.COMPLETED == "completed"
        assert DeliverableStatus.CANCELLED == "cancelled"


class TestPricingActionEnum:
    def test_member_count(self) -> None:
        assert len(PricingAction) == 6

    def test_values(self) -> None:
        assert PricingAction.PROPOSAL == "proposal"
        assert PricingAction.COUNTER == "counter"
        assert PricingAction.ACCEPT == "accept"
        assert PricingAction.REJECT == "reject"
        assert PricingAction.ADJUST == "adjust"
        assert PricingAction.FINAL == "final"


class TestClientTypeEnum:
    def test_member_count(self) -> None:
        assert len(ClientType) == 2

    def test_values(self) -> None:
        assert ClientType.COMPANY == "company"
        assert ClientType.INDIVIDUAL == "individual"


# ============================================================================
# Case Status Transitions Tests
# ============================================================================


class TestCaseStatusTransitions:
    def test_all_statuses_have_entries(self) -> None:
        for status in CaseStatus:
            assert status.value in CASE_STATUS_TRANSITIONS, (
                f"Missing transition entry for {status.value}"
            )
        print("INFO [TestLegalDeskDTO]: All statuses have transition entries - PASSED")

    def test_archived_has_empty_list(self) -> None:
        assert CASE_STATUS_TRANSITIONS[CaseStatus.ARCHIVED] == []
        print("INFO [TestLegalDeskDTO]: Archived has empty transitions - PASSED")

    def test_new_transitions(self) -> None:
        transitions = CASE_STATUS_TRANSITIONS[CaseStatus.NEW]
        assert CaseStatus.CLASSIFYING in transitions
        assert CaseStatus.OPEN in transitions
        assert CaseStatus.CLOSED in transitions

    def test_completed_transitions(self) -> None:
        transitions = CASE_STATUS_TRANSITIONS[CaseStatus.COMPLETED]
        assert CaseStatus.CLOSED in transitions
        assert CaseStatus.ARCHIVED in transitions

    def test_all_transition_targets_are_valid(self) -> None:
        valid_values = {s.value for s in CaseStatus}
        for source, targets in CASE_STATUS_TRANSITIONS.items():
            for target in targets:
                assert target in valid_values or target in CaseStatus.__members__.values(), (
                    f"Invalid transition target '{target}' from '{source}'"
                )
        print("INFO [TestLegalDeskDTO]: All transition targets valid - PASSED")


# ============================================================================
# Client DTO Tests
# ============================================================================


class TestClientCreateDTO:
    def test_all_fields(self) -> None:
        dto = ClientCreateDTO(
            name="Acme Corp",
            client_type=ClientType.COMPANY,
            contact_email="contact@acme.com",
            contact_phone="+34 612 345 678",
            country="Spain",
            industry="Technology",
            notes="Important client",
        )
        assert dto.name == "Acme Corp"
        assert dto.client_type == ClientType.COMPANY
        assert dto.contact_email == "contact@acme.com"
        print("INFO [TestLegalDeskDTO]: ClientCreateDTO all fields - PASSED")

    def test_required_only(self) -> None:
        dto = ClientCreateDTO(name="Simple Client")
        assert dto.name == "Simple Client"
        assert dto.client_type == ClientType.COMPANY
        assert dto.contact_email is None
        assert dto.notes is None
        print("INFO [TestLegalDeskDTO]: ClientCreateDTO required only - PASSED")

    def test_empty_name_rejected(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            ClientCreateDTO(name="")
        assert "name" in str(exc_info.value)
        print("INFO [TestLegalDeskDTO]: ClientCreateDTO empty name rejected - PASSED")

    def test_name_max_length(self) -> None:
        dto = ClientCreateDTO(name="A" * 255)
        assert len(dto.name) == 255

    def test_name_over_max_length_rejected(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            ClientCreateDTO(name="A" * 256)
        assert "name" in str(exc_info.value)

    def test_individual_type(self) -> None:
        dto = ClientCreateDTO(name="John Doe", client_type=ClientType.INDIVIDUAL)
        assert dto.client_type == ClientType.INDIVIDUAL


class TestClientUpdateDTO:
    def test_partial_update(self) -> None:
        dto = ClientUpdateDTO(name="Updated Name")
        assert dto.name == "Updated Name"
        assert dto.client_type is None
        assert dto.contact_email is None

    def test_all_none(self) -> None:
        dto = ClientUpdateDTO()
        assert dto.name is None
        assert dto.is_active is None


class TestClientResponseDTO:
    def test_from_dict(self) -> None:
        dto = ClientResponseDTO(
            id=1,
            name="Test Client",
            client_type="company",
            is_active=True,
            created_at=datetime(2026, 1, 1, 12, 0, 0),
        )
        assert dto.id == 1
        assert dto.name == "Test Client"
        print("INFO [TestLegalDeskDTO]: ClientResponseDTO from dict - PASSED")

    def test_from_attributes(self) -> None:
        mock = MagicMock()
        mock.id = 1
        mock.name = "Mock Client"
        mock.client_type = "company"
        mock.contact_email = "mock@test.com"
        mock.contact_phone = None
        mock.country = "Spain"
        mock.industry = None
        mock.notes = None
        mock.is_active = True
        mock.created_at = datetime(2026, 1, 1)
        mock.updated_at = None
        dto = ClientResponseDTO.model_validate(mock, from_attributes=True)
        assert dto.id == 1
        assert dto.name == "Mock Client"
        print("INFO [TestLegalDeskDTO]: ClientResponseDTO from_attributes - PASSED")


# ============================================================================
# Specialist DTO Tests
# ============================================================================


class TestExpertiseDTO:
    def test_defaults(self) -> None:
        dto = ExpertiseDTO(legal_domain=LegalDomain.CORPORATE)
        assert dto.proficiency_level == ProficiencyLevel.INTERMEDIATE
        assert dto.years_in_domain == 0

    def test_all_fields(self) -> None:
        dto = ExpertiseDTO(
            legal_domain=LegalDomain.IP,
            proficiency_level=ProficiencyLevel.EXPERT,
            years_in_domain=15,
        )
        assert dto.legal_domain == LegalDomain.IP
        assert dto.years_in_domain == 15

    def test_negative_years_rejected(self) -> None:
        with pytest.raises(ValidationError):
            ExpertiseDTO(legal_domain=LegalDomain.TAX, years_in_domain=-1)


class TestJurisdictionDTO:
    def test_required_only(self) -> None:
        dto = JurisdictionDTO(country="Spain")
        assert dto.country == "Spain"
        assert dto.region is None
        assert dto.is_primary is False

    def test_all_fields(self) -> None:
        dto = JurisdictionDTO(country="Spain", region="Catalonia", is_primary=True)
        assert dto.is_primary is True

    def test_empty_country_rejected(self) -> None:
        with pytest.raises(ValidationError):
            JurisdictionDTO(country="")


class TestSpecialistCreateDTO:
    def test_all_fields(self) -> None:
        dto = SpecialistCreateDTO(
            full_name="Jane Smith",
            email="jane@law.com",
            phone="+34 600 000 000",
            years_experience=10,
            hourly_rate=Decimal("150.00"),
            currency="EUR",
            max_concurrent_cases=3,
            expertise=[ExpertiseDTO(legal_domain=LegalDomain.CORPORATE)],
            jurisdictions=[JurisdictionDTO(country="Spain", is_primary=True)],
        )
        assert dto.full_name == "Jane Smith"
        assert dto.hourly_rate == Decimal("150.00")
        assert len(dto.expertise) == 1
        assert len(dto.jurisdictions) == 1
        print("INFO [TestLegalDeskDTO]: SpecialistCreateDTO all fields - PASSED")

    def test_required_only(self) -> None:
        dto = SpecialistCreateDTO(full_name="Minimal Specialist", email="min@law.com")
        assert dto.years_experience == 0
        assert dto.currency == "EUR"
        assert dto.max_concurrent_cases == 5
        assert dto.expertise == []
        assert dto.jurisdictions == []

    def test_empty_name_rejected(self) -> None:
        with pytest.raises(ValidationError):
            SpecialistCreateDTO(full_name="", email="test@law.com")

    def test_negative_experience_rejected(self) -> None:
        with pytest.raises(ValidationError):
            SpecialistCreateDTO(
                full_name="Test", email="test@law.com", years_experience=-1
            )

    def test_zero_max_cases_rejected(self) -> None:
        with pytest.raises(ValidationError):
            SpecialistCreateDTO(
                full_name="Test", email="test@law.com", max_concurrent_cases=0
            )

    def test_zero_hourly_rate_rejected(self) -> None:
        with pytest.raises(ValidationError):
            SpecialistCreateDTO(
                full_name="Test", email="test@law.com", hourly_rate=Decimal("0")
            )


class TestSpecialistUpdateDTO:
    def test_partial_update(self) -> None:
        dto = SpecialistUpdateDTO(full_name="Updated Name")
        assert dto.full_name == "Updated Name"
        assert dto.email is None

    def test_all_none(self) -> None:
        dto = SpecialistUpdateDTO()
        assert dto.full_name is None
        assert dto.is_active is None


class TestSpecialistResponseDTO:
    def test_from_attributes(self) -> None:
        mock = MagicMock()
        mock.id = 1
        mock.full_name = "Jane Smith"
        mock.email = "jane@law.com"
        mock.phone = None
        mock.years_experience = 10
        mock.hourly_rate = Decimal("150.00")
        mock.currency = "EUR"
        mock.max_concurrent_cases = 5
        mock.current_workload = 2
        mock.overall_score = Decimal("4.50")
        mock.is_active = True
        mock.created_at = datetime(2026, 1, 1)
        mock.updated_at = None
        dto = SpecialistResponseDTO.model_validate(mock, from_attributes=True)
        assert dto.id == 1
        assert dto.overall_score == Decimal("4.50")
        print("INFO [TestLegalDeskDTO]: SpecialistResponseDTO from_attributes - PASSED")


class TestSpecialistDetailDTO:
    def test_with_expertise_and_jurisdictions(self) -> None:
        dto = SpecialistDetailDTO(
            id=1,
            full_name="Detail Specialist",
            email="detail@law.com",
            years_experience=5,
            currency="EUR",
            max_concurrent_cases=5,
            current_workload=1,
            overall_score=Decimal("3.50"),
            is_active=True,
            created_at=datetime(2026, 1, 1),
            expertise=[
                ExpertiseDTO(legal_domain=LegalDomain.CORPORATE, proficiency_level=ProficiencyLevel.EXPERT),
            ],
            jurisdictions=[
                JurisdictionDTO(country="Spain", is_primary=True),
            ],
        )
        assert len(dto.expertise) == 1
        assert len(dto.jurisdictions) == 1
        assert dto.expertise[0].legal_domain == LegalDomain.CORPORATE


class TestSpecialistFilterDTO:
    def test_all_none(self) -> None:
        dto = SpecialistFilterDTO()
        assert dto.legal_domain is None
        assert dto.is_active is None
        assert dto.min_experience is None

    def test_with_filters(self) -> None:
        dto = SpecialistFilterDTO(
            legal_domain=LegalDomain.TAX,
            is_active=True,
            min_experience=5,
        )
        assert dto.legal_domain == LegalDomain.TAX
        assert dto.min_experience == 5


# ============================================================================
# Case DTO Tests
# ============================================================================


class TestCaseCreateDTO:
    def test_all_fields(self) -> None:
        dto = CaseCreateDTO(
            title="Corporate merger review",
            client_id=1,
            legal_domain=LegalDomain.CORPORATE,
            description="Review of merger documents",
            case_type=CaseType.ADVISORY,
            complexity=CaseComplexity.HIGH,
            priority=CasePriority.URGENT,
            budget=Decimal("50000.00"),
            deadline=date(2026, 12, 31),
        )
        assert dto.title == "Corporate merger review"
        assert dto.legal_domain == LegalDomain.CORPORATE
        assert dto.budget == Decimal("50000.00")
        print("INFO [TestLegalDeskDTO]: CaseCreateDTO all fields - PASSED")

    def test_required_only(self) -> None:
        dto = CaseCreateDTO(
            title="Simple case",
            client_id=1,
            legal_domain=LegalDomain.LABOR,
        )
        assert dto.complexity == CaseComplexity.MEDIUM
        assert dto.priority == CasePriority.MEDIUM
        assert dto.budget is None
        assert dto.deadline is None

    def test_empty_title_rejected(self) -> None:
        with pytest.raises(ValidationError):
            CaseCreateDTO(title="", client_id=1, legal_domain=LegalDomain.TAX)

    def test_zero_budget_valid(self) -> None:
        dto = CaseCreateDTO(
            title="Pro bono case",
            client_id=1,
            legal_domain=LegalDomain.LABOR,
            budget=Decimal("0"),
        )
        assert dto.budget == Decimal("0")
        print("INFO [TestLegalDeskDTO]: CaseCreateDTO zero budget valid - PASSED")

    def test_negative_budget_rejected(self) -> None:
        with pytest.raises(ValidationError):
            CaseCreateDTO(
                title="Test",
                client_id=1,
                legal_domain=LegalDomain.TAX,
                budget=Decimal("-100"),
            )


class TestCaseUpdateDTO:
    def test_partial_update(self) -> None:
        dto = CaseUpdateDTO(status=CaseStatus.ACTIVE)
        assert dto.status == CaseStatus.ACTIVE
        assert dto.title is None

    def test_all_none(self) -> None:
        dto = CaseUpdateDTO()
        assert dto.status is None
        assert dto.budget is None


class TestCaseResponseDTO:
    def test_from_attributes(self) -> None:
        mock = MagicMock()
        mock.id = 1
        mock.case_number = "LD-2026-0001"
        mock.title = "Test Case"
        mock.description = None
        mock.client_id = 1
        mock.legal_domain = "corporate"
        mock.complexity = "medium"
        mock.priority = "medium"
        mock.status = "new"
        mock.budget = None
        mock.estimated_cost = None
        mock.final_quote = None
        mock.margin_percentage = None
        mock.deadline = None
        mock.ai_classification = None
        mock.created_at = datetime(2026, 1, 1)
        mock.updated_at = None
        dto = CaseResponseDTO.model_validate(mock, from_attributes=True)
        assert dto.case_number == "LD-2026-0001"
        assert dto.ai_classification is None
        print("INFO [TestLegalDeskDTO]: CaseResponseDTO from_attributes - PASSED")

    def test_with_ai_classification(self) -> None:
        dto = CaseResponseDTO(
            id=1,
            case_number="LD-2026-0002",
            title="AI Case",
            client_id=1,
            legal_domain="corporate",
            complexity="high",
            priority="urgent",
            status="classifying",
            ai_classification={"domain": "corporate", "confidence": 0.95},
            created_at=datetime(2026, 1, 1),
        )
        assert dto.ai_classification == {"domain": "corporate", "confidence": 0.95}


class TestCaseDetailDTO:
    def test_with_related_entities(self) -> None:
        dto = CaseDetailDTO(
            id=1,
            case_number="LD-2026-0001",
            title="Detail Case",
            client_id=1,
            legal_domain="corporate",
            complexity="medium",
            priority="medium",
            status="active",
            created_at=datetime(2026, 1, 1),
            client=ClientResponseDTO(
                id=1,
                name="Client A",
                client_type="company",
                is_active=True,
                created_at=datetime(2026, 1, 1),
            ),
            specialists=[
                AssignmentResponseDTO(
                    id=1,
                    case_id=1,
                    specialist_id=1,
                    role="lead",
                    status="active",
                    fee_currency="EUR",
                    assigned_at=datetime(2026, 1, 2),
                ),
            ],
            deliverables=[
                DeliverableResponseDTO(
                    id=1,
                    case_id=1,
                    title="Draft contract",
                    status="pending",
                    created_at=datetime(2026, 1, 3),
                ),
            ],
        )
        assert dto.client is not None
        assert dto.client.name == "Client A"
        assert len(dto.specialists) == 1
        assert len(dto.deliverables) == 1
        print("INFO [TestLegalDeskDTO]: CaseDetailDTO with related entities - PASSED")

    def test_empty_related(self) -> None:
        dto = CaseDetailDTO(
            id=1,
            case_number="LD-2026-0001",
            title="Empty Detail Case",
            client_id=1,
            legal_domain="corporate",
            complexity="medium",
            priority="medium",
            status="new",
            created_at=datetime(2026, 1, 1),
        )
        assert dto.client is None
        assert dto.specialists == []
        assert dto.deliverables == []


class TestCaseFilterDTO:
    def test_all_none(self) -> None:
        dto = CaseFilterDTO()
        assert dto.status is None
        assert dto.legal_domain is None
        assert dto.priority is None
        assert dto.case_type is None
        assert dto.client_id is None
        assert dto.complexity is None
        print("INFO [TestLegalDeskDTO]: CaseFilterDTO all none - PASSED")

    def test_with_filters(self) -> None:
        dto = CaseFilterDTO(
            status=CaseStatus.ACTIVE,
            legal_domain=LegalDomain.TAX,
            priority=CasePriority.HIGH,
        )
        assert dto.status == CaseStatus.ACTIVE
        assert dto.legal_domain == LegalDomain.TAX


class TestCaseListItemDTO:
    def test_from_dict(self) -> None:
        dto = CaseListItemDTO(
            id=1,
            case_number="LD-2026-0001",
            title="List Item Case",
            client_id=1,
            legal_domain="corporate",
            priority="medium",
            status="new",
            deadline=date(2026, 6, 30),
            created_at=datetime(2026, 1, 1),
        )
        assert dto.case_number == "LD-2026-0001"
        assert dto.deadline == date(2026, 6, 30)


# ============================================================================
# Assignment DTO Tests
# ============================================================================


class TestAssignmentCreateDTO:
    def test_all_fields(self) -> None:
        dto = AssignmentCreateDTO(
            case_id=1,
            specialist_id=2,
            role=AssignmentRole.SUPPORT,
            proposed_fee=Decimal("5000.00"),
            fee_currency="USD",
        )
        assert dto.case_id == 1
        assert dto.role == AssignmentRole.SUPPORT
        assert dto.proposed_fee == Decimal("5000.00")

    def test_defaults(self) -> None:
        dto = AssignmentCreateDTO(case_id=1, specialist_id=2)
        assert dto.role == AssignmentRole.LEAD
        assert dto.proposed_fee is None
        assert dto.fee_currency == "EUR"

    def test_zero_fee_valid(self) -> None:
        dto = AssignmentCreateDTO(
            case_id=1, specialist_id=2, proposed_fee=Decimal("0")
        )
        assert dto.proposed_fee == Decimal("0")


class TestAssignmentResponseDTO:
    def test_from_attributes(self) -> None:
        mock = MagicMock()
        mock.id = 1
        mock.case_id = 1
        mock.specialist_id = 2
        mock.role = "lead"
        mock.status = "proposed"
        mock.proposed_fee = Decimal("5000.00")
        mock.agreed_fee = None
        mock.fee_currency = "EUR"
        mock.assigned_at = datetime(2026, 1, 1)
        mock.responded_at = None
        dto = AssignmentResponseDTO.model_validate(mock, from_attributes=True)
        assert dto.proposed_fee == Decimal("5000.00")
        assert dto.agreed_fee is None


# ============================================================================
# Deliverable DTO Tests
# ============================================================================


class TestDeliverableCreateDTO:
    def test_all_fields(self) -> None:
        dto = DeliverableCreateDTO(
            case_id=1,
            title="Contract draft",
            specialist_id=2,
            description="First draft of the contract",
            due_date=date(2026, 3, 15),
        )
        assert dto.title == "Contract draft"
        assert dto.due_date == date(2026, 3, 15)

    def test_required_only(self) -> None:
        dto = DeliverableCreateDTO(case_id=1, title="Simple deliverable")
        assert dto.specialist_id is None
        assert dto.description is None
        assert dto.due_date is None

    def test_empty_title_rejected(self) -> None:
        with pytest.raises(ValidationError):
            DeliverableCreateDTO(case_id=1, title="")


class TestDeliverableUpdateDTO:
    def test_partial_update(self) -> None:
        dto = DeliverableUpdateDTO(status=DeliverableStatus.COMPLETED)
        assert dto.status == DeliverableStatus.COMPLETED
        assert dto.title is None

    def test_all_none(self) -> None:
        dto = DeliverableUpdateDTO()
        assert dto.title is None
        assert dto.status is None


class TestDeliverableResponseDTO:
    def test_from_attributes(self) -> None:
        mock = MagicMock()
        mock.id = 1
        mock.case_id = 1
        mock.specialist_id = None
        mock.title = "Test Deliverable"
        mock.description = None
        mock.status = "pending"
        mock.due_date = date(2026, 6, 30)
        mock.completed_at = None
        mock.created_at = datetime(2026, 1, 1)
        mock.updated_at = None
        dto = DeliverableResponseDTO.model_validate(mock, from_attributes=True)
        assert dto.title == "Test Deliverable"
        assert dto.due_date == date(2026, 6, 30)


# ============================================================================
# Message DTO Tests
# ============================================================================


class TestMessageCreateDTO:
    def test_all_fields(self) -> None:
        dto = MessageCreateDTO(
            case_id=1,
            message="Please review the attached documents.",
            sender_type="specialist",
            sender_name="Jane Smith",
            is_internal=True,
        )
        assert dto.message == "Please review the attached documents."
        assert dto.is_internal is True

    def test_required_only(self) -> None:
        dto = MessageCreateDTO(case_id=1, message="Hello")
        assert dto.sender_type == "system"
        assert dto.sender_name is None
        assert dto.is_internal is False

    def test_empty_message_rejected(self) -> None:
        with pytest.raises(ValidationError):
            MessageCreateDTO(case_id=1, message="")


class TestMessageResponseDTO:
    def test_from_attributes(self) -> None:
        mock = MagicMock()
        mock.id = 1
        mock.case_id = 1
        mock.sender_type = "system"
        mock.sender_name = None
        mock.message = "Case created"
        mock.is_internal = False
        mock.created_at = datetime(2026, 1, 1)
        dto = MessageResponseDTO.model_validate(mock, from_attributes=True)
        assert dto.message == "Case created"


# ============================================================================
# Document DTO Tests
# ============================================================================


class TestDocumentCreateDTO:
    def test_all_fields(self) -> None:
        dto = DocumentCreateDTO(
            case_id=1,
            file_name="contract.pdf",
            file_url="https://storage.example.com/contract.pdf",
            file_type="application/pdf",
            file_size_bytes=1024000,
            uploaded_by="admin@example.com",
        )
        assert dto.file_name == "contract.pdf"
        assert dto.file_size_bytes == 1024000

    def test_required_only(self) -> None:
        dto = DocumentCreateDTO(
            case_id=1,
            file_name="doc.pdf",
            file_url="https://storage.example.com/doc.pdf",
        )
        assert dto.file_type is None
        assert dto.file_size_bytes is None

    def test_empty_file_name_rejected(self) -> None:
        with pytest.raises(ValidationError):
            DocumentCreateDTO(
                case_id=1,
                file_name="",
                file_url="https://storage.example.com/doc.pdf",
            )

    def test_empty_file_url_rejected(self) -> None:
        with pytest.raises(ValidationError):
            DocumentCreateDTO(case_id=1, file_name="doc.pdf", file_url="")

    def test_negative_file_size_rejected(self) -> None:
        with pytest.raises(ValidationError):
            DocumentCreateDTO(
                case_id=1,
                file_name="doc.pdf",
                file_url="https://storage.example.com/doc.pdf",
                file_size_bytes=-1,
            )


class TestDocumentResponseDTO:
    def test_from_attributes(self) -> None:
        mock = MagicMock()
        mock.id = 1
        mock.case_id = 1
        mock.file_name = "contract.pdf"
        mock.file_url = "https://storage.example.com/contract.pdf"
        mock.file_type = "application/pdf"
        mock.file_size_bytes = 1024000
        mock.uploaded_by = "admin"
        mock.created_at = datetime(2026, 1, 1)
        dto = DocumentResponseDTO.model_validate(mock, from_attributes=True)
        assert dto.file_name == "contract.pdf"


# ============================================================================
# Pricing DTO Tests
# ============================================================================


class TestPricingProposalDTO:
    def test_all_fields(self) -> None:
        dto = PricingProposalDTO(
            case_id=1,
            action=PricingAction.PROPOSAL,
            new_amount=Decimal("10000.00"),
            previous_amount=Decimal("8000.00"),
            currency="EUR",
            changed_by="admin@example.com",
            notes="Initial proposal",
        )
        assert dto.new_amount == Decimal("10000.00")
        assert dto.action == PricingAction.PROPOSAL

    def test_required_only(self) -> None:
        dto = PricingProposalDTO(
            case_id=1,
            action=PricingAction.FINAL,
            new_amount=Decimal("5000.00"),
        )
        assert dto.currency == "EUR"
        assert dto.previous_amount is None
        assert dto.changed_by is None

    def test_zero_amount_valid(self) -> None:
        dto = PricingProposalDTO(
            case_id=1,
            action=PricingAction.ADJUST,
            new_amount=Decimal("0"),
        )
        assert dto.new_amount == Decimal("0")

    def test_negative_amount_rejected(self) -> None:
        with pytest.raises(ValidationError):
            PricingProposalDTO(
                case_id=1,
                action=PricingAction.PROPOSAL,
                new_amount=Decimal("-100"),
            )


class TestPricingHistoryResponseDTO:
    def test_from_attributes(self) -> None:
        mock = MagicMock()
        mock.id = 1
        mock.case_id = 1
        mock.action = "proposal"
        mock.previous_amount = None
        mock.new_amount = Decimal("10000.00")
        mock.currency = "EUR"
        mock.changed_by = "admin"
        mock.notes = None
        mock.created_at = datetime(2026, 1, 1)
        dto = PricingHistoryResponseDTO.model_validate(mock, from_attributes=True)
        assert dto.new_amount == Decimal("10000.00")


# ============================================================================
# Scoring DTO Tests
# ============================================================================


class TestScoreSubmitDTO:
    def test_all_fields(self) -> None:
        dto = ScoreSubmitDTO(
            specialist_id=1,
            case_id=1,
            quality_score=Decimal("4.50"),
            teamwork_score=Decimal("4.00"),
            delivery_score=Decimal("3.50"),
            satisfaction_score=Decimal("5.00"),
            overall_score=Decimal("4.25"),
            feedback="Excellent work on the case.",
        )
        assert dto.quality_score == Decimal("4.50")
        assert dto.overall_score == Decimal("4.25")
        print("INFO [TestLegalDeskDTO]: ScoreSubmitDTO all fields - PASSED")

    def test_required_only(self) -> None:
        dto = ScoreSubmitDTO(specialist_id=1, case_id=1)
        assert dto.quality_score is None
        assert dto.feedback is None

    def test_boundary_zero(self) -> None:
        dto = ScoreSubmitDTO(
            specialist_id=1,
            case_id=1,
            quality_score=Decimal("0.00"),
            overall_score=Decimal("0.00"),
        )
        assert dto.quality_score == Decimal("0.00")
        print("INFO [TestLegalDeskDTO]: ScoreSubmitDTO boundary zero - PASSED")

    def test_boundary_five(self) -> None:
        dto = ScoreSubmitDTO(
            specialist_id=1,
            case_id=1,
            quality_score=Decimal("5.00"),
            overall_score=Decimal("5.00"),
        )
        assert dto.quality_score == Decimal("5.00")
        print("INFO [TestLegalDeskDTO]: ScoreSubmitDTO boundary five - PASSED")

    def test_score_exceeds_maximum_rejected(self) -> None:
        with pytest.raises(ValidationError):
            ScoreSubmitDTO(
                specialist_id=1,
                case_id=1,
                quality_score=Decimal("5.01"),
            )
        print("INFO [TestLegalDeskDTO]: ScoreSubmitDTO over max rejected - PASSED")

    def test_negative_score_rejected(self) -> None:
        with pytest.raises(ValidationError):
            ScoreSubmitDTO(
                specialist_id=1,
                case_id=1,
                quality_score=Decimal("-0.01"),
            )


class TestScoreResponseDTO:
    def test_from_attributes(self) -> None:
        mock = MagicMock()
        mock.id = 1
        mock.specialist_id = 1
        mock.case_id = 1
        mock.quality_score = Decimal("4.50")
        mock.teamwork_score = Decimal("4.00")
        mock.delivery_score = None
        mock.satisfaction_score = None
        mock.overall_score = Decimal("4.25")
        mock.feedback = "Good work"
        mock.scored_at = datetime(2026, 2, 1)
        dto = ScoreResponseDTO.model_validate(mock, from_attributes=True)
        assert dto.quality_score == Decimal("4.50")
        assert dto.delivery_score is None


# ============================================================================
# Assignment Engine DTO Tests
# ============================================================================


class TestSpecialistCandidateDTO:
    def test_all_fields(self) -> None:
        dto = SpecialistCandidateDTO(
            specialist_id=1,
            full_name="Jane Smith",
            email="jane@law.com",
            match_score=Decimal("0.85"),
            hourly_rate=Decimal("150.00"),
            currency="EUR",
            current_workload=2,
            max_concurrent_cases=5,
            expertise_match=["corporate", "commercial"],
            jurisdiction_match=["Spain"],
        )
        assert dto.match_score == Decimal("0.85")
        assert len(dto.expertise_match) == 2
        print("INFO [TestLegalDeskDTO]: SpecialistCandidateDTO all fields - PASSED")

    def test_match_score_zero(self) -> None:
        dto = SpecialistCandidateDTO(
            specialist_id=1,
            full_name="Low Match",
            email="low@law.com",
            match_score=Decimal("0"),
            current_workload=0,
            max_concurrent_cases=5,
        )
        assert dto.match_score == Decimal("0")

    def test_match_score_one(self) -> None:
        dto = SpecialistCandidateDTO(
            specialist_id=1,
            full_name="Perfect Match",
            email="perfect@law.com",
            match_score=Decimal("1"),
            current_workload=0,
            max_concurrent_cases=5,
        )
        assert dto.match_score == Decimal("1")

    def test_match_score_over_one_rejected(self) -> None:
        with pytest.raises(ValidationError):
            SpecialistCandidateDTO(
                specialist_id=1,
                full_name="Over Match",
                email="over@law.com",
                match_score=Decimal("1.01"),
                current_workload=0,
                max_concurrent_cases=5,
            )

    def test_empty_lists(self) -> None:
        dto = SpecialistCandidateDTO(
            specialist_id=1,
            full_name="No Match Lists",
            email="no@law.com",
            match_score=Decimal("0.50"),
            current_workload=0,
            max_concurrent_cases=5,
        )
        assert dto.expertise_match == []
        assert dto.jurisdiction_match == []


class TestSuggestionResponseDTO:
    def test_with_candidates(self) -> None:
        candidate = SpecialistCandidateDTO(
            specialist_id=1,
            full_name="Jane Smith",
            email="jane@law.com",
            match_score=Decimal("0.90"),
            current_workload=1,
            max_concurrent_cases=5,
        )
        dto = SuggestionResponseDTO(
            case_id=1,
            legal_domain="corporate",
            candidates=[candidate],
            generated_at=datetime(2026, 1, 1, 12, 0, 0),
        )
        assert len(dto.candidates) == 1
        assert dto.candidates[0].match_score == Decimal("0.90")

    def test_empty_candidates(self) -> None:
        dto = SuggestionResponseDTO(
            case_id=1,
            legal_domain="immigration",
            generated_at=datetime(2026, 1, 1),
        )
        assert dto.candidates == []


# ============================================================================
# Classification & Analytics DTO Tests
# ============================================================================


class TestClassificationResultDTO:
    def test_all_fields(self) -> None:
        dto = ClassificationResultDTO(
            legal_domain=LegalDomain.CORPORATE,
            complexity=CaseComplexity.HIGH,
            case_type=CaseType.ADVISORY,
            confidence=Decimal("0.95"),
            suggested_tags=["merger", "acquisition"],
        )
        assert dto.legal_domain == LegalDomain.CORPORATE
        assert dto.confidence == Decimal("0.95")
        assert len(dto.suggested_tags) == 2
        print("INFO [TestLegalDeskDTO]: ClassificationResultDTO all fields - PASSED")

    def test_confidence_zero(self) -> None:
        dto = ClassificationResultDTO(
            legal_domain=LegalDomain.TAX,
            complexity=CaseComplexity.LOW,
            case_type=CaseType.LITIGATION,
            confidence=Decimal("0"),
        )
        assert dto.confidence == Decimal("0")

    def test_confidence_one(self) -> None:
        dto = ClassificationResultDTO(
            legal_domain=LegalDomain.LABOR,
            complexity=CaseComplexity.MEDIUM,
            case_type=CaseType.ADVISORY,
            confidence=Decimal("1"),
        )
        assert dto.confidence == Decimal("1")

    def test_confidence_over_one_rejected(self) -> None:
        with pytest.raises(ValidationError):
            ClassificationResultDTO(
                legal_domain=LegalDomain.TAX,
                complexity=CaseComplexity.LOW,
                case_type=CaseType.ADVISORY,
                confidence=Decimal("1.01"),
            )

    def test_empty_tags(self) -> None:
        dto = ClassificationResultDTO(
            legal_domain=LegalDomain.IP,
            complexity=CaseComplexity.CRITICAL,
            case_type=CaseType.LITIGATION,
            confidence=Decimal("0.80"),
        )
        assert dto.suggested_tags == []


class TestDashboardStatsDTO:
    def test_all_fields(self) -> None:
        dto = DashboardStatsDTO(
            total_cases=100,
            active_cases=25,
            completed_cases=70,
            total_specialists=15,
            avg_case_duration_days=Decimal("45.5"),
            total_revenue=Decimal("500000.00"),
            cases_by_status={"new": 5, "active": 25, "completed": 70},
            cases_by_domain={"corporate": 40, "tax": 30, "labor": 30},
            cases_by_priority={"low": 20, "medium": 50, "high": 25, "urgent": 5},
        )
        assert dto.total_cases == 100
        assert dto.cases_by_status["active"] == 25
        print("INFO [TestLegalDeskDTO]: DashboardStatsDTO all fields - PASSED")

    def test_empty_dicts(self) -> None:
        dto = DashboardStatsDTO(
            total_cases=0,
            active_cases=0,
            completed_cases=0,
            total_specialists=0,
        )
        assert dto.cases_by_status == {}
        assert dto.cases_by_domain == {}
        assert dto.cases_by_priority == {}
        assert dto.avg_case_duration_days is None
        assert dto.total_revenue is None
        print("INFO [TestLegalDeskDTO]: DashboardStatsDTO empty dicts - PASSED")
