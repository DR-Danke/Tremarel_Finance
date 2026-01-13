"""Recurring template service for business logic."""

from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy.orm import Session

from src.interface.recurring_template_dto import (
    RecurringTemplateCreateDTO,
    RecurringTemplateUpdateDTO,
)
from src.models.recurring_template import RecurringTemplate
from src.repository.recurring_template_repository import recurring_template_repository


class RecurringTemplateService:
    """Service for recurring template business logic."""

    def create_template(
        self,
        db: Session,
        data: RecurringTemplateCreateDTO,
    ) -> RecurringTemplate:
        """
        Create a new recurring template.

        Args:
            db: Database session
            data: Template creation data

        Returns:
            Created RecurringTemplate object
        """
        print(f"INFO [RecurringTemplateService]: Creating template '{data.name}' for entity {data.entity_id}")
        template = recurring_template_repository.create_template(
            db=db,
            entity_id=data.entity_id,
            category_id=data.category_id,
            name=data.name,
            amount=data.amount,
            type=data.type,
            frequency=data.frequency,
            start_date=data.start_date,
            description=data.description,
            notes=data.notes,
            end_date=data.end_date,
        )
        print(f"INFO [RecurringTemplateService]: Template {template.id} created successfully")
        return template

    def get_template(
        self,
        db: Session,
        template_id: UUID,
        entity_id: UUID,
    ) -> Optional[RecurringTemplate]:
        """
        Get a recurring template by ID, validating entity ownership.

        Args:
            db: Database session
            template_id: Template UUID
            entity_id: Entity UUID for validation

        Returns:
            RecurringTemplate object if found and belongs to entity, None otherwise
        """
        print(f"INFO [RecurringTemplateService]: Getting template {template_id}")
        template = recurring_template_repository.get_template_by_id(db, template_id)
        if template and template.entity_id != entity_id:
            print(f"ERROR [RecurringTemplateService]: Template {template_id} does not belong to entity {entity_id}")
            return None
        return template

    def list_templates(
        self,
        db: Session,
        entity_id: UUID,
        include_inactive: bool = False,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[RecurringTemplate], int]:
        """
        List recurring templates for an entity with pagination.

        Args:
            db: Database session
            entity_id: Entity UUID to filter by
            include_inactive: Whether to include inactive templates
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Tuple of (list of templates, total count)
        """
        print(f"INFO [RecurringTemplateService]: Listing templates for entity {entity_id}")
        templates = recurring_template_repository.get_templates_by_entity(
            db=db,
            entity_id=entity_id,
            include_inactive=include_inactive,
            skip=skip,
            limit=limit,
        )
        total = recurring_template_repository.count_templates_by_entity(
            db=db,
            entity_id=entity_id,
            include_inactive=include_inactive,
        )
        print(f"INFO [RecurringTemplateService]: Found {len(templates)} templates (total: {total})")
        return templates, total

    def update_template(
        self,
        db: Session,
        template_id: UUID,
        entity_id: UUID,
        data: RecurringTemplateUpdateDTO,
    ) -> Optional[RecurringTemplate]:
        """
        Update an existing recurring template.

        Args:
            db: Database session
            template_id: Template UUID
            entity_id: Entity UUID for validation
            data: Update data

        Returns:
            Updated RecurringTemplate object if found and updated, None otherwise
        """
        print(f"INFO [RecurringTemplateService]: Updating template {template_id}")
        template = recurring_template_repository.get_template_by_id(db, template_id)
        if not template:
            print(f"ERROR [RecurringTemplateService]: Template {template_id} not found")
            return None
        if template.entity_id != entity_id:
            print(f"ERROR [RecurringTemplateService]: Template {template_id} does not belong to entity {entity_id}")
            return None

        # Update fields if provided
        if data.category_id is not None:
            template.category_id = data.category_id
        if data.name is not None:
            template.name = data.name
        if data.amount is not None:
            template.amount = data.amount
        if data.type is not None:
            template.type = data.type
        if data.description is not None:
            template.description = data.description
        if data.notes is not None:
            template.notes = data.notes
        if data.frequency is not None:
            template.frequency = data.frequency
        if data.start_date is not None:
            template.start_date = data.start_date
        if data.end_date is not None:
            template.end_date = data.end_date
        if data.is_active is not None:
            template.is_active = data.is_active

        updated = recurring_template_repository.update_template(db, template)
        print(f"INFO [RecurringTemplateService]: Template {template_id} updated successfully")
        return updated

    def deactivate_template(
        self,
        db: Session,
        template_id: UUID,
        entity_id: UUID,
    ) -> Optional[RecurringTemplate]:
        """
        Deactivate a recurring template (soft delete).

        Args:
            db: Database session
            template_id: Template UUID
            entity_id: Entity UUID for validation

        Returns:
            Deactivated RecurringTemplate object if found, None otherwise
        """
        print(f"INFO [RecurringTemplateService]: Deactivating template {template_id}")
        template = recurring_template_repository.get_template_by_id(db, template_id)
        if not template:
            print(f"ERROR [RecurringTemplateService]: Template {template_id} not found")
            return None
        if template.entity_id != entity_id:
            print(f"ERROR [RecurringTemplateService]: Template {template_id} does not belong to entity {entity_id}")
            return None

        deactivated = recurring_template_repository.deactivate_template(db, template)
        print(f"INFO [RecurringTemplateService]: Template {template_id} deactivated successfully")
        return deactivated

    def delete_template(
        self,
        db: Session,
        template_id: UUID,
        entity_id: UUID,
    ) -> bool:
        """
        Delete a recurring template (hard delete).

        Args:
            db: Database session
            template_id: Template UUID
            entity_id: Entity UUID for validation

        Returns:
            True if deleted, False if not found or not owned
        """
        print(f"INFO [RecurringTemplateService]: Deleting template {template_id}")
        template = recurring_template_repository.get_template_by_id(db, template_id)
        if not template:
            print(f"ERROR [RecurringTemplateService]: Template {template_id} not found")
            return False
        if template.entity_id != entity_id:
            print(f"ERROR [RecurringTemplateService]: Template {template_id} does not belong to entity {entity_id}")
            return False

        recurring_template_repository.delete_template(db, template)
        print(f"INFO [RecurringTemplateService]: Template {template_id} deleted successfully")
        return True


# Singleton instance
recurring_template_service = RecurringTemplateService()
