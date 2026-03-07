"""Legal Desk document service for business logic."""

from sqlalchemy.orm import Session

from src.interface.legaldesk_dto import DocumentCreateDTO
from src.models.ld_case_document import LdCaseDocument
from src.repository.ld_document_repository import ld_document_repository


class LdDocumentService:
    """Service for Legal Desk document business logic."""

    def create_document(self, db: Session, case_id: int, data: DocumentCreateDTO) -> LdCaseDocument:
        """
        Create a new document record for a case.

        Args:
            db: Database session
            case_id: Case identifier
            data: Document creation data

        Returns:
            Created LdCaseDocument object
        """
        print(f"INFO [LdDocumentService]: Creating document for case {case_id}")
        doc_data = data.model_dump()
        doc_data["case_id"] = case_id
        document = ld_document_repository.create(db, doc_data)
        print(f"INFO [LdDocumentService]: Document created with id {document.id}")
        return document

    def get_case_documents(self, db: Session, case_id: int) -> list[LdCaseDocument]:
        """
        Get all documents for a case.

        Args:
            db: Database session
            case_id: Case identifier

        Returns:
            List of LdCaseDocument objects
        """
        print(f"INFO [LdDocumentService]: Getting documents for case {case_id}")
        documents = ld_document_repository.get_by_case(db, case_id)
        print(f"INFO [LdDocumentService]: Found {len(documents)} documents for case {case_id}")
        return documents


# Singleton instance
ld_document_service = LdDocumentService()
