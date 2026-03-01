"""Pipeline stage repository for database operations."""

from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from src.models.pipeline_stage import PipelineStage


class PipelineStageRepository:
    """Repository for PipelineStage database operations."""

    def create_stage(
        self,
        db: Session,
        entity_id: UUID,
        name: str,
        display_name: str,
        order_index: int,
        color: Optional[str] = None,
        is_default: bool = False,
    ) -> PipelineStage:
        """
        Create a new pipeline stage in the database.

        Args:
            db: Database session
            entity_id: Entity UUID this stage belongs to
            name: Machine-readable stage identifier
            display_name: Human-readable stage label
            order_index: Position in Kanban display (0-based)
            color: Optional hex color for UI
            is_default: Whether this is the initial stage for new prospects

        Returns:
            Created PipelineStage object
        """
        print(f"INFO [PipelineStageRepository]: Creating stage '{name}' for entity {entity_id}")
        stage = PipelineStage(
            entity_id=entity_id,
            name=name,
            display_name=display_name,
            order_index=order_index,
            color=color,
            is_default=is_default,
        )
        db.add(stage)
        db.commit()
        db.refresh(stage)
        print(f"INFO [PipelineStageRepository]: Stage created with id {stage.id}")
        return stage

    def get_stage_by_id(self, db: Session, stage_id: UUID) -> Optional[PipelineStage]:
        """
        Find a pipeline stage by ID.

        Args:
            db: Database session
            stage_id: PipelineStage UUID

        Returns:
            PipelineStage object if found, None otherwise
        """
        print(f"INFO [PipelineStageRepository]: Looking up stage by id {stage_id}")
        stage = db.query(PipelineStage).filter(PipelineStage.id == stage_id).first()
        if stage:
            print(f"INFO [PipelineStageRepository]: Found stage '{stage.name}'")
        else:
            print(f"INFO [PipelineStageRepository]: No stage found with id {stage_id}")
        return stage

    def get_stages_by_entity(
        self, db: Session, entity_id: UUID, active_only: bool = True
    ) -> List[PipelineStage]:
        """
        Get pipeline stages for an entity, ordered by order_index.

        Args:
            db: Database session
            entity_id: Entity UUID to filter by
            active_only: If True, only return active stages

        Returns:
            List of PipelineStage objects ordered by order_index
        """
        print(f"INFO [PipelineStageRepository]: Fetching stages for entity {entity_id} (active_only={active_only})")
        query = db.query(PipelineStage).filter(PipelineStage.entity_id == entity_id)
        if active_only:
            query = query.filter(PipelineStage.is_active == True)  # noqa: E712
        stages = query.order_by(PipelineStage.order_index).all()
        print(f"INFO [PipelineStageRepository]: Found {len(stages)} stages")
        return stages

    def get_stage_by_name(
        self, db: Session, entity_id: UUID, name: str
    ) -> Optional[PipelineStage]:
        """
        Find a pipeline stage by entity and name.

        Args:
            db: Database session
            entity_id: Entity UUID
            name: Stage name to look up

        Returns:
            PipelineStage object if found, None otherwise
        """
        print(f"INFO [PipelineStageRepository]: Looking up stage '{name}' for entity {entity_id}")
        stage = (
            db.query(PipelineStage)
            .filter(PipelineStage.entity_id == entity_id, PipelineStage.name == name)
            .first()
        )
        if stage:
            print(f"INFO [PipelineStageRepository]: Found stage '{stage.name}' (id={stage.id})")
        else:
            print(f"INFO [PipelineStageRepository]: No stage found with name '{name}'")
        return stage

    def count_stages_by_entity(
        self, db: Session, entity_id: UUID, active_only: bool = True
    ) -> int:
        """
        Count pipeline stages for an entity.

        Args:
            db: Database session
            entity_id: Entity UUID to filter by
            active_only: If True, only count active stages

        Returns:
            Count of stages
        """
        print(f"INFO [PipelineStageRepository]: Counting stages for entity {entity_id}")
        query = db.query(PipelineStage).filter(PipelineStage.entity_id == entity_id)
        if active_only:
            query = query.filter(PipelineStage.is_active == True)  # noqa: E712
        count = query.count()
        print(f"INFO [PipelineStageRepository]: Count result: {count}")
        return count

    def update_stage(self, db: Session, stage: PipelineStage) -> PipelineStage:
        """
        Update an existing pipeline stage.

        Args:
            db: Database session
            stage: PipelineStage object with updated values

        Returns:
            Updated PipelineStage object
        """
        print(f"INFO [PipelineStageRepository]: Updating stage {stage.id}")
        db.add(stage)
        db.commit()
        db.refresh(stage)
        print(f"INFO [PipelineStageRepository]: Stage {stage.id} updated successfully")
        return stage

    def delete_stage(self, db: Session, stage: PipelineStage) -> None:
        """
        Delete a pipeline stage.

        Args:
            db: Database session
            stage: PipelineStage object to delete
        """
        print(f"INFO [PipelineStageRepository]: Deleting stage {stage.id}")
        db.delete(stage)
        db.commit()
        print(f"INFO [PipelineStageRepository]: Stage {stage.id} deleted successfully")


# Singleton instance
pipeline_stage_repository = PipelineStageRepository()
