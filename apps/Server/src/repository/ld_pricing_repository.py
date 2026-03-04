"""Legal Desk pricing history repository for database operations."""

from typing import Optional

from sqlalchemy.orm import Session

from src.models.ld_pricing_history import LdPricingHistory


class LdPricingRepository:
    """Repository for LdPricingHistory database operations."""

    def create(self, db: Session, data: dict) -> LdPricingHistory:
        """
        Insert a new pricing history record.

        Args:
            db: Database session
            data: Pricing history field values

        Returns:
            Created LdPricingHistory object
        """
        case_id = data.get("case_id")
        action = data.get("action")
        print(f"INFO [LdPricingRepository]: Creating pricing entry for case {case_id}, action={action}")
        entry = LdPricingHistory(**data)
        db.add(entry)
        db.commit()
        db.refresh(entry)
        print(f"INFO [LdPricingRepository]: Pricing entry created with id {entry.id}")
        return entry

    def get_by_case(self, db: Session, case_id: int) -> list[LdPricingHistory]:
        """
        Return all pricing history for a case, ordered chronologically.

        Args:
            db: Database session
            case_id: Case primary key

        Returns:
            List of LdPricingHistory objects ordered by created_at ascending
        """
        print(f"INFO [LdPricingRepository]: Getting pricing history for case {case_id}")
        entries = (
            db.query(LdPricingHistory)
            .filter(LdPricingHistory.case_id == case_id)
            .order_by(LdPricingHistory.created_at.asc())
            .all()
        )
        print(f"INFO [LdPricingRepository]: Found {len(entries)} pricing entries for case {case_id}")
        return entries

    def get_latest(self, db: Session, case_id: int) -> Optional[LdPricingHistory]:
        """
        Return the most recent pricing entry for a case.

        Args:
            db: Database session
            case_id: Case primary key

        Returns:
            Most recent LdPricingHistory if found, None otherwise
        """
        print(f"INFO [LdPricingRepository]: Getting latest pricing entry for case {case_id}")
        entry = (
            db.query(LdPricingHistory)
            .filter(LdPricingHistory.case_id == case_id)
            .order_by(LdPricingHistory.created_at.desc())
            .first()
        )
        if entry:
            print(f"INFO [LdPricingRepository]: Latest pricing entry id={entry.id}, action={entry.action}")
        else:
            print(f"INFO [LdPricingRepository]: No pricing entries found for case {case_id}")
        return entry


# Singleton instance
ld_pricing_repository = LdPricingRepository()
