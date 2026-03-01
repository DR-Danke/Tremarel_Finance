"""Prospect service for business logic."""

from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy.orm import Session

from src.interface.prospect_dto import ProspectCreateDTO, ProspectUpdateDTO
from src.interface.stage_transition_dto import StageTransitionCreateDTO
from src.models.prospect import Prospect
from src.repository.pipeline_stage_repository import pipeline_stage_repository
from src.repository.prospect_repository import prospect_repository
from src.repository.stage_transition_repository import stage_transition_repository


class ProspectService:
    """Service for prospect business logic."""

    def create_prospect(self, db: Session, data: ProspectCreateDTO) -> Prospect:
        """
        Create a new prospect.

        Args:
            db: Database session
            data: Prospect creation data

        Returns:
            Created Prospect object
        """
        print(f"INFO [ProspectService]: Creating prospect '{data.company_name}' for entity {data.entity_id}")
        prospect = prospect_repository.create_prospect(
            db=db,
            entity_id=data.entity_id,
            company_name=data.company_name,
            contact_name=data.contact_name,
            contact_email=data.contact_email,
            contact_phone=data.contact_phone,
            stage=data.stage,
            estimated_value=data.estimated_value,
            source=data.source,
            notes=data.notes,
        )
        print(f"INFO [ProspectService]: Prospect '{prospect.company_name}' created with id {prospect.id}")
        return prospect

    def get_prospect(
        self, db: Session, prospect_id: UUID, entity_id: UUID
    ) -> Optional[Prospect]:
        """
        Get a prospect by ID, validating entity ownership.

        Args:
            db: Database session
            prospect_id: Prospect UUID
            entity_id: Entity UUID for validation

        Returns:
            Prospect object if found and belongs to entity, None otherwise
        """
        print(f"INFO [ProspectService]: Getting prospect {prospect_id}")
        prospect = prospect_repository.get_prospect_by_id(db, prospect_id)
        if prospect and prospect.entity_id != entity_id:
            print(f"ERROR [ProspectService]: Prospect {prospect_id} does not belong to entity {entity_id}")
            return None
        return prospect

    def list_prospects(
        self,
        db: Session,
        entity_id: UUID,
        stage: Optional[str] = None,
        is_active: Optional[bool] = None,
        source: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[Prospect], int]:
        """
        List prospects for an entity with optional filters.

        Args:
            db: Database session
            entity_id: Entity UUID to filter by
            stage: Optional stage filter
            is_active: Optional active status filter
            source: Optional source filter
            skip: Pagination offset
            limit: Maximum results to return

        Returns:
            Tuple of (list of prospects, total count)
        """
        print(f"INFO [ProspectService]: Listing prospects for entity {entity_id}")
        prospects = prospect_repository.get_prospects_by_entity(
            db, entity_id, stage, is_active, source, skip, limit
        )
        total = prospect_repository.count_prospects_by_entity(
            db, entity_id, stage, is_active, source
        )
        print(f"INFO [ProspectService]: Found {len(prospects)} prospects (total: {total})")
        return prospects, total

    def update_prospect(
        self,
        db: Session,
        prospect_id: UUID,
        entity_id: UUID,
        data: ProspectUpdateDTO,
    ) -> Optional[Prospect]:
        """
        Update an existing prospect.

        Args:
            db: Database session
            prospect_id: Prospect UUID
            entity_id: Entity UUID for validation
            data: Update data

        Returns:
            Updated Prospect object if found and updated, None otherwise
        """
        print(f"INFO [ProspectService]: Updating prospect {prospect_id}")
        prospect = prospect_repository.get_prospect_by_id(db, prospect_id)
        if not prospect:
            print(f"ERROR [ProspectService]: Prospect {prospect_id} not found")
            return None
        if prospect.entity_id != entity_id:
            print(f"ERROR [ProspectService]: Prospect {prospect_id} does not belong to entity {entity_id}")
            return None

        if data.company_name is not None:
            prospect.company_name = data.company_name
        if data.contact_name is not None:
            prospect.contact_name = data.contact_name
        if data.contact_email is not None:
            prospect.contact_email = data.contact_email
        if data.contact_phone is not None:
            prospect.contact_phone = data.contact_phone
        if data.stage is not None:
            prospect.stage = data.stage
        if data.estimated_value is not None:
            prospect.estimated_value = data.estimated_value
        if data.source is not None:
            prospect.source = data.source
        if data.notes is not None:
            prospect.notes = data.notes
        if data.is_active is not None:
            prospect.is_active = data.is_active

        updated = prospect_repository.update_prospect(db, prospect)
        print(f"INFO [ProspectService]: Prospect {prospect_id} updated successfully")
        return updated

    def update_prospect_stage(
        self,
        db: Session,
        prospect_id: UUID,
        entity_id: UUID,
        new_stage: str,
        user_id: Optional[UUID] = None,
        notes: Optional[str] = None,
    ) -> Optional[Prospect]:
        """
        Update a prospect's stage and record the transition in the audit trail.

        Args:
            db: Database session
            prospect_id: Prospect UUID
            entity_id: Entity UUID for validation
            new_stage: New stage name
            user_id: User who triggered the change
            notes: Optional transition notes

        Returns:
            Updated Prospect object if found and updated, None otherwise
        """
        print(f"INFO [ProspectService]: Updating stage for prospect {prospect_id} to '{new_stage}'")
        prospect = prospect_repository.get_prospect_by_id(db, prospect_id)
        if not prospect:
            print(f"ERROR [ProspectService]: Prospect {prospect_id} not found")
            return None
        if prospect.entity_id != entity_id:
            print(f"ERROR [ProspectService]: Prospect {prospect_id} does not belong to entity {entity_id}")
            return None

        old_stage_name = prospect.stage

        # Look up PipelineStage records by name for audit trail
        old_stage_record = pipeline_stage_repository.get_stage_by_name(db, entity_id, old_stage_name)
        new_stage_record = pipeline_stage_repository.get_stage_by_name(db, entity_id, new_stage)

        # Update the prospect's stage
        prospect.stage = new_stage
        updated = prospect_repository.update_prospect(db, prospect)

        # Record the stage transition in the audit trail
        from_stage_id = old_stage_record.id if old_stage_record else None
        to_stage_id = new_stage_record.id if new_stage_record else None

        if to_stage_id:
            transition_data = StageTransitionCreateDTO(
                prospect_id=prospect_id,
                entity_id=entity_id,
                from_stage_id=from_stage_id,
                to_stage_id=to_stage_id,
                transitioned_by=user_id,
                notes=notes,
            )
            stage_transition_repository.create_transition(
                db=db,
                prospect_id=transition_data.prospect_id,
                entity_id=transition_data.entity_id,
                from_stage_id=transition_data.from_stage_id,
                to_stage_id=transition_data.to_stage_id,
                transitioned_by=transition_data.transitioned_by,
                notes=transition_data.notes,
            )
            print(f"INFO [ProspectService]: Stage transition recorded: {old_stage_name} -> {new_stage}")
        else:
            print(f"WARN [ProspectService]: No PipelineStage record found for '{new_stage}', transition not recorded")

        print(f"INFO [ProspectService]: Prospect {prospect_id} stage updated to '{new_stage}'")
        return updated

    def delete_prospect(self, db: Session, prospect_id: UUID, entity_id: UUID) -> bool:
        """
        Delete a prospect.

        Args:
            db: Database session
            prospect_id: Prospect UUID
            entity_id: Entity UUID for validation

        Returns:
            True if deleted, False if not found or not owned
        """
        print(f"INFO [ProspectService]: Deleting prospect {prospect_id}")
        prospect = prospect_repository.get_prospect_by_id(db, prospect_id)
        if not prospect:
            print(f"ERROR [ProspectService]: Prospect {prospect_id} not found")
            return False
        if prospect.entity_id != entity_id:
            print(f"ERROR [ProspectService]: Prospect {prospect_id} does not belong to entity {entity_id}")
            return False

        prospect_repository.delete_prospect(db, prospect)
        print(f"INFO [ProspectService]: Prospect {prospect_id} deleted successfully")
        return True


# Singleton instance
prospect_service = ProspectService()
