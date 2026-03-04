"""Legal Desk specialist repository for database operations."""

from decimal import Decimal
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.models.ld_specialist import LdSpecialist
from src.models.ld_specialist_expertise import LdSpecialistExpertise
from src.models.ld_specialist_jurisdiction import LdSpecialistJurisdiction
from src.models.ld_specialist_score import LdSpecialistScore


class LdSpecialistRepository:
    """Repository for LdSpecialist database operations."""

    def create(self, db: Session, data: dict) -> LdSpecialist:
        """
        Create a new specialist.

        Args:
            db: Database session
            data: Specialist field values

        Returns:
            Created LdSpecialist object
        """
        print(f"INFO [LdSpecialistRepository]: Creating specialist with data {data}")
        specialist = LdSpecialist(**data)
        db.add(specialist)
        db.commit()
        db.refresh(specialist)
        print(f"INFO [LdSpecialistRepository]: Specialist created with id {specialist.id}")
        return specialist

    def get_by_id(self, db: Session, specialist_id: int) -> Optional[LdSpecialist]:
        """
        Find a specialist by ID.

        Args:
            db: Database session
            specialist_id: Specialist primary key

        Returns:
            LdSpecialist if found, None otherwise
        """
        print(f"INFO [LdSpecialistRepository]: Looking up specialist by id {specialist_id}")
        specialist = db.query(LdSpecialist).filter(LdSpecialist.id == specialist_id).first()
        if specialist:
            print(f"INFO [LdSpecialistRepository]: Found specialist '{specialist.full_name}'")
        else:
            print(f"INFO [LdSpecialistRepository]: No specialist found with id {specialist_id}")
        return specialist

    def list_all(self, db: Session, filters: Optional[dict] = None) -> list[LdSpecialist]:
        """
        List specialists with optional filters.

        Args:
            db: Database session
            filters: Optional dict with keys: is_active, legal_domain, min_experience, max_workload

        Returns:
            List of LdSpecialist objects
        """
        filters = filters or {}
        print(f"INFO [LdSpecialistRepository]: Listing specialists with filters {filters}")
        query = db.query(LdSpecialist)

        if "is_active" in filters and filters["is_active"] is not None:
            query = query.filter(LdSpecialist.is_active == filters["is_active"])  # noqa: E712

        if "legal_domain" in filters and filters["legal_domain"] is not None:
            query = query.join(LdSpecialistExpertise).filter(
                LdSpecialistExpertise.legal_domain == filters["legal_domain"]
            )

        if "min_experience" in filters and filters["min_experience"] is not None:
            query = query.filter(LdSpecialist.years_experience >= filters["min_experience"])

        if "max_workload" in filters and filters["max_workload"] is not None:
            query = query.filter(LdSpecialist.current_workload <= filters["max_workload"])

        specialists = query.order_by(LdSpecialist.created_at.desc()).all()
        print(f"INFO [LdSpecialistRepository]: Found {len(specialists)} specialists")
        return specialists

    def update(self, db: Session, specialist_id: int, data: dict) -> Optional[LdSpecialist]:
        """
        Update a specialist by ID.

        Args:
            db: Database session
            specialist_id: Specialist primary key
            data: Fields to update

        Returns:
            Updated LdSpecialist if found, None otherwise
        """
        print(f"INFO [LdSpecialistRepository]: Updating specialist {specialist_id} with {data}")
        specialist = self.get_by_id(db, specialist_id)
        if not specialist:
            return None
        for key, value in data.items():
            setattr(specialist, key, value)
        db.commit()
        db.refresh(specialist)
        print(f"INFO [LdSpecialistRepository]: Specialist {specialist_id} updated successfully")
        return specialist

    def update_status(self, db: Session, specialist_id: int, status: str) -> Optional[LdSpecialist]:
        """
        Update specialist active status.

        Maps status string to is_active boolean:
        - "active" -> True
        - "inactive" / "on_leave" -> False

        Args:
            db: Database session
            specialist_id: Specialist primary key
            status: Status string ("active", "inactive", "on_leave")

        Returns:
            Updated LdSpecialist if found, None otherwise
        """
        print(f"INFO [LdSpecialistRepository]: Updating specialist {specialist_id} status to '{status}'")
        is_active = status.lower() == "active"
        return self.update(db, specialist_id, {"is_active": is_active})

    def get_available(
        self, db: Session, domain: str, jurisdiction: Optional[str] = None
    ) -> list[LdSpecialist]:
        """
        Get available specialists for a domain and optional jurisdiction.

        Filters by: active status, matching domain expertise, workload capacity.
        Optionally filters by jurisdiction country.

        Args:
            db: Database session
            domain: Legal domain to match
            jurisdiction: Optional country to match

        Returns:
            List of available LdSpecialist objects
        """
        print(f"INFO [LdSpecialistRepository]: Getting available specialists for domain='{domain}', jurisdiction='{jurisdiction}'")
        query = (
            db.query(LdSpecialist)
            .join(LdSpecialistExpertise)
            .filter(
                LdSpecialistExpertise.legal_domain == domain,
                LdSpecialist.is_active == True,  # noqa: E712
                LdSpecialist.current_workload < LdSpecialist.max_concurrent_cases,
            )
        )

        if jurisdiction:
            query = query.join(LdSpecialistJurisdiction).filter(
                LdSpecialistJurisdiction.country == jurisdiction
            )

        specialists = query.all()
        print(f"INFO [LdSpecialistRepository]: Found {len(specialists)} available specialists")
        return specialists

    def update_workload(self, db: Session, specialist_id: int, delta: int) -> Optional[LdSpecialist]:
        """
        Increment or decrement specialist workload.

        Args:
            db: Database session
            specialist_id: Specialist primary key
            delta: Value to add (positive) or subtract (negative)

        Returns:
            Updated LdSpecialist if found, None otherwise
        """
        print(f"INFO [LdSpecialistRepository]: Updating workload for specialist {specialist_id} by {delta}")
        specialist = self.get_by_id(db, specialist_id)
        if not specialist:
            return None
        specialist.current_workload = specialist.current_workload + delta
        db.commit()
        db.refresh(specialist)
        print(f"INFO [LdSpecialistRepository]: Specialist {specialist_id} workload is now {specialist.current_workload}")
        return specialist

    def update_overall_score(self, db: Session, specialist_id: int) -> Optional[LdSpecialist]:
        """
        Recalculate and update specialist overall score from all score records.

        Args:
            db: Database session
            specialist_id: Specialist primary key

        Returns:
            Updated LdSpecialist if found, None otherwise
        """
        print(f"INFO [LdSpecialistRepository]: Recalculating overall score for specialist {specialist_id}")
        specialist = self.get_by_id(db, specialist_id)
        if not specialist:
            return None

        avg_score = (
            db.query(func.avg(LdSpecialistScore.overall_score))
            .filter(LdSpecialistScore.specialist_id == specialist_id)
            .scalar()
        )

        specialist.overall_score = Decimal(str(round(avg_score, 2))) if avg_score else Decimal("0.00")
        db.commit()
        db.refresh(specialist)
        print(f"INFO [LdSpecialistRepository]: Specialist {specialist_id} overall score updated to {specialist.overall_score}")
        return specialist


# Singleton instance
ld_specialist_repository = LdSpecialistRepository()
