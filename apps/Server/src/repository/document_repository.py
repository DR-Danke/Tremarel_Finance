"""Document repository for database operations."""

from datetime import date, timedelta
from typing import Any, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from src.models.document import Document


class DocumentRepository:
    """Repository for Document database operations."""

    def create(
        self,
        db: Session,
        restaurant_id: UUID,
        doc_type: str,
        file_url: Optional[str],
        issue_date: Optional[date],
        expiration_date: Optional[date],
        person_id: Optional[UUID],
        description: Optional[str],
    ) -> Document:
        """
        Create a new document in a restaurant.

        Args:
            db: Database session
            restaurant_id: Restaurant UUID
            doc_type: Document type (e.g., contrato, permiso, factura)
            file_url: URL or path to uploaded file
            issue_date: Date the document was issued
            expiration_date: Date the document expires
            person_id: Person UUID linked to this document
            description: Document description

        Returns:
            Created Document object
        """
        print(f"INFO [DocumentRepository]: Creating document type '{doc_type}' for restaurant {restaurant_id}")
        document = Document(
            restaurant_id=restaurant_id,
            type=doc_type,
            file_url=file_url,
            issue_date=issue_date,
            expiration_date=expiration_date,
            person_id=person_id,
            description=description,
        )
        db.add(document)
        db.commit()
        db.refresh(document)
        print(f"INFO [DocumentRepository]: Document created with id {document.id}")
        return document

    def get_by_id(self, db: Session, document_id: UUID) -> Optional[Document]:
        """
        Find a document by ID.

        Args:
            db: Database session
            document_id: Document UUID

        Returns:
            Document object if found, None otherwise
        """
        print(f"INFO [DocumentRepository]: Looking up document by id {document_id}")
        document = db.query(Document).filter(Document.id == document_id).first()
        if document:
            print(f"INFO [DocumentRepository]: Found document type '{document.type}'")
        else:
            print(f"INFO [DocumentRepository]: No document found with id {document_id}")
        return document

    def get_by_restaurant(
        self,
        db: Session,
        restaurant_id: UUID,
        type_filter: Optional[str] = None,
    ) -> list[Document]:
        """
        Get all documents in a restaurant, with optional type filter.

        Args:
            db: Database session
            restaurant_id: Restaurant UUID
            type_filter: Optional document type to filter by

        Returns:
            List of Document objects
        """
        print(f"INFO [DocumentRepository]: Getting documents for restaurant {restaurant_id} (type_filter={type_filter})")
        query = db.query(Document).filter(Document.restaurant_id == restaurant_id)
        if type_filter:
            query = query.filter(Document.type == type_filter)
        documents = query.all()
        print(f"INFO [DocumentRepository]: Found {len(documents)} documents for restaurant {restaurant_id}")
        return documents

    def update(self, db: Session, document: Document) -> Document:
        """
        Update an existing document.

        Args:
            db: Database session
            document: Document object with updated values

        Returns:
            Updated Document object
        """
        print(f"INFO [DocumentRepository]: Updating document {document.id}")
        db.add(document)
        db.commit()
        db.refresh(document)
        print(f"INFO [DocumentRepository]: Document {document.id} updated successfully")
        return document

    def delete(self, db: Session, document_id: UUID) -> bool:
        """
        Delete a document from the database.

        Args:
            db: Database session
            document_id: Document UUID

        Returns:
            True if deleted, False if not found
        """
        print(f"INFO [DocumentRepository]: Deleting document {document_id}")
        document = db.query(Document).filter(Document.id == document_id).first()
        if document:
            db.delete(document)
            db.commit()
            print(f"INFO [DocumentRepository]: Document {document_id} deleted successfully")
            return True
        print(f"INFO [DocumentRepository]: Document {document_id} not found for deletion")
        return False

    def update_processing_status(
        self,
        db: Session,
        document_id: UUID,
        status: str,
        result: Optional[dict[str, Any]] = None,
    ) -> Optional[Document]:
        """
        Update the processing_status and processing_result fields on a document.

        Args:
            db: Database session
            document_id: Document UUID
            status: Processing status (pending, processing, completed, failed)
            result: Optional processing result dict

        Returns:
            Updated Document object, or None if not found
        """
        print(f"INFO [DocumentRepository]: Updating processing status to '{status}' for document {document_id}")
        document = db.query(Document).filter(Document.id == document_id).first()
        if document is None:
            print(f"INFO [DocumentRepository]: Document {document_id} not found for processing status update")
            return None
        document.processing_status = status
        document.processing_result = result
        db.commit()
        db.refresh(document)
        print(f"INFO [DocumentRepository]: Processing status updated to '{status}' for document {document_id}")
        return document

    def get_expiring(self, db: Session, restaurant_id: UUID, days_ahead: int = 30) -> list[Document]:
        """
        Get documents where expiration_date is between today and today + days_ahead.

        Args:
            db: Database session
            restaurant_id: Restaurant UUID
            days_ahead: Number of days ahead to look for expiring documents

        Returns:
            List of expiring Document objects
        """
        print(f"INFO [DocumentRepository]: Getting expiring documents for restaurant {restaurant_id} (days_ahead={days_ahead})")
        today = date.today()
        threshold = today + timedelta(days=days_ahead)
        documents = (
            db.query(Document)
            .filter(
                Document.restaurant_id == restaurant_id,
                Document.expiration_date >= today,
                Document.expiration_date <= threshold,
            )
            .all()
        )
        print(f"INFO [DocumentRepository]: Found {len(documents)} expiring documents")
        return documents

    def count_active(self, db: Session, restaurant_id: UUID) -> int:
        """
        Count documents where expiration_date is NULL or >= today.

        Args:
            db: Database session
            restaurant_id: Restaurant UUID

        Returns:
            Count of active documents
        """
        print(f"INFO [DocumentRepository]: Counting active documents for restaurant {restaurant_id}")
        today = date.today()
        from sqlalchemy import or_

        count = (
            db.query(Document)
            .filter(
                Document.restaurant_id == restaurant_id,
                or_(
                    Document.expiration_date.is_(None),
                    Document.expiration_date >= today,
                ),
            )
            .count()
        )
        print(f"INFO [DocumentRepository]: Found {count} active documents")
        return count


# Singleton instance
document_repository = DocumentRepository()
