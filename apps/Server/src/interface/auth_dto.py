"""Pydantic DTOs for authentication requests and responses."""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserRegisterDTO(BaseModel):
    """DTO for user registration request."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="Password (minimum 8 characters)")
    first_name: Optional[str] = Field(None, max_length=100, description="User first name")
    last_name: Optional[str] = Field(None, max_length=100, description="User last name")


class UserLoginDTO(BaseModel):
    """DTO for user login request."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class UserResponseDTO(BaseModel):
    """DTO for user information in responses."""

    id: UUID = Field(..., description="User unique identifier")
    email: str = Field(..., description="User email address")
    first_name: Optional[str] = Field(None, description="User first name")
    last_name: Optional[str] = Field(None, description="User last name")
    role: str = Field(..., description="User role (admin, manager, user, viewer)")
    is_active: bool = Field(..., description="Whether user account is active")

    model_config = {"from_attributes": True}


class TokenResponseDTO(BaseModel):
    """DTO for authentication token response."""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    user: UserResponseDTO = Field(..., description="Authenticated user information")
