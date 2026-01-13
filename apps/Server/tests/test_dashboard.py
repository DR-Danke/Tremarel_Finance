"""Tests for dashboard endpoints."""

from datetime import date
from decimal import Decimal
from typing import Generator
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.orm import Session

from main import app
from src.adapter.rest.dependencies import get_db
from src.models.category import Category
from src.models.transaction import Transaction
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
# Dashboard Stats Endpoint Tests
# ============================================================================


@pytest.mark.asyncio
async def test_get_dashboard_stats_no_auth() -> None:
    """Test that unauthenticated request returns 401."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        entity_id = uuid4()
        response = await client.get(f"/api/dashboard/stats?entity_id={entity_id}")

    assert response.status_code == 401
    print("INFO [TestDashboard]: test_get_dashboard_stats_no_auth - PASSED")


@pytest.mark.asyncio
async def test_get_dashboard_stats_success() -> None:
    """Test successful dashboard stats retrieval."""
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
            "src.core.services.dashboard_service.DashboardService.get_current_month_summary"
        ) as mock_summary, patch(
            "src.core.services.dashboard_service.DashboardService.get_monthly_trends"
        ) as mock_trends, patch(
            "src.core.services.dashboard_service.DashboardService.get_expense_breakdown"
        ) as mock_breakdown:
            # Setup auth mocks
            mock_auth_repo.get_user_by_email.return_value = mock_user
            mock_auth_repo.get_user_by_id.return_value = mock_user
            mock_pwd_context.verify.return_value = True

            # Setup dashboard service mocks
            from src.interface.dashboard_dto import (
                CategoryBreakdownDTO,
                CurrentMonthSummaryDTO,
                MonthlyTotalDTO,
            )

            mock_summary.return_value = CurrentMonthSummaryDTO(
                total_income=Decimal("1000.00"),
                total_expenses=Decimal("500.00"),
                net_balance=Decimal("500.00"),
            )
            mock_trends.return_value = [
                MonthlyTotalDTO(
                    month="Jan 2024",
                    year=2024,
                    month_number=1,
                    income=Decimal("1000.00"),
                    expenses=Decimal("500.00"),
                )
            ]
            mock_breakdown.return_value = [
                CategoryBreakdownDTO(
                    category_id=str(uuid4()),
                    category_name="Food",
                    amount=Decimal("300.00"),
                    percentage=60.0,
                    color="#FF5733",
                )
            ]

            token = await get_auth_token(client, mock_user)
            response = await client.get(
                f"/api/dashboard/stats?entity_id={entity_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 200
    data = response.json()
    assert "current_month_summary" in data
    assert "monthly_trends" in data
    assert "expense_breakdown" in data
    assert data["current_month_summary"]["total_income"] == "1000.00"
    assert data["current_month_summary"]["total_expenses"] == "500.00"
    assert data["current_month_summary"]["net_balance"] == "500.00"
    print("INFO [TestDashboard]: test_get_dashboard_stats_success - PASSED")


@pytest.mark.asyncio
async def test_get_dashboard_stats_empty_data() -> None:
    """Test dashboard stats with no transactions."""
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
            "src.core.services.dashboard_service.DashboardService.get_current_month_summary"
        ) as mock_summary, patch(
            "src.core.services.dashboard_service.DashboardService.get_monthly_trends"
        ) as mock_trends, patch(
            "src.core.services.dashboard_service.DashboardService.get_expense_breakdown"
        ) as mock_breakdown:
            mock_auth_repo.get_user_by_email.return_value = mock_user
            mock_auth_repo.get_user_by_id.return_value = mock_user
            mock_pwd_context.verify.return_value = True

            from src.interface.dashboard_dto import (
                CurrentMonthSummaryDTO,
            )

            mock_summary.return_value = CurrentMonthSummaryDTO(
                total_income=Decimal("0"),
                total_expenses=Decimal("0"),
                net_balance=Decimal("0"),
            )
            mock_trends.return_value = []
            mock_breakdown.return_value = []

            token = await get_auth_token(client, mock_user)
            response = await client.get(
                f"/api/dashboard/stats?entity_id={entity_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 200
    data = response.json()
    assert data["current_month_summary"]["total_income"] == "0"
    assert data["current_month_summary"]["total_expenses"] == "0"
    assert data["current_month_summary"]["net_balance"] == "0"
    assert data["monthly_trends"] == []
    assert data["expense_breakdown"] == []
    print("INFO [TestDashboard]: test_get_dashboard_stats_empty_data - PASSED")


@pytest.mark.asyncio
async def test_get_dashboard_stats_only_income() -> None:
    """Test dashboard stats with only income transactions."""
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
            "src.core.services.dashboard_service.DashboardService.get_current_month_summary"
        ) as mock_summary, patch(
            "src.core.services.dashboard_service.DashboardService.get_monthly_trends"
        ) as mock_trends, patch(
            "src.core.services.dashboard_service.DashboardService.get_expense_breakdown"
        ) as mock_breakdown:
            mock_auth_repo.get_user_by_email.return_value = mock_user
            mock_auth_repo.get_user_by_id.return_value = mock_user
            mock_pwd_context.verify.return_value = True

            from src.interface.dashboard_dto import (
                CurrentMonthSummaryDTO,
                MonthlyTotalDTO,
            )

            mock_summary.return_value = CurrentMonthSummaryDTO(
                total_income=Decimal("2500.00"),
                total_expenses=Decimal("0"),
                net_balance=Decimal("2500.00"),
            )
            mock_trends.return_value = [
                MonthlyTotalDTO(
                    month="Jan 2024",
                    year=2024,
                    month_number=1,
                    income=Decimal("2500.00"),
                    expenses=Decimal("0"),
                )
            ]
            mock_breakdown.return_value = []  # No expenses

            token = await get_auth_token(client, mock_user)
            response = await client.get(
                f"/api/dashboard/stats?entity_id={entity_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 200
    data = response.json()
    assert data["current_month_summary"]["total_income"] == "2500.00"
    assert data["current_month_summary"]["total_expenses"] == "0"
    assert data["current_month_summary"]["net_balance"] == "2500.00"
    assert data["expense_breakdown"] == []
    print("INFO [TestDashboard]: test_get_dashboard_stats_only_income - PASSED")


@pytest.mark.asyncio
async def test_get_dashboard_stats_only_expenses() -> None:
    """Test dashboard stats with only expense transactions."""
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
            "src.core.services.dashboard_service.DashboardService.get_current_month_summary"
        ) as mock_summary, patch(
            "src.core.services.dashboard_service.DashboardService.get_monthly_trends"
        ) as mock_trends, patch(
            "src.core.services.dashboard_service.DashboardService.get_expense_breakdown"
        ) as mock_breakdown:
            mock_auth_repo.get_user_by_email.return_value = mock_user
            mock_auth_repo.get_user_by_id.return_value = mock_user
            mock_pwd_context.verify.return_value = True

            from src.interface.dashboard_dto import (
                CategoryBreakdownDTO,
                CurrentMonthSummaryDTO,
                MonthlyTotalDTO,
            )

            mock_summary.return_value = CurrentMonthSummaryDTO(
                total_income=Decimal("0"),
                total_expenses=Decimal("800.00"),
                net_balance=Decimal("-800.00"),  # Negative balance
            )
            mock_trends.return_value = [
                MonthlyTotalDTO(
                    month="Jan 2024",
                    year=2024,
                    month_number=1,
                    income=Decimal("0"),
                    expenses=Decimal("800.00"),
                )
            ]
            mock_breakdown.return_value = [
                CategoryBreakdownDTO(
                    category_id=str(uuid4()),
                    category_name="Rent",
                    amount=Decimal("500.00"),
                    percentage=62.5,
                    color="#4287f5",
                ),
                CategoryBreakdownDTO(
                    category_id=str(uuid4()),
                    category_name="Utilities",
                    amount=Decimal("300.00"),
                    percentage=37.5,
                    color="#f54242",
                ),
            ]

            token = await get_auth_token(client, mock_user)
            response = await client.get(
                f"/api/dashboard/stats?entity_id={entity_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 200
    data = response.json()
    assert data["current_month_summary"]["total_income"] == "0"
    assert data["current_month_summary"]["total_expenses"] == "800.00"
    assert data["current_month_summary"]["net_balance"] == "-800.00"
    assert len(data["expense_breakdown"]) == 2
    print("INFO [TestDashboard]: test_get_dashboard_stats_only_expenses - PASSED")


@pytest.mark.asyncio
async def test_get_dashboard_stats_multiple_months() -> None:
    """Test dashboard stats with multiple months of data."""
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
            "src.core.services.dashboard_service.DashboardService.get_current_month_summary"
        ) as mock_summary, patch(
            "src.core.services.dashboard_service.DashboardService.get_monthly_trends"
        ) as mock_trends, patch(
            "src.core.services.dashboard_service.DashboardService.get_expense_breakdown"
        ) as mock_breakdown:
            mock_auth_repo.get_user_by_email.return_value = mock_user
            mock_auth_repo.get_user_by_id.return_value = mock_user
            mock_pwd_context.verify.return_value = True

            from src.interface.dashboard_dto import (
                CurrentMonthSummaryDTO,
                MonthlyTotalDTO,
            )

            mock_summary.return_value = CurrentMonthSummaryDTO(
                total_income=Decimal("3000.00"),
                total_expenses=Decimal("1500.00"),
                net_balance=Decimal("1500.00"),
            )
            mock_trends.return_value = [
                MonthlyTotalDTO(
                    month="Aug 2024",
                    year=2024,
                    month_number=8,
                    income=Decimal("2500.00"),
                    expenses=Decimal("1200.00"),
                ),
                MonthlyTotalDTO(
                    month="Sep 2024",
                    year=2024,
                    month_number=9,
                    income=Decimal("2800.00"),
                    expenses=Decimal("1400.00"),
                ),
                MonthlyTotalDTO(
                    month="Oct 2024",
                    year=2024,
                    month_number=10,
                    income=Decimal("3000.00"),
                    expenses=Decimal("1500.00"),
                ),
                MonthlyTotalDTO(
                    month="Nov 2024",
                    year=2024,
                    month_number=11,
                    income=Decimal("2700.00"),
                    expenses=Decimal("1300.00"),
                ),
                MonthlyTotalDTO(
                    month="Dec 2024",
                    year=2024,
                    month_number=12,
                    income=Decimal("3200.00"),
                    expenses=Decimal("1800.00"),
                ),
                MonthlyTotalDTO(
                    month="Jan 2025",
                    year=2025,
                    month_number=1,
                    income=Decimal("3000.00"),
                    expenses=Decimal("1500.00"),
                ),
            ]
            mock_breakdown.return_value = []

            token = await get_auth_token(client, mock_user)
            response = await client.get(
                f"/api/dashboard/stats?entity_id={entity_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 200
    data = response.json()
    assert len(data["monthly_trends"]) == 6
    print("INFO [TestDashboard]: test_get_dashboard_stats_multiple_months - PASSED")


@pytest.mark.asyncio
async def test_get_dashboard_stats_missing_entity_id() -> None:
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
                "/api/dashboard/stats",
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 422
    print("INFO [TestDashboard]: test_get_dashboard_stats_missing_entity_id - PASSED")
