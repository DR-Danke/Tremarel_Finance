"""Authentication service for user registration, login, and JWT management."""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from src.config.settings import get_settings
from src.models.user_model import User
from src.repository.user_repository import user_repository

# Password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """
    Authentication service for handling user auth operations.

    Provides password hashing, JWT token management, and user authentication.
    Following Clean Architecture, this is the core business logic layer.
    """

    def __init__(self) -> None:
        """Initialize AuthService with settings."""
        self.settings = get_settings()
        print("INFO [AuthService]: AuthService initialized")

    def hash_password(self, password: str) -> str:
        """
        Hash a password using bcrypt.

        Args:
            password: Plain text password

        Returns:
            Hashed password string
        """
        print("INFO [AuthService]: Hashing password")
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.

        Args:
            plain_password: Plain text password to verify
            hashed_password: Stored hashed password

        Returns:
            True if password matches, False otherwise
        """
        print("INFO [AuthService]: Verifying password")
        return pwd_context.verify(plain_password, hashed_password)

    def create_access_token(self, user_id: str, email: str, role: str) -> str:
        """
        Create a JWT access token.

        Args:
            user_id: User UUID as string
            email: User email address
            role: User role

        Returns:
            Encoded JWT token string
        """
        print(f"INFO [AuthService]: Creating access token for user {email}")
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=self.settings.JWT_EXPIRE_MINUTES
        )
        to_encode: Dict[str, Any] = {
            "sub": user_id,
            "email": email,
            "role": role,
            "exp": expire,
        }
        encoded_jwt = jwt.encode(
            to_encode,
            self.settings.JWT_SECRET_KEY,
            algorithm=self.settings.JWT_ALGORITHM,
        )
        print(f"INFO [AuthService]: Access token created, expires at {expire.isoformat()}")
        return encoded_jwt

    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Decode and validate a JWT token.

        Args:
            token: JWT token string

        Returns:
            Decoded token payload dict if valid, None otherwise
        """
        print("INFO [AuthService]: Decoding JWT token")
        try:
            payload = jwt.decode(
                token,
                self.settings.JWT_SECRET_KEY,
                algorithms=[self.settings.JWT_ALGORITHM],
            )
            user_id = payload.get("sub")
            email = payload.get("email")
            role = payload.get("role")

            if user_id is None or email is None or role is None:
                print("ERROR [AuthService]: Token missing required claims")
                return None

            print(f"INFO [AuthService]: Token decoded successfully for user {email}")
            return {
                "id": user_id,
                "email": email,
                "role": role,
            }
        except JWTError as e:
            print(f"ERROR [AuthService]: JWT decode error: {str(e)}")
            return None

    def register_user(
        self,
        db: Session,
        email: str,
        password: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
    ) -> Optional[User]:
        """
        Register a new user.

        Args:
            db: Database session
            email: User email address
            password: Plain text password
            first_name: Optional first name
            last_name: Optional last name

        Returns:
            Created User object if successful, None if email already exists
        """
        print(f"INFO [AuthService]: Registering new user with email {email}")

        # Check if email already exists
        if user_repository.email_exists(db, email):
            print(f"ERROR [AuthService]: Email already registered: {email}")
            return None

        # Hash password and create user
        password_hash = self.hash_password(password)
        user = user_repository.create(
            db=db,
            email=email,
            password_hash=password_hash,
            first_name=first_name,
            last_name=last_name,
        )
        print(f"INFO [AuthService]: User registered successfully with id {user.id}")
        return user

    def authenticate_user(
        self, db: Session, email: str, password: str
    ) -> Optional[User]:
        """
        Authenticate a user with email and password.

        Args:
            db: Database session
            email: User email address
            password: Plain text password

        Returns:
            User object if authentication successful, None otherwise
        """
        print(f"INFO [AuthService]: Authenticating user {email}")

        user = user_repository.get_by_email(db, email)
        if not user:
            print(f"ERROR [AuthService]: User not found: {email}")
            return None

        if not user.is_active:
            print(f"ERROR [AuthService]: User account is inactive: {email}")
            return None

        if not self.verify_password(password, user.password_hash):
            print(f"ERROR [AuthService]: Invalid password for user: {email}")
            return None

        print(f"INFO [AuthService]: User authenticated successfully: {email}")
        return user


# Singleton instance for use throughout the application
auth_service = AuthService()

print("INFO [AuthService]: AuthService loaded")
