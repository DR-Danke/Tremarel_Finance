"""Recurring template API endpoint routes."""

from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from uuid import UUID

from src.adapter.rest.dependencies import get_current_user, get_db
from src.adapter.rest.rbac_dependencies import require_roles
from src.core.services.recurring_template_service import recurring_template_service
from src.interface.recurring_template_dto import (
    RecurringTemplateCreateDTO,
    RecurringTemplateListResponseDTO,
    RecurringTemplateResponseDTO,
    RecurringTemplateUpdateDTO,
)

router = APIRouter(prefix="/api/recurring-templates", tags=["Recurring Templates"])


@router.post("/", response_model=RecurringTemplateResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_recurring_template(
    data: RecurringTemplateCreateDTO,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RecurringTemplateResponseDTO:
    """
    Create a new recurring template.

    Creates a recurring transaction template for the specified entity. Requires authentication.

    Args:
        data: Template creation data
        current_user: Current authenticated user
        db: Database session

    Returns:
        RecurringTemplateResponseDTO: Created template data
    """
    print(f"INFO [RecurringTemplateRoutes]: Create template request from user {current_user['id']}")

    template = recurring_template_service.create_template(db, data)

    print(f"INFO [RecurringTemplateRoutes]: Template {template.id} created successfully")
    return RecurringTemplateResponseDTO.model_validate(template)


@router.get("/", response_model=RecurringTemplateListResponseDTO)
async def list_recurring_templates(
    entity_id: UUID = Query(..., description="Entity ID to filter templates"),
    include_inactive: bool = Query(False, description="Include inactive templates"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum records to return"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RecurringTemplateListResponseDTO:
    """
    List recurring templates for an entity.

    Supports pagination and optional filtering to include inactive templates.

    Args:
        entity_id: Entity UUID to filter by
        include_inactive: Whether to include inactive templates
        skip: Pagination offset
        limit: Maximum results to return
        current_user: Current authenticated user
        db: Database session

    Returns:
        RecurringTemplateListResponseDTO: List of templates with total count
    """
    print(f"INFO [RecurringTemplateRoutes]: List templates request for entity {entity_id}")

    templates, total = recurring_template_service.list_templates(
        db=db,
        entity_id=entity_id,
        include_inactive=include_inactive,
        skip=skip,
        limit=limit,
    )

    print(f"INFO [RecurringTemplateRoutes]: Returning {len(templates)} templates (total: {total})")
    return RecurringTemplateListResponseDTO(
        templates=[RecurringTemplateResponseDTO.model_validate(t) for t in templates],
        total=total,
    )


@router.get("/{template_id}", response_model=RecurringTemplateResponseDTO)
async def get_recurring_template(
    template_id: UUID,
    entity_id: UUID = Query(..., description="Entity ID for validation"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RecurringTemplateResponseDTO:
    """
    Get a single recurring template by ID.

    Args:
        template_id: Template UUID
        entity_id: Entity UUID for validation
        current_user: Current authenticated user
        db: Database session

    Returns:
        RecurringTemplateResponseDTO: Template data

    Raises:
        HTTPException: 404 if template not found or doesn't belong to entity
    """
    print(f"INFO [RecurringTemplateRoutes]: Get template {template_id}")

    template = recurring_template_service.get_template(db, template_id, entity_id)
    if not template:
        print(f"ERROR [RecurringTemplateRoutes]: Template {template_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recurring template not found",
        )

    print(f"INFO [RecurringTemplateRoutes]: Returning template {template_id}")
    return RecurringTemplateResponseDTO.model_validate(template)


@router.put("/{template_id}", response_model=RecurringTemplateResponseDTO)
async def update_recurring_template(
    template_id: UUID,
    data: RecurringTemplateUpdateDTO,
    entity_id: UUID = Query(..., description="Entity ID for validation"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RecurringTemplateResponseDTO:
    """
    Update an existing recurring template.

    Args:
        template_id: Template UUID
        data: Update data
        entity_id: Entity UUID for validation
        current_user: Current authenticated user
        db: Database session

    Returns:
        RecurringTemplateResponseDTO: Updated template data

    Raises:
        HTTPException: 404 if template not found or doesn't belong to entity
    """
    print(f"INFO [RecurringTemplateRoutes]: Update template {template_id}")

    template = recurring_template_service.update_template(db, template_id, entity_id, data)
    if not template:
        print(f"ERROR [RecurringTemplateRoutes]: Template {template_id} not found or update failed")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recurring template not found",
        )

    print(f"INFO [RecurringTemplateRoutes]: Template {template_id} updated successfully")
    return RecurringTemplateResponseDTO.model_validate(template)


@router.post("/{template_id}/deactivate", response_model=RecurringTemplateResponseDTO)
async def deactivate_recurring_template(
    template_id: UUID,
    entity_id: UUID = Query(..., description="Entity ID for validation"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RecurringTemplateResponseDTO:
    """
    Deactivate a recurring template (soft delete).

    This preserves the template for historical reference but prevents it
    from being used for new transactions.

    Args:
        template_id: Template UUID
        entity_id: Entity UUID for validation
        current_user: Current authenticated user
        db: Database session

    Returns:
        RecurringTemplateResponseDTO: Deactivated template data

    Raises:
        HTTPException: 404 if template not found or doesn't belong to entity
    """
    print(f"INFO [RecurringTemplateRoutes]: Deactivate template {template_id}")

    template = recurring_template_service.deactivate_template(db, template_id, entity_id)
    if not template:
        print(f"ERROR [RecurringTemplateRoutes]: Template {template_id} not found or deactivation failed")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recurring template not found",
        )

    print(f"INFO [RecurringTemplateRoutes]: Template {template_id} deactivated successfully")
    return RecurringTemplateResponseDTO.model_validate(template)


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recurring_template(
    template_id: UUID,
    entity_id: UUID = Query(..., description="Entity ID for validation"),
    current_user: Dict[str, Any] = Depends(require_roles(["admin", "manager"])),
    db: Session = Depends(get_db),
) -> None:
    """
    Delete a recurring template (hard delete).

    Only admin or manager roles can permanently delete templates.
    Consider using deactivate endpoint instead to preserve history.

    Args:
        template_id: Template UUID
        entity_id: Entity UUID for validation
        current_user: Current authenticated user (must be admin or manager)
        db: Database session

    Raises:
        HTTPException: 404 if template not found or doesn't belong to entity
        HTTPException: 403 if user doesn't have required role
    """
    print(f"INFO [RecurringTemplateRoutes]: Delete template {template_id} by user {current_user['id']}")

    success = recurring_template_service.delete_template(db, template_id, entity_id)
    if not success:
        print(f"ERROR [RecurringTemplateRoutes]: Template {template_id} not found or delete failed")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recurring template not found",
        )

    print(f"INFO [RecurringTemplateRoutes]: Template {template_id} deleted successfully")
