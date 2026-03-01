"""Pipeline stage service for business logic."""

from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy.orm import Session

from src.interface.pipeline_stage_dto import PipelineStageCreateDTO, PipelineStageUpdateDTO
from src.interface.stage_transition_dto import StageTransitionCreateDTO
from src.models.pipeline_stage import PipelineStage
from src.models.stage_transition import StageTransition
from src.repository.pipeline_stage_repository import pipeline_stage_repository
from src.repository.stage_transition_repository import stage_transition_repository

# Default pipeline stages matching the prospects.stage CHECK constraint
DEFAULT_STAGES = [
    {"name": "lead", "display_name": "Lead", "order_index": 0, "color": "#90CAF9", "is_default": True},
    {"name": "contacted", "display_name": "Contacted", "order_index": 1, "color": "#80DEEA"},
    {"name": "qualified", "display_name": "Qualified", "order_index": 2, "color": "#A5D6A7"},
    {"name": "proposal", "display_name": "Proposal", "order_index": 3, "color": "#FFE082"},
    {"name": "negotiation", "display_name": "Negotiation", "order_index": 4, "color": "#FFAB91"},
    {"name": "won", "display_name": "Won", "order_index": 5, "color": "#66BB6A"},
    {"name": "lost", "display_name": "Lost", "order_index": 6, "color": "#EF5350"},
]


class PipelineStageService:
    """Service for pipeline stage business logic."""

    def create_stage(self, db: Session, data: PipelineStageCreateDTO) -> PipelineStage:
        """
        Create a new pipeline stage.

        Args:
            db: Database session
            data: Pipeline stage creation data

        Returns:
            Created PipelineStage object
        """
        print(f"INFO [PipelineStageService]: Creating stage '{data.name}' for entity {data.entity_id}")
        stage = pipeline_stage_repository.create_stage(
            db=db,
            entity_id=data.entity_id,
            name=data.name,
            display_name=data.display_name,
            order_index=data.order_index,
            color=data.color,
            is_default=data.is_default,
        )
        print(f"INFO [PipelineStageService]: Stage '{stage.name}' created with id {stage.id}")
        return stage

    def get_stage(
        self, db: Session, stage_id: UUID, entity_id: UUID
    ) -> Optional[PipelineStage]:
        """
        Get a pipeline stage by ID, validating entity ownership.

        Args:
            db: Database session
            stage_id: PipelineStage UUID
            entity_id: Entity UUID for validation

        Returns:
            PipelineStage object if found and belongs to entity, None otherwise
        """
        print(f"INFO [PipelineStageService]: Getting stage {stage_id}")
        stage = pipeline_stage_repository.get_stage_by_id(db, stage_id)
        if stage and stage.entity_id != entity_id:
            print(f"ERROR [PipelineStageService]: Stage {stage_id} does not belong to entity {entity_id}")
            return None
        return stage

    def list_stages(
        self, db: Session, entity_id: UUID, active_only: bool = True
    ) -> Tuple[List[PipelineStage], int]:
        """
        List pipeline stages for an entity.

        Args:
            db: Database session
            entity_id: Entity UUID to filter by
            active_only: If True, only return active stages

        Returns:
            Tuple of (list of stages ordered by order_index, total count)
        """
        print(f"INFO [PipelineStageService]: Listing stages for entity {entity_id}")
        stages = pipeline_stage_repository.get_stages_by_entity(db, entity_id, active_only)
        total = pipeline_stage_repository.count_stages_by_entity(db, entity_id, active_only)
        print(f"INFO [PipelineStageService]: Found {len(stages)} stages (total: {total})")
        return stages, total

    def update_stage(
        self,
        db: Session,
        stage_id: UUID,
        entity_id: UUID,
        data: PipelineStageUpdateDTO,
    ) -> Optional[PipelineStage]:
        """
        Update an existing pipeline stage.

        Args:
            db: Database session
            stage_id: PipelineStage UUID
            entity_id: Entity UUID for validation
            data: Update data

        Returns:
            Updated PipelineStage object if found and updated, None otherwise
        """
        print(f"INFO [PipelineStageService]: Updating stage {stage_id}")
        stage = pipeline_stage_repository.get_stage_by_id(db, stage_id)
        if not stage:
            print(f"ERROR [PipelineStageService]: Stage {stage_id} not found")
            return None
        if stage.entity_id != entity_id:
            print(f"ERROR [PipelineStageService]: Stage {stage_id} does not belong to entity {entity_id}")
            return None

        if data.name is not None:
            stage.name = data.name
        if data.display_name is not None:
            stage.display_name = data.display_name
        if data.order_index is not None:
            stage.order_index = data.order_index
        if data.color is not None:
            stage.color = data.color
        if data.is_default is not None:
            stage.is_default = data.is_default
        if data.is_active is not None:
            stage.is_active = data.is_active

        updated = pipeline_stage_repository.update_stage(db, stage)
        print(f"INFO [PipelineStageService]: Stage {stage_id} updated successfully")
        return updated

    def delete_stage(self, db: Session, stage_id: UUID, entity_id: UUID) -> bool:
        """
        Delete a pipeline stage.

        Args:
            db: Database session
            stage_id: PipelineStage UUID
            entity_id: Entity UUID for validation

        Returns:
            True if deleted, False if not found or not owned
        """
        print(f"INFO [PipelineStageService]: Deleting stage {stage_id}")
        stage = pipeline_stage_repository.get_stage_by_id(db, stage_id)
        if not stage:
            print(f"ERROR [PipelineStageService]: Stage {stage_id} not found")
            return False
        if stage.entity_id != entity_id:
            print(f"ERROR [PipelineStageService]: Stage {stage_id} does not belong to entity {entity_id}")
            return False

        pipeline_stage_repository.delete_stage(db, stage)
        print(f"INFO [PipelineStageService]: Stage {stage_id} deleted successfully")
        return True

    def seed_default_stages(self, db: Session, entity_id: UUID) -> List[PipelineStage]:
        """
        Seed default pipeline stages for an entity.

        Creates the seven standard stages (lead, contacted, qualified, proposal,
        negotiation, won, lost) with correct order_index. Skips if entity already
        has stages.

        Args:
            db: Database session
            entity_id: Entity UUID to seed stages for

        Returns:
            List of created PipelineStage objects (empty if entity already has stages)
        """
        print(f"INFO [PipelineStageService]: Seeding default stages for entity {entity_id}")
        existing_count = pipeline_stage_repository.count_stages_by_entity(
            db, entity_id, active_only=False
        )
        if existing_count > 0:
            print(f"INFO [PipelineStageService]: Entity {entity_id} already has {existing_count} stages, skipping seed")
            return []

        created_stages = []
        for stage_data in DEFAULT_STAGES:
            stage = pipeline_stage_repository.create_stage(
                db=db,
                entity_id=entity_id,
                name=stage_data["name"],
                display_name=stage_data["display_name"],
                order_index=stage_data["order_index"],
                color=stage_data.get("color"),
                is_default=stage_data.get("is_default", False),
            )
            created_stages.append(stage)

        print(f"INFO [PipelineStageService]: Seeded {len(created_stages)} default stages for entity {entity_id}")
        return created_stages

    def record_transition(
        self, db: Session, data: StageTransitionCreateDTO
    ) -> StageTransition:
        """
        Record a stage transition.

        Args:
            db: Database session
            data: Stage transition creation data

        Returns:
            Created StageTransition object
        """
        print(f"INFO [PipelineStageService]: Recording transition for prospect {data.prospect_id}")
        transition = stage_transition_repository.create_transition(
            db=db,
            prospect_id=data.prospect_id,
            entity_id=data.entity_id,
            from_stage_id=data.from_stage_id,
            to_stage_id=data.to_stage_id,
            transitioned_by=data.transitioned_by,
            notes=data.notes,
        )
        print(f"INFO [PipelineStageService]: Transition {transition.id} recorded")
        return transition

    def get_prospect_transitions(
        self,
        db: Session,
        prospect_id: UUID,
        entity_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[StageTransition], int]:
        """
        Get stage transition history for a prospect.

        Args:
            db: Database session
            prospect_id: Prospect UUID
            entity_id: Entity UUID for validation
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Tuple of (list of transitions, total count)
        """
        print(f"INFO [PipelineStageService]: Getting transitions for prospect {prospect_id}")
        transitions = stage_transition_repository.get_transitions_by_prospect(
            db, prospect_id, skip, limit
        )
        total = stage_transition_repository.count_transitions_by_prospect(db, prospect_id)
        print(f"INFO [PipelineStageService]: Found {len(transitions)} transitions (total: {total})")
        return transitions, total


# Singleton instance
pipeline_stage_service = PipelineStageService()
