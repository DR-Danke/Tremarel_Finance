"""User repository for database operations."""

from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from src.models.user_model import User


class UserRepository:
    """
    Repository for User database operations.

    Handles all data access layer operations for the users table.
    Following Clean Architecture, this class only handles database operations.
    """

    def create(
        self,
        db: Session,
        email: str,
        password_hash: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
    ) -> User:
        """
        Create a new user in the database.

        Args:
            db: Database session
            email: User email address
            password_hash: Hashed password
            first_name: Optional first name
            last_name: Optional last name

        Returns:
            Created User object
        """
        print(f"INFO [UserRepository]: Creating user with email {email}")
        user = User(
            email=email,
            password_hash=password_hash,
            first_name=first_name,
            last_name=last_name,
            role="user",
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"INFO [UserRepository]: User created with id {user.id}")
        return user

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """
        Get a user by email address.

        Args:
            db: Database session
            email: User email address

        Returns:
            User object if found, None otherwise
        """
        print(f"INFO [UserRepository]: Looking up user by email {email}")
        user = db.query(User).filter(User.email == email).first()
        if user:
            print(f"INFO [UserRepository]: User found with id {user.id}")
        else:
            print(f"INFO [UserRepository]: No user found with email {email}")
        return user

    def get_by_id(self, db: Session, user_id: UUID) -> Optional[User]:
        """
        Get a user by ID.

        Args:
            db: Database session
            user_id: User UUID

        Returns:
            User object if found, None otherwise
        """
        print(f"INFO [UserRepository]: Looking up user by id {user_id}")
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            print(f"INFO [UserRepository]: User found with email {user.email}")
        else:
            print(f"INFO [UserRepository]: No user found with id {user_id}")
        return user

    def email_exists(self, db: Session, email: str) -> bool:
        """
        Check if an email already exists in the database.

        Args:
            db: Database session
            email: Email address to check

        Returns:
            True if email exists, False otherwise
        """
        print(f"INFO [UserRepository]: Checking if email exists: {email}")
        exists = db.query(User).filter(User.email == email).first() is not None
        print(f"INFO [UserRepository]: Email exists: {exists}")
        return exists


# Singleton instance for use throughout the application
user_repository = UserRepository()

print("INFO [UserRepository]: UserRepository loaded")
