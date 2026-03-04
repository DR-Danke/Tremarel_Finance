"""Unit tests for LdAssignmentRepository."""

from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from src.models.ld_case_specialist import LdCaseSpecialist
from src.repository.ld_assignment_repository import LdAssignmentRepository


@pytest.fixture
def repo():
    return LdAssignmentRepository()


@pytest.fixture
def mock_db():
    return MagicMock()


class TestCreateAssignment:
    def test_create_assignment_sets_fields(self, repo, mock_db):
        data = {
            "case_id": 1,
            "specialist_id": 2,
            "role": "lead",
            "proposed_fee": Decimal("1500.00"),
            "fee_currency": "USD",
        }
        repo.create_assignment(mock_db, data)
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
        created = mock_db.add.call_args[0][0]
        assert isinstance(created, LdCaseSpecialist)
        assert created.case_id == 1
        assert created.specialist_id == 2
        assert created.role == "lead"
        assert created.proposed_fee == Decimal("1500.00")
        assert created.fee_currency == "USD"
        assert created.status == "pending"

    def test_create_assignment_defaults(self, repo, mock_db):
        data = {"case_id": 1, "specialist_id": 2}
        repo.create_assignment(mock_db, data)
        created = mock_db.add.call_args[0][0]
        assert created.role == "assigned"
        assert created.fee_currency == "EUR"
        assert created.status == "pending"


class TestGetCaseSpecialists:
    def test_get_case_specialists_filters_and_orders(self, repo, mock_db):
        mock_query = mock_db.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_order = mock_filter.order_by.return_value
        mock_order.all.return_value = [MagicMock(), MagicMock()]

        result = repo.get_case_specialists(mock_db, case_id=5)

        mock_db.query.assert_called_once_with(LdCaseSpecialist)
        assert len(result) == 2


class TestGetSpecialistCases:
    def test_get_specialist_cases_filters_and_orders(self, repo, mock_db):
        mock_query = mock_db.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_order = mock_filter.order_by.return_value
        mock_order.all.return_value = [MagicMock()]

        result = repo.get_specialist_cases(mock_db, specialist_id=3)

        mock_db.query.assert_called_once_with(LdCaseSpecialist)
        assert len(result) == 1


class TestUpdateAssignmentStatus:
    def test_update_status_not_found(self, repo, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None
        result = repo.update_assignment_status(mock_db, assignment_id=999, status="accepted")
        assert result is None

    def test_update_status_from_pending_sets_responded_at(self, repo, mock_db):
        assignment = MagicMock()
        assignment.status = "pending"
        assignment.responded_at = None
        mock_db.query.return_value.filter.return_value.first.return_value = assignment

        result = repo.update_assignment_status(mock_db, assignment_id=1, status="accepted")

        assert result.status == "accepted"
        assert result.responded_at is not None
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    def test_update_status_from_non_pending_no_responded_at(self, repo, mock_db):
        assignment = MagicMock()
        assignment.status = "accepted"
        original_responded_at = assignment.responded_at
        mock_db.query.return_value.filter.return_value.first.return_value = assignment

        repo.update_assignment_status(mock_db, assignment_id=1, status="completed")

        assert assignment.status == "completed"
        assert assignment.responded_at == original_responded_at


class TestUpdateFees:
    def test_update_fees_not_found(self, repo, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None
        result = repo.update_fees(
            mock_db,
            assignment_id=999,
            proposed_fee=Decimal("1000.00"),
            agreed_fee=Decimal("900.00"),
            fee_type="EUR",
        )
        assert result is None

    def test_update_fees_sets_decimal_values(self, repo, mock_db):
        assignment = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = assignment

        result = repo.update_fees(
            mock_db,
            assignment_id=1,
            proposed_fee=Decimal("2500.50"),
            agreed_fee=Decimal("2300.00"),
            fee_type="USD",
        )

        assert result.proposed_fee == Decimal("2500.50")
        assert result.agreed_fee == Decimal("2300.00")
        assert result.fee_currency == "USD"
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
