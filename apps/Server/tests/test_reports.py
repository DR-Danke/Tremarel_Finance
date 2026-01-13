"""Tests for reports endpoints."""

from decimal import Decimal
from typing import Generator
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.orm import Session

from main import app
from src.adapter.rest.dependencies import get_db
from src.models.user import User


# Mock database session for tests
def get_mock_db() -> Generator[MagicMock, None, None]:
    """Get a mock database session for testing."""
    mock_db = MagicMock(spec=Session)
    yield mock_db


# Override the get_db dependency for all tests
app.dependency_overrides[get_db] = get_mock_db


# Pre-computed bcrypt hash for "password123"
PASSWORD_HASH = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4Y1L.VIxMfp2r2Ve"


def create_mock_user(
    email: str = "test@example.com",
    role: str = "user",
    is_active: bool = True,
) -> User:
    """Create a mock user with pre-computed password hash."""
    user = MagicMock(spec=User)
    user.id = uuid4()
    user.email = email
    user.password_hash = PASSWORD_HASH
    user.first_name = "Test"
    user.last_name = "User"
    user.role = role
    user.is_active = is_active
    return user


async def get_auth_token(client: AsyncClient, mock_user: User) -> str:
    """Helper to get auth token for a mocked user."""
    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_repo, patch(
        "src.core.services.auth_service.pwd_context"
    ) as mock_pwd_context:
        mock_repo.get_user_by_email.return_value = mock_user
        mock_pwd_context.verify.return_value = True

        response = await client.post(
            "/api/auth/login",
            json={"email": mock_user.email, "password": "password123"},
        )
        return response.json()["access_token"]


# ============================================================================
# Reports Data Endpoint Tests
# ============================================================================


@pytest.mark.asyncio
async def test_get_report_data_no_auth() -> None:
    """Test that unauthenticated request returns 401."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        entity_id = uuid4()
        response = await client.get(
            f"/api/reports/data?entity_id={entity_id}"
            "&start_date=2024-01-01&end_date=2024-01-31"
        )

    assert response.status_code == 401
    print("INFO [TestReports]: test_get_report_data_no_auth - PASSED")


@pytest.mark.asyncio
async def test_get_report_data_success() -> None:
    """Test successful report data retrieval."""
    mock_user = create_mock_user()
    entity_id = uuid4()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        with patch(
            "src.core.services.auth_service.user_repository"
        ) as mock_auth_repo, patch(
            "src.core.services.auth_service.pwd_context"
        ) as mock_pwd_context, patch(
            "src.core.services.reports_service.ReportsService.get_report_summary"
        ) as mock_summary, patch(
            "src.core.services.reports_service.ReportsService.get_income_expense_comparison"
        ) as mock_comparison, patch(
            "src.core.services.reports_service.ReportsService.get_category_summary"
        ) as mock_breakdown:
            # Setup auth mocks
            mock_auth_repo.get_user_by_email.return_value = mock_user
            mock_auth_repo.get_user_by_id.return_value = mock_user
            mock_pwd_context.verify.return_value = True

            # Setup reports service mocks
            from src.interface.reports_dto import (
                CategorySummaryDTO,
                IncomeExpenseComparisonDTO,
                ReportSummaryDTO,
            )

            mock_summary.return_value = ReportSummaryDTO(
                total_income=Decimal("5000.00"),
                total_expenses=Decimal("3000.00"),
                net_balance=Decimal("2000.00"),
                transaction_count=25,
            )
            mock_comparison.return_value = [
                IncomeExpenseComparisonDTO(
                    period="Jan 2024",
                    month=1,
                    year=2024,
                    income=Decimal("5000.00"),
                    expenses=Decimal("3000.00"),
                )
            ]
            mock_breakdown.return_value = [
                CategorySummaryDTO(
                    category_id=str(uuid4()),
                    category_name="Salary",
                    amount=Decimal("5000.00"),
                    percentage=100.0,
                    type="income",
                    color="#4caf50",
                ),
                CategorySummaryDTO(
                    category_id=str(uuid4()),
                    category_name="Food",
                    amount=Decimal("1500.00"),
                    percentage=50.0,
                    type="expense",
                    color="#f44336",
                ),
            ]

            token = await get_auth_token(client, mock_user)
            response = await client.get(
                f"/api/reports/data?entity_id={entity_id}"
                "&start_date=2024-01-01&end_date=2024-01-31",
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert "income_expense_comparison" in data
    assert "category_breakdown" in data
    assert data["summary"]["total_income"] == "5000.00"
    assert data["summary"]["total_expenses"] == "3000.00"
    assert data["summary"]["net_balance"] == "2000.00"
    assert data["summary"]["transaction_count"] == 25
    print("INFO [TestReports]: test_get_report_data_success - PASSED")


@pytest.mark.asyncio
async def test_get_report_data_only_income() -> None:
    """Test report data with only income transactions."""
    mock_user = create_mock_user()
    entity_id = uuid4()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        with patch(
            "src.core.services.auth_service.user_repository"
        ) as mock_auth_repo, patch(
            "src.core.services.auth_service.pwd_context"
        ) as mock_pwd_context, patch(
            "src.core.services.reports_service.ReportsService.get_report_summary"
        ) as mock_summary, patch(
            "src.core.services.reports_service.ReportsService.get_income_expense_comparison"
        ) as mock_comparison, patch(
            "src.core.services.reports_service.ReportsService.get_category_summary"
        ) as mock_breakdown:
            mock_auth_repo.get_user_by_email.return_value = mock_user
            mock_auth_repo.get_user_by_id.return_value = mock_user
            mock_pwd_context.verify.return_value = True

            from src.interface.reports_dto import (
                CategorySummaryDTO,
                IncomeExpenseComparisonDTO,
                ReportSummaryDTO,
            )

            mock_summary.return_value = ReportSummaryDTO(
                total_income=Decimal("8000.00"),
                total_expenses=Decimal("0"),
                net_balance=Decimal("8000.00"),
                transaction_count=5,
            )
            mock_comparison.return_value = [
                IncomeExpenseComparisonDTO(
                    period="Jan 2024",
                    month=1,
                    year=2024,
                    income=Decimal("8000.00"),
                    expenses=Decimal("0"),
                )
            ]
            mock_breakdown.return_value = [
                CategorySummaryDTO(
                    category_id=str(uuid4()),
                    category_name="Salary",
                    amount=Decimal("8000.00"),
                    percentage=100.0,
                    type="income",
                    color="#4caf50",
                )
            ]

            token = await get_auth_token(client, mock_user)
            response = await client.get(
                f"/api/reports/data?entity_id={entity_id}"
                "&start_date=2024-01-01&end_date=2024-01-31",
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 200
    data = response.json()
    assert data["summary"]["total_income"] == "8000.00"
    assert data["summary"]["total_expenses"] == "0"
    assert data["summary"]["net_balance"] == "8000.00"
    print("INFO [TestReports]: test_get_report_data_only_income - PASSED")


@pytest.mark.asyncio
async def test_get_report_data_only_expenses() -> None:
    """Test report data with only expense transactions."""
    mock_user = create_mock_user()
    entity_id = uuid4()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        with patch(
            "src.core.services.auth_service.user_repository"
        ) as mock_auth_repo, patch(
            "src.core.services.auth_service.pwd_context"
        ) as mock_pwd_context, patch(
            "src.core.services.reports_service.ReportsService.get_report_summary"
        ) as mock_summary, patch(
            "src.core.services.reports_service.ReportsService.get_income_expense_comparison"
        ) as mock_comparison, patch(
            "src.core.services.reports_service.ReportsService.get_category_summary"
        ) as mock_breakdown:
            mock_auth_repo.get_user_by_email.return_value = mock_user
            mock_auth_repo.get_user_by_id.return_value = mock_user
            mock_pwd_context.verify.return_value = True

            from src.interface.reports_dto import (
                CategorySummaryDTO,
                IncomeExpenseComparisonDTO,
                ReportSummaryDTO,
            )

            mock_summary.return_value = ReportSummaryDTO(
                total_income=Decimal("0"),
                total_expenses=Decimal("2500.00"),
                net_balance=Decimal("-2500.00"),
                transaction_count=10,
            )
            mock_comparison.return_value = [
                IncomeExpenseComparisonDTO(
                    period="Jan 2024",
                    month=1,
                    year=2024,
                    income=Decimal("0"),
                    expenses=Decimal("2500.00"),
                )
            ]
            mock_breakdown.return_value = [
                CategorySummaryDTO(
                    category_id=str(uuid4()),
                    category_name="Rent",
                    amount=Decimal("1500.00"),
                    percentage=60.0,
                    type="expense",
                    color="#f44336",
                ),
                CategorySummaryDTO(
                    category_id=str(uuid4()),
                    category_name="Utilities",
                    amount=Decimal("1000.00"),
                    percentage=40.0,
                    type="expense",
                    color="#e91e63",
                ),
            ]

            token = await get_auth_token(client, mock_user)
            response = await client.get(
                f"/api/reports/data?entity_id={entity_id}"
                "&start_date=2024-01-01&end_date=2024-01-31",
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 200
    data = response.json()
    assert data["summary"]["total_income"] == "0"
    assert data["summary"]["total_expenses"] == "2500.00"
    assert data["summary"]["net_balance"] == "-2500.00"
    assert len(data["category_breakdown"]) == 2
    print("INFO [TestReports]: test_get_report_data_only_expenses - PASSED")


@pytest.mark.asyncio
async def test_get_report_data_empty() -> None:
    """Test report data with no transactions in date range."""
    mock_user = create_mock_user()
    entity_id = uuid4()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        with patch(
            "src.core.services.auth_service.user_repository"
        ) as mock_auth_repo, patch(
            "src.core.services.auth_service.pwd_context"
        ) as mock_pwd_context, patch(
            "src.core.services.reports_service.ReportsService.get_report_summary"
        ) as mock_summary, patch(
            "src.core.services.reports_service.ReportsService.get_income_expense_comparison"
        ) as mock_comparison, patch(
            "src.core.services.reports_service.ReportsService.get_category_summary"
        ) as mock_breakdown:
            mock_auth_repo.get_user_by_email.return_value = mock_user
            mock_auth_repo.get_user_by_id.return_value = mock_user
            mock_pwd_context.verify.return_value = True

            from src.interface.reports_dto import ReportSummaryDTO

            mock_summary.return_value = ReportSummaryDTO(
                total_income=Decimal("0"),
                total_expenses=Decimal("0"),
                net_balance=Decimal("0"),
                transaction_count=0,
            )
            mock_comparison.return_value = []
            mock_breakdown.return_value = []

            token = await get_auth_token(client, mock_user)
            response = await client.get(
                f"/api/reports/data?entity_id={entity_id}"
                "&start_date=2024-01-01&end_date=2024-01-31",
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 200
    data = response.json()
    assert data["summary"]["total_income"] == "0"
    assert data["summary"]["total_expenses"] == "0"
    assert data["summary"]["net_balance"] == "0"
    assert data["summary"]["transaction_count"] == 0
    assert data["income_expense_comparison"] == []
    assert data["category_breakdown"] == []
    print("INFO [TestReports]: test_get_report_data_empty - PASSED")


@pytest.mark.asyncio
async def test_get_report_data_missing_entity_id() -> None:
    """Test that missing entity_id parameter returns 422."""
    mock_user = create_mock_user()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        with patch(
            "src.core.services.auth_service.user_repository"
        ) as mock_auth_repo, patch(
            "src.core.services.auth_service.pwd_context"
        ) as mock_pwd_context:
            mock_auth_repo.get_user_by_email.return_value = mock_user
            mock_auth_repo.get_user_by_id.return_value = mock_user
            mock_pwd_context.verify.return_value = True

            token = await get_auth_token(client, mock_user)
            response = await client.get(
                "/api/reports/data?start_date=2024-01-01&end_date=2024-01-31",
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 422
    print("INFO [TestReports]: test_get_report_data_missing_entity_id - PASSED")


@pytest.mark.asyncio
async def test_get_report_data_missing_dates() -> None:
    """Test that missing date parameters returns 422."""
    mock_user = create_mock_user()
    entity_id = uuid4()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        with patch(
            "src.core.services.auth_service.user_repository"
        ) as mock_auth_repo, patch(
            "src.core.services.auth_service.pwd_context"
        ) as mock_pwd_context:
            mock_auth_repo.get_user_by_email.return_value = mock_user
            mock_auth_repo.get_user_by_id.return_value = mock_user
            mock_pwd_context.verify.return_value = True

            token = await get_auth_token(client, mock_user)
            response = await client.get(
                f"/api/reports/data?entity_id={entity_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 422
    print("INFO [TestReports]: test_get_report_data_missing_dates - PASSED")


# ============================================================================
# CSV Export Endpoint Tests
# ============================================================================


@pytest.mark.asyncio
async def test_export_csv_no_auth() -> None:
    """Test that unauthenticated request returns 401."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        entity_id = uuid4()
        response = await client.get(
            f"/api/reports/export/csv?entity_id={entity_id}"
            "&start_date=2024-01-01&end_date=2024-01-31"
        )

    assert response.status_code == 401
    print("INFO [TestReports]: test_export_csv_no_auth - PASSED")


@pytest.mark.asyncio
async def test_export_csv_success() -> None:
    """Test successful CSV export."""
    mock_user = create_mock_user()
    entity_id = uuid4()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        with patch(
            "src.core.services.auth_service.user_repository"
        ) as mock_auth_repo, patch(
            "src.core.services.auth_service.pwd_context"
        ) as mock_pwd_context, patch(
            "src.core.services.reports_service.ReportsService.export_transactions_csv"
        ) as mock_export:
            mock_auth_repo.get_user_by_email.return_value = mock_user
            mock_auth_repo.get_user_by_id.return_value = mock_user
            mock_pwd_context.verify.return_value = True

            # Mock CSV content
            csv_content = (
                "Date,Type,Category,Amount,Description,Notes\n"
                "2024-01-15,income,Salary,5000.00,Monthly salary,\n"
                "2024-01-10,expense,Food,150.00,Groceries,Weekly shopping\n"
            )
            mock_export.return_value = csv_content

            token = await get_auth_token(client, mock_user)
            response = await client.get(
                f"/api/reports/export/csv?entity_id={entity_id}"
                "&start_date=2024-01-01&end_date=2024-01-31",
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "attachment" in response.headers["content-disposition"]
    assert "transactions_2024-01-01_2024-01-31.csv" in response.headers["content-disposition"]

    # Verify CSV content
    content = response.text
    assert "Date,Type,Category,Amount,Description,Notes" in content
    assert "Salary" in content
    assert "Food" in content
    print("INFO [TestReports]: test_export_csv_success - PASSED")


@pytest.mark.asyncio
async def test_export_csv_empty() -> None:
    """Test CSV export with no transactions."""
    mock_user = create_mock_user()
    entity_id = uuid4()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        with patch(
            "src.core.services.auth_service.user_repository"
        ) as mock_auth_repo, patch(
            "src.core.services.auth_service.pwd_context"
        ) as mock_pwd_context, patch(
            "src.core.services.reports_service.ReportsService.export_transactions_csv"
        ) as mock_export:
            mock_auth_repo.get_user_by_email.return_value = mock_user
            mock_auth_repo.get_user_by_id.return_value = mock_user
            mock_pwd_context.verify.return_value = True

            # Empty CSV (header only)
            csv_content = "Date,Type,Category,Amount,Description,Notes\n"
            mock_export.return_value = csv_content

            token = await get_auth_token(client, mock_user)
            response = await client.get(
                f"/api/reports/export/csv?entity_id={entity_id}"
                "&start_date=2024-01-01&end_date=2024-01-31",
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 200
    content = response.text
    lines = content.strip().split("\n")
    assert len(lines) == 1  # Only header
    assert "Date,Type,Category,Amount,Description,Notes" in content
    print("INFO [TestReports]: test_export_csv_empty - PASSED")


@pytest.mark.asyncio
async def test_export_csv_missing_params() -> None:
    """Test that missing parameters returns 422."""
    mock_user = create_mock_user()
    entity_id = uuid4()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        with patch(
            "src.core.services.auth_service.user_repository"
        ) as mock_auth_repo, patch(
            "src.core.services.auth_service.pwd_context"
        ) as mock_pwd_context:
            mock_auth_repo.get_user_by_email.return_value = mock_user
            mock_auth_repo.get_user_by_id.return_value = mock_user
            mock_pwd_context.verify.return_value = True

            token = await get_auth_token(client, mock_user)
            response = await client.get(
                f"/api/reports/export/csv?entity_id={entity_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 422
    print("INFO [TestReports]: test_export_csv_missing_params - PASSED")
