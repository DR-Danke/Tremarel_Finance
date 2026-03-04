"""Repository for Legal Desk case message operations."""

from sqlalchemy.orm import Session

from src.models.ld_case_message import LdCaseMessage


class LdMessageRepository:
    """Repository for LdCaseMessage database operations."""

    def create(self, db: Session, data: dict) -> LdCaseMessage:
        """
        Create a new case message.

        Args:
            db: Database session
            data: Dict with case_id, sender_type, sender_name, message, is_internal

        Returns:
            Created LdCaseMessage object
        """
        print(f"INFO [LdMessageRepository]: Creating message for case {data.get('case_id')}")
        message = LdCaseMessage(
            case_id=data["case_id"],
            sender_type=data["sender_type"],
            sender_name=data.get("sender_name"),
            message=data["message"],
            is_internal=data.get("is_internal", False),
        )
        db.add(message)
        db.commit()
        db.refresh(message)
        print(f"INFO [LdMessageRepository]: Message created with id {message.id}")
        return message

    def get_by_case(self, db: Session, case_id: int, include_internal: bool = False) -> list[LdCaseMessage]:
        """
        Get messages for a case, ordered by created_at ASC.

        When include_internal is False, filters out internal messages.

        Args:
            db: Database session
            case_id: Case identifier
            include_internal: Whether to include internal messages

        Returns:
            List of LdCaseMessage objects
        """
        print(f"INFO [LdMessageRepository]: Getting messages for case {case_id} (include_internal={include_internal})")
        query = db.query(LdCaseMessage).filter(LdCaseMessage.case_id == case_id)
        if not include_internal:
            query = query.filter(LdCaseMessage.is_internal == False)  # noqa: E712
        results = query.order_by(LdCaseMessage.created_at.asc()).all()
        print(f"INFO [LdMessageRepository]: Found {len(results)} messages for case {case_id}")
        return results


# Singleton instance
ld_message_repository = LdMessageRepository()
