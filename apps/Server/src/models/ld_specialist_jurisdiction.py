"""SQLAlchemy LdSpecialistJurisdiction model for specialist-jurisdiction junction."""

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, UniqueConstraint

from src.config.database import Base


class LdSpecialistJurisdiction(Base):
    """
    Legal Desk specialist jurisdiction model.

    Junction table linking specialists to countries/regions with primary flag.
    Maps to the ld_specialist_jurisdictions table in PostgreSQL database.
    """

    __tablename__ = "ld_specialist_jurisdictions"
    __table_args__ = (
        UniqueConstraint("specialist_id", "country", "region", name="uq_specialist_jurisdiction"),
    )

    id: int = Column(Integer, primary_key=True)
    specialist_id: int = Column(
        Integer, ForeignKey("ld_specialists.id", ondelete="CASCADE"), nullable=False
    )
    country: str = Column(String(100), nullable=False)
    region: Optional[str] = Column(String(100), nullable=True)
    is_primary: bool = Column(Boolean, default=False)
    created_at: datetime = Column(DateTime(timezone=True), default=datetime.utcnow)

    def __repr__(self) -> str:
        """String representation of LdSpecialistJurisdiction."""
        return f"<LdSpecialistJurisdiction(id={self.id}, specialist_id={self.specialist_id}, country={self.country})>"
