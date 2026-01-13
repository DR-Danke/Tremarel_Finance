"""Pydantic DTOs for authentication endpoints."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserRegisterRequest(BaseModel):
    """Request DTO for user registration."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")
    first_name: Optional[str] = Field(None, max_length=100, description="User first name")
    last_name: Optional[str] = Field(None, max_length=100, description="User last name")

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password meets minimum requirements."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v


class UserLoginRequest(BaseModel):
    """Request DTO for user login."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class TokenResponse(BaseModel):
    """Response DTO for authentication tokens."""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")


class UserResponse(BaseModel):
    """Response DTO for user information."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="User unique identifier")
    email: str = Field(..., description="User email address")
    first_name: Optional[str] = Field(None, description="User first name")
    last_name: Optional[str] = Field(None, description="User last name")
    role: str = Field(..., description="User role (admin, manager, user, viewer)")
    is_active: bool = Field(..., description="Whether user account is active")
    created_at: datetime = Field(..., description="Account creation timestamp")


class AuthTokenPayload(BaseModel):
    """JWT token payload structure."""

    sub: str = Field(..., description="Subject (user ID)")
    email: str = Field(..., description="User email")
    role: str = Field(..., description="User role")
    exp: int = Field(..., description="Expiration timestamp")


print("INFO [AuthDTO]: Auth DTOs loaded")
