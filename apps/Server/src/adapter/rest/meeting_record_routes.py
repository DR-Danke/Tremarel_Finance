"""Meeting record API endpoint routes."""

from datetime import date
from typing import Any, Dict, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from src.adapter.rest.dependencies import get_current_user, get_db
from src.adapter.rest.rbac_dependencies import require_roles
from src.core.services.meeting_record_service import meeting_record_service
from src.interface.meeting_record_dto import (
    MeetingRecordCreateDTO,
    MeetingRecordFilterDTO,
    MeetingRecordListResponseDTO,
    MeetingRecordResponseDTO,
    MeetingRecordUpdateDTO,
)

router = APIRouter(prefix="/api/meeting-records", tags=["Meeting Records"])


@router.post("/", response_model=MeetingRecordResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_meeting_record(
    data: MeetingRecordCreateDTO,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MeetingRecordResponseDTO:
    """
    Create a new meeting record.

    Args:
        data: Meeting record creation data
        current_user: Current authenticated user
        db: Database session

    Returns:
        MeetingRecordResponseDTO: Created meeting record data
    """
    print(f"INFO [MeetingRecordRoutes]: Create meeting record request from user {current_user['id']}")

    record = meeting_record_service.create_meeting_record(db, data)

    print(f"INFO [MeetingRecordRoutes]: Meeting record {record.id} created successfully")
    return MeetingRecordResponseDTO.model_validate(record)


@router.get("/", response_model=MeetingRecordListResponseDTO)
async def list_meeting_records(
    entity_id: UUID = Query(..., description="Entity ID to filter meeting records"),
    prospect_id: Optional[UUID] = Query(None, description="Filter by prospect ID"),
    is_active: Optional[bool] = Query(True, description="Filter by active status"),
    meeting_date_from: Optional[date] = Query(None, description="Filter meetings from this date"),
    meeting_date_to: Optional[date] = Query(None, description="Filter meetings up to this date"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum records to return"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MeetingRecordListResponseDTO:
    """
    List meeting records for an entity with pagination and filters.

    Args:
        entity_id: Entity UUID to filter by
        prospect_id: Optional prospect UUID filter
        is_active: Optional active status filter (defaults to True)
        meeting_date_from: Optional start date filter
        meeting_date_to: Optional end date filter
        skip: Pagination offset
        limit: Maximum results to return
        current_user: Current authenticated user
        db: Database session

    Returns:
        MeetingRecordListResponseDTO: Paginated list of meeting records
    """
    print(f"INFO [MeetingRecordRoutes]: List meeting records request for entity {entity_id}")

    filters = MeetingRecordFilterDTO(
        prospect_id=prospect_id,
        is_active=is_active,
        meeting_date_from=meeting_date_from,
        meeting_date_to=meeting_date_to,
    )

    records, total = meeting_record_service.list_meeting_records(db, entity_id, filters, skip, limit)

    print(f"INFO [MeetingRecordRoutes]: Returning {len(records)} meeting records (total: {total})")
    return MeetingRecordListResponseDTO(
        meeting_records=[MeetingRecordResponseDTO.model_validate(r) for r in records],
        total=total,
    )


@router.get("/{record_id}", response_model=MeetingRecordResponseDTO)
async def get_meeting_record(
    record_id: UUID,
    entity_id: UUID = Query(..., description="Entity ID for validation"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MeetingRecordResponseDTO:
    """
    Get a single meeting record by ID.

    Args:
        record_id: MeetingRecord UUID
        entity_id: Entity UUID for validation
        current_user: Current authenticated user
        db: Database session

    Returns:
        MeetingRecordResponseDTO: Meeting record data

    Raises:
        HTTPException: 404 if record not found or doesn't belong to entity
    """
    print(f"INFO [MeetingRecordRoutes]: Get meeting record {record_id}")

    record = meeting_record_service.get_meeting_record(db, record_id, entity_id)
    if not record:
        print(f"ERROR [MeetingRecordRoutes]: Meeting record {record_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting record not found",
        )

    print(f"INFO [MeetingRecordRoutes]: Returning meeting record {record_id}")
    return MeetingRecordResponseDTO.model_validate(record)


@router.get("/{record_id}/html")
async def get_meeting_record_html(
    record_id: UUID,
    entity_id: UUID = Query(..., description="Entity ID for validation"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    """
    Download HTML output for a meeting record.

    Args:
        record_id: MeetingRecord UUID
        entity_id: Entity UUID for validation
        current_user: Current authenticated user
        db: Database session

    Returns:
        Response: HTML content with text/html media type

    Raises:
        HTTPException: 404 if record not found or has no html_output
    """
    print(f"INFO [MeetingRecordRoutes]: Get HTML for meeting record {record_id}")

    record = meeting_record_service.get_meeting_record(db, record_id, entity_id)
    if not record or not record.html_output:
        print(f"ERROR [MeetingRecordRoutes]: Meeting record {record_id} not found or no HTML output")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting record or HTML output not found",
        )

    print(f"INFO [MeetingRecordRoutes]: Returning HTML for meeting record {record_id}")
    return Response(content=record.html_output, media_type="text/html")


@router.put("/{record_id}", response_model=MeetingRecordResponseDTO)
async def update_meeting_record(
    record_id: UUID,
    data: MeetingRecordUpdateDTO,
    entity_id: UUID = Query(..., description="Entity ID for validation"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MeetingRecordResponseDTO:
    """
    Update an existing meeting record.

    Args:
        record_id: MeetingRecord UUID
        data: Update data
        entity_id: Entity UUID for validation
        current_user: Current authenticated user
        db: Database session

    Returns:
        MeetingRecordResponseDTO: Updated meeting record data

    Raises:
        HTTPException: 404 if record not found or doesn't belong to entity
    """
    print(f"INFO [MeetingRecordRoutes]: Update meeting record {record_id}")

    record = meeting_record_service.update_meeting_record(db, record_id, entity_id, data)
    if not record:
        print(f"ERROR [MeetingRecordRoutes]: Meeting record {record_id} not found or update failed")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting record not found",
        )

    print(f"INFO [MeetingRecordRoutes]: Meeting record {record_id} updated successfully")
    return MeetingRecordResponseDTO.model_validate(record)


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_meeting_record(
    record_id: UUID,
    entity_id: UUID = Query(..., description="Entity ID for validation"),
    current_user: Dict[str, Any] = Depends(require_roles(["admin", "manager"])),
    db: Session = Depends(get_db),
) -> None:
    """
    Delete a meeting record.

    Only admin or manager roles can delete meeting records.

    Args:
        record_id: MeetingRecord UUID
        entity_id: Entity UUID for validation
        current_user: Current authenticated user (must be admin or manager)
        db: Database session

    Raises:
        HTTPException: 404 if record not found or doesn't belong to entity
        HTTPException: 403 if user doesn't have required role
    """
    print(f"INFO [MeetingRecordRoutes]: Delete meeting record {record_id} by user {current_user['id']}")

    success = meeting_record_service.delete_meeting_record(db, record_id, entity_id)
    if not success:
        print(f"ERROR [MeetingRecordRoutes]: Meeting record {record_id} not found or delete failed")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting record not found",
        )

    print(f"INFO [MeetingRecordRoutes]: Meeting record {record_id} deleted successfully")
