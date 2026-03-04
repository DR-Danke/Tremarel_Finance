"""SQLAlchemy LdClient model for Legal Desk client entities."""

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship

from src.config.database import Base


class LdClient(Base):
    """
    Legal Desk client model.

    Represents a company or individual client with contact information.
    Maps to the ld_clients table in PostgreSQL database.
    """

    __tablename__ = "ld_clients"

    id: int = Column(Integer, primary_key=True)
    name: str = Column(String(255), nullable=False)
    client_type: str = Column(String(50), nullable=False, default="company")
    contact_email: Optional[str] = Column(String(255), nullable=True)
    contact_phone: Optional[str] = Column(String(100), nullable=True)
    country: Optional[str] = Column(String(100), nullable=True)
    industry: Optional[str] = Column(String(100), nullable=True)
    notes: Optional[str] = Column(Text, nullable=True)
    is_active: bool = Column(Boolean, default=True)
    created_at: datetime = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Optional[datetime] = Column(DateTime(timezone=True), onupdate=datetime.utcnow)

    cases = relationship("LdCase", backref="client")

    def __repr__(self) -> str:
        """String representation of LdClient."""
        return f"<LdClient(id={self.id}, name={self.name}, client_type={self.client_type})>"
