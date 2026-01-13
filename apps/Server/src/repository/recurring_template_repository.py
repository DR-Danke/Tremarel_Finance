"""Recurring template repository for database operations."""

from datetime import date
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from src.models.recurring_template import RecurringTemplate


class RecurringTemplateRepository:
    """Repository for RecurringTemplate database operations."""

    def create_template(
        self,
        db: Session,
        entity_id: UUID,
        category_id: UUID,
        name: str,
        amount: Decimal,
        type: str,
        frequency: str,
        start_date: date,
        description: Optional[str] = None,
        notes: Optional[str] = None,
        end_date: Optional[date] = None,
    ) -> RecurringTemplate:
        """
        Create a new recurring template in the database.

        Args:
            db: Database session
            entity_id: Entity UUID the template belongs to
            category_id: Category UUID for the template
            name: Template name
            amount: Template amount
            type: Transaction type (income or expense)
            frequency: Recurrence frequency (daily, weekly, monthly, yearly)
            start_date: Start date for recurrence
            description: Template description (optional)
            notes: Additional notes (optional)
            end_date: End date for recurrence (optional)

        Returns:
            Created RecurringTemplate object
        """
        print(f"INFO [RecurringTemplateRepository]: Creating template '{name}' for entity {entity_id}")
        template = RecurringTemplate(
            entity_id=entity_id,
            category_id=category_id,
            name=name,
            amount=amount,
            type=type,
            frequency=frequency,
            start_date=start_date,
            description=description,
            notes=notes,
            end_date=end_date,
            is_active=True,
        )
        db.add(template)
        db.commit()
        db.refresh(template)
        print(f"INFO [RecurringTemplateRepository]: Template created with id {template.id}")
        return template

    def get_template_by_id(
        self, db: Session, template_id: UUID
    ) -> Optional[RecurringTemplate]:
        """
        Find a recurring template by ID.

        Args:
            db: Database session
            template_id: Template UUID

        Returns:
            RecurringTemplate object if found, None otherwise
        """
        print(f"INFO [RecurringTemplateRepository]: Looking up template by id {template_id}")
        template = db.query(RecurringTemplate).filter(RecurringTemplate.id == template_id).first()
        if template:
            print(f"INFO [RecurringTemplateRepository]: Found template {template.id}")
        else:
            print(f"INFO [RecurringTemplateRepository]: No template found with id {template_id}")
        return template

    def get_templates_by_entity(
        self,
        db: Session,
        entity_id: UUID,
        include_inactive: bool = False,
        skip: int = 0,
        limit: int = 100,
    ) -> List[RecurringTemplate]:
        """
        Get recurring templates for an entity.

        Args:
            db: Database session
            entity_id: Entity UUID to filter by
            include_inactive: Whether to include inactive templates
            skip: Number of records to skip (pagination)
            limit: Maximum number of records to return

        Returns:
            List of RecurringTemplate objects
        """
        print(f"INFO [RecurringTemplateRepository]: Fetching templates for entity {entity_id}")
        query = db.query(RecurringTemplate).filter(RecurringTemplate.entity_id == entity_id)

        if not include_inactive:
            print("INFO [RecurringTemplateRepository]: Filtering to active templates only")
            query = query.filter(RecurringTemplate.is_active.is_(True))

        query = query.order_by(RecurringTemplate.created_at.desc())
        templates = query.offset(skip).limit(limit).all()
        print(f"INFO [RecurringTemplateRepository]: Found {len(templates)} templates")
        return templates

    def count_templates_by_entity(
        self,
        db: Session,
        entity_id: UUID,
        include_inactive: bool = False,
    ) -> int:
        """
        Count recurring templates for an entity.

        Args:
            db: Database session
            entity_id: Entity UUID to filter by
            include_inactive: Whether to include inactive templates

        Returns:
            Count of templates matching criteria
        """
        print(f"INFO [RecurringTemplateRepository]: Counting templates for entity {entity_id}")
        query = db.query(RecurringTemplate).filter(RecurringTemplate.entity_id == entity_id)

        if not include_inactive:
            query = query.filter(RecurringTemplate.is_active.is_(True))

        count = query.count()
        print(f"INFO [RecurringTemplateRepository]: Count result: {count}")
        return count

    def update_template(self, db: Session, template: RecurringTemplate) -> RecurringTemplate:
        """
        Update an existing recurring template.

        Args:
            db: Database session
            template: RecurringTemplate object with updated values

        Returns:
            Updated RecurringTemplate object
        """
        print(f"INFO [RecurringTemplateRepository]: Updating template {template.id}")
        db.add(template)
        db.commit()
        db.refresh(template)
        print(f"INFO [RecurringTemplateRepository]: Template {template.id} updated successfully")
        return template

    def deactivate_template(self, db: Session, template: RecurringTemplate) -> RecurringTemplate:
        """
        Deactivate a recurring template (soft delete).

        Args:
            db: Database session
            template: RecurringTemplate object to deactivate

        Returns:
            Deactivated RecurringTemplate object
        """
        print(f"INFO [RecurringTemplateRepository]: Deactivating template {template.id}")
        template.is_active = False
        db.add(template)
        db.commit()
        db.refresh(template)
        print(f"INFO [RecurringTemplateRepository]: Template {template.id} deactivated successfully")
        return template

    def delete_template(self, db: Session, template: RecurringTemplate) -> None:
        """
        Delete a recurring template (hard delete).

        Args:
            db: Database session
            template: RecurringTemplate object to delete
        """
        print(f"INFO [RecurringTemplateRepository]: Deleting template {template.id}")
        db.delete(template)
        db.commit()
        print(f"INFO [RecurringTemplateRepository]: Template {template.id} deleted successfully")


# Singleton instance
recurring_template_repository = RecurringTemplateRepository()
