"""Legal Desk case repository for database operations."""

from datetime import datetime
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.interface.legaldesk_dto import CaseFilterDTO
from src.models.ld_case import LdCase


class LdCaseRepository:
    """Repository for LdCase database operations."""

    def create(self, db: Session, case_data: dict) -> LdCase:
        """
        Create a new case.

        Args:
            db: Database session
            case_data: Case field values

        Returns:
            Created LdCase object
        """
        print(f"INFO [LdCaseRepository]: Creating case with data {case_data}")
        case = LdCase(**case_data)
        db.add(case)
        db.commit()
        db.refresh(case)
        print(f"INFO [LdCaseRepository]: Case created with id {case.id}, number {case.case_number}")
        return case

    def get_by_id(self, db: Session, case_id: int) -> Optional[LdCase]:
        """
        Find a case by ID.

        Args:
            db: Database session
            case_id: Case primary key

        Returns:
            LdCase if found, None otherwise
        """
        print(f"INFO [LdCaseRepository]: Looking up case by id {case_id}")
        case = db.query(LdCase).filter(LdCase.id == case_id).first()
        if case:
            print(f"INFO [LdCaseRepository]: Found case '{case.case_number}'")
        else:
            print(f"INFO [LdCaseRepository]: No case found with id {case_id}")
        return case

    def list_cases(
        self, db: Session, filters: CaseFilterDTO, limit: int = 100, offset: int = 0
    ) -> list[LdCase]:
        """
        List cases with filtering and pagination.

        Args:
            db: Database session
            filters: CaseFilterDTO with optional filter fields
            limit: Max results (default 100)
            offset: Skip count (default 0)

        Returns:
            List of LdCase objects
        """
        print(f"INFO [LdCaseRepository]: Listing cases with filters={filters}, limit={limit}, offset={offset}")
        query = db.query(LdCase)

        if filters.status is not None:
            query = query.filter(LdCase.status == filters.status.value)

        if filters.legal_domain is not None:
            query = query.filter(LdCase.legal_domain == filters.legal_domain.value)

        if filters.priority is not None:
            query = query.filter(LdCase.priority == filters.priority.value)

        if filters.client_id is not None:
            query = query.filter(LdCase.client_id == filters.client_id)

        if filters.complexity is not None:
            query = query.filter(LdCase.complexity == filters.complexity.value)

        # Note: case_type filter skipped — LdCase model has no case_type column

        cases = query.order_by(LdCase.created_at.desc()).offset(offset).limit(limit).all()
        print(f"INFO [LdCaseRepository]: Found {len(cases)} cases")
        return cases

    def update(self, db: Session, case_id: int, data: dict) -> Optional[LdCase]:
        """
        Update a case by ID.

        Args:
            db: Database session
            case_id: Case primary key
            data: Fields to update

        Returns:
            Updated LdCase if found, None otherwise
        """
        print(f"INFO [LdCaseRepository]: Updating case {case_id} with {data}")
        case = self.get_by_id(db, case_id)
        if not case:
            return None
        for key, value in data.items():
            setattr(case, key, value)
        db.commit()
        db.refresh(case)
        print(f"INFO [LdCaseRepository]: Case {case_id} updated successfully")
        return case

    def update_status(self, db: Session, case_id: int, status: str) -> Optional[LdCase]:
        """
        Update only the status field of a case.

        Args:
            db: Database session
            case_id: Case primary key
            status: New status value

        Returns:
            Updated LdCase if found, None otherwise
        """
        print(f"INFO [LdCaseRepository]: Updating case {case_id} status to '{status}'")
        return self.update(db, case_id, {"status": status})

    def generate_case_number(self, db: Session) -> str:
        """
        Generate a sequential case number in format LD-YYYYMM-NNNN.

        Args:
            db: Database session

        Returns:
            Generated case number string
        """
        now = datetime.utcnow()
        year_month = now.strftime("%Y%m")
        prefix = f"LD-{year_month}-"

        count = (
            db.query(func.count(LdCase.id))
            .filter(LdCase.case_number.like(f"{prefix}%"))
            .scalar()
        )

        next_number = (count or 0) + 1
        case_number = f"{prefix}{next_number:04d}"
        print(f"INFO [LdCaseRepository]: Generated case number {case_number}")
        return case_number

    def get_by_client(self, db: Session, client_id: int) -> list[LdCase]:
        """
        Get all cases for a client.

        Args:
            db: Database session
            client_id: Client primary key

        Returns:
            List of LdCase objects
        """
        print(f"INFO [LdCaseRepository]: Getting cases for client {client_id}")
        cases = (
            db.query(LdCase)
            .filter(LdCase.client_id == client_id)
            .order_by(LdCase.created_at.desc())
            .all()
        )
        print(f"INFO [LdCaseRepository]: Found {len(cases)} cases for client {client_id}")
        return cases

    def count_by_status(self, db: Session) -> dict:
        """
        Count cases grouped by status.

        Args:
            db: Database session

        Returns:
            Dictionary of {status_string: count}
        """
        print("INFO [LdCaseRepository]: Counting cases by status")
        results = (
            db.query(LdCase.status, func.count(LdCase.id))
            .group_by(LdCase.status)
            .all()
        )
        status_counts = {status: count for status, count in results}
        print(f"INFO [LdCaseRepository]: Status counts: {status_counts}")
        return status_counts


# Singleton instance
ld_case_repository = LdCaseRepository()
