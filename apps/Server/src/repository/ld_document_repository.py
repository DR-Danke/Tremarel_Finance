"""Repository for Legal Desk case document operations."""

from sqlalchemy.orm import Session

from src.models.ld_case_document import LdCaseDocument


class LdDocumentRepository:
    """Repository for LdCaseDocument database operations."""

    def create(self, db: Session, data: dict) -> LdCaseDocument:
        """
        Create a new case document record.

        Args:
            db: Database session
            data: Dict with case_id, file_name, file_url, file_type, file_size_bytes, uploaded_by

        Returns:
            Created LdCaseDocument object
        """
        print(f"INFO [LdDocumentRepository]: Creating document for case {data.get('case_id')}")
        document = LdCaseDocument(
            case_id=data["case_id"],
            file_name=data["file_name"],
            file_url=data["file_url"],
            file_type=data.get("file_type"),
            file_size_bytes=data.get("file_size_bytes"),
            uploaded_by=data.get("uploaded_by"),
        )
        db.add(document)
        db.commit()
        db.refresh(document)
        print(f"INFO [LdDocumentRepository]: Document created with id {document.id}")
        return document

    def get_by_case(self, db: Session, case_id: int) -> list[LdCaseDocument]:
        """
        Get all documents for a case, ordered by created_at ASC.

        Args:
            db: Database session
            case_id: Case identifier

        Returns:
            List of LdCaseDocument objects
        """
        print(f"INFO [LdDocumentRepository]: Getting documents for case {case_id}")
        results = (
            db.query(LdCaseDocument)
            .filter(LdCaseDocument.case_id == case_id)
            .order_by(LdCaseDocument.created_at.asc())
            .all()
        )
        print(f"INFO [LdDocumentRepository]: Found {len(results)} documents for case {case_id}")
        return results


# Singleton instance
ld_document_repository = LdDocumentRepository()
