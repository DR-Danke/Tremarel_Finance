"""Pydantic DTOs for invoice OCR processing requests and responses."""

from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class InvoiceItemDTO(BaseModel):
    """DTO for a single extracted invoice line item."""

    product_name: str = Field(..., description="Product name extracted from invoice")
    quantity: Decimal = Field(..., description="Quantity of the product")
    unit: str = Field(..., description="Unit of measurement")
    unit_price: Decimal = Field(..., description="Unit price of the product")
    supplier_name: Optional[str] = Field(None, description="Supplier name extracted from invoice")


class InvoiceMatchedItemDTO(BaseModel):
    """DTO for an invoice item that matched an existing resource."""

    item: InvoiceItemDTO = Field(..., description="The matched invoice item")
    resource_id: UUID = Field(..., description="UUID of the matched resource")


class InvoiceProcessingResultDTO(BaseModel):
    """DTO for the complete invoice processing result."""

    document_id: UUID = Field(..., description="UUID of the processed document")
    matched_count: int = Field(..., description="Number of items matched to existing resources")
    unmatched_count: int = Field(..., description="Number of items that could not be matched")
    matched_items: list[InvoiceMatchedItemDTO] = Field(default_factory=list, description="List of matched items with resource IDs")
    unmatched_items: list[InvoiceItemDTO] = Field(default_factory=list, description="List of unmatched items for manual review")
    processing_status: str = Field(..., description="Processing status: completed or failed")
