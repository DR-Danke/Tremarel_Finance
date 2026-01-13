"""Entity endpoint routes."""

from typing import Any, Dict, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.adapter.rest.dependencies import get_current_user, get_db
from src.core.services.entity_service import entity_service
from src.interface.entity_dto import (
    EntityCreateDTO,
    EntityMemberDTO,
    EntityResponseDTO,
    EntityUpdateDTO,
    UserEntityCreateDTO,
    UserEntityResponseDTO,
)

router = APIRouter(prefix="/api/entities", tags=["Entities"])


@router.post("", response_model=EntityResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_entity(
    entity_data: EntityCreateDTO,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> EntityResponseDTO:
    """
    Create a new entity.

    Creates a new entity and adds the current user as admin.

    Args:
        entity_data: Entity creation data
        db: Database session
        current_user: Current authenticated user

    Returns:
        EntityResponseDTO: Created entity information
    """
    print(f"INFO [EntityRoutes]: Create entity request from user {current_user['email']}")

    user_id = UUID(current_user["id"])
    entity = entity_service.create_entity(db, user_id, entity_data)

    print(f"INFO [EntityRoutes]: Entity '{entity.name}' created successfully")
    return EntityResponseDTO.model_validate(entity)


@router.get("", response_model=List[EntityResponseDTO])
async def list_entities(
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> List[EntityResponseDTO]:
    """
    List all entities the current user belongs to.

    Args:
        db: Database session
        current_user: Current authenticated user

    Returns:
        List of EntityResponseDTO objects
    """
    print(f"INFO [EntityRoutes]: List entities request from user {current_user['email']}")

    user_id = UUID(current_user["id"])
    entities = entity_service.get_user_entities(db, user_id)

    print(f"INFO [EntityRoutes]: Returning {len(entities)} entities")
    return [EntityResponseDTO.model_validate(entity) for entity in entities]


@router.get("/{entity_id}", response_model=EntityResponseDTO)
async def get_entity(
    entity_id: UUID,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> EntityResponseDTO:
    """
    Get a specific entity by ID.

    Args:
        entity_id: Entity UUID
        db: Database session
        current_user: Current authenticated user

    Returns:
        EntityResponseDTO: Entity information

    Raises:
        HTTPException: 403 if user doesn't have access, 404 if not found
    """
    print(f"INFO [EntityRoutes]: Get entity {entity_id} request from user {current_user['email']}")

    user_id = UUID(current_user["id"])
    try:
        entity = entity_service.get_entity(db, entity_id, user_id)
        if entity is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Entity not found",
            )
        print(f"INFO [EntityRoutes]: Returning entity '{entity.name}'")
        return EntityResponseDTO.model_validate(entity)
    except PermissionError as e:
        print(f"ERROR [EntityRoutes]: Access denied: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.put("/{entity_id}", response_model=EntityResponseDTO)
async def update_entity(
    entity_id: UUID,
    entity_data: EntityUpdateDTO,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> EntityResponseDTO:
    """
    Update an entity.

    Only admin or manager can update entity.

    Args:
        entity_id: Entity UUID
        entity_data: Entity update data
        db: Database session
        current_user: Current authenticated user

    Returns:
        EntityResponseDTO: Updated entity information

    Raises:
        HTTPException: 403 if insufficient permissions, 404 if not found
    """
    print(f"INFO [EntityRoutes]: Update entity {entity_id} request from user {current_user['email']}")

    user_id = UUID(current_user["id"])
    try:
        entity = entity_service.update_entity(db, entity_id, user_id, entity_data)
        print(f"INFO [EntityRoutes]: Entity '{entity.name}' updated successfully")
        return EntityResponseDTO.model_validate(entity)
    except PermissionError as e:
        print(f"ERROR [EntityRoutes]: Permission denied: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except ValueError as e:
        print(f"ERROR [EntityRoutes]: Entity not found: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.delete("/{entity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_entity(
    entity_id: UUID,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> None:
    """
    Delete an entity.

    Only admin can delete entity.

    Args:
        entity_id: Entity UUID
        db: Database session
        current_user: Current authenticated user

    Raises:
        HTTPException: 403 if not admin, 404 if not found
    """
    print(f"INFO [EntityRoutes]: Delete entity {entity_id} request from user {current_user['email']}")

    user_id = UUID(current_user["id"])
    try:
        entity_service.delete_entity(db, entity_id, user_id)
        print(f"INFO [EntityRoutes]: Entity {entity_id} deleted successfully")
    except PermissionError as e:
        print(f"ERROR [EntityRoutes]: Permission denied: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except ValueError as e:
        print(f"ERROR [EntityRoutes]: Entity not found: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post("/{entity_id}/members", response_model=UserEntityResponseDTO, status_code=status.HTTP_201_CREATED)
async def add_member(
    entity_id: UUID,
    member_data: UserEntityCreateDTO,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> UserEntityResponseDTO:
    """
    Add a member to an entity.

    Only admin or manager can add members.

    Args:
        entity_id: Entity UUID
        member_data: Member data including user_id and role
        db: Database session
        current_user: Current authenticated user

    Returns:
        UserEntityResponseDTO: Created membership information

    Raises:
        HTTPException: 403 if insufficient permissions, 400 if already a member
    """
    print(f"INFO [EntityRoutes]: Add member to entity {entity_id} request from user {current_user['email']}")

    user_id = UUID(current_user["id"])
    try:
        user_entity = entity_service.add_member(
            db,
            entity_id,
            user_id,
            member_data.user_id,
            member_data.role,
        )
        print(f"INFO [EntityRoutes]: Member {member_data.user_id} added to entity {entity_id}")
        return UserEntityResponseDTO.model_validate(user_entity)
    except PermissionError as e:
        print(f"ERROR [EntityRoutes]: Permission denied: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except ValueError as e:
        print(f"ERROR [EntityRoutes]: Bad request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/{entity_id}/members/{member_user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
    entity_id: UUID,
    member_user_id: UUID,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> None:
    """
    Remove a member from an entity.

    Only admin can remove members.

    Args:
        entity_id: Entity UUID
        member_user_id: User UUID to remove
        db: Database session
        current_user: Current authenticated user

    Raises:
        HTTPException: 403 if not admin, 400 if removing last admin or user not a member
    """
    print(f"INFO [EntityRoutes]: Remove member {member_user_id} from entity {entity_id} by {current_user['email']}")

    user_id = UUID(current_user["id"])
    try:
        entity_service.remove_member(db, entity_id, user_id, member_user_id)
        print(f"INFO [EntityRoutes]: Member {member_user_id} removed from entity {entity_id}")
    except PermissionError as e:
        print(f"ERROR [EntityRoutes]: Permission denied: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except ValueError as e:
        print(f"ERROR [EntityRoutes]: Bad request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/{entity_id}/members", response_model=List[EntityMemberDTO])
async def list_members(
    entity_id: UUID,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> List[EntityMemberDTO]:
    """
    List all members of an entity.

    Any entity member can view the member list.

    Args:
        entity_id: Entity UUID
        db: Database session
        current_user: Current authenticated user

    Returns:
        List of EntityMemberDTO objects

    Raises:
        HTTPException: 403 if user is not a member of the entity
    """
    print(f"INFO [EntityRoutes]: List members for entity {entity_id} by {current_user['email']}")

    user_id = UUID(current_user["id"])
    try:
        members = entity_service.get_entity_members(db, entity_id, user_id)
        print(f"INFO [EntityRoutes]: Returning {len(members)} members")
        return [EntityMemberDTO(**member) for member in members]
    except PermissionError as e:
        print(f"ERROR [EntityRoutes]: Permission denied: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
