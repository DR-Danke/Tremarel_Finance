"""Unit tests for LdPricingService."""

from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from src.core.services.ld_pricing_service import LdPricingService


@pytest.fixture
def service():
    """Create a fresh LdPricingService instance."""
    return LdPricingService()


@pytest.fixture
def mock_db():
    """Create a mock database session."""
    return MagicMock()


@pytest.fixture
def mock_case():
    """Create a mock LdCase object."""
    case = MagicMock()
    case.id = 1
    case.case_number = "LD-202603-0001"
    case.estimated_cost = None
    case.final_quote = None
    case.margin_percentage = None
    return case


@pytest.fixture
def mock_pricing_entry():
    """Create a mock LdPricingHistory object."""
    entry = MagicMock()
    entry.id = 1
    entry.case_id = 1
    entry.action = "proposal"
    entry.previous_amount = Decimal("800.00")
    entry.new_amount = Decimal("1000.00")
    entry.currency = "EUR"
    entry.changed_by = "admin@faroo.com"
    entry.notes = "Initial proposal"
    entry.created_at = "2026-03-01T00:00:00"
    return entry


@patch("src.core.services.ld_pricing_service.ld_case_repository")
@patch("src.core.services.ld_pricing_service.ld_pricing_repository")
class TestCreateProposal:
    """Tests for LdPricingService.create_proposal."""

    def test_create_proposal_calculates_margin(
        self, mock_pricing_repo, mock_case_repo, service, mock_db, mock_case, mock_pricing_entry
    ):
        """Given specialist_cost=800, client_price=1000, verify margin=20.0%."""
        mock_case_repo.get_by_id.return_value = mock_case
        mock_pricing_repo.create.return_value = mock_pricing_entry
        mock_case_repo.update.return_value = mock_case

        result = service.create_proposal(
            mock_db,
            case_id=1,
            specialist_cost=Decimal("800"),
            client_price=Decimal("1000"),
            notes="Test proposal",
            created_by="admin@faroo.com",
        )

        assert result == mock_pricing_entry
        mock_pricing_repo.create.assert_called_once()
        create_data = mock_pricing_repo.create.call_args[0][1]
        assert create_data["action"] == "proposal"
        assert create_data["previous_amount"] == Decimal("800")
        assert create_data["new_amount"] == Decimal("1000")

        mock_case_repo.update.assert_called_once_with(
            mock_db, 1, {"estimated_cost": Decimal("800")}
        )

    def test_create_proposal_case_not_found(
        self, mock_pricing_repo, mock_case_repo, service, mock_db
    ):
        """Verify raises ValueError when case doesn't exist."""
        mock_case_repo.get_by_id.return_value = None

        with pytest.raises(ValueError, match="Case 999 not found"):
            service.create_proposal(
                mock_db,
                case_id=999,
                specialist_cost=Decimal("800"),
                client_price=Decimal("1000"),
            )

    def test_create_proposal_zero_client_price(
        self, mock_pricing_repo, mock_case_repo, service, mock_db, mock_case
    ):
        """Verify raises ValueError when client_price is 0."""
        mock_case_repo.get_by_id.return_value = mock_case

        with pytest.raises(ValueError, match="client_price must be greater than 0"):
            service.create_proposal(
                mock_db,
                case_id=1,
                specialist_cost=Decimal("800"),
                client_price=Decimal("0"),
            )


@patch("src.core.services.ld_pricing_service.ld_case_repository")
@patch("src.core.services.ld_pricing_service.ld_pricing_repository")
class TestSubmitCounter:
    """Tests for LdPricingService.submit_counter."""

    def test_submit_counter_calculates_margin(
        self, mock_pricing_repo, mock_case_repo, service, mock_db, mock_case, mock_pricing_entry
    ):
        """Given specialist_cost=900, client_price=1200, verify margin=25.0%."""
        mock_case_repo.get_by_id.return_value = mock_case
        mock_pricing_entry.action = "counter"
        mock_pricing_repo.create.return_value = mock_pricing_entry

        result = service.submit_counter(
            mock_db,
            case_id=1,
            specialist_cost=Decimal("900"),
            client_price=Decimal("1200"),
            notes="Counter offer",
            created_by="admin@faroo.com",
        )

        assert result == mock_pricing_entry
        create_data = mock_pricing_repo.create.call_args[0][1]
        assert create_data["action"] == "counter"
        assert create_data["previous_amount"] == Decimal("900")
        assert create_data["new_amount"] == Decimal("1200")

    def test_submit_counter_case_not_found(
        self, mock_pricing_repo, mock_case_repo, service, mock_db
    ):
        """Verify raises ValueError when case doesn't exist."""
        mock_case_repo.get_by_id.return_value = None

        with pytest.raises(ValueError, match="Case 999 not found"):
            service.submit_counter(
                mock_db,
                case_id=999,
                specialist_cost=Decimal("900"),
                client_price=Decimal("1200"),
            )


@patch("src.core.services.ld_pricing_service.ld_case_repository")
@patch("src.core.services.ld_pricing_service.ld_pricing_repository")
class TestAcceptPricing:
    """Tests for LdPricingService.accept_pricing."""

    def test_accept_pricing_locks_case(
        self, mock_pricing_repo, mock_case_repo, service, mock_db, mock_case, mock_pricing_entry
    ):
        """Verify final_quote and margin_percentage are set on case."""
        mock_case_repo.get_by_id.return_value = mock_case
        mock_pricing_repo.get_latest.return_value = mock_pricing_entry
        mock_case_repo.update.return_value = mock_case

        accept_entry = MagicMock()
        accept_entry.action = "accept"
        mock_pricing_repo.create.return_value = accept_entry

        result = service.accept_pricing(mock_db, case_id=1, created_by="admin@faroo.com")

        assert result == accept_entry

        # Verify case was locked with correct financial fields
        update_data = mock_case_repo.update.call_args[0][2]
        assert update_data["final_quote"] == Decimal("1000.00")
        expected_margin = ((Decimal("1000.00") - Decimal("800.00")) / Decimal("1000.00")) * 100
        assert update_data["margin_percentage"] == expected_margin

        # Verify accept entry created
        create_data = mock_pricing_repo.create.call_args[0][1]
        assert create_data["action"] == "accept"
        assert create_data["previous_amount"] == Decimal("800.00")
        assert create_data["new_amount"] == Decimal("1000.00")

    def test_accept_pricing_no_history(
        self, mock_pricing_repo, mock_case_repo, service, mock_db, mock_case
    ):
        """Verify raises ValueError when no pricing history exists."""
        mock_case_repo.get_by_id.return_value = mock_case
        mock_pricing_repo.get_latest.return_value = None

        with pytest.raises(ValueError, match="No pricing history exists"):
            service.accept_pricing(mock_db, case_id=1)

    def test_accept_pricing_case_not_found(
        self, mock_pricing_repo, mock_case_repo, service, mock_db
    ):
        """Verify raises ValueError when case doesn't exist."""
        mock_case_repo.get_by_id.return_value = None

        with pytest.raises(ValueError, match="Case 999 not found"):
            service.accept_pricing(mock_db, case_id=999)


@patch("src.core.services.ld_pricing_service.ld_case_repository")
@patch("src.core.services.ld_pricing_service.ld_pricing_repository")
class TestRejectPricing:
    """Tests for LdPricingService.reject_pricing."""

    def test_reject_pricing_stores_notes(
        self, mock_pricing_repo, mock_case_repo, service, mock_db, mock_case
    ):
        """Verify pricing entry with action=reject and notes created."""
        mock_case_repo.get_by_id.return_value = mock_case
        reject_entry = MagicMock()
        reject_entry.action = "reject"
        mock_pricing_repo.create.return_value = reject_entry

        result = service.reject_pricing(
            mock_db,
            case_id=1,
            notes="Price too high",
            created_by="client@example.com",
        )

        assert result == reject_entry
        create_data = mock_pricing_repo.create.call_args[0][1]
        assert create_data["action"] == "reject"
        assert create_data["notes"] == "Price too high"
        assert create_data["changed_by"] == "client@example.com"

    def test_reject_pricing_case_not_found(
        self, mock_pricing_repo, mock_case_repo, service, mock_db
    ):
        """Verify raises ValueError when case doesn't exist."""
        mock_case_repo.get_by_id.return_value = None

        with pytest.raises(ValueError, match="Case 999 not found"):
            service.reject_pricing(mock_db, case_id=999, notes="Not needed")


@patch("src.core.services.ld_pricing_service.ld_case_repository")
@patch("src.core.services.ld_pricing_service.ld_pricing_repository")
class TestGetPricingHistory:
    """Tests for LdPricingService.get_pricing_history."""

    def test_get_pricing_history_returns_dtos(
        self, mock_pricing_repo, mock_case_repo, service, mock_db, mock_pricing_entry
    ):
        """Verify returns list of PricingHistoryResponseDTO."""
        mock_pricing_repo.get_by_case.return_value = [mock_pricing_entry]

        result = service.get_pricing_history(mock_db, case_id=1)

        assert len(result) == 1
        assert result[0].id == 1
        assert result[0].action == "proposal"
        assert result[0].new_amount == Decimal("1000.00")

    def test_get_pricing_history_empty(
        self, mock_pricing_repo, mock_case_repo, service, mock_db
    ):
        """Verify returns empty list when no entries."""
        mock_pricing_repo.get_by_case.return_value = []

        result = service.get_pricing_history(mock_db, case_id=1)

        assert result == []
