"""User repository for database operations."""

from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from src.models.user import User


class UserRepository:
    """Repository for User database operations."""

    def create_user(
        self,
        db: Session,
        email: str,
        password_hash: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        role: str = "user",
    ) -> User:
        """
        Create a new user in the database.

        Args:
            db: Database session
            email: User email address
            password_hash: Hashed password
            first_name: User first name (optional)
            last_name: User last name (optional)
            role: User role (default: "user")

        Returns:
            Created User object
        """
        print(f"INFO [UserRepository]: Creating user with email {email}")
        user = User(
            email=email,
            password_hash=password_hash,
            first_name=first_name,
            last_name=last_name,
            role=role,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"INFO [UserRepository]: User created with id {user.id}")
        return user

    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        """
        Find a user by email address.

        Args:
            db: Database session
            email: User email address

        Returns:
            User object if found, None otherwise
        """
        print(f"INFO [UserRepository]: Looking up user by email {email}")
        user = db.query(User).filter(User.email == email).first()
        if user:
            print(f"INFO [UserRepository]: Found user with id {user.id}")
        else:
            print(f"INFO [UserRepository]: No user found with email {email}")
        return user

    def get_user_by_id(self, db: Session, user_id: UUID) -> Optional[User]:
        """
        Find a user by ID.

        Args:
            db: Database session
            user_id: User UUID

        Returns:
            User object if found, None otherwise
        """
        print(f"INFO [UserRepository]: Looking up user by id {user_id}")
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            print(f"INFO [UserRepository]: Found user {user.email}")
        else:
            print(f"INFO [UserRepository]: No user found with id {user_id}")
        return user

    def update_user(self, db: Session, user: User) -> User:
        """
        Update an existing user.

        Args:
            db: Database session
            user: User object with updated values

        Returns:
            Updated User object
        """
        print(f"INFO [UserRepository]: Updating user {user.id}")
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"INFO [UserRepository]: User {user.id} updated successfully")
        return user


# Singleton instance
user_repository = UserRepository()
