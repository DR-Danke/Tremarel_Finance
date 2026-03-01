"""Prospect CRUD API endpoint routes."""

from typing import Any, Dict, Literal, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.adapter.rest.dependencies import get_current_user, get_db
from src.adapter.rest.rbac_dependencies import require_roles
from src.core.services.prospect_service import prospect_service
from src.interface.prospect_dto import (
    ProspectCreateDTO,
    ProspectListResponseDTO,
    ProspectResponseDTO,
    ProspectUpdateDTO,
)

router = APIRouter(prefix="/api/prospects", tags=["Prospects"])


class ProspectStageUpdateDTO(BaseModel):
    """DTO for prospect stage update request (route-specific)."""

    new_stage: Literal["lead", "contacted", "qualified", "proposal", "negotiation", "won", "lost"] = Field(
        ..., description="New pipeline stage"
    )
    notes: Optional[str] = Field(None, description="Optional transition notes")


@router.post("/", response_model=ProspectResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_prospect(
    data: ProspectCreateDTO,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProspectResponseDTO:
    """
    Create a new prospect.

    Args:
        data: Prospect creation data
        current_user: Current authenticated user
        db: Database session

    Returns:
        ProspectResponseDTO: Created prospect data
    """
    print(f"INFO [ProspectRoutes]: Create prospect request from user {current_user['id']}")

    prospect = prospect_service.create_prospect(db, data)

    print(f"INFO [ProspectRoutes]: Prospect {prospect.id} created successfully")
    return ProspectResponseDTO.model_validate(prospect)


@router.get("/", response_model=ProspectListResponseDTO)
async def list_prospects(
    entity_id: UUID = Query(..., description="Entity ID to filter prospects"),
    stage: Optional[str] = Query(None, description="Filter by pipeline stage"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    source: Optional[str] = Query(None, description="Filter by prospect source"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum records to return"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProspectListResponseDTO:
    """
    List prospects for an entity with optional filters.

    Args:
        entity_id: Entity UUID to filter by
        stage: Optional pipeline stage filter
        is_active: Optional active status filter
        source: Optional source filter
        skip: Pagination offset
        limit: Maximum results to return
        current_user: Current authenticated user
        db: Database session

    Returns:
        ProspectListResponseDTO: Paginated list of prospects
    """
    print(f"INFO [ProspectRoutes]: List prospects request for entity {entity_id}")

    prospects, total = prospect_service.list_prospects(
        db, entity_id, stage, is_active, source, skip, limit
    )

    print(f"INFO [ProspectRoutes]: Returning {len(prospects)} prospects (total: {total})")
    return ProspectListResponseDTO(
        prospects=[ProspectResponseDTO.model_validate(p) for p in prospects],
        total=total,
    )


@router.get("/{prospect_id}", response_model=ProspectResponseDTO)
async def get_prospect(
    prospect_id: UUID,
    entity_id: UUID = Query(..., description="Entity ID for validation"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProspectResponseDTO:
    """
    Get a single prospect by ID.

    Args:
        prospect_id: Prospect UUID
        entity_id: Entity UUID for validation
        current_user: Current authenticated user
        db: Database session

    Returns:
        ProspectResponseDTO: Prospect data

    Raises:
        HTTPException: 404 if prospect not found or doesn't belong to entity
    """
    print(f"INFO [ProspectRoutes]: Get prospect {prospect_id}")

    prospect = prospect_service.get_prospect(db, prospect_id, entity_id)
    if not prospect:
        print(f"ERROR [ProspectRoutes]: Prospect {prospect_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prospect not found",
        )

    print(f"INFO [ProspectRoutes]: Returning prospect {prospect_id}")
    return ProspectResponseDTO.model_validate(prospect)


@router.put("/{prospect_id}", response_model=ProspectResponseDTO)
async def update_prospect(
    prospect_id: UUID,
    data: ProspectUpdateDTO,
    entity_id: UUID = Query(..., description="Entity ID for validation"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProspectResponseDTO:
    """
    Update an existing prospect.

    Args:
        prospect_id: Prospect UUID
        data: Update data
        entity_id: Entity UUID for validation
        current_user: Current authenticated user
        db: Database session

    Returns:
        ProspectResponseDTO: Updated prospect data

    Raises:
        HTTPException: 404 if prospect not found or doesn't belong to entity
    """
    print(f"INFO [ProspectRoutes]: Update prospect {prospect_id}")

    prospect = prospect_service.update_prospect(db, prospect_id, entity_id, data)
    if not prospect:
        print(f"ERROR [ProspectRoutes]: Prospect {prospect_id} not found or update failed")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prospect not found",
        )

    print(f"INFO [ProspectRoutes]: Prospect {prospect_id} updated successfully")
    return ProspectResponseDTO.model_validate(prospect)


@router.patch("/{prospect_id}/stage", response_model=ProspectResponseDTO)
async def update_prospect_stage(
    prospect_id: UUID,
    data: ProspectStageUpdateDTO,
    entity_id: UUID = Query(..., description="Entity ID for validation"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProspectResponseDTO:
    """
    Update a prospect's pipeline stage with audit trail tracking.

    Looks up PipelineStage records by name, updates the prospect's stage,
    and creates an immutable StageTransition audit record.

    Args:
        prospect_id: Prospect UUID
        data: Stage update data with new_stage and optional notes
        entity_id: Entity UUID for validation
        current_user: Current authenticated user
        db: Database session

    Returns:
        ProspectResponseDTO: Updated prospect data

    Raises:
        HTTPException: 404 if prospect not found or doesn't belong to entity
    """
    print(f"INFO [ProspectRoutes]: Update stage for prospect {prospect_id} to '{data.new_stage}'")

    prospect = prospect_service.update_prospect_stage(
        db=db,
        prospect_id=prospect_id,
        entity_id=entity_id,
        new_stage=data.new_stage,
        user_id=UUID(current_user["id"]),
        notes=data.notes,
    )
    if not prospect:
        print(f"ERROR [ProspectRoutes]: Prospect {prospect_id} not found or stage update failed")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prospect not found",
        )

    print(f"INFO [ProspectRoutes]: Prospect {prospect_id} stage updated to '{data.new_stage}'")
    return ProspectResponseDTO.model_validate(prospect)


@router.delete("/{prospect_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_prospect(
    prospect_id: UUID,
    entity_id: UUID = Query(..., description="Entity ID for validation"),
    current_user: Dict[str, Any] = Depends(require_roles(["admin", "manager"])),
    db: Session = Depends(get_db),
) -> None:
    """
    Delete a prospect.

    Only admin or manager roles can delete prospects.

    Args:
        prospect_id: Prospect UUID
        entity_id: Entity UUID for validation
        current_user: Current authenticated user (must be admin or manager)
        db: Database session

    Raises:
        HTTPException: 404 if prospect not found or doesn't belong to entity
        HTTPException: 403 if user doesn't have required role
    """
    print(f"INFO [ProspectRoutes]: Delete prospect {prospect_id} by user {current_user['id']}")

    success = prospect_service.delete_prospect(db, prospect_id, entity_id)
    if not success:
        print(f"ERROR [ProspectRoutes]: Prospect {prospect_id} not found or delete failed")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prospect not found",
        )

    print(f"INFO [ProspectRoutes]: Prospect {prospect_id} deleted successfully")
