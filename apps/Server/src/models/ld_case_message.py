"""SQLAlchemy LdCaseMessage model for case message threads."""

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text

from src.config.database import Base


class LdCaseMessage(Base):
    """
    Legal Desk case message model.

    Represents messages in a case thread with sender type and internal flag.
    Maps to the ld_case_messages table in PostgreSQL database.
    """

    __tablename__ = "ld_case_messages"

    id: int = Column(Integer, primary_key=True)
    case_id: int = Column(
        Integer, ForeignKey("ld_cases.id", ondelete="CASCADE"), nullable=False
    )
    sender_type: str = Column(String(50), nullable=False)
    sender_name: Optional[str] = Column(String(255), nullable=True)
    message: str = Column(Text, nullable=False)
    is_internal: bool = Column(Boolean, default=False)
    created_at: datetime = Column(DateTime(timezone=True), default=datetime.utcnow)

    def __repr__(self) -> str:
        """String representation of LdCaseMessage."""
        return f"<LdCaseMessage(id={self.id}, case_id={self.case_id}, sender_type={self.sender_type})>"
