"""Person service for business logic operations."""

from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from src.interface.person_dto import PersonCreateDTO, PersonUpdateDTO
from src.models.person import Person
from src.repository.person_repository import person_repository
from src.repository.restaurant_repository import restaurant_repository


class PersonService:
    """Service for person business logic with restaurant-scoped authorization."""

    def _check_restaurant_access(self, db: Session, user_id: UUID, restaurant_id: UUID) -> None:
        """
        Check that a user has membership in a restaurant.

        Args:
            db: Database session
            user_id: User UUID
            restaurant_id: Restaurant UUID

        Raises:
            PermissionError: If user doesn't have access to the restaurant
        """
        role = restaurant_repository.get_user_restaurant_role(db, user_id, restaurant_id)
        if role is None:
            print(f"ERROR [PersonService]: User {user_id} doesn't have access to restaurant {restaurant_id}")
            raise PermissionError("User doesn't have access to this restaurant")

    def create_person(
        self,
        db: Session,
        user_id: UUID,
        data: PersonCreateDTO,
    ) -> Person:
        """
        Create a new person in a restaurant.

        Args:
            db: Database session
            user_id: ID of the user creating the person
            data: Person creation data

        Returns:
            Created Person object

        Raises:
            PermissionError: If user doesn't have access to the restaurant
        """
        print(f"INFO [PersonService]: Creating person '{data.name}' in restaurant {data.restaurant_id} by user {user_id}")

        self._check_restaurant_access(db, user_id, data.restaurant_id)

        person = person_repository.create(
            db=db,
            restaurant_id=data.restaurant_id,
            name=data.name,
            role=data.role,
            email=data.email,
            whatsapp=data.whatsapp,
            person_type=data.type.value,
        )

        print(f"INFO [PersonService]: Person '{person.name}' created with id {person.id}")
        return person

    def get_persons(
        self,
        db: Session,
        user_id: UUID,
        restaurant_id: UUID,
        type_filter: Optional[str] = None,
    ) -> list[Person]:
        """
        Get all persons in a restaurant.

        Args:
            db: Database session
            user_id: User UUID
            restaurant_id: Restaurant UUID
            type_filter: Optional person type to filter by

        Returns:
            List of Person objects

        Raises:
            PermissionError: If user doesn't have access to the restaurant
        """
        print(f"INFO [PersonService]: Getting persons for restaurant {restaurant_id} by user {user_id}")

        self._check_restaurant_access(db, user_id, restaurant_id)

        return person_repository.get_by_restaurant(db, restaurant_id, type_filter)

    def get_person(
        self,
        db: Session,
        user_id: UUID,
        person_id: UUID,
    ) -> Person:
        """
        Get a person by ID if user has access to the person's restaurant.

        Args:
            db: Database session
            user_id: User UUID
            person_id: Person UUID

        Returns:
            Person object

        Raises:
            PermissionError: If user doesn't have access to the restaurant
            ValueError: If person not found
        """
        print(f"INFO [PersonService]: Getting person {person_id} for user {user_id}")

        person = person_repository.get_by_id(db, person_id)
        if person is None:
            print(f"ERROR [PersonService]: Person {person_id} not found")
            raise ValueError("Person not found")

        self._check_restaurant_access(db, user_id, person.restaurant_id)

        return person

    def update_person(
        self,
        db: Session,
        user_id: UUID,
        person_id: UUID,
        data: PersonUpdateDTO,
    ) -> Person:
        """
        Update a person if user has access to the person's restaurant.

        Args:
            db: Database session
            user_id: User UUID
            person_id: Person UUID
            data: Person update data

        Returns:
            Updated Person object

        Raises:
            PermissionError: If user doesn't have access to the restaurant
            ValueError: If person not found
        """
        print(f"INFO [PersonService]: Updating person {person_id} by user {user_id}")

        person = person_repository.get_by_id(db, person_id)
        if person is None:
            print(f"ERROR [PersonService]: Person {person_id} not found")
            raise ValueError("Person not found")

        self._check_restaurant_access(db, user_id, person.restaurant_id)

        # Update fields if provided
        if data.name is not None:
            person.name = data.name
        if data.role is not None:
            person.role = data.role
        if data.email is not None:
            person.email = data.email
        if data.whatsapp is not None:
            person.whatsapp = data.whatsapp
        if data.type is not None:
            person.type = data.type.value

        updated_person = person_repository.update(db, person)
        print(f"INFO [PersonService]: Person {person_id} updated successfully")
        return updated_person

    def delete_person(
        self,
        db: Session,
        user_id: UUID,
        person_id: UUID,
    ) -> bool:
        """
        Delete a person if user has access to the person's restaurant.

        Args:
            db: Database session
            user_id: User UUID
            person_id: Person UUID

        Returns:
            True if deleted

        Raises:
            PermissionError: If user doesn't have access to the restaurant
            ValueError: If person not found
        """
        print(f"INFO [PersonService]: Deleting person {person_id} by user {user_id}")

        person = person_repository.get_by_id(db, person_id)
        if person is None:
            print(f"ERROR [PersonService]: Person {person_id} not found")
            raise ValueError("Person not found")

        self._check_restaurant_access(db, user_id, person.restaurant_id)

        deleted = person_repository.delete(db, person_id)
        if not deleted:
            print(f"ERROR [PersonService]: Person {person_id} not found for deletion")
            raise ValueError("Person not found")

        print(f"INFO [PersonService]: Person {person_id} deleted successfully")
        return True

    def search_persons(
        self,
        db: Session,
        user_id: UUID,
        restaurant_id: UUID,
        query: str,
    ) -> list[Person]:
        """
        Search persons by name within a restaurant.

        Args:
            db: Database session
            user_id: User UUID
            restaurant_id: Restaurant UUID
            query: Search query string

        Returns:
            List of matching Person objects

        Raises:
            PermissionError: If user doesn't have access to the restaurant
        """
        print(f"INFO [PersonService]: Searching persons in restaurant {restaurant_id} with query '{query}' by user {user_id}")

        self._check_restaurant_access(db, user_id, restaurant_id)

        return person_repository.search(db, restaurant_id, query)


# Singleton instance
person_service = PersonService()
