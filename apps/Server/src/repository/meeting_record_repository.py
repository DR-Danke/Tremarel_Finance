"""Meeting record repository for database operations."""

import json
from datetime import date
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from src.interface.meeting_record_dto import MeetingRecordFilterDTO
from src.models.meeting_record import MeetingRecord


class MeetingRecordRepository:
    """Repository for MeetingRecord database operations."""

    def create_meeting_record(
        self,
        db: Session,
        entity_id: UUID,
        prospect_id: UUID,
        title: str,
        transcript_ref: Optional[str] = None,
        summary: Optional[str] = None,
        action_items: Optional[List[str]] = None,
        participants: Optional[List[str]] = None,
        html_output: Optional[str] = None,
        meeting_date: Optional[date] = None,
    ) -> MeetingRecord:
        """
        Create a new meeting record in the database.

        Args:
            db: Database session
            entity_id: Entity UUID this record belongs to
            prospect_id: Prospect UUID this meeting is linked to
            title: Human-readable meeting title
            transcript_ref: Reference to original transcript file/URL
            summary: Structured summary of the meeting
            action_items: List of action items (serialized to JSON string)
            participants: List of participant names (serialized to JSON string)
            html_output: Formatted HTML content for download
            meeting_date: Date when the meeting occurred

        Returns:
            Created MeetingRecord object
        """
        print(f"INFO [MeetingRecordRepository]: Creating meeting record '{title}' for entity {entity_id}")
        record = MeetingRecord(
            entity_id=entity_id,
            prospect_id=prospect_id,
            title=title,
            transcript_ref=transcript_ref,
            summary=summary,
            action_items=json.dumps(action_items) if action_items is not None else None,
            participants=json.dumps(participants) if participants is not None else None,
            html_output=html_output,
            meeting_date=meeting_date,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        print(f"INFO [MeetingRecordRepository]: Meeting record created with id {record.id}")
        return record

    def get_meeting_record_by_id(self, db: Session, record_id: UUID) -> Optional[MeetingRecord]:
        """
        Find a meeting record by ID.

        Args:
            db: Database session
            record_id: MeetingRecord UUID

        Returns:
            MeetingRecord object if found, None otherwise
        """
        print(f"INFO [MeetingRecordRepository]: Looking up meeting record by id {record_id}")
        record = db.query(MeetingRecord).filter(MeetingRecord.id == record_id).first()
        if record:
            print(f"INFO [MeetingRecordRepository]: Found meeting record '{record.title}'")
        else:
            print(f"INFO [MeetingRecordRepository]: No meeting record found with id {record_id}")
        return record

    def get_meeting_records_by_entity(
        self,
        db: Session,
        entity_id: UUID,
        filters: Optional[MeetingRecordFilterDTO] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[MeetingRecord]:
        """
        Get meeting records for an entity with optional filters and pagination.

        Args:
            db: Database session
            entity_id: Entity UUID to filter by
            filters: Optional filter criteria
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of MeetingRecord objects
        """
        print(f"INFO [MeetingRecordRepository]: Fetching meeting records for entity {entity_id}")
        query = db.query(MeetingRecord).filter(MeetingRecord.entity_id == entity_id)

        if filters:
            if filters.prospect_id is not None:
                query = query.filter(MeetingRecord.prospect_id == filters.prospect_id)
            if filters.is_active is not None:
                query = query.filter(MeetingRecord.is_active == filters.is_active)  # noqa: E712
            if filters.meeting_date_from is not None:
                query = query.filter(MeetingRecord.meeting_date >= filters.meeting_date_from)
            if filters.meeting_date_to is not None:
                query = query.filter(MeetingRecord.meeting_date <= filters.meeting_date_to)

        records = (
            query.order_by(
                MeetingRecord.meeting_date.desc().nullslast(),
                MeetingRecord.created_at.desc(),
            )
            .offset(skip)
            .limit(limit)
            .all()
        )
        print(f"INFO [MeetingRecordRepository]: Found {len(records)} meeting records")
        return records

    def count_meeting_records_by_entity(
        self,
        db: Session,
        entity_id: UUID,
        filters: Optional[MeetingRecordFilterDTO] = None,
    ) -> int:
        """
        Count meeting records for an entity with optional filters.

        Args:
            db: Database session
            entity_id: Entity UUID to filter by
            filters: Optional filter criteria

        Returns:
            Count of matching records
        """
        print(f"INFO [MeetingRecordRepository]: Counting meeting records for entity {entity_id}")
        query = db.query(MeetingRecord).filter(MeetingRecord.entity_id == entity_id)

        if filters:
            if filters.prospect_id is not None:
                query = query.filter(MeetingRecord.prospect_id == filters.prospect_id)
            if filters.is_active is not None:
                query = query.filter(MeetingRecord.is_active == filters.is_active)  # noqa: E712
            if filters.meeting_date_from is not None:
                query = query.filter(MeetingRecord.meeting_date >= filters.meeting_date_from)
            if filters.meeting_date_to is not None:
                query = query.filter(MeetingRecord.meeting_date <= filters.meeting_date_to)

        count = query.count()
        print(f"INFO [MeetingRecordRepository]: Count result: {count}")
        return count

    def update_meeting_record(self, db: Session, record: MeetingRecord) -> MeetingRecord:
        """
        Update an existing meeting record.

        Args:
            db: Database session
            record: MeetingRecord object with updated values

        Returns:
            Updated MeetingRecord object
        """
        print(f"INFO [MeetingRecordRepository]: Updating meeting record {record.id}")
        db.add(record)
        db.commit()
        db.refresh(record)
        print(f"INFO [MeetingRecordRepository]: Meeting record {record.id} updated successfully")
        return record

    def delete_meeting_record(self, db: Session, record: MeetingRecord) -> None:
        """
        Delete a meeting record.

        Args:
            db: Database session
            record: MeetingRecord object to delete
        """
        print(f"INFO [MeetingRecordRepository]: Deleting meeting record {record.id}")
        db.delete(record)
        db.commit()
        print(f"INFO [MeetingRecordRepository]: Meeting record {record.id} deleted successfully")


# Singleton instance
meeting_record_repository = MeetingRecordRepository()
