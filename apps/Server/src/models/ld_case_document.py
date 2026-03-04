"""SQLAlchemy LdCaseDocument model for case document attachments."""

from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, String

from src.config.database import Base


class LdCaseDocument(Base):
    """
    Legal Desk case document model.

    Tracks document attachments for a case with file metadata.
    Maps to the ld_case_documents table in PostgreSQL database.
    """

    __tablename__ = "ld_case_documents"

    id: int = Column(Integer, primary_key=True)
    case_id: int = Column(
        Integer, ForeignKey("ld_cases.id", ondelete="CASCADE"), nullable=False
    )
    file_name: str = Column(String(500), nullable=False)
    file_url: str = Column(String(1000), nullable=False)
    file_type: Optional[str] = Column(String(100), nullable=True)
    file_size_bytes: Optional[int] = Column(BigInteger, nullable=True)
    uploaded_by: Optional[str] = Column(String(255), nullable=True)
    created_at: datetime = Column(DateTime(timezone=True), default=datetime.utcnow)

    def __repr__(self) -> str:
        """String representation of LdCaseDocument."""
        return f"<LdCaseDocument(id={self.id}, case_id={self.case_id}, file_name={self.file_name})>"
