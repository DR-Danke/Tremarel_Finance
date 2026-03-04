"""Unit tests for Invoice OCR DTOs, InvoiceItem model, and StubOCRAdapter."""

from decimal import Decimal

import pytest

from src.core.services.ocr_service import InvoiceItem
from src.interface.invoice_dto import (
    InvoiceItemDTO,
    InvoiceMatchedItemDTO,
    InvoiceProcessingResultDTO,
)


# ============================================================================
# InvoiceItem Pydantic Model Tests
# ============================================================================


def test_invoice_item_valid() -> None:
    """Test InvoiceItem creation with valid data."""
    item = InvoiceItem(
        product_name="Tomate",
        quantity=Decimal("10.0"),
        unit="kg",
        unit_price=Decimal("2.50"),
        supplier_name="Distribuidora ABC",
    )
    assert item.product_name == "Tomate"
    assert item.quantity == Decimal("10.0")
    assert item.unit == "kg"
    assert item.unit_price == Decimal("2.50")
    assert item.supplier_name == "Distribuidora ABC"
    print("INFO [TestInvoiceOCR]: test_invoice_item_valid - PASSED")


def test_invoice_item_without_supplier() -> None:
    """Test InvoiceItem creation without optional supplier_name."""
    item = InvoiceItem(
        product_name="Aceite",
        quantity=Decimal("5.0"),
        unit="litro",
        unit_price=Decimal("8.75"),
    )
    assert item.supplier_name is None
    print("INFO [TestInvoiceOCR]: test_invoice_item_without_supplier - PASSED")


def test_invoice_item_missing_required_field() -> None:
    """Test InvoiceItem raises error when required field is missing."""
    with pytest.raises(Exception):
        InvoiceItem(
            quantity=Decimal("10.0"),
            unit="kg",
            unit_price=Decimal("2.50"),
        )
    print("INFO [TestInvoiceOCR]: test_invoice_item_missing_required_field - PASSED")


def test_invoice_item_negative_quantity() -> None:
    """Test InvoiceItem rejects negative quantity."""
    with pytest.raises(Exception):
        InvoiceItem(
            product_name="Tomate",
            quantity=Decimal("-1.0"),
            unit="kg",
            unit_price=Decimal("2.50"),
        )
    print("INFO [TestInvoiceOCR]: test_invoice_item_negative_quantity - PASSED")


def test_invoice_item_negative_unit_price() -> None:
    """Test InvoiceItem rejects negative unit_price."""
    with pytest.raises(Exception):
        InvoiceItem(
            product_name="Tomate",
            quantity=Decimal("10.0"),
            unit="kg",
            unit_price=Decimal("-2.50"),
        )
    print("INFO [TestInvoiceOCR]: test_invoice_item_negative_unit_price - PASSED")


def test_invoice_item_from_string_decimals() -> None:
    """Test InvoiceItem accepts string decimal values (from OCR output)."""
    item = InvoiceItem(
        product_name="Harina",
        quantity="20.0",
        unit="kg",
        unit_price="1.20",
    )
    assert item.quantity == Decimal("20.0")
    assert item.unit_price == Decimal("1.20")
    print("INFO [TestInvoiceOCR]: test_invoice_item_from_string_decimals - PASSED")


# ============================================================================
# Invoice DTO Tests
# ============================================================================


def test_invoice_item_dto_serialization() -> None:
    """Test InvoiceItemDTO serialization."""
    dto = InvoiceItemDTO(
        product_name="Tomate",
        quantity=Decimal("10.0"),
        unit="kg",
        unit_price=Decimal("2.50"),
        supplier_name="Distribuidora ABC",
    )
    data = dto.model_dump()
    assert data["product_name"] == "Tomate"
    assert data["quantity"] == Decimal("10.0")
    print("INFO [TestInvoiceOCR]: test_invoice_item_dto_serialization - PASSED")


def test_invoice_processing_result_dto() -> None:
    """Test InvoiceProcessingResultDTO serialization."""
    from uuid import uuid4

    doc_id = uuid4()
    resource_id = uuid4()

    item_dto = InvoiceItemDTO(
        product_name="Tomate",
        quantity=Decimal("10.0"),
        unit="kg",
        unit_price=Decimal("2.50"),
    )
    matched = InvoiceMatchedItemDTO(item=item_dto, resource_id=resource_id)
    unmatched = InvoiceItemDTO(
        product_name="Salsa BBQ Especial",
        quantity=Decimal("3.0"),
        unit="litro",
        unit_price=Decimal("12.00"),
    )

    result = InvoiceProcessingResultDTO(
        document_id=doc_id,
        matched_count=1,
        unmatched_count=1,
        matched_items=[matched],
        unmatched_items=[unmatched],
        processing_status="completed",
    )
    assert result.matched_count == 1
    assert result.unmatched_count == 1
    assert result.matched_items[0].resource_id == resource_id
    assert result.unmatched_items[0].product_name == "Salsa BBQ Especial"
    assert result.processing_status == "completed"
    print("INFO [TestInvoiceOCR]: test_invoice_processing_result_dto - PASSED")


# ============================================================================
# StubOCRAdapter Tests
# ============================================================================


@pytest.mark.asyncio
async def test_stub_ocr_adapter_returns_mock_data() -> None:
    """Test StubOCRAdapter returns well-formed mock invoice data."""
    from src.adapter.ocr_stub_adapter import StubOCRAdapter

    adapter = StubOCRAdapter()
    items = await adapter.extract_invoice_items("fake://invoice.pdf")

    assert isinstance(items, list)
    assert len(items) >= 3

    for item in items:
        assert "product_name" in item
        assert "quantity" in item
        assert "unit" in item
        assert "unit_price" in item

    # Verify the last item is the "unmatched" one
    assert items[-1]["product_name"] == "Salsa BBQ Especial"
    print("INFO [TestInvoiceOCR]: test_stub_ocr_adapter_returns_mock_data - PASSED")


@pytest.mark.asyncio
async def test_ocr_service_process_invoice() -> None:
    """Test OCRService transforms raw dicts into InvoiceItem instances."""
    from src.adapter.ocr_stub_adapter import StubOCRAdapter
    from src.core.services.ocr_service import OCRService

    service = OCRService(StubOCRAdapter())
    items = await service.process_invoice("fake://invoice.pdf")

    assert len(items) >= 3
    for item in items:
        assert isinstance(item, InvoiceItem)
        assert item.quantity > 0
        assert item.unit_price > 0
    print("INFO [TestInvoiceOCR]: test_ocr_service_process_invoice - PASSED")
