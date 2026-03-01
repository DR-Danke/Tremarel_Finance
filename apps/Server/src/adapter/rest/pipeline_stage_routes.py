"""Pipeline stage and stage transition API endpoint routes."""

from typing import Any, Dict, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.adapter.rest.dependencies import get_current_user, get_db
from src.adapter.rest.rbac_dependencies import require_roles
from src.core.services.pipeline_stage_service import pipeline_stage_service
from src.interface.pipeline_stage_dto import (
    PipelineStageCreateDTO,
    PipelineStageListResponseDTO,
    PipelineStageResponseDTO,
    PipelineStageUpdateDTO,
)
from src.interface.stage_transition_dto import (
    StageTransitionListResponseDTO,
    StageTransitionResponseDTO,
)

router = APIRouter(prefix="/api/pipeline-stages", tags=["Pipeline Stages"])


class SeedRequestDTO(BaseModel):
    """DTO for seed default stages request."""

    entity_id: UUID = Field(..., description="Entity ID to seed stages for")


@router.post("/", response_model=PipelineStageResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_pipeline_stage(
    data: PipelineStageCreateDTO,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PipelineStageResponseDTO:
    """
    Create a new pipeline stage.

    Args:
        data: Pipeline stage creation data
        current_user: Current authenticated user
        db: Database session

    Returns:
        PipelineStageResponseDTO: Created pipeline stage data
    """
    print(f"INFO [PipelineStageRoutes]: Create stage request from user {current_user['id']}")

    stage = pipeline_stage_service.create_stage(db, data)

    print(f"INFO [PipelineStageRoutes]: Stage {stage.id} created successfully")
    return PipelineStageResponseDTO.model_validate(stage)


@router.get("/", response_model=PipelineStageListResponseDTO)
async def list_pipeline_stages(
    entity_id: UUID = Query(..., description="Entity ID to filter stages"),
    active_only: bool = Query(True, description="Filter to active stages only"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum records to return"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PipelineStageListResponseDTO:
    """
    List pipeline stages for an entity.

    Args:
        entity_id: Entity UUID to filter by
        active_only: Whether to return only active stages
        skip: Pagination offset
        limit: Maximum results to return
        current_user: Current authenticated user
        db: Database session

    Returns:
        PipelineStageListResponseDTO: Paginated list of pipeline stages
    """
    print(f"INFO [PipelineStageRoutes]: List stages request for entity {entity_id}")

    stages, total = pipeline_stage_service.list_stages(db, entity_id, active_only)

    print(f"INFO [PipelineStageRoutes]: Returning {len(stages)} stages (total: {total})")
    return PipelineStageListResponseDTO(
        stages=[PipelineStageResponseDTO.model_validate(s) for s in stages],
        total=total,
    )


@router.get("/{stage_id}", response_model=PipelineStageResponseDTO)
async def get_pipeline_stage(
    stage_id: UUID,
    entity_id: UUID = Query(..., description="Entity ID for validation"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PipelineStageResponseDTO:
    """
    Get a single pipeline stage by ID.

    Args:
        stage_id: PipelineStage UUID
        entity_id: Entity UUID for validation
        current_user: Current authenticated user
        db: Database session

    Returns:
        PipelineStageResponseDTO: Pipeline stage data

    Raises:
        HTTPException: 404 if stage not found or doesn't belong to entity
    """
    print(f"INFO [PipelineStageRoutes]: Get stage {stage_id}")

    stage = pipeline_stage_service.get_stage(db, stage_id, entity_id)
    if not stage:
        print(f"ERROR [PipelineStageRoutes]: Stage {stage_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pipeline stage not found",
        )

    print(f"INFO [PipelineStageRoutes]: Returning stage {stage_id}")
    return PipelineStageResponseDTO.model_validate(stage)


@router.put("/{stage_id}", response_model=PipelineStageResponseDTO)
async def update_pipeline_stage(
    stage_id: UUID,
    data: PipelineStageUpdateDTO,
    entity_id: UUID = Query(..., description="Entity ID for validation"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PipelineStageResponseDTO:
    """
    Update an existing pipeline stage.

    Args:
        stage_id: PipelineStage UUID
        data: Update data
        entity_id: Entity UUID for validation
        current_user: Current authenticated user
        db: Database session

    Returns:
        PipelineStageResponseDTO: Updated pipeline stage data

    Raises:
        HTTPException: 404 if stage not found or doesn't belong to entity
    """
    print(f"INFO [PipelineStageRoutes]: Update stage {stage_id}")

    stage = pipeline_stage_service.update_stage(db, stage_id, entity_id, data)
    if not stage:
        print(f"ERROR [PipelineStageRoutes]: Stage {stage_id} not found or update failed")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pipeline stage not found",
        )

    print(f"INFO [PipelineStageRoutes]: Stage {stage_id} updated successfully")
    return PipelineStageResponseDTO.model_validate(stage)


@router.delete("/{stage_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pipeline_stage(
    stage_id: UUID,
    entity_id: UUID = Query(..., description="Entity ID for validation"),
    current_user: Dict[str, Any] = Depends(require_roles(["admin", "manager"])),
    db: Session = Depends(get_db),
) -> None:
    """
    Delete a pipeline stage.

    Only admin or manager roles can delete pipeline stages.

    Args:
        stage_id: PipelineStage UUID
        entity_id: Entity UUID for validation
        current_user: Current authenticated user (must be admin or manager)
        db: Database session

    Raises:
        HTTPException: 404 if stage not found or doesn't belong to entity
        HTTPException: 403 if user doesn't have required role
    """
    print(f"INFO [PipelineStageRoutes]: Delete stage {stage_id} by user {current_user['id']}")

    success = pipeline_stage_service.delete_stage(db, stage_id, entity_id)
    if not success:
        print(f"ERROR [PipelineStageRoutes]: Stage {stage_id} not found or delete failed")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pipeline stage not found",
        )

    print(f"INFO [PipelineStageRoutes]: Stage {stage_id} deleted successfully")


@router.post("/seed", response_model=List[PipelineStageResponseDTO], status_code=status.HTTP_201_CREATED)
async def seed_default_stages(
    data: SeedRequestDTO,
    current_user: Dict[str, Any] = Depends(require_roles(["admin", "manager"])),
    db: Session = Depends(get_db),
) -> List[PipelineStageResponseDTO]:
    """
    Seed default pipeline stages for an entity.

    Creates the seven standard stages (lead, contacted, qualified, proposal,
    negotiation, won, lost). Skips if entity already has stages.

    Only admin or manager roles can seed stages.

    Args:
        data: Seed request with entity_id
        current_user: Current authenticated user (must be admin or manager)
        db: Database session

    Returns:
        List of created pipeline stage DTOs
    """
    print(f"INFO [PipelineStageRoutes]: Seed stages request for entity {data.entity_id} by user {current_user['id']}")

    stages = pipeline_stage_service.seed_default_stages(db, data.entity_id)

    print(f"INFO [PipelineStageRoutes]: Seeded {len(stages)} stages for entity {data.entity_id}")
    return [PipelineStageResponseDTO.model_validate(s) for s in stages]


@router.get("/transitions/{prospect_id}", response_model=StageTransitionListResponseDTO)
async def get_prospect_transitions(
    prospect_id: UUID,
    entity_id: UUID = Query(..., description="Entity ID for validation"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum records to return"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StageTransitionListResponseDTO:
    """
    Get stage transition history for a prospect.

    Args:
        prospect_id: Prospect UUID
        entity_id: Entity UUID for validation
        skip: Pagination offset
        limit: Maximum results to return
        current_user: Current authenticated user
        db: Database session

    Returns:
        StageTransitionListResponseDTO: Paginated list of stage transitions
    """
    print(f"INFO [PipelineStageRoutes]: Get transitions for prospect {prospect_id}")

    transitions, total = pipeline_stage_service.get_prospect_transitions(
        db, prospect_id, entity_id, skip, limit
    )

    print(f"INFO [PipelineStageRoutes]: Returning {len(transitions)} transitions (total: {total})")
    return StageTransitionListResponseDTO(
        transitions=[StageTransitionResponseDTO.model_validate(t) for t in transitions],
        total=total,
    )
