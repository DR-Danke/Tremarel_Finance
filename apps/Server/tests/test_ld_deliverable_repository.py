"""Unit tests for LdDeliverableRepository."""

from datetime import datetime
from unittest.mock import MagicMock

import pytest

from src.models.ld_case_deliverable import LdCaseDeliverable
from src.repository.ld_deliverable_repository import LdDeliverableRepository


@pytest.fixture
def repo():
    return LdDeliverableRepository()


@pytest.fixture
def mock_db():
    return MagicMock()


class TestCreate:
    def test_create_sets_fields_and_defaults(self, repo, mock_db):
        data = {
            "case_id": 1,
            "title": "Draft contract",
            "description": "Initial draft",
            "specialist_id": 2,
        }
        repo.create(mock_db, data)
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
        created = mock_db.add.call_args[0][0]
        assert isinstance(created, LdCaseDeliverable)
        assert created.case_id == 1
        assert created.title == "Draft contract"
        assert created.description == "Initial draft"
        assert created.specialist_id == 2
        assert created.status == "pending"

    def test_create_minimal(self, repo, mock_db):
        data = {"case_id": 3, "title": "Review document"}
        repo.create(mock_db, data)
        created = mock_db.add.call_args[0][0]
        assert created.case_id == 3
        assert created.title == "Review document"
        assert created.description is None
        assert created.specialist_id is None


class TestGetByCase:
    def test_get_by_case_filters_and_orders(self, repo, mock_db):
        mock_query = mock_db.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_order = mock_filter.order_by.return_value
        mock_order.all.return_value = [MagicMock(), MagicMock(), MagicMock()]

        result = repo.get_by_case(mock_db, case_id=1)

        mock_db.query.assert_called_once_with(LdCaseDeliverable)
        assert len(result) == 3


class TestUpdate:
    def test_update_not_found(self, repo, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None
        result = repo.update(mock_db, deliverable_id=999, data={"title": "New"})
        assert result is None

    def test_update_partial(self, repo, mock_db):
        deliverable = MagicMock(spec=LdCaseDeliverable)
        deliverable.title = "Old title"
        deliverable.description = "Old desc"
        mock_db.query.return_value.filter.return_value.first.return_value = deliverable

        result = repo.update(mock_db, deliverable_id=1, data={"title": "New title"})

        assert result.title == "New title"
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()


class TestUpdateStatus:
    def test_update_status_not_found(self, repo, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None
        result = repo.update_status(mock_db, deliverable_id=999, status="completed")
        assert result is None

    def test_update_status_to_completed_sets_completed_at(self, repo, mock_db):
        deliverable = MagicMock()
        deliverable.completed_at = None
        mock_db.query.return_value.filter.return_value.first.return_value = deliverable

        result = repo.update_status(mock_db, deliverable_id=1, status="completed")

        assert result.status == "completed"
        assert result.completed_at is not None
        mock_db.commit.assert_called_once()

    def test_update_status_to_in_progress_no_completed_at(self, repo, mock_db):
        deliverable = MagicMock()
        deliverable.completed_at = None
        mock_db.query.return_value.filter.return_value.first.return_value = deliverable

        repo.update_status(mock_db, deliverable_id=1, status="in_progress")

        assert deliverable.status == "in_progress"
        assert deliverable.completed_at is None

    def test_update_status_to_cancelled_no_completed_at(self, repo, mock_db):
        deliverable = MagicMock()
        deliverable.completed_at = None
        mock_db.query.return_value.filter.return_value.first.return_value = deliverable

        repo.update_status(mock_db, deliverable_id=1, status="cancelled")

        assert deliverable.status == "cancelled"
        assert deliverable.completed_at is None
