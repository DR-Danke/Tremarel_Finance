"""OCR service abstraction for invoice data extraction."""

from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class InvoiceItem(BaseModel):
    """Pydantic model for a single extracted invoice line item."""

    product_name: str = Field(..., description="Product name extracted from invoice")
    quantity: Decimal = Field(..., gt=0, description="Quantity of the product")
    unit: str = Field(..., description="Unit of measurement")
    unit_price: Decimal = Field(..., gt=0, description="Unit price of the product")
    supplier_name: Optional[str] = Field(None, description="Supplier name extracted from invoice")


class OCRAdapter(ABC):
    """Abstract base class for OCR provider adapters."""

    @abstractmethod
    async def extract_invoice_items(self, file_url: str) -> list[dict]:
        """
        Extract line items from an invoice file.

        Args:
            file_url: URL or path to the invoice file

        Returns:
            List of dicts with keys: product_name, quantity, unit, unit_price, supplier_name
        """


class OCRService:
    """Service wrapper that uses an OCR adapter to extract and validate invoice items."""

    def __init__(self, adapter: OCRAdapter) -> None:
        self.adapter = adapter
        print(f"INFO [OCRService]: Initialized with adapter {type(adapter).__name__}")

    async def process_invoice(self, file_url: str) -> list[InvoiceItem]:
        """
        Extract invoice items from a file and validate them as InvoiceItem models.

        Args:
            file_url: URL or path to the invoice file

        Returns:
            List of validated InvoiceItem objects
        """
        print(f"INFO [OCRService]: Processing invoice from {file_url}")
        raw_items = await self.adapter.extract_invoice_items(file_url)
        print(f"INFO [OCRService]: Extracted {len(raw_items)} raw items from OCR")

        items = []
        for raw in raw_items:
            item = InvoiceItem(**raw)
            items.append(item)

        print(f"INFO [OCRService]: Validated {len(items)} invoice items")
        return items
