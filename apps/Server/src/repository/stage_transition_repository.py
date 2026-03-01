"""Stage transition repository for database operations."""

from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from src.models.stage_transition import StageTransition


class StageTransitionRepository:
    """Repository for StageTransition database operations. Read/create only — transitions are immutable."""

    def create_transition(
        self,
        db: Session,
        prospect_id: UUID,
        entity_id: UUID,
        from_stage_id: Optional[UUID],
        to_stage_id: UUID,
        transitioned_by: Optional[UUID] = None,
        notes: Optional[str] = None,
    ) -> StageTransition:
        """
        Create a new stage transition record.

        Args:
            db: Database session
            prospect_id: Prospect being transitioned
            entity_id: Entity UUID for scoping
            from_stage_id: Previous stage ID (None for initial assignment)
            to_stage_id: Target stage ID
            transitioned_by: User who triggered the change (None for system)
            notes: Optional transition notes

        Returns:
            Created StageTransition object
        """
        print(f"INFO [StageTransitionRepository]: Creating transition for prospect {prospect_id}")
        transition = StageTransition(
            prospect_id=prospect_id,
            entity_id=entity_id,
            from_stage_id=from_stage_id,
            to_stage_id=to_stage_id,
            transitioned_by=transitioned_by,
            notes=notes,
        )
        db.add(transition)
        db.commit()
        db.refresh(transition)
        print(f"INFO [StageTransitionRepository]: Transition created with id {transition.id}")
        return transition

    def get_transitions_by_prospect(
        self, db: Session, prospect_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[StageTransition]:
        """
        Get stage transitions for a prospect, ordered by created_at descending.

        Args:
            db: Database session
            prospect_id: Prospect UUID
            skip: Number of records to skip (pagination)
            limit: Maximum number of records to return

        Returns:
            List of StageTransition objects
        """
        print(f"INFO [StageTransitionRepository]: Fetching transitions for prospect {prospect_id}")
        transitions = (
            db.query(StageTransition)
            .filter(StageTransition.prospect_id == prospect_id)
            .order_by(StageTransition.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        print(f"INFO [StageTransitionRepository]: Found {len(transitions)} transitions")
        return transitions

    def count_transitions_by_prospect(self, db: Session, prospect_id: UUID) -> int:
        """
        Count stage transitions for a prospect.

        Args:
            db: Database session
            prospect_id: Prospect UUID

        Returns:
            Count of transitions
        """
        print(f"INFO [StageTransitionRepository]: Counting transitions for prospect {prospect_id}")
        count = (
            db.query(StageTransition)
            .filter(StageTransition.prospect_id == prospect_id)
            .count()
        )
        print(f"INFO [StageTransitionRepository]: Count result: {count}")
        return count

    def get_transitions_by_entity(
        self, db: Session, entity_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[StageTransition]:
        """
        Get stage transitions for an entity, ordered by created_at descending.

        Args:
            db: Database session
            entity_id: Entity UUID
            skip: Number of records to skip (pagination)
            limit: Maximum number of records to return

        Returns:
            List of StageTransition objects
        """
        print(f"INFO [StageTransitionRepository]: Fetching transitions for entity {entity_id}")
        transitions = (
            db.query(StageTransition)
            .filter(StageTransition.entity_id == entity_id)
            .order_by(StageTransition.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        print(f"INFO [StageTransitionRepository]: Found {len(transitions)} transitions")
        return transitions

    def count_transitions_by_entity(self, db: Session, entity_id: UUID) -> int:
        """
        Count stage transitions for an entity.

        Args:
            db: Database session
            entity_id: Entity UUID

        Returns:
            Count of transitions
        """
        print(f"INFO [StageTransitionRepository]: Counting transitions for entity {entity_id}")
        count = (
            db.query(StageTransition)
            .filter(StageTransition.entity_id == entity_id)
            .count()
        )
        print(f"INFO [StageTransitionRepository]: Count result: {count}")
        return count


# Singleton instance
stage_transition_repository = StageTransitionRepository()
