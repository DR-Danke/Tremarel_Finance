"""SQLAlchemy LdSpecialistExpertise model for specialist-domain junction."""

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint

from src.config.database import Base


class LdSpecialistExpertise(Base):
    """
    Legal Desk specialist expertise model.

    Junction table linking specialists to legal domains with proficiency levels.
    Maps to the ld_specialist_expertise table in PostgreSQL database.
    """

    __tablename__ = "ld_specialist_expertise"
    __table_args__ = (
        UniqueConstraint("specialist_id", "legal_domain", name="uq_specialist_expertise"),
    )

    id: int = Column(Integer, primary_key=True)
    specialist_id: int = Column(
        Integer, ForeignKey("ld_specialists.id", ondelete="CASCADE"), nullable=False
    )
    legal_domain: str = Column(String(100), nullable=False)
    proficiency_level: str = Column(String(50), default="intermediate")
    years_in_domain: int = Column(Integer, default=0)
    created_at: datetime = Column(DateTime(timezone=True), default=datetime.utcnow)

    def __repr__(self) -> str:
        """String representation of LdSpecialistExpertise."""
        return f"<LdSpecialistExpertise(id={self.id}, specialist_id={self.specialist_id}, legal_domain={self.legal_domain})>"
