"""Reports API endpoint routes."""

from datetime import date
from typing import Any, Dict
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from src.adapter.rest.dependencies import get_current_user, get_db
from src.core.services.reports_service import reports_service
from src.interface.reports_dto import ReportDataResponseDTO

router = APIRouter(prefix="/api/reports", tags=["Reports"])


@router.get("/data", response_model=ReportDataResponseDTO)
async def get_report_data(
    entity_id: UUID = Query(..., description="Entity ID to get report data for"),
    start_date: date = Query(..., description="Start date for the report period"),
    end_date: date = Query(..., description="End date for the report period"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ReportDataResponseDTO:
    """
    Get report data for an entity within a date range.

    Returns summary totals, monthly income vs expense comparison,
    and category breakdown with percentages.

    Args:
        entity_id: Entity UUID to get report data for
        start_date: Start date for the report period
        end_date: End date for the report period
        current_user: Current authenticated user
        db: Database session

    Returns:
        ReportDataResponseDTO: Complete report data
    """
    print(
        f"INFO [ReportsRoutes]: Report data request from user {current_user['id']} "
        f"for entity {entity_id} ({start_date} to {end_date})"
    )

    report_data = reports_service.get_report_data(
        db, entity_id, start_date, end_date
    )

    print("INFO [ReportsRoutes]: Report data returned successfully")
    return report_data


@router.get("/export/csv")
async def export_csv(
    entity_id: UUID = Query(..., description="Entity ID to export data for"),
    start_date: date = Query(..., description="Start date for the export period"),
    end_date: date = Query(..., description="End date for the export period"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StreamingResponse:
    """
    Export transactions to CSV format.

    Returns a streaming CSV file with all transactions in the date range.

    Args:
        entity_id: Entity UUID to export data for
        start_date: Start date for the export period
        end_date: End date for the export period
        current_user: Current authenticated user
        db: Database session

    Returns:
        StreamingResponse: CSV file download
    """
    print(
        f"INFO [ReportsRoutes]: CSV export request from user {current_user['id']} "
        f"for entity {entity_id} ({start_date} to {end_date})"
    )

    csv_content = reports_service.export_transactions_csv(
        db, entity_id, start_date, end_date
    )

    # Generate filename with date range
    filename = f"transactions_{start_date.isoformat()}_{end_date.isoformat()}.csv"

    print(f"INFO [ReportsRoutes]: CSV export generated: {filename}")

    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Type": "text/csv; charset=utf-8",
        },
    )
