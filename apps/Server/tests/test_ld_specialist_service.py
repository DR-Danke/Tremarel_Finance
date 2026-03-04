"""Unit tests for LdSpecialistService."""

from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from src.core.services.ld_specialist_service import LdSpecialistService
from src.interface.legaldesk_dto import (
    ExpertiseDTO,
    JurisdictionDTO,
    LegalDomain,
    ProficiencyLevel,
    ScoreSubmitDTO,
    SpecialistCreateDTO,
    SpecialistUpdateDTO,
)


@pytest.fixture
def service():
    """Create a fresh LdSpecialistService instance."""
    return LdSpecialistService()


@pytest.fixture
def mock_db():
    """Create a mock database session."""
    return MagicMock()


@pytest.fixture
def mock_specialist():
    """Create a mock LdSpecialist object."""
    specialist = MagicMock()
    specialist.id = 1
    specialist.full_name = "Jane Doe"
    specialist.email = "jane@example.com"
    specialist.expertise = []
    specialist.jurisdictions = []
    specialist.scores = []
    return specialist


class TestCreateSpecialist:
    """Tests for LdSpecialistService.create."""

    @patch("src.core.services.ld_specialist_service.ld_specialist_repository")
    def test_create_specialist_with_expertise_and_jurisdictions(
        self, mock_repo, service, mock_db, mock_specialist
    ):
        """Should create specialist and add sub-entities."""
        mock_repo.create.return_value = mock_specialist
        data = SpecialistCreateDTO(
            full_name="Jane Doe",
            email="jane@example.com",
            years_experience=10,
            expertise=[
                ExpertiseDTO(
                    legal_domain=LegalDomain.CORPORATE,
                    proficiency_level=ProficiencyLevel.EXPERT,
                    years_in_domain=8,
                ),
            ],
            jurisdictions=[
                JurisdictionDTO(country="Spain", region="Madrid", is_primary=True),
            ],
        )

        result = service.create(mock_db, data)

        mock_repo.create.assert_called_once()
        assert mock_db.add.call_count == 2  # 1 expertise + 1 jurisdiction
        mock_db.flush.assert_called_once()
        assert result == mock_specialist

    @patch("src.core.services.ld_specialist_service.ld_specialist_repository")
    def test_create_specialist_without_sub_entities(
        self, mock_repo, service, mock_db, mock_specialist
    ):
        """Should create specialist without expertise/jurisdictions."""
        mock_repo.create.return_value = mock_specialist
        data = SpecialistCreateDTO(
            full_name="Jane Doe",
            email="jane@example.com",
        )

        result = service.create(mock_db, data)

        mock_repo.create.assert_called_once()
        mock_db.add.assert_not_called()
        mock_db.flush.assert_not_called()
        assert result == mock_specialist


class TestUpdateSpecialist:
    """Tests for LdSpecialistService.update."""

    @patch("src.core.services.ld_specialist_service.ld_specialist_repository")
    def test_update_specialist_success(self, mock_repo, service, mock_db, mock_specialist):
        """Should update specialist when found."""
        mock_repo.get_by_id.return_value = mock_specialist
        mock_repo.update.return_value = mock_specialist
        data = SpecialistUpdateDTO(full_name="Jane Smith")

        result = service.update(mock_db, 1, data)

        mock_repo.get_by_id.assert_called_once_with(mock_db, 1)
        mock_repo.update.assert_called_once()
        assert result == mock_specialist

    @patch("src.core.services.ld_specialist_service.ld_specialist_repository")
    def test_update_specialist_not_found(self, mock_repo, service, mock_db):
        """Should return None when specialist not found."""
        mock_repo.get_by_id.return_value = None

        result = service.update(mock_db, 999, SpecialistUpdateDTO(full_name="Updated"))

        mock_repo.get_by_id.assert_called_once_with(mock_db, 999)
        mock_repo.update.assert_not_called()
        assert result is None


class TestGetSpecialistDetail:
    """Tests for LdSpecialistService.get_specialist_detail."""

    @patch("src.core.services.ld_specialist_service.ld_specialist_repository")
    def test_get_specialist_detail(self, mock_repo, service, mock_db, mock_specialist):
        """Should return specialist with relationships loaded."""
        mock_repo.get_by_id.return_value = mock_specialist

        result = service.get_specialist_detail(mock_db, 1)

        mock_repo.get_by_id.assert_called_once_with(mock_db, 1)
        assert result == mock_specialist


class TestListAll:
    """Tests for LdSpecialistService.list_all."""

    @patch("src.core.services.ld_specialist_service.ld_specialist_repository")
    def test_list_all_with_filters(self, mock_repo, service, mock_db, mock_specialist):
        """Should delegate to repository with filters."""
        mock_repo.list_all.return_value = [mock_specialist]
        filters = {"is_active": True, "legal_domain": "corporate"}

        result = service.list_all(mock_db, filters)

        mock_repo.list_all.assert_called_once_with(mock_db, filters)
        assert len(result) == 1


class TestAddExpertise:
    """Tests for LdSpecialistService.add_expertise."""

    def test_add_expertise(self, service, mock_db):
        """Should create LdSpecialistExpertise via ORM."""
        result = service.add_expertise(mock_db, 1, "corporate", "expert")

        mock_db.add.assert_called_once()
        mock_db.flush.assert_called_once()
        assert result.specialist_id == 1
        assert result.legal_domain == "corporate"
        assert result.proficiency_level == "expert"


class TestAddJurisdiction:
    """Tests for LdSpecialistService.add_jurisdiction."""

    def test_add_jurisdiction(self, service, mock_db):
        """Should create LdSpecialistJurisdiction via ORM."""
        result = service.add_jurisdiction(mock_db, 1, "Spain", "Madrid", True)

        mock_db.add.assert_called_once()
        mock_db.flush.assert_called_once()
        assert result.specialist_id == 1
        assert result.country == "Spain"
        assert result.region == "Madrid"
        assert result.is_primary is True


class TestSubmitScore:
    """Tests for LdSpecialistService.submit_score."""

    @patch("src.core.services.ld_specialist_service.ld_specialist_repository")
    def test_submit_score(self, mock_repo, service, mock_db):
        """Should create score, calculate average, and update specialist aggregate."""
        scores = ScoreSubmitDTO(
            specialist_id=1,
            case_id=10,
            quality_score=Decimal("4.00"),
            teamwork_score=Decimal("3.50"),
            delivery_score=Decimal("4.50"),
            satisfaction_score=Decimal("4.00"),
        )

        result = service.submit_score(mock_db, 1, 10, scores)

        mock_db.add.assert_called_once()
        mock_db.flush.assert_called_once()
        mock_repo.update_overall_score.assert_called_once_with(mock_db, 1)
        assert result.specialist_id == 1
        assert result.case_id == 10
        assert result.overall_score == Decimal("4.00")

    @patch("src.core.services.ld_specialist_service.ld_specialist_repository")
    def test_submit_score_partial_fields(self, mock_repo, service, mock_db):
        """Should average only provided score fields."""
        scores = ScoreSubmitDTO(
            specialist_id=1,
            case_id=10,
            quality_score=Decimal("5.00"),
            delivery_score=Decimal("3.00"),
        )

        result = service.submit_score(mock_db, 1, 10, scores)

        assert result.overall_score == Decimal("4.00")
        mock_repo.update_overall_score.assert_called_once_with(mock_db, 1)
