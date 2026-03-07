"""Person endpoint routes."""

from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.adapter.rest.dependencies import get_current_user, get_db
from src.adapter.rest.rbac_dependencies import require_roles
from src.core.services.person_service import person_service
from src.interface.person_dto import (
    PersonCreateDTO,
    PersonResponseDTO,
    PersonType,
    PersonUpdateDTO,
)

router = APIRouter(prefix="/api/persons", tags=["Persons"])


@router.post("", response_model=PersonResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_person(
    data: PersonCreateDTO,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> PersonResponseDTO:
    """
    Create a new person in a restaurant.

    Args:
        data: Person creation data
        db: Database session
        current_user: Current authenticated user

    Returns:
        PersonResponseDTO: Created person information
    """
    print(f"INFO [PersonRoutes]: Create person request from user {current_user['email']}")

    user_id = UUID(current_user["id"])
    try:
        person = person_service.create_person(db, user_id, data)
        print(f"INFO [PersonRoutes]: Person '{person.name}' created successfully")
        return PersonResponseDTO.model_validate(person)
    except PermissionError as e:
        print(f"ERROR [PersonRoutes]: Access denied: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.get("/search", response_model=List[PersonResponseDTO])
async def search_persons(
    restaurant_id: UUID = Query(..., description="Restaurant UUID to search within"),
    query: str = Query("", description="Search query for person name"),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> List[PersonResponseDTO]:
    """
    Search persons by name within a restaurant.

    Args:
        restaurant_id: Restaurant UUID
        query: Search query string
        db: Database session
        current_user: Current authenticated user

    Returns:
        List of matching PersonResponseDTO objects
    """
    print(f"INFO [PersonRoutes]: Search persons request from user {current_user['email']} (query='{query}')")

    user_id = UUID(current_user["id"])
    try:
        persons = person_service.search_persons(db, user_id, restaurant_id, query)
        print(f"INFO [PersonRoutes]: Returning {len(persons)} search results")
        return [PersonResponseDTO.model_validate(p) for p in persons]
    except PermissionError as e:
        print(f"ERROR [PersonRoutes]: Access denied: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.get("", response_model=List[PersonResponseDTO])
async def list_persons(
    restaurant_id: UUID = Query(..., description="Restaurant UUID to list persons for"),
    type: Optional[PersonType] = Query(None, description="Filter by person type"),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> List[PersonResponseDTO]:
    """
    List all persons in a restaurant, with optional type filter.

    Args:
        restaurant_id: Restaurant UUID
        type: Optional person type filter
        db: Database session
        current_user: Current authenticated user

    Returns:
        List of PersonResponseDTO objects
    """
    print(f"INFO [PersonRoutes]: List persons request from user {current_user['email']} (restaurant={restaurant_id})")

    user_id = UUID(current_user["id"])
    type_filter = type.value if type else None
    try:
        persons = person_service.get_persons(db, user_id, restaurant_id, type_filter)
        print(f"INFO [PersonRoutes]: Returning {len(persons)} persons")
        return [PersonResponseDTO.model_validate(p) for p in persons]
    except PermissionError as e:
        print(f"ERROR [PersonRoutes]: Access denied: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.get("/{person_id}", response_model=PersonResponseDTO)
async def get_person(
    person_id: UUID,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> PersonResponseDTO:
    """
    Get a specific person by ID.

    Args:
        person_id: Person UUID
        db: Database session
        current_user: Current authenticated user

    Returns:
        PersonResponseDTO: Person information
    """
    print(f"INFO [PersonRoutes]: Get person {person_id} request from user {current_user['email']}")

    user_id = UUID(current_user["id"])
    try:
        person = person_service.get_person(db, user_id, person_id)
        print(f"INFO [PersonRoutes]: Returning person '{person.name}'")
        return PersonResponseDTO.model_validate(person)
    except PermissionError as e:
        print(f"ERROR [PersonRoutes]: Access denied: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except ValueError as e:
        print(f"ERROR [PersonRoutes]: Person not found: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.put("/{person_id}", response_model=PersonResponseDTO)
async def update_person(
    person_id: UUID,
    data: PersonUpdateDTO,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> PersonResponseDTO:
    """
    Update a person.

    Args:
        person_id: Person UUID
        data: Person update data
        db: Database session
        current_user: Current authenticated user

    Returns:
        PersonResponseDTO: Updated person information
    """
    print(f"INFO [PersonRoutes]: Update person {person_id} request from user {current_user['email']}")

    user_id = UUID(current_user["id"])
    try:
        person = person_service.update_person(db, user_id, person_id, data)
        print(f"INFO [PersonRoutes]: Person '{person.name}' updated successfully")
        return PersonResponseDTO.model_validate(person)
    except PermissionError as e:
        print(f"ERROR [PersonRoutes]: Access denied: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except ValueError as e:
        print(f"ERROR [PersonRoutes]: Person not found: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.delete("/{person_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_person(
    person_id: UUID,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_roles(["admin", "manager"])),
) -> None:
    """
    Delete a person.

    Only admin or manager roles can delete.

    Args:
        person_id: Person UUID
        db: Database session
        current_user: Current authenticated user (admin or manager)
    """
    print(f"INFO [PersonRoutes]: Delete person {person_id} request from user {current_user['email']}")

    user_id = UUID(current_user["id"])
    try:
        person_service.delete_person(db, user_id, person_id)
        print(f"INFO [PersonRoutes]: Person {person_id} deleted successfully")
    except PermissionError as e:
        print(f"ERROR [PersonRoutes]: Access denied: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except ValueError as e:
        print(f"ERROR [PersonRoutes]: Person not found: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
