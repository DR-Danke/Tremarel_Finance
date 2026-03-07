"""Unit tests for LdAssignmentService."""

from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from src.core.services.ld_assignment_service import LdAssignmentService
from src.interface.legaldesk_dto import AssignmentCreateDTO


@pytest.fixture
def service():
    return LdAssignmentService()


@pytest.fixture
def mock_db():
    return MagicMock()


def _make_expertise(legal_domain="corporate", proficiency_level="expert", years_in_domain=10):
    """Helper to create a mock expertise object."""
    exp = MagicMock()
    exp.legal_domain = legal_domain
    exp.proficiency_level = proficiency_level
    exp.years_in_domain = years_in_domain
    return exp


def _make_jurisdiction(country="Spain", region=None, is_primary=True):
    """Helper to create a mock jurisdiction object."""
    jur = MagicMock()
    jur.country = country
    jur.region = region
    jur.is_primary = is_primary
    return jur


def _make_specialist(
    id=1,
    full_name="Test Specialist",
    email="test@example.com",
    years_experience=10,
    overall_score=Decimal("4.00"),
    current_workload=2,
    max_concurrent_cases=5,
    hourly_rate=Decimal("150.00"),
    currency="EUR",
    expertise=None,
    jurisdictions=None,
):
    """Helper to create a mock specialist."""
    spec = MagicMock()
    spec.id = id
    spec.full_name = full_name
    spec.email = email
    spec.years_experience = years_experience
    spec.overall_score = overall_score
    spec.current_workload = current_workload
    spec.max_concurrent_cases = max_concurrent_cases
    spec.hourly_rate = hourly_rate
    spec.currency = currency
    spec.expertise = expertise or [_make_expertise()]
    spec.jurisdictions = jurisdictions or [_make_jurisdiction()]
    return spec


def _make_case(id=1, legal_domain="corporate", client_id=10):
    """Helper to create a mock case."""
    case = MagicMock()
    case.id = id
    case.legal_domain = legal_domain
    case.client_id = client_id
    return case


def _make_client(id=10, country="Spain"):
    """Helper to create a mock client."""
    client = MagicMock()
    client.id = id
    client.country = country
    return client


@patch("src.core.services.ld_assignment_service.ld_specialist_repository")
@patch("src.core.services.ld_assignment_service.ld_client_repository")
@patch("src.core.services.ld_assignment_service.ld_case_repository")
class TestSuggestSpecialists:
    def test_suggest_specialists_case_not_found(
        self, mock_case_repo, mock_client_repo, mock_spec_repo, service, mock_db
    ):
        mock_case_repo.get_by_id.return_value = None
        with pytest.raises(ValueError, match="Case not found"):
            service.suggest_specialists(mock_db, case_id=999)

    def test_suggest_specialists_no_candidates(
        self, mock_case_repo, mock_client_repo, mock_spec_repo, service, mock_db
    ):
        mock_case_repo.get_by_id.return_value = _make_case()
        mock_client_repo.get_by_id.return_value = _make_client()
        mock_spec_repo.get_available.return_value = []

        result = service.suggest_specialists(mock_db, case_id=1)

        assert result.case_id == 1
        assert result.candidates == []

    def test_suggest_specialists_returns_ranked_candidates(
        self, mock_case_repo, mock_client_repo, mock_spec_repo, service, mock_db
    ):
        mock_case_repo.get_by_id.return_value = _make_case()
        mock_client_repo.get_by_id.return_value = _make_client()

        low_spec = _make_specialist(
            id=1,
            full_name="Low",
            overall_score=Decimal("1.00"),
            expertise=[_make_expertise(proficiency_level="junior")],
        )
        high_spec = _make_specialist(
            id=2,
            full_name="High",
            overall_score=Decimal("5.00"),
            expertise=[_make_expertise(proficiency_level="expert")],
        )
        mock_spec_repo.get_available.return_value = [low_spec, high_spec]

        result = service.suggest_specialists(mock_db, case_id=1)

        assert len(result.candidates) == 2
        assert result.candidates[0].full_name == "High"
        assert result.candidates[1].full_name == "Low"
        assert result.candidates[0].match_score > result.candidates[1].match_score

    def test_suggest_specialists_limits_to_top_5(
        self, mock_case_repo, mock_client_repo, mock_spec_repo, service, mock_db
    ):
        mock_case_repo.get_by_id.return_value = _make_case()
        mock_client_repo.get_by_id.return_value = _make_client()

        specialists = [
            _make_specialist(
                id=i,
                full_name=f"Spec{i}",
                email=f"spec{i}@test.com",
                overall_score=Decimal(str(round(i * 0.5, 2))),
            )
            for i in range(1, 8)
        ]
        mock_spec_repo.get_available.return_value = specialists

        result = service.suggest_specialists(mock_db, case_id=1)

        assert len(result.candidates) == 5

    def test_suggest_specialists_no_jurisdiction_gives_full_points(
        self, mock_case_repo, mock_client_repo, mock_spec_repo, service, mock_db
    ):
        mock_case_repo.get_by_id.return_value = _make_case()
        client = _make_client(country=None)
        mock_client_repo.get_by_id.return_value = client
        mock_spec_repo.get_available.return_value = [_make_specialist()]

        result = service.suggest_specialists(mock_db, case_id=1)

        assert len(result.candidates) == 1
        assert any("No jurisdiction requirement" in r for r in result.candidates[0].match_reasons)

    def test_suggest_specialists_score_normalized_to_0_1(
        self, mock_case_repo, mock_client_repo, mock_spec_repo, service, mock_db
    ):
        mock_case_repo.get_by_id.return_value = _make_case()
        mock_client_repo.get_by_id.return_value = _make_client()
        mock_spec_repo.get_available.return_value = [_make_specialist()]

        result = service.suggest_specialists(mock_db, case_id=1)

        for candidate in result.candidates:
            assert candidate.match_score >= 0
            assert candidate.match_score <= 1

    def test_suggest_specialists_score_clamped_when_exceeding_100(
        self, mock_case_repo, mock_client_repo, mock_spec_repo, service, mock_db
    ):
        """Verify match_score is clamped to 1.0 even when raw score exceeds 100."""
        max_specialist = _make_specialist(
            overall_score=Decimal("5.00"),
            years_experience=25,
            current_workload=0,
            max_concurrent_cases=10,
            expertise=[_make_expertise(proficiency_level="expert", years_in_domain=20)],
            jurisdictions=[_make_jurisdiction(country="Spain")],
        )
        mock_case_repo.get_by_id.return_value = _make_case()
        mock_client_repo.get_by_id.return_value = _make_client(country="Spain")
        mock_spec_repo.get_available.return_value = [max_specialist]

        result = service.suggest_specialists(mock_db, case_id=1)

        assert len(result.candidates) == 1
        assert result.candidates[0].match_score <= Decimal("1.0")
        assert result.candidates[0].match_score >= Decimal("0")


class TestCalculateMatchScore:
    def setup_method(self):
        self.service = LdAssignmentService()
        self.case = _make_case()
        self.base_specialist = _make_specialist()

    def test_expert_proficiency_scores_30(self):
        expertise = _make_expertise(proficiency_level="expert")
        score, reasons = self.service._calculate_match_score(
            self.base_specialist, self.case, expertise, "Spain"
        )
        assert any("30/30" in r for r in reasons)

    def test_intermediate_proficiency_scores_20(self):
        expertise = _make_expertise(proficiency_level="intermediate")
        score, reasons = self.service._calculate_match_score(
            self.base_specialist, self.case, expertise, "Spain"
        )
        assert any("20/30" in r for r in reasons)

    def test_junior_proficiency_scores_10(self):
        expertise = _make_expertise(proficiency_level="junior")
        score, reasons = self.service._calculate_match_score(
            self.base_specialist, self.case, expertise, "Spain"
        )
        assert any("10/30" in r for r in reasons)

    def test_overall_score_calculation(self):
        specialist = _make_specialist(overall_score=Decimal("4.00"))
        expertise = _make_expertise()
        score, reasons = self.service._calculate_match_score(
            specialist, self.case, expertise, "Spain"
        )
        # (4.0 / 5.0) * 25 = 20.0
        assert any("20.0/25" in r for r in reasons)

    def test_workload_availability_calculation(self):
        specialist = _make_specialist(current_workload=1, max_concurrent_cases=5)
        expertise = _make_expertise()
        score, reasons = self.service._calculate_match_score(
            specialist, self.case, expertise, "Spain"
        )
        # ((5 - 1) / 5) * 20 = 16.0
        assert any("16.0/20" in r for r in reasons)

    def test_jurisdiction_no_requirement_gives_15(self):
        expertise = _make_expertise()
        score, reasons = self.service._calculate_match_score(
            self.base_specialist, self.case, expertise, None
        )
        assert any("No jurisdiction requirement: 15/15" in r for r in reasons)

    def test_jurisdiction_full_coverage_gives_15(self):
        specialist = _make_specialist(
            jurisdictions=[_make_jurisdiction(country="Spain", region=None)]
        )
        expertise = _make_expertise()
        score, reasons = self.service._calculate_match_score(
            specialist, self.case, expertise, "Spain"
        )
        assert any("Full jurisdiction coverage" in r and "15/15" in r for r in reasons)

    def test_jurisdiction_regional_only_gives_10(self):
        specialist = _make_specialist(
            jurisdictions=[_make_jurisdiction(country="Spain", region="Catalonia")]
        )
        expertise = _make_expertise()
        score, reasons = self.service._calculate_match_score(
            specialist, self.case, expertise, "Spain"
        )
        assert any("Regional jurisdiction coverage" in r and "10/15" in r for r in reasons)

    def test_years_experience_capped_at_10(self):
        specialist = _make_specialist(years_experience=30)
        expertise = _make_expertise()
        score, reasons = self.service._calculate_match_score(
            specialist, self.case, expertise, None
        )
        # min(30/20 * 10, 10) = 10
        assert any("10.0/10" in r for r in reasons)

    def test_max_score_is_100(self):
        specialist = _make_specialist(
            years_experience=20,
            overall_score=Decimal("5.00"),
            current_workload=0,
            max_concurrent_cases=5,
            jurisdictions=[_make_jurisdiction(country="Spain", region=None)],
        )
        expertise = _make_expertise(proficiency_level="expert")
        score, reasons = self.service._calculate_match_score(
            specialist, self.case, expertise, "Spain"
        )
        assert score == 100.0

    def test_reasons_list_has_5_entries(self):
        expertise = _make_expertise()
        score, reasons = self.service._calculate_match_score(
            self.base_specialist, self.case, expertise, "Spain"
        )
        assert len(reasons) == 5


@patch("src.core.services.ld_assignment_service.ld_specialist_repository")
@patch("src.core.services.ld_assignment_service.ld_assignment_repository")
@patch("src.core.services.ld_assignment_service.ld_case_repository")
class TestAssignSpecialist:
    def test_assign_specialist_case_not_found(
        self, mock_case_repo, mock_assign_repo, mock_spec_repo, service, mock_db
    ):
        mock_case_repo.get_by_id.return_value = None
        data = AssignmentCreateDTO(case_id=999, specialist_id=1)
        with pytest.raises(ValueError, match="Case not found"):
            service.assign_specialist(mock_db, data)

    def test_assign_specialist_specialist_not_found(
        self, mock_case_repo, mock_assign_repo, mock_spec_repo, service, mock_db
    ):
        mock_case_repo.get_by_id.return_value = _make_case()
        mock_spec_repo.get_by_id.return_value = None
        data = AssignmentCreateDTO(case_id=1, specialist_id=999)
        with pytest.raises(ValueError, match="Specialist not found"):
            service.assign_specialist(mock_db, data)

    def test_assign_specialist_creates_and_increments_workload(
        self, mock_case_repo, mock_assign_repo, mock_spec_repo, service, mock_db
    ):
        mock_case_repo.get_by_id.return_value = _make_case()
        mock_spec_repo.get_by_id.return_value = _make_specialist()
        mock_assign_repo.create_assignment.return_value = MagicMock(id=42)

        data = AssignmentCreateDTO(case_id=1, specialist_id=1)
        result = service.assign_specialist(mock_db, data)

        mock_assign_repo.create_assignment.assert_called_once()
        mock_spec_repo.update_workload.assert_called_once_with(mock_db, 1, 1)
        assert result.id == 42

    def test_assign_specialist_passes_correct_data(
        self, mock_case_repo, mock_assign_repo, mock_spec_repo, service, mock_db
    ):
        mock_case_repo.get_by_id.return_value = _make_case()
        mock_spec_repo.get_by_id.return_value = _make_specialist()
        mock_assign_repo.create_assignment.return_value = MagicMock(id=1)

        data = AssignmentCreateDTO(
            case_id=5,
            specialist_id=3,
            role="lead",
            proposed_fee=Decimal("2000.00"),
            fee_currency="USD",
        )
        service.assign_specialist(mock_db, data)

        call_args = mock_assign_repo.create_assignment.call_args[0]
        passed_data = call_args[1]
        assert passed_data["case_id"] == 5
        assert passed_data["specialist_id"] == 3
        assert passed_data["role"] == "lead"
        assert passed_data["proposed_fee"] == Decimal("2000.00")
        assert passed_data["fee_currency"] == "USD"


@patch("src.core.services.ld_assignment_service.ld_specialist_repository")
@patch("src.core.services.ld_assignment_service.ld_assignment_repository")
class TestUpdateAssignmentStatus:
    def test_update_status_not_found(
        self, mock_assign_repo, mock_spec_repo, service, mock_db
    ):
        mock_assign_repo.update_assignment_status.return_value = None
        with pytest.raises(ValueError, match="Assignment not found"):
            service.update_assignment_status(mock_db, assignment_id=999, status="completed")

    def test_update_status_completed_decrements_workload(
        self, mock_assign_repo, mock_spec_repo, service, mock_db
    ):
        assignment = MagicMock()
        assignment.specialist_id = 5
        mock_assign_repo.update_assignment_status.return_value = assignment

        service.update_assignment_status(mock_db, assignment_id=1, status="completed")

        mock_spec_repo.update_workload.assert_called_once_with(mock_db, 5, -1)

    def test_update_status_rejected_decrements_workload(
        self, mock_assign_repo, mock_spec_repo, service, mock_db
    ):
        assignment = MagicMock()
        assignment.specialist_id = 3
        mock_assign_repo.update_assignment_status.return_value = assignment

        service.update_assignment_status(mock_db, assignment_id=2, status="rejected")

        mock_spec_repo.update_workload.assert_called_once_with(mock_db, 3, -1)

    def test_update_status_active_no_workload_change(
        self, mock_assign_repo, mock_spec_repo, service, mock_db
    ):
        assignment = MagicMock()
        assignment.specialist_id = 1
        mock_assign_repo.update_assignment_status.return_value = assignment

        service.update_assignment_status(mock_db, assignment_id=1, status="active")

        mock_spec_repo.update_workload.assert_not_called()


@patch("src.core.services.ld_assignment_service.ld_assignment_repository")
class TestGetCaseSpecialists:
    def test_get_case_specialists_delegates_to_repository(
        self, mock_assign_repo, service, mock_db
    ):
        expected = [MagicMock(), MagicMock()]
        mock_assign_repo.get_case_specialists.return_value = expected

        result = service.get_case_specialists(mock_db, case_id=7)

        mock_assign_repo.get_case_specialists.assert_called_once_with(mock_db, 7)
        assert result == expected
