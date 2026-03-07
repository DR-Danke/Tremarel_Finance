"""Legal Desk deliverable service for business logic."""

from typing import Optional

from sqlalchemy.orm import Session

from src.interface.legaldesk_dto import DeliverableCreateDTO, DeliverableUpdateDTO
from src.models.ld_case_deliverable import LdCaseDeliverable
from src.repository.ld_deliverable_repository import ld_deliverable_repository


class LdDeliverableService:
    """Service for Legal Desk deliverable business logic."""

    def create_deliverable(self, db: Session, case_id: int, data: DeliverableCreateDTO) -> LdCaseDeliverable:
        """
        Create a new deliverable for a case.

        Args:
            db: Database session
            case_id: Case identifier
            data: Deliverable creation data

        Returns:
            Created LdCaseDeliverable object
        """
        print(f"INFO [LdDeliverableService]: Creating deliverable for case {case_id}")
        data.case_id = case_id
        deliverable = ld_deliverable_repository.create(db, data.model_dump())
        print(f"INFO [LdDeliverableService]: Deliverable created with id {deliverable.id}")
        return deliverable

    def get_case_deliverables(self, db: Session, case_id: int) -> list[LdCaseDeliverable]:
        """
        Get all deliverables for a case.

        Args:
            db: Database session
            case_id: Case identifier

        Returns:
            List of LdCaseDeliverable objects
        """
        print(f"INFO [LdDeliverableService]: Getting deliverables for case {case_id}")
        deliverables = ld_deliverable_repository.get_by_case(db, case_id)
        print(f"INFO [LdDeliverableService]: Found {len(deliverables)} deliverables for case {case_id}")
        return deliverables

    def update_deliverable(self, db: Session, deliverable_id: int, data: DeliverableUpdateDTO) -> Optional[LdCaseDeliverable]:
        """
        Update an existing deliverable.

        Args:
            db: Database session
            deliverable_id: Deliverable primary key
            data: Update data (partial)

        Returns:
            Updated LdCaseDeliverable if found, None otherwise
        """
        print(f"INFO [LdDeliverableService]: Updating deliverable {deliverable_id}")
        updated = ld_deliverable_repository.update(db, deliverable_id, data.model_dump(exclude_unset=True))
        if updated:
            print(f"INFO [LdDeliverableService]: Deliverable {deliverable_id} updated successfully")
        else:
            print(f"INFO [LdDeliverableService]: Deliverable {deliverable_id} not found")
        return updated

    def update_deliverable_status(self, db: Session, deliverable_id: int, status: str) -> Optional[LdCaseDeliverable]:
        """
        Update deliverable status.

        Args:
            db: Database session
            deliverable_id: Deliverable primary key
            status: New status value

        Returns:
            Updated LdCaseDeliverable if found, None otherwise
        """
        print(f"INFO [LdDeliverableService]: Updating deliverable {deliverable_id} status to '{status}'")
        updated = ld_deliverable_repository.update_status(db, deliverable_id, status)
        if updated:
            print(f"INFO [LdDeliverableService]: Deliverable {deliverable_id} status updated to '{status}'")
        else:
            print(f"INFO [LdDeliverableService]: Deliverable {deliverable_id} not found")
        return updated


# Singleton instance
ld_deliverable_service = LdDeliverableService()
