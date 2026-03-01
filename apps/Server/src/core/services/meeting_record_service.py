"""Meeting record service for business logic."""

import json
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy.orm import Session

from src.interface.meeting_record_dto import (
    MeetingRecordCreateDTO,
    MeetingRecordFilterDTO,
    MeetingRecordUpdateDTO,
)
from src.models.meeting_record import MeetingRecord
from src.repository.meeting_record_repository import meeting_record_repository


class MeetingRecordService:
    """Service for meeting record business logic."""

    def create_meeting_record(self, db: Session, data: MeetingRecordCreateDTO) -> MeetingRecord:
        """
        Create a new meeting record.

        Args:
            db: Database session
            data: Meeting record creation data

        Returns:
            Created MeetingRecord object
        """
        print(f"INFO [MeetingRecordService]: Creating meeting record '{data.title}' for entity {data.entity_id}")
        record = meeting_record_repository.create_meeting_record(
            db=db,
            entity_id=data.entity_id,
            prospect_id=data.prospect_id,
            title=data.title,
            transcript_ref=data.transcript_ref,
            summary=data.summary,
            action_items=data.action_items,
            participants=data.participants,
            html_output=data.html_output,
            meeting_date=data.meeting_date,
        )
        print(f"INFO [MeetingRecordService]: Meeting record created with id {record.id}")
        return record

    def get_meeting_record(
        self, db: Session, record_id: UUID, entity_id: UUID
    ) -> Optional[MeetingRecord]:
        """
        Get a meeting record by ID, validating entity ownership.

        Args:
            db: Database session
            record_id: MeetingRecord UUID
            entity_id: Entity UUID for validation

        Returns:
            MeetingRecord object if found and belongs to entity, None otherwise
        """
        print(f"INFO [MeetingRecordService]: Getting meeting record {record_id}")
        record = meeting_record_repository.get_meeting_record_by_id(db, record_id)
        if record and record.entity_id != entity_id:
            print(f"ERROR [MeetingRecordService]: Meeting record {record_id} does not belong to entity {entity_id}")
            return None
        return record

    def list_meeting_records(
        self,
        db: Session,
        entity_id: UUID,
        filters: Optional[MeetingRecordFilterDTO] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[MeetingRecord], int]:
        """
        List meeting records for an entity with filters and pagination.

        Args:
            db: Database session
            entity_id: Entity UUID to filter by
            filters: Optional filter criteria
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Tuple of (list of meeting records, total count)
        """
        print(f"INFO [MeetingRecordService]: Listing meeting records for entity {entity_id}")
        records = meeting_record_repository.get_meeting_records_by_entity(
            db, entity_id, filters, skip, limit
        )
        total = meeting_record_repository.count_meeting_records_by_entity(
            db, entity_id, filters
        )
        print(f"INFO [MeetingRecordService]: Found {len(records)} meeting records (total: {total})")
        return records, total

    def update_meeting_record(
        self,
        db: Session,
        record_id: UUID,
        entity_id: UUID,
        data: MeetingRecordUpdateDTO,
    ) -> Optional[MeetingRecord]:
        """
        Update an existing meeting record.

        Args:
            db: Database session
            record_id: MeetingRecord UUID
            entity_id: Entity UUID for validation
            data: Update data

        Returns:
            Updated MeetingRecord object if found and updated, None otherwise
        """
        print(f"INFO [MeetingRecordService]: Updating meeting record {record_id}")
        record = meeting_record_repository.get_meeting_record_by_id(db, record_id)
        if not record:
            print(f"ERROR [MeetingRecordService]: Meeting record {record_id} not found")
            return None
        if record.entity_id != entity_id:
            print(f"ERROR [MeetingRecordService]: Meeting record {record_id} does not belong to entity {entity_id}")
            return None

        if data.title is not None:
            record.title = data.title
        if data.transcript_ref is not None:
            record.transcript_ref = data.transcript_ref
        if data.summary is not None:
            record.summary = data.summary
        if data.action_items is not None:
            record.action_items = json.dumps(data.action_items)
        if data.participants is not None:
            record.participants = json.dumps(data.participants)
        if data.html_output is not None:
            record.html_output = data.html_output
        if data.meeting_date is not None:
            record.meeting_date = data.meeting_date
        if data.is_active is not None:
            record.is_active = data.is_active

        updated = meeting_record_repository.update_meeting_record(db, record)
        print(f"INFO [MeetingRecordService]: Meeting record {record_id} updated successfully")
        return updated

    def delete_meeting_record(self, db: Session, record_id: UUID, entity_id: UUID) -> bool:
        """
        Delete a meeting record.

        Args:
            db: Database session
            record_id: MeetingRecord UUID
            entity_id: Entity UUID for validation

        Returns:
            True if deleted, False if not found or not owned
        """
        print(f"INFO [MeetingRecordService]: Deleting meeting record {record_id}")
        record = meeting_record_repository.get_meeting_record_by_id(db, record_id)
        if not record:
            print(f"ERROR [MeetingRecordService]: Meeting record {record_id} not found")
            return False
        if record.entity_id != entity_id:
            print(f"ERROR [MeetingRecordService]: Meeting record {record_id} does not belong to entity {entity_id}")
            return False

        meeting_record_repository.delete_meeting_record(db, record)
        print(f"INFO [MeetingRecordService]: Meeting record {record_id} deleted successfully")
        return True


# Singleton instance
meeting_record_service = MeetingRecordService()
