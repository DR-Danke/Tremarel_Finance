"""Pydantic DTOs for document requests and responses."""

from datetime import date, datetime, timedelta
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class DocumentCreateDTO(BaseModel):
    """DTO for document creation request."""

    restaurant_id: UUID = Field(..., description="Restaurant UUID this document belongs to")
    type: str = Field(..., min_length=1, max_length=100, description="Document type (e.g., contrato, permiso, factura, licencia)")
    issue_date: Optional[date] = Field(None, description="Date the document was issued")
    expiration_date: Optional[date] = Field(None, description="Date the document expires")
    person_id: Optional[UUID] = Field(None, description="Person UUID linked to this document")
    description: Optional[str] = Field(None, description="Document description or notes")

    @model_validator(mode="after")
    def validate_dates(self) -> "DocumentCreateDTO":
        """Validate that expiration_date is after issue_date if both are provided."""
        if self.issue_date is not None and self.expiration_date is not None:
            if self.expiration_date <= self.issue_date:
                raise ValueError("expiration_date must be after issue_date")
        return self


class DocumentUpdateDTO(BaseModel):
    """DTO for document update request (partial update)."""

    type: Optional[str] = Field(None, min_length=1, max_length=100, description="Document type")
    issue_date: Optional[date] = Field(None, description="Date the document was issued")
    expiration_date: Optional[date] = Field(None, description="Date the document expires")
    person_id: Optional[UUID] = Field(None, description="Person UUID linked to this document")
    description: Optional[str] = Field(None, description="Document description or notes")


class DocumentResponseDTO(BaseModel):
    """DTO for document information in responses."""

    id: UUID = Field(..., description="Document unique identifier")
    restaurant_id: UUID = Field(..., description="Restaurant UUID")
    type: str = Field(..., description="Document type")
    file_url: Optional[str] = Field(None, description="URL or path to the uploaded file")
    issue_date: Optional[date] = Field(None, description="Date the document was issued")
    expiration_date: Optional[date] = Field(None, description="Date the document expires")
    person_id: Optional[UUID] = Field(None, description="Person UUID linked to this document")
    description: Optional[str] = Field(None, description="Document description or notes")
    expiration_status: str = Field("valid", description="Computed expiration status: valid, expiring_soon, expired")
    created_at: datetime = Field(..., description="Document creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Document last update timestamp")

    model_config = {"from_attributes": True}

    @model_validator(mode="before")
    @classmethod
    def compute_expiration_status(cls, data: object) -> object:
        """Compute expiration_status from expiration_date."""
        today = date.today()
        threshold = today + timedelta(days=30)

        if hasattr(data, "expiration_date"):
            # ORM model object
            exp_date = data.expiration_date
            if exp_date is None:
                status = "valid"
            elif exp_date < today:
                status = "expired"
            elif exp_date <= threshold:
                status = "expiring_soon"
            else:
                status = "valid"

            obj_dict = {
                "id": data.id,
                "restaurant_id": data.restaurant_id,
                "type": data.type,
                "file_url": getattr(data, "file_url", None),
                "issue_date": getattr(data, "issue_date", None),
                "expiration_date": exp_date,
                "person_id": getattr(data, "person_id", None),
                "description": getattr(data, "description", None),
                "expiration_status": status,
                "created_at": data.created_at,
                "updated_at": getattr(data, "updated_at", None),
            }
            return obj_dict
        elif isinstance(data, dict):
            exp_date = data.get("expiration_date")
            if exp_date is None:
                data["expiration_status"] = "valid"
            elif isinstance(exp_date, date) and exp_date < today:
                data["expiration_status"] = "expired"
            elif isinstance(exp_date, date) and exp_date <= threshold:
                data["expiration_status"] = "expiring_soon"
            else:
                data["expiration_status"] = "valid"
        return data
