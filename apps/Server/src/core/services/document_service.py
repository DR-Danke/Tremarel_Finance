"""Document service for business logic operations."""

import os
import uuid
from datetime import date, timedelta
from typing import Optional
from uuid import UUID

from fastapi import UploadFile
from sqlalchemy.orm import Session

from src.interface.document_dto import DocumentCreateDTO, DocumentUpdateDTO
from src.models.document import Document
from src.repository.document_repository import document_repository
from src.repository.restaurant_repository import restaurant_repository


class DocumentService:
    """Service for document business logic with restaurant-scoped authorization."""

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
            print(f"ERROR [DocumentService]: User {user_id} doesn't have access to restaurant {restaurant_id}")
            raise PermissionError("User doesn't have access to this restaurant")

    def create_document(
        self,
        db: Session,
        user_id: UUID,
        data: DocumentCreateDTO,
        file_url: Optional[str] = None,
    ) -> Document:
        """
        Create a new document in a restaurant.

        Args:
            db: Database session
            user_id: ID of the user creating the document
            data: Document creation data
            file_url: Optional file URL from upload

        Returns:
            Created Document object

        Raises:
            PermissionError: If user doesn't have access to the restaurant
        """
        print(f"INFO [DocumentService]: Creating document type '{data.type}' in restaurant {data.restaurant_id} by user {user_id}")

        self._check_restaurant_access(db, user_id, data.restaurant_id)

        document = document_repository.create(
            db=db,
            restaurant_id=data.restaurant_id,
            doc_type=data.type,
            file_url=file_url,
            issue_date=data.issue_date,
            expiration_date=data.expiration_date,
            person_id=data.person_id,
            description=data.description,
        )

        if document.expiration_date is not None:
            days_until = (document.expiration_date - date.today()).days
            if days_until <= 30:
                print(f"WARNING [DocumentService]: Document '{document.type}' expires in {days_until} days")

        print(f"INFO [DocumentService]: Document type '{document.type}' created with id {document.id}")
        return document

    def get_documents(
        self,
        db: Session,
        user_id: UUID,
        restaurant_id: UUID,
        type_filter: Optional[str] = None,
        expiration_status_filter: Optional[str] = None,
    ) -> list[Document]:
        """
        Get all documents in a restaurant.

        Args:
            db: Database session
            user_id: User UUID
            restaurant_id: Restaurant UUID
            type_filter: Optional document type to filter by
            expiration_status_filter: Optional expiration status filter (valid, expiring_soon, expired)

        Returns:
            List of Document objects

        Raises:
            PermissionError: If user doesn't have access to the restaurant
        """
        print(f"INFO [DocumentService]: Getting documents for restaurant {restaurant_id} by user {user_id}")

        self._check_restaurant_access(db, user_id, restaurant_id)

        documents = document_repository.get_by_restaurant(db, restaurant_id, type_filter)

        if expiration_status_filter:
            today = date.today()
            threshold = today + timedelta(days=30)
            filtered = []
            for doc in documents:
                if doc.expiration_date is None:
                    status = "valid"
                elif doc.expiration_date < today:
                    status = "expired"
                elif doc.expiration_date <= threshold:
                    status = "expiring_soon"
                else:
                    status = "valid"

                if status == expiration_status_filter:
                    filtered.append(doc)
            return filtered

        return documents

    def get_document(
        self,
        db: Session,
        user_id: UUID,
        document_id: UUID,
    ) -> Document:
        """
        Get a document by ID if user has access to the document's restaurant.

        Args:
            db: Database session
            user_id: User UUID
            document_id: Document UUID

        Returns:
            Document object

        Raises:
            PermissionError: If user doesn't have access to the restaurant
            ValueError: If document not found
        """
        print(f"INFO [DocumentService]: Getting document {document_id} for user {user_id}")

        document = document_repository.get_by_id(db, document_id)
        if document is None:
            print(f"ERROR [DocumentService]: Document {document_id} not found")
            raise ValueError("Document not found")

        self._check_restaurant_access(db, user_id, document.restaurant_id)

        return document

    def update_document(
        self,
        db: Session,
        user_id: UUID,
        document_id: UUID,
        data: DocumentUpdateDTO,
    ) -> Document:
        """
        Update a document if user has access to the document's restaurant.

        Args:
            db: Database session
            user_id: User UUID
            document_id: Document UUID
            data: Document update data

        Returns:
            Updated Document object

        Raises:
            PermissionError: If user doesn't have access to the restaurant
            ValueError: If document not found
        """
        print(f"INFO [DocumentService]: Updating document {document_id} by user {user_id}")

        document = document_repository.get_by_id(db, document_id)
        if document is None:
            print(f"ERROR [DocumentService]: Document {document_id} not found")
            raise ValueError("Document not found")

        self._check_restaurant_access(db, user_id, document.restaurant_id)

        # Update fields if provided
        if data.type is not None:
            document.type = data.type
        if data.issue_date is not None:
            document.issue_date = data.issue_date
        if data.expiration_date is not None:
            document.expiration_date = data.expiration_date
        if data.person_id is not None:
            document.person_id = data.person_id
        if data.description is not None:
            document.description = data.description

        updated_document = document_repository.update(db, document)

        print(f"INFO [DocumentService]: Document {document_id} updated successfully")
        return updated_document

    def delete_document(
        self,
        db: Session,
        user_id: UUID,
        document_id: UUID,
    ) -> bool:
        """
        Delete a document if user has access to the document's restaurant.

        Args:
            db: Database session
            user_id: User UUID
            document_id: Document UUID

        Returns:
            True if deleted

        Raises:
            PermissionError: If user doesn't have access to the restaurant
            ValueError: If document not found
        """
        print(f"INFO [DocumentService]: Deleting document {document_id} by user {user_id}")

        document = document_repository.get_by_id(db, document_id)
        if document is None:
            print(f"ERROR [DocumentService]: Document {document_id} not found")
            raise ValueError("Document not found")

        self._check_restaurant_access(db, user_id, document.restaurant_id)

        deleted = document_repository.delete(db, document_id)
        if not deleted:
            print(f"ERROR [DocumentService]: Document {document_id} not found for deletion")
            raise ValueError("Document not found")

        print(f"INFO [DocumentService]: Document {document_id} deleted successfully")
        return True

    def get_expiring_documents(
        self,
        db: Session,
        user_id: UUID,
        restaurant_id: UUID,
        days_ahead: int = 30,
    ) -> list[Document]:
        """
        Get documents where expiration_date is within days_ahead for a restaurant.

        Args:
            db: Database session
            user_id: User UUID
            restaurant_id: Restaurant UUID
            days_ahead: Number of days ahead to look

        Returns:
            List of expiring Document objects

        Raises:
            PermissionError: If user doesn't have access to the restaurant
        """
        print(f"INFO [DocumentService]: Getting expiring documents for restaurant {restaurant_id} by user {user_id}")

        self._check_restaurant_access(db, user_id, restaurant_id)

        return document_repository.get_expiring(db, restaurant_id, days_ahead)

    def save_upload_file(self, file: UploadFile) -> str:
        """
        Save an uploaded file to the uploads/documents/ directory.

        Args:
            file: FastAPI UploadFile object

        Returns:
            Relative path to the saved file
        """
        upload_dir = "uploads/documents"
        os.makedirs(upload_dir, exist_ok=True)

        # Generate unique filename to prevent collisions
        file_ext = os.path.splitext(file.filename or "file")[1]
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(upload_dir, unique_filename)

        print(f"INFO [DocumentService]: Saving uploaded file to {file_path}")

        with open(file_path, "wb") as f:
            content = file.file.read()
            f.write(content)

        print(f"INFO [DocumentService]: File saved successfully: {file_path}")
        return file_path


# Singleton instance
document_service = DocumentService()
