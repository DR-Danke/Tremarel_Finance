"""Dashboard API endpoint routes."""

from typing import Any, Dict
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.adapter.rest.dependencies import get_current_user, get_db
from src.core.services.dashboard_service import dashboard_service
from src.interface.dashboard_dto import DashboardStatsResponseDTO

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardStatsResponseDTO)
async def get_dashboard_stats(
    entity_id: UUID = Query(..., description="Entity ID to get dashboard stats for"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DashboardStatsResponseDTO:
    """
    Get dashboard statistics for an entity.

    Returns current month summary (income, expenses, net balance),
    monthly trends for the last 6 months, and expense breakdown by category.

    Args:
        entity_id: Entity UUID to get stats for
        current_user: Current authenticated user
        db: Database session

    Returns:
        DashboardStatsResponseDTO: Complete dashboard statistics
    """
    print(f"INFO [DashboardRoutes]: Dashboard stats request from user {current_user['id']} for entity {entity_id}")

    stats = dashboard_service.get_dashboard_stats(db, entity_id)

    print("INFO [DashboardRoutes]: Dashboard stats returned successfully")
    return stats
