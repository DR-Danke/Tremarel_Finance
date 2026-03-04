"""Repository for Legal Desk case deliverable operations."""

from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from src.models.ld_case_deliverable import LdCaseDeliverable


class LdDeliverableRepository:
    """Repository for LdCaseDeliverable database operations."""

    def create(self, db: Session, data: dict) -> LdCaseDeliverable:
        """
        Create a new case deliverable.

        Args:
            db: Database session
            data: Dict with case_id, title, description, specialist_id, due_date

        Returns:
            Created LdCaseDeliverable object
        """
        print(f"INFO [LdDeliverableRepository]: Creating deliverable for case {data.get('case_id')}")
        deliverable = LdCaseDeliverable(
            case_id=data["case_id"],
            title=data["title"],
            description=data.get("description"),
            specialist_id=data.get("specialist_id"),
            due_date=data.get("due_date"),
            status=data.get("status", "pending"),
        )
        db.add(deliverable)
        db.commit()
        db.refresh(deliverable)
        print(f"INFO [LdDeliverableRepository]: Deliverable created with id {deliverable.id}")
        return deliverable

    def get_by_case(self, db: Session, case_id: int) -> list[LdCaseDeliverable]:
        """
        Get all deliverables for a case, ordered by created_at ASC.

        Args:
            db: Database session
            case_id: Case identifier

        Returns:
            List of LdCaseDeliverable objects
        """
        print(f"INFO [LdDeliverableRepository]: Getting deliverables for case {case_id}")
        results = (
            db.query(LdCaseDeliverable)
            .filter(LdCaseDeliverable.case_id == case_id)
            .order_by(LdCaseDeliverable.created_at.asc())
            .all()
        )
        print(f"INFO [LdDeliverableRepository]: Found {len(results)} deliverables for case {case_id}")
        return results

    def update(self, db: Session, deliverable_id: int, data: dict) -> Optional[LdCaseDeliverable]:
        """
        Partial update of a deliverable. Only sets fields present in data.

        Args:
            db: Database session
            deliverable_id: Deliverable identifier
            data: Dict with fields to update

        Returns:
            Updated LdCaseDeliverable or None if not found
        """
        print(f"INFO [LdDeliverableRepository]: Updating deliverable {deliverable_id}")
        deliverable = db.query(LdCaseDeliverable).filter(LdCaseDeliverable.id == deliverable_id).first()
        if not deliverable:
            print(f"INFO [LdDeliverableRepository]: Deliverable {deliverable_id} not found")
            return None
        for key, value in data.items():
            if hasattr(deliverable, key):
                setattr(deliverable, key, value)
        db.commit()
        db.refresh(deliverable)
        print(f"INFO [LdDeliverableRepository]: Deliverable {deliverable_id} updated")
        return deliverable

    def update_status(self, db: Session, deliverable_id: int, status: str) -> Optional[LdCaseDeliverable]:
        """
        Update deliverable status. Sets completed_at when status is 'completed'.

        Args:
            db: Database session
            deliverable_id: Deliverable identifier
            status: New status value

        Returns:
            Updated LdCaseDeliverable or None if not found
        """
        print(f"INFO [LdDeliverableRepository]: Updating status for deliverable {deliverable_id} to '{status}'")
        deliverable = db.query(LdCaseDeliverable).filter(LdCaseDeliverable.id == deliverable_id).first()
        if not deliverable:
            print(f"INFO [LdDeliverableRepository]: Deliverable {deliverable_id} not found")
            return None
        deliverable.status = status
        if status == "completed":
            deliverable.completed_at = datetime.utcnow()
        db.commit()
        db.refresh(deliverable)
        print(f"INFO [LdDeliverableRepository]: Deliverable {deliverable_id} status updated to '{status}'")
        return deliverable


# Singleton instance
ld_deliverable_repository = LdDeliverableRepository()
