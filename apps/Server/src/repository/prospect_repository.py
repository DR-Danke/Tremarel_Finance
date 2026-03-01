"""Prospect repository for database operations."""

from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from src.models.prospect import Prospect


class ProspectRepository:
    """Repository for Prospect database operations."""

    def create_prospect(
        self,
        db: Session,
        entity_id: UUID,
        company_name: str,
        contact_name: Optional[str] = None,
        contact_email: Optional[str] = None,
        contact_phone: Optional[str] = None,
        stage: str = "lead",
        estimated_value: Optional[Decimal] = None,
        source: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Prospect:
        """
        Create a new prospect in the database.

        Args:
            db: Database session
            entity_id: Entity UUID this prospect belongs to
            company_name: Prospect company/organization name
            contact_name: Primary contact person name
            contact_email: Primary contact email
            contact_phone: Primary contact phone
            stage: Pipeline stage (default: lead)
            estimated_value: Estimated deal value
            source: Where the prospect came from
            notes: Free-form notes

        Returns:
            Created Prospect object
        """
        print(f"INFO [ProspectRepository]: Creating prospect '{company_name}' for entity {entity_id}")
        prospect = Prospect(
            entity_id=entity_id,
            company_name=company_name,
            contact_name=contact_name,
            contact_email=contact_email,
            contact_phone=contact_phone,
            stage=stage,
            estimated_value=estimated_value,
            source=source,
            notes=notes,
        )
        db.add(prospect)
        db.commit()
        db.refresh(prospect)
        print(f"INFO [ProspectRepository]: Prospect created with id {prospect.id}")
        return prospect

    def get_prospect_by_id(self, db: Session, prospect_id: UUID) -> Optional[Prospect]:
        """
        Find a prospect by ID.

        Args:
            db: Database session
            prospect_id: Prospect UUID

        Returns:
            Prospect object if found, None otherwise
        """
        print(f"INFO [ProspectRepository]: Looking up prospect by id {prospect_id}")
        prospect = db.query(Prospect).filter(Prospect.id == prospect_id).first()
        if prospect:
            print(f"INFO [ProspectRepository]: Found prospect '{prospect.company_name}'")
        else:
            print(f"INFO [ProspectRepository]: No prospect found with id {prospect_id}")
        return prospect

    def get_prospects_by_entity(
        self,
        db: Session,
        entity_id: UUID,
        stage: Optional[str] = None,
        is_active: Optional[bool] = None,
        source: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Prospect]:
        """
        Get prospects for an entity with optional filters and pagination.

        Args:
            db: Database session
            entity_id: Entity UUID to filter by
            stage: Optional stage filter
            is_active: Optional active status filter
            source: Optional source filter
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Prospect objects
        """
        print(f"INFO [ProspectRepository]: Fetching prospects for entity {entity_id} (stage={stage}, is_active={is_active}, source={source})")
        query = db.query(Prospect).filter(Prospect.entity_id == entity_id)
        if stage is not None:
            query = query.filter(Prospect.stage == stage)
        if is_active is not None:
            query = query.filter(Prospect.is_active == is_active)  # noqa: E712
        if source is not None:
            query = query.filter(Prospect.source == source)
        prospects = query.order_by(Prospect.created_at.desc()).offset(skip).limit(limit).all()
        print(f"INFO [ProspectRepository]: Found {len(prospects)} prospects")
        return prospects

    def count_prospects_by_entity(
        self,
        db: Session,
        entity_id: UUID,
        stage: Optional[str] = None,
        is_active: Optional[bool] = None,
        source: Optional[str] = None,
    ) -> int:
        """
        Count prospects for an entity with optional filters.

        Args:
            db: Database session
            entity_id: Entity UUID to filter by
            stage: Optional stage filter
            is_active: Optional active status filter
            source: Optional source filter

        Returns:
            Count of prospects
        """
        print(f"INFO [ProspectRepository]: Counting prospects for entity {entity_id}")
        query = db.query(Prospect).filter(Prospect.entity_id == entity_id)
        if stage is not None:
            query = query.filter(Prospect.stage == stage)
        if is_active is not None:
            query = query.filter(Prospect.is_active == is_active)  # noqa: E712
        if source is not None:
            query = query.filter(Prospect.source == source)
        count = query.count()
        print(f"INFO [ProspectRepository]: Count result: {count}")
        return count

    def update_prospect(self, db: Session, prospect: Prospect) -> Prospect:
        """
        Update an existing prospect.

        Args:
            db: Database session
            prospect: Prospect object with updated values

        Returns:
            Updated Prospect object
        """
        print(f"INFO [ProspectRepository]: Updating prospect {prospect.id}")
        db.add(prospect)
        db.commit()
        db.refresh(prospect)
        print(f"INFO [ProspectRepository]: Prospect {prospect.id} updated successfully")
        return prospect

    def delete_prospect(self, db: Session, prospect: Prospect) -> None:
        """
        Delete a prospect.

        Args:
            db: Database session
            prospect: Prospect object to delete
        """
        print(f"INFO [ProspectRepository]: Deleting prospect {prospect.id}")
        db.delete(prospect)
        db.commit()
        print(f"INFO [ProspectRepository]: Prospect {prospect.id} deleted successfully")


# Singleton instance
prospect_repository = ProspectRepository()
