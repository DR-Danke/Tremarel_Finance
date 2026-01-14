"""Authentication service for user registration, login, and JWT management."""

from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

import bcrypt
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from src.config.settings import get_settings
from src.interface.auth_dto import UserRegisterDTO
from src.models.user import User
from src.repository.user_repository import user_repository

settings = get_settings()


class AuthService:
    """Service for authentication business logic."""

    def hash_password(self, password: str) -> str:
        """
        Hash a password using bcrypt.

        Args:
            password: Plain text password

        Returns:
            Hashed password string
        """
        print("INFO [AuthService]: Hashing password")
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain password against a hashed password.

        Args:
            plain_password: Plain text password to verify
            hashed_password: Hashed password to compare against

        Returns:
            True if password matches, False otherwise
        """
        print("INFO [AuthService]: Verifying password")
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

    def create_access_token(self, data: dict) -> str:
        """
        Create a JWT access token.

        Args:
            data: Payload data to encode in the token

        Returns:
            Encoded JWT token string
        """
        print("INFO [AuthService]: Creating access token")
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )
        print(f"INFO [AuthService]: Access token created, expires at {expire}")
        return encoded_jwt

    def decode_access_token(self, token: str) -> Optional[dict]:
        """
        Decode and validate a JWT access token.

        Args:
            token: JWT token string to decode

        Returns:
            Decoded payload dict if valid, None if invalid or expired
        """
        print("INFO [AuthService]: Decoding access token")
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
            print("INFO [AuthService]: Access token decoded successfully")
            return payload
        except JWTError as e:
            print(f"ERROR [AuthService]: Failed to decode token: {str(e)}")
            return None

    def register_user(self, db: Session, user_data: UserRegisterDTO) -> User:
        """
        Register a new user.

        Args:
            db: Database session
            user_data: User registration data

        Returns:
            Created User object

        Raises:
            ValueError: If email is already registered
        """
        print(f"INFO [AuthService]: Registering new user with email {user_data.email}")

        # Check if email already exists
        existing_user = user_repository.get_user_by_email(db, user_data.email)
        if existing_user:
            print(f"ERROR [AuthService]: Email {user_data.email} already registered")
            raise ValueError("Email already registered")

        # Hash password and create user
        password_hash = self.hash_password(user_data.password)
        user = user_repository.create_user(
            db=db,
            email=user_data.email,
            password_hash=password_hash,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
        )

        print(f"INFO [AuthService]: User {user.id} registered successfully")
        return user

    def authenticate_user(self, db: Session, email: str, password: str) -> Optional[User]:
        """
        Authenticate a user by email and password.

        Args:
            db: Database session
            email: User email address
            password: Plain text password

        Returns:
            User object if authentication succeeds, None otherwise
        """
        print(f"INFO [AuthService]: Authenticating user {email}")

        # Find user by email
        user = user_repository.get_user_by_email(db, email)
        if not user:
            print(f"ERROR [AuthService]: User {email} not found")
            return None

        # Verify password
        if not self.verify_password(password, user.password_hash):
            print(f"ERROR [AuthService]: Invalid password for user {email}")
            return None

        # Check if user is active
        if not user.is_active:
            print(f"ERROR [AuthService]: User {email} is inactive")
            return None

        print(f"INFO [AuthService]: User {email} authenticated successfully")
        return user

    def get_user_by_id(self, db: Session, user_id: UUID) -> Optional[User]:
        """
        Get a user by their ID.

        Args:
            db: Database session
            user_id: User UUID

        Returns:
            User object if found, None otherwise
        """
        return user_repository.get_user_by_id(db, user_id)


# Singleton instance
auth_service = AuthService()
