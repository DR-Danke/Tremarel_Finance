"""Repository for Legal Desk case-specialist assignment operations."""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy.orm import Session

from src.models.ld_case_specialist import LdCaseSpecialist


class LdAssignmentRepository:
    """Repository for LdCaseSpecialist (assignment) database operations."""

    def create_assignment(self, db: Session, data: dict) -> LdCaseSpecialist:
        """
        Create a new case-specialist assignment.

        Args:
            db: Database session
            data: Dict with case_id, specialist_id, role, proposed_fee, fee_currency

        Returns:
            Created LdCaseSpecialist object
        """
        print(f"INFO [LdAssignmentRepository]: Creating assignment for case {data.get('case_id')} specialist {data.get('specialist_id')}")
        assignment = LdCaseSpecialist(
            case_id=data["case_id"],
            specialist_id=data["specialist_id"],
            role=data.get("role", "assigned"),
            proposed_fee=data.get("proposed_fee"),
            fee_currency=data.get("fee_currency", "EUR"),
            status=data.get("status", "pending"),
        )
        db.add(assignment)
        db.commit()
        db.refresh(assignment)
        print(f"INFO [LdAssignmentRepository]: Assignment created with id {assignment.id}")
        return assignment

    def get_case_specialists(self, db: Session, case_id: int) -> list[LdCaseSpecialist]:
        """
        Get all assignments for a case, ordered by assigned_at DESC.

        Args:
            db: Database session
            case_id: Case identifier

        Returns:
            List of LdCaseSpecialist objects
        """
        print(f"INFO [LdAssignmentRepository]: Getting specialists for case {case_id}")
        results = (
            db.query(LdCaseSpecialist)
            .filter(LdCaseSpecialist.case_id == case_id)
            .order_by(LdCaseSpecialist.assigned_at.desc())
            .all()
        )
        print(f"INFO [LdAssignmentRepository]: Found {len(results)} assignments for case {case_id}")
        return results

    def get_specialist_cases(self, db: Session, specialist_id: int) -> list[LdCaseSpecialist]:
        """
        Get all assignments for a specialist, ordered by assigned_at DESC.

        Args:
            db: Database session
            specialist_id: Specialist identifier

        Returns:
            List of LdCaseSpecialist objects
        """
        print(f"INFO [LdAssignmentRepository]: Getting cases for specialist {specialist_id}")
        results = (
            db.query(LdCaseSpecialist)
            .filter(LdCaseSpecialist.specialist_id == specialist_id)
            .order_by(LdCaseSpecialist.assigned_at.desc())
            .all()
        )
        print(f"INFO [LdAssignmentRepository]: Found {len(results)} assignments for specialist {specialist_id}")
        return results

    def update_assignment_status(self, db: Session, assignment_id: int, status: str) -> Optional[LdCaseSpecialist]:
        """
        Update the status of an assignment. Sets responded_at when transitioning from pending.

        Args:
            db: Database session
            assignment_id: Assignment identifier
            status: New status value

        Returns:
            Updated LdCaseSpecialist or None if not found
        """
        print(f"INFO [LdAssignmentRepository]: Updating status for assignment {assignment_id} to '{status}'")
        assignment = db.query(LdCaseSpecialist).filter(LdCaseSpecialist.id == assignment_id).first()
        if not assignment:
            print(f"INFO [LdAssignmentRepository]: Assignment {assignment_id} not found")
            return None
        if assignment.status == "pending" and status != "pending":
            assignment.responded_at = datetime.utcnow()
        assignment.status = status
        db.commit()
        db.refresh(assignment)
        print(f"INFO [LdAssignmentRepository]: Assignment {assignment_id} status updated to '{status}'")
        return assignment

    def update_fees(
        self,
        db: Session,
        assignment_id: int,
        proposed_fee: Decimal,
        agreed_fee: Decimal,
        fee_type: str,
    ) -> Optional[LdCaseSpecialist]:
        """
        Update fee fields on an assignment.

        Args:
            db: Database session
            assignment_id: Assignment identifier
            proposed_fee: Proposed fee amount
            agreed_fee: Agreed fee amount
            fee_type: Fee currency code (maps to fee_currency column)

        Returns:
            Updated LdCaseSpecialist or None if not found
        """
        print(f"INFO [LdAssignmentRepository]: Updating fees for assignment {assignment_id}")
        assignment = db.query(LdCaseSpecialist).filter(LdCaseSpecialist.id == assignment_id).first()
        if not assignment:
            print(f"INFO [LdAssignmentRepository]: Assignment {assignment_id} not found")
            return None
        assignment.proposed_fee = proposed_fee
        assignment.agreed_fee = agreed_fee
        assignment.fee_currency = fee_type
        db.commit()
        db.refresh(assignment)
        print(f"INFO [LdAssignmentRepository]: Fees updated for assignment {assignment_id}")
        return assignment


# Singleton instance
ld_assignment_repository = LdAssignmentRepository()
