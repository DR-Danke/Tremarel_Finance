"""Legal Desk case service for business logic."""

from typing import Optional

from sqlalchemy.orm import Session

from src.interface.legaldesk_dto import (
    CASE_STATUS_TRANSITIONS,
    CaseCreateDTO,
    CaseFilterDTO,
    CaseUpdateDTO,
)
from src.models.ld_case import LdCase
from src.repository.ld_case_repository import ld_case_repository


class LdCaseService:
    """Service for Legal Desk case business logic."""

    def create_case(self, db: Session, data: CaseCreateDTO, current_user: dict) -> LdCase:
        """
        Create a new legal case with auto-generated case number.

        Args:
            db: Database session
            data: Case creation data
            current_user: Authenticated user dict

        Returns:
            Created LdCase object
        """
        print(f"INFO [LdCaseService]: Creating case '{data.title}' for client {data.client_id}")
        case_number = ld_case_repository.generate_case_number(db)
        case_data = data.model_dump()
        case_data["case_number"] = case_number
        case_data["status"] = "new"
        # Convert enum values to strings for ORM
        for field in ("legal_domain", "complexity", "priority"):
            if case_data.get(field) is not None:
                case_data[field] = case_data[field].value if hasattr(case_data[field], "value") else case_data[field]
        # Remove DTO-only fields not present on the ORM model
        case_data.pop("case_type", None)
        case = ld_case_repository.create(db, case_data)
        print(f"INFO [LdCaseService]: Case created with id {case.id}, number {case_number}")
        return case

    def update_case(self, db: Session, case_id: int, data: CaseUpdateDTO) -> Optional[LdCase]:
        """
        Update an existing case.

        Args:
            db: Database session
            case_id: Case primary key
            data: Update data (partial)

        Returns:
            Updated LdCase if found, None otherwise
        """
        print(f"INFO [LdCaseService]: Updating case {case_id}")
        existing = ld_case_repository.get_by_id(db, case_id)
        if not existing:
            print(f"INFO [LdCaseService]: Case {case_id} not found")
            return None
        updated = ld_case_repository.update(db, case_id, data.model_dump(exclude_unset=True))
        print(f"INFO [LdCaseService]: Case {case_id} updated successfully")
        return updated

    def update_case_status(self, db: Session, case_id: int, new_status: str) -> Optional[LdCase]:
        """
        Update case status with transition validation.

        Validates the transition against CASE_STATUS_TRANSITIONS state machine.
        Raises ValueError if the transition is invalid.

        Args:
            db: Database session
            case_id: Case primary key
            new_status: Target status value

        Returns:
            Updated LdCase if found and transition valid, None if case not found

        Raises:
            ValueError: If the status transition is not allowed
        """
        print(f"INFO [LdCaseService]: Updating case {case_id} status to '{new_status}'")
        case = ld_case_repository.get_by_id(db, case_id)
        if not case:
            print(f"INFO [LdCaseService]: Case {case_id} not found")
            return None

        current_status = case.status
        allowed = CASE_STATUS_TRANSITIONS.get(current_status, [])

        if new_status not in allowed:
            msg = f"Invalid status transition: '{current_status}' -> '{new_status}'. Allowed: {allowed}"
            print(f"ERROR [LdCaseService]: {msg}")
            raise ValueError(msg)

        updated = ld_case_repository.update_status(db, case_id, new_status)
        print(f"INFO [LdCaseService]: Case {case_id} status updated from '{current_status}' to '{new_status}'")
        return updated

    def get_case_with_details(self, db: Session, case_id: int) -> Optional[LdCase]:
        """
        Get a case with all related entities loaded via ORM relationships.

        Args:
            db: Database session
            case_id: Case primary key

        Returns:
            LdCase with relationships if found, None otherwise
        """
        print(f"INFO [LdCaseService]: Getting case detail for {case_id}")
        case = ld_case_repository.get_by_id(db, case_id)
        if case:
            print(f"INFO [LdCaseService]: Found case '{case.case_number}' with {len(case.specialists)} specialists")
        else:
            print(f"INFO [LdCaseService]: Case {case_id} not found")
        return case

    def list_cases(self, db: Session, filters: CaseFilterDTO) -> list[LdCase]:
        """
        List cases with filtering.

        Args:
            db: Database session
            filters: CaseFilterDTO with optional filter fields

        Returns:
            List of LdCase objects
        """
        print(f"INFO [LdCaseService]: Listing cases with filters={filters}")
        cases = ld_case_repository.list_cases(db, filters)
        print(f"INFO [LdCaseService]: Found {len(cases)} cases")
        return cases


# Singleton instance
ld_case_service = LdCaseService()
