"""Invoice processor service: OCR extraction, resource matching, cost update, and inventory movement creation."""

import asyncio
from uuid import UUID

from sqlalchemy.orm import Session

from src.adapter.ocr_stub_adapter import StubOCRAdapter
from src.core.services.ocr_service import OCRService
from src.repository.document_repository import document_repository
from src.repository.inventory_movement_repository import inventory_movement_repository
from src.repository.resource_repository import resource_repository
from src.repository.restaurant_repository import restaurant_repository


# Module-level OCR service (swappable adapter)
ocr_service = OCRService(StubOCRAdapter())


class InvoiceProcessor:
    """Service that orchestrates invoice OCR processing pipeline."""

    def _check_restaurant_access(self, db: Session, user_id: UUID, restaurant_id: UUID) -> None:
        """
        Check that a user has membership in a restaurant.

        Args:
            db: Database session
            user_id: User UUID
            restaurant_id: Restaurant UUID

        Raises:
            PermissionError: If user doesn't have access to the restaurant
        """
        role = restaurant_repository.get_user_restaurant_role(db, user_id, restaurant_id)
        if role is None:
            print(f"ERROR [InvoiceProcessor]: User {user_id} doesn't have access to restaurant {restaurant_id}")
            raise PermissionError("User doesn't have access to this restaurant")

    def process_invoice_document(self, db: Session, user_id: UUID, document_id: UUID) -> dict:
        """
        Process a supplier invoice document through OCR pipeline.

        Steps:
        1. Fetch document and validate type/file_url
        2. Extract items via OCR
        3. Match items to existing resources (case-insensitive)
        4. Update last_unit_cost on matched resources
        5. Create entry inventory movements for matched items
        6. Store results on document record

        Args:
            db: Database session
            user_id: User UUID triggering the processing
            document_id: Document UUID to process

        Returns:
            Dict with matched_count, unmatched_count, matched_items, unmatched_items, processing_status

        Raises:
            ValueError: If document not found, wrong type, or no file_url
            PermissionError: If user doesn't have restaurant access
        """
        print(f"INFO [InvoiceProcessor]: Starting invoice processing for document {document_id} by user {user_id}")

        # 1. Fetch document
        document = document_repository.get_by_id(db, document_id)
        if document is None:
            print(f"ERROR [InvoiceProcessor]: Document {document_id} not found")
            raise ValueError("Document not found")

        # 2. Check restaurant access
        self._check_restaurant_access(db, user_id, document.restaurant_id)

        # 3. Validate document type
        if document.type != "factura_proveedor":
            print(f"ERROR [InvoiceProcessor]: Document {document_id} type is '{document.type}', expected 'factura_proveedor'")
            raise ValueError("Only documents of type 'factura_proveedor' can be processed")

        # 4. Validate file_url
        if document.file_url is None:
            print(f"ERROR [InvoiceProcessor]: Document {document_id} has no file_url")
            raise ValueError("Document has no file attached for OCR processing")

        # 5. Set status to processing
        document_repository.update_processing_status(db, document_id, "processing")

        try:
            # 6. Extract items via OCR
            print(f"INFO [InvoiceProcessor]: Calling OCR service for document {document_id}")
            items = asyncio.get_event_loop().run_until_complete(
                ocr_service.process_invoice(document.file_url)
            )
            print(f"INFO [InvoiceProcessor]: OCR returned {len(items)} items")

            matched_items: list[dict] = []
            unmatched_items: list[dict] = []

            # 7. Match items to resources
            for item in items:
                resource = resource_repository.find_by_name(db, document.restaurant_id, item.product_name)

                item_dict = {
                    "product_name": item.product_name,
                    "quantity": str(item.quantity),
                    "unit": item.unit,
                    "unit_price": str(item.unit_price),
                    "supplier_name": item.supplier_name,
                }

                if resource is not None:
                    print(f"INFO [InvoiceProcessor]: Matched '{item.product_name}' to resource {resource.id}")

                    # 8. Update last_unit_cost
                    resource.last_unit_cost = item.unit_price
                    resource_repository.update(db, resource)
                    print(f"INFO [InvoiceProcessor]: Updated last_unit_cost to {item.unit_price} for resource {resource.id}")

                    # 9. Create entry inventory movement
                    movement = inventory_movement_repository.create(
                        db=db,
                        resource_id=resource.id,
                        movement_type="entry",
                        quantity=item.quantity,
                        reason="compra",
                        date=None,
                        person_id=None,
                        restaurant_id=document.restaurant_id,
                        notes=f"Auto-created from invoice OCR (document {document_id})",
                    )
                    print(f"INFO [InvoiceProcessor]: Created inventory movement {movement.id} for resource {resource.id}")

                    # 10. Update current_stock
                    resource.current_stock = resource.current_stock + item.quantity
                    resource_repository.update(db, resource)
                    print(f"INFO [InvoiceProcessor]: Updated stock to {resource.current_stock} for resource {resource.id}")

                    matched_items.append({
                        "item": item_dict,
                        "resource_id": str(resource.id),
                    })
                else:
                    print(f"INFO [InvoiceProcessor]: No match found for '{item.product_name}' — flagged for manual review")
                    unmatched_items.append(item_dict)

            # 11. Build result
            result = {
                "document_id": str(document_id),
                "matched_count": len(matched_items),
                "unmatched_count": len(unmatched_items),
                "matched_items": matched_items,
                "unmatched_items": unmatched_items,
                "processing_status": "completed",
            }

            # 12. Update document with completed status and result
            document_repository.update_processing_status(db, document_id, "completed", result)
            print(f"INFO [InvoiceProcessor]: Invoice processing completed for document {document_id}: {len(matched_items)} matched, {len(unmatched_items)} unmatched")

            return result

        except Exception as e:
            print(f"ERROR [InvoiceProcessor]: Invoice processing failed for document {document_id}: {str(e)}")
            error_result = {"error": str(e), "processing_status": "failed"}
            document_repository.update_processing_status(db, document_id, "failed", error_result)
            raise


# Singleton instance
invoice_processor = InvoiceProcessor()
