"""Stub OCR adapter returning mock invoice data for development and testing."""

# TODO: Implement real OCR adapters (Google Cloud Vision, AWS Textract, OpenAI Vision)
# by creating new classes that implement OCRAdapter and swapping in InvoiceProcessor.

from src.core.services.ocr_service import OCRAdapter


class StubOCRAdapter(OCRAdapter):
    """Stub OCR adapter that returns hardcoded mock invoice data."""

    async def extract_invoice_items(self, file_url: str) -> list[dict]:
        """
        Return mock invoice line items for development and testing.

        The last item ("Salsa BBQ Especial") is intentionally unlikely to match
        any existing resource, to exercise the unmatched-item flow.

        Args:
            file_url: URL or path to the invoice file (ignored in stub)

        Returns:
            List of dicts with mock invoice line items
        """
        print(f"INFO [StubOCRAdapter]: Extracting mock invoice items from {file_url}")

        mock_items = [
            {
                "product_name": "Tomate",
                "quantity": "10.0",
                "unit": "kg",
                "unit_price": "2.50",
                "supplier_name": "Distribuidora ABC",
            },
            {
                "product_name": "Aceite de oliva",
                "quantity": "5.0",
                "unit": "litro",
                "unit_price": "8.75",
                "supplier_name": "Distribuidora ABC",
            },
            {
                "product_name": "Harina de trigo",
                "quantity": "20.0",
                "unit": "kg",
                "unit_price": "1.20",
                "supplier_name": "Distribuidora ABC",
            },
            {
                "product_name": "Salsa BBQ Especial",
                "quantity": "3.0",
                "unit": "litro",
                "unit_price": "12.00",
                "supplier_name": "Distribuidora ABC",
            },
        ]

        print(f"INFO [StubOCRAdapter]: Returning {len(mock_items)} mock items")
        return mock_items
