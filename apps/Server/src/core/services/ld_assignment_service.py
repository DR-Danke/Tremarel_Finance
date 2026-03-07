"""Legal Desk specialist assignment engine service.

Orchestrates specialist suggestion scoring, assignment lifecycle,
and workload management for legal case assignments.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy.orm import Session

from src.interface.legaldesk_dto import (
    AssignmentCreateDTO,
    SpecialistCandidateDTO,
    SuggestionResponseDTO,
)
from src.models.ld_case_specialist import LdCaseSpecialist
from src.repository.ld_assignment_repository import ld_assignment_repository
from src.repository.ld_case_repository import ld_case_repository
from src.repository.ld_client_repository import ld_client_repository
from src.repository.ld_specialist_repository import ld_specialist_repository

_PROFICIENCY_SCORES = {"expert": 30, "intermediate": 20, "junior": 10}
_MAX_CANDIDATES = 5


class LdAssignmentService:
    """Service for intelligent specialist assignment and lifecycle management."""

    def suggest_specialists(self, db: Session, case_id: int) -> SuggestionResponseDTO:
        """
        Score and rank specialists for a case.

        Fetches case details, resolves jurisdiction from client country,
        retrieves filtered candidates, scores each on 5 weighted factors,
        and returns the top 5 ranked by match score descending.

        Args:
            db: Database session
            case_id: Case identifier

        Returns:
            SuggestionResponseDTO with ranked candidates

        Raises:
            ValueError: If case not found
        """
        print(f"INFO [LdAssignmentService]: Suggesting specialists for case {case_id}")

        case = ld_case_repository.get_by_id(db, case_id)
        if not case:
            print(f"ERROR [LdAssignmentService]: Case {case_id} not found")
            raise ValueError("Case not found")

        client = ld_client_repository.get_by_id(db, case.client_id)
        client_country: Optional[str] = client.country if client else None

        print(f"INFO [LdAssignmentService]: Case domain={case.legal_domain}, jurisdiction={client_country}")

        specialists = ld_specialist_repository.get_available(
            db, case.legal_domain, client_country
        )

        candidates: list[SpecialistCandidateDTO] = []
        for specialist in specialists:
            expertise = None
            for e in specialist.expertise:
                if e.legal_domain == case.legal_domain:
                    expertise = e
                    break
            if not expertise:
                continue

            score, reasons = self._calculate_match_score(
                specialist, case, expertise, client_country
            )
            normalized_score = Decimal(str(round(min(score, 100) / 100, 4)))

            expertise_matches = [
                e.legal_domain for e in specialist.expertise
            ]
            jurisdiction_matches = [
                j.country for j in specialist.jurisdictions
            ]

            candidate = SpecialistCandidateDTO(
                specialist_id=specialist.id,
                full_name=specialist.full_name,
                email=specialist.email,
                match_score=normalized_score,
                hourly_rate=specialist.hourly_rate,
                currency=specialist.currency,
                current_workload=specialist.current_workload,
                max_concurrent_cases=specialist.max_concurrent_cases,
                expertise_match=expertise_matches,
                jurisdiction_match=jurisdiction_matches,
                match_reasons=reasons,
            )
            candidates.append(candidate)

        candidates.sort(key=lambda c: c.match_score, reverse=True)
        top_candidates = candidates[:_MAX_CANDIDATES]

        print(f"INFO [LdAssignmentService]: Returning {len(top_candidates)} candidates for case {case_id}")

        return SuggestionResponseDTO(
            case_id=case_id,
            legal_domain=case.legal_domain,
            candidates=top_candidates,
            generated_at=datetime.utcnow(),
        )

    def _calculate_match_score(
        self, specialist, case, expertise, client_country: Optional[str]
    ) -> tuple[float, list[str]]:
        """
        Calculate a 0-100 match score across 5 weighted factors.

        Factors:
            - Expertise proficiency (30 pts)
            - Overall score (25 pts)
            - Workload availability (20 pts)
            - Jurisdiction match (15 pts)
            - Years experience (10 pts)

        Args:
            specialist: LdSpecialist ORM instance
            case: LdCase ORM instance
            expertise: LdSpecialistExpertise matching the case domain
            client_country: Jurisdiction country or None

        Returns:
            Tuple of (score, reasons list)
        """
        reasons: list[str] = []
        total = 0.0

        # 1. Expertise proficiency (30 pts)
        proficiency = expertise.proficiency_level.lower() if expertise.proficiency_level else "junior"
        prof_score = _PROFICIENCY_SCORES.get(proficiency, 10)
        total += prof_score
        reasons.append(f"Expertise proficiency ({proficiency}): {prof_score}/30 pts")

        # 2. Overall score (25 pts)
        overall = float(specialist.overall_score) if specialist.overall_score else 0.0
        overall_pts = (overall / 5.0) * 25
        total += overall_pts
        reasons.append(f"Overall score ({overall}/5.0): {overall_pts:.1f}/25 pts")

        # 3. Workload availability (20 pts)
        max_cases = specialist.max_concurrent_cases or 1
        if max_cases > 0:
            workload_pts = ((max_cases - specialist.current_workload) / max_cases) * 20
        else:
            workload_pts = 0.0
        total += workload_pts
        reasons.append(
            f"Workload availability ({specialist.current_workload}/{max_cases}): {workload_pts:.1f}/20 pts"
        )

        # 4. Jurisdiction match (15 pts)
        if client_country is None:
            jurisdiction_pts = 15.0
            reasons.append("No jurisdiction requirement: 15/15 pts")
        else:
            jurisdiction_pts = 0.0
            best_coverage = None
            for j in specialist.jurisdictions:
                if j.country == client_country:
                    if j.region is None:
                        best_coverage = "full"
                        break
                    else:
                        best_coverage = "regional"
            if best_coverage == "full":
                jurisdiction_pts = 15.0
                reasons.append(f"Full jurisdiction coverage ({client_country}): 15/15 pts")
            elif best_coverage == "regional":
                jurisdiction_pts = 10.0
                reasons.append(f"Regional jurisdiction coverage ({client_country}): 10/15 pts")
            else:
                reasons.append(f"No jurisdiction match ({client_country}): 0/15 pts")
        total += jurisdiction_pts

        # 5. Years experience (10 pts)
        years = specialist.years_experience or 0
        experience_pts = min(years / 20 * 10, 10)
        total += experience_pts
        reasons.append(f"Years experience ({years} yrs): {experience_pts:.1f}/10 pts")

        return (total, reasons)

    def assign_specialist(self, db: Session, data: AssignmentCreateDTO) -> LdCaseSpecialist:
        """
        Create a specialist assignment and increment workload.

        Args:
            db: Database session
            data: Assignment creation DTO

        Returns:
            Created LdCaseSpecialist

        Raises:
            ValueError: If case or specialist not found
        """
        print(f"INFO [LdAssignmentService]: Assigning specialist {data.specialist_id} to case {data.case_id}")

        case = ld_case_repository.get_by_id(db, data.case_id)
        if not case:
            print(f"ERROR [LdAssignmentService]: Case {data.case_id} not found")
            raise ValueError("Case not found")

        specialist = ld_specialist_repository.get_by_id(db, data.specialist_id)
        if not specialist:
            print(f"ERROR [LdAssignmentService]: Specialist {data.specialist_id} not found")
            raise ValueError("Specialist not found")

        assignment = ld_assignment_repository.create_assignment(db, {
            "case_id": data.case_id,
            "specialist_id": data.specialist_id,
            "role": data.role.value if hasattr(data.role, "value") else data.role,
            "proposed_fee": data.proposed_fee,
            "fee_currency": data.fee_currency,
        })

        ld_specialist_repository.update_workload(db, data.specialist_id, 1)

        print(f"INFO [LdAssignmentService]: Assignment {assignment.id} created, workload incremented")
        return assignment

    def update_assignment_status(
        self, db: Session, assignment_id: int, status: str
    ) -> LdCaseSpecialist:
        """
        Update assignment status with workload management.

        Decrements specialist workload when status is "completed" or "rejected".

        Args:
            db: Database session
            assignment_id: Assignment identifier
            status: New status value

        Returns:
            Updated LdCaseSpecialist

        Raises:
            ValueError: If assignment not found
        """
        print(f"INFO [LdAssignmentService]: Updating assignment {assignment_id} status to '{status}'")

        assignment = ld_assignment_repository.update_assignment_status(db, assignment_id, status)
        if not assignment:
            print(f"ERROR [LdAssignmentService]: Assignment {assignment_id} not found")
            raise ValueError("Assignment not found")

        if status in ("completed", "rejected"):
            ld_specialist_repository.update_workload(db, assignment.specialist_id, -1)
            print(f"INFO [LdAssignmentService]: Workload decremented for specialist {assignment.specialist_id}")

        print(f"INFO [LdAssignmentService]: Assignment {assignment_id} status updated to '{status}'")
        return assignment

    def get_case_specialists(self, db: Session, case_id: int) -> list[LdCaseSpecialist]:
        """
        Get all specialist assignments for a case.

        Args:
            db: Database session
            case_id: Case identifier

        Returns:
            List of LdCaseSpecialist objects
        """
        print(f"INFO [LdAssignmentService]: Getting specialists for case {case_id}")
        return ld_assignment_repository.get_case_specialists(db, case_id)


# Singleton instance
ld_assignment_service = LdAssignmentService()
