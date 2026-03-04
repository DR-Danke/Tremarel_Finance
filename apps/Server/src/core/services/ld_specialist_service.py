"""Legal Desk specialist service for business logic."""

from decimal import Decimal
from typing import Optional

from sqlalchemy.orm import Session

from src.interface.legaldesk_dto import ScoreSubmitDTO, SpecialistCreateDTO, SpecialistUpdateDTO
from src.models.ld_specialist import LdSpecialist
from src.models.ld_specialist_expertise import LdSpecialistExpertise
from src.models.ld_specialist_jurisdiction import LdSpecialistJurisdiction
from src.models.ld_specialist_score import LdSpecialistScore
from src.repository.ld_specialist_repository import ld_specialist_repository


class LdSpecialistService:
    """Service for Legal Desk specialist business logic."""

    def create(self, db: Session, data: SpecialistCreateDTO) -> LdSpecialist:
        """
        Create a new specialist with expertise and jurisdictions.

        Args:
            db: Database session
            data: Specialist creation data including expertise and jurisdictions

        Returns:
            Created LdSpecialist object
        """
        print(f"INFO [LdSpecialistService]: Creating specialist '{data.full_name}'")
        specialist_data = data.model_dump(exclude={"expertise", "jurisdictions"})
        specialist = ld_specialist_repository.create(db, specialist_data)

        for exp in data.expertise:
            expertise = LdSpecialistExpertise(
                specialist_id=specialist.id,
                legal_domain=exp.legal_domain.value,
                proficiency_level=exp.proficiency_level.value,
                years_in_domain=exp.years_in_domain,
            )
            db.add(expertise)
            print(f"INFO [LdSpecialistService]: Added expertise '{exp.legal_domain.value}' for specialist {specialist.id}")

        for jur in data.jurisdictions:
            jurisdiction = LdSpecialistJurisdiction(
                specialist_id=specialist.id,
                country=jur.country,
                region=jur.region,
                is_primary=jur.is_primary,
            )
            db.add(jurisdiction)
            print(f"INFO [LdSpecialistService]: Added jurisdiction '{jur.country}' for specialist {specialist.id}")

        if data.expertise or data.jurisdictions:
            db.flush()

        print(f"INFO [LdSpecialistService]: Specialist '{specialist.full_name}' created with id {specialist.id}")
        return specialist

    def update(self, db: Session, specialist_id: int, data: SpecialistUpdateDTO) -> Optional[LdSpecialist]:
        """
        Update an existing specialist.

        Args:
            db: Database session
            specialist_id: Specialist primary key
            data: Update data (partial)

        Returns:
            Updated LdSpecialist if found, None otherwise
        """
        print(f"INFO [LdSpecialistService]: Updating specialist {specialist_id}")
        existing = ld_specialist_repository.get_by_id(db, specialist_id)
        if not existing:
            print(f"INFO [LdSpecialistService]: Specialist {specialist_id} not found")
            return None
        update_data = data.model_dump(exclude_unset=True, exclude={"expertise", "jurisdictions"})
        updated = ld_specialist_repository.update(db, specialist_id, update_data)
        print(f"INFO [LdSpecialistService]: Specialist {specialist_id} updated successfully")
        return updated

    def get_specialist_detail(self, db: Session, specialist_id: int) -> Optional[LdSpecialist]:
        """
        Get specialist with full details (expertise, jurisdictions, scores).

        Args:
            db: Database session
            specialist_id: Specialist primary key

        Returns:
            LdSpecialist with loaded relationships if found, None otherwise
        """
        print(f"INFO [LdSpecialistService]: Getting specialist detail for {specialist_id}")
        specialist = ld_specialist_repository.get_by_id(db, specialist_id)
        if specialist:
            print(f"INFO [LdSpecialistService]: Found specialist '{specialist.full_name}'")
        else:
            print(f"INFO [LdSpecialistService]: Specialist {specialist_id} not found")
        return specialist

    def list_all(self, db: Session, filters: Optional[dict] = None) -> list[LdSpecialist]:
        """
        List specialists with optional filters.

        Args:
            db: Database session
            filters: Optional filter dict

        Returns:
            List of LdSpecialist objects
        """
        print(f"INFO [LdSpecialistService]: Listing specialists with filters={filters}")
        specialists = ld_specialist_repository.list_all(db, filters)
        print(f"INFO [LdSpecialistService]: Found {len(specialists)} specialists")
        return specialists

    def add_expertise(
        self, db: Session, specialist_id: int, domain: str, proficiency: str
    ) -> LdSpecialistExpertise:
        """
        Add an expertise record for a specialist.

        Args:
            db: Database session
            specialist_id: Specialist primary key
            domain: Legal domain string
            proficiency: Proficiency level string

        Returns:
            Created LdSpecialistExpertise object
        """
        print(f"INFO [LdSpecialistService]: Adding expertise '{domain}' for specialist {specialist_id}")
        expertise = LdSpecialistExpertise(
            specialist_id=specialist_id,
            legal_domain=domain,
            proficiency_level=proficiency,
        )
        db.add(expertise)
        db.flush()
        print(f"INFO [LdSpecialistService]: Expertise '{domain}' added with id {expertise.id}")
        return expertise

    def add_jurisdiction(
        self,
        db: Session,
        specialist_id: int,
        country: str,
        region: Optional[str],
        is_primary: bool,
    ) -> LdSpecialistJurisdiction:
        """
        Add a jurisdiction record for a specialist.

        Args:
            db: Database session
            specialist_id: Specialist primary key
            country: Country name
            region: Optional region within country
            is_primary: Whether this is the primary jurisdiction

        Returns:
            Created LdSpecialistJurisdiction object
        """
        print(f"INFO [LdSpecialistService]: Adding jurisdiction '{country}' for specialist {specialist_id}")
        jurisdiction = LdSpecialistJurisdiction(
            specialist_id=specialist_id,
            country=country,
            region=region,
            is_primary=is_primary,
        )
        db.add(jurisdiction)
        db.flush()
        print(f"INFO [LdSpecialistService]: Jurisdiction '{country}' added with id {jurisdiction.id}")
        return jurisdiction

    def submit_score(
        self, db: Session, specialist_id: int, case_id: int, scores: ScoreSubmitDTO
    ) -> LdSpecialistScore:
        """
        Submit performance scores for a specialist on a case.

        Calculates overall_score as the average of provided score fields,
        then recalculates the specialist's aggregate score.

        Args:
            db: Database session
            specialist_id: Specialist primary key
            case_id: Case primary key
            scores: Score submission data

        Returns:
            Created LdSpecialistScore object
        """
        print(f"INFO [LdSpecialistService]: Submitting score for specialist {specialist_id} on case {case_id}")

        score_fields = [
            scores.quality_score,
            scores.teamwork_score,
            scores.delivery_score,
            scores.satisfaction_score,
        ]
        provided_scores = [s for s in score_fields if s is not None]
        overall = (
            Decimal(str(round(sum(provided_scores) / len(provided_scores), 2)))
            if provided_scores
            else scores.overall_score
        )

        score = LdSpecialistScore(
            specialist_id=specialist_id,
            case_id=case_id,
            quality_score=scores.quality_score,
            teamwork_score=scores.teamwork_score,
            delivery_score=scores.delivery_score,
            satisfaction_score=scores.satisfaction_score,
            overall_score=overall,
            feedback=scores.feedback,
        )
        db.add(score)
        db.flush()

        ld_specialist_repository.update_overall_score(db, specialist_id)
        print(f"INFO [LdSpecialistService]: Score submitted with id {score.id}, overall={overall}")
        return score


# Singleton instance
ld_specialist_service = LdSpecialistService()
