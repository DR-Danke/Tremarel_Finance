"""Person repository for database operations."""

from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from src.models.person import Person


class PersonRepository:
    """Repository for Person database operations."""

    def create(
        self,
        db: Session,
        restaurant_id: UUID,
        name: str,
        role: str,
        email: Optional[str],
        whatsapp: Optional[str],
        person_type: str,
    ) -> Person:
        """
        Create a new person in a restaurant.

        Args:
            db: Database session
            restaurant_id: Restaurant UUID
            name: Person full name
            role: Person role (free-text)
            email: Person email (optional)
            whatsapp: WhatsApp number (optional)
            person_type: Person type (employee, supplier, owner)

        Returns:
            Created Person object
        """
        print(f"INFO [PersonRepository]: Creating person '{name}' for restaurant {restaurant_id}")
        person = Person(
            restaurant_id=restaurant_id,
            name=name,
            role=role,
            email=email,
            whatsapp=whatsapp,
            type=person_type,
        )
        db.add(person)
        db.commit()
        db.refresh(person)
        print(f"INFO [PersonRepository]: Person created with id {person.id}")
        return person

    def get_by_id(self, db: Session, person_id: UUID) -> Optional[Person]:
        """
        Find a person by ID.

        Args:
            db: Database session
            person_id: Person UUID

        Returns:
            Person object if found, None otherwise
        """
        print(f"INFO [PersonRepository]: Looking up person by id {person_id}")
        person = db.query(Person).filter(Person.id == person_id).first()
        if person:
            print(f"INFO [PersonRepository]: Found person '{person.name}'")
        else:
            print(f"INFO [PersonRepository]: No person found with id {person_id}")
        return person

    def get_by_restaurant(
        self,
        db: Session,
        restaurant_id: UUID,
        type_filter: Optional[str] = None,
    ) -> list[Person]:
        """
        Get all persons in a restaurant, with optional type filter.

        Args:
            db: Database session
            restaurant_id: Restaurant UUID
            type_filter: Optional person type to filter by

        Returns:
            List of Person objects
        """
        print(f"INFO [PersonRepository]: Getting persons for restaurant {restaurant_id} (type_filter={type_filter})")
        query = db.query(Person).filter(Person.restaurant_id == restaurant_id)
        if type_filter:
            query = query.filter(Person.type == type_filter)
        persons = query.all()
        print(f"INFO [PersonRepository]: Found {len(persons)} persons for restaurant {restaurant_id}")
        return persons

    def update(self, db: Session, person: Person) -> Person:
        """
        Update an existing person.

        Args:
            db: Database session
            person: Person object with updated values

        Returns:
            Updated Person object
        """
        print(f"INFO [PersonRepository]: Updating person {person.id}")
        db.add(person)
        db.commit()
        db.refresh(person)
        print(f"INFO [PersonRepository]: Person {person.id} updated successfully")
        return person

    def delete(self, db: Session, person_id: UUID) -> bool:
        """
        Delete a person from the database.

        Args:
            db: Database session
            person_id: Person UUID

        Returns:
            True if deleted, False if not found
        """
        print(f"INFO [PersonRepository]: Deleting person {person_id}")
        person = db.query(Person).filter(Person.id == person_id).first()
        if person:
            db.delete(person)
            db.commit()
            print(f"INFO [PersonRepository]: Person {person_id} deleted successfully")
            return True
        print(f"INFO [PersonRepository]: Person {person_id} not found for deletion")
        return False

    def search(self, db: Session, restaurant_id: UUID, query: str) -> list[Person]:
        """
        Search persons by name within a restaurant using ILIKE.

        Args:
            db: Database session
            restaurant_id: Restaurant UUID
            query: Search query string

        Returns:
            List of matching Person objects
        """
        print(f"INFO [PersonRepository]: Searching persons in restaurant {restaurant_id} with query '{query}'")
        persons = (
            db.query(Person)
            .filter(Person.restaurant_id == restaurant_id, Person.name.ilike(f"%{query}%"))
            .all()
        )
        print(f"INFO [PersonRepository]: Found {len(persons)} matching persons")
        return persons


# Singleton instance
person_repository = PersonRepository()
