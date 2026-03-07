"""Legal Desk message service for business logic."""

from sqlalchemy.orm import Session

from src.interface.legaldesk_dto import MessageCreateDTO
from src.models.ld_case_message import LdCaseMessage
from src.repository.ld_message_repository import ld_message_repository


class LdMessageService:
    """Service for Legal Desk message business logic."""

    def create_message(self, db: Session, case_id: int, data: MessageCreateDTO) -> LdCaseMessage:
        """
        Create a new message on a case.

        Args:
            db: Database session
            case_id: Case identifier
            data: Message creation data

        Returns:
            Created LdCaseMessage object
        """
        print(f"INFO [LdMessageService]: Creating message for case {case_id}")
        msg_data = data.model_dump()
        msg_data["case_id"] = case_id
        message = ld_message_repository.create(db, msg_data)
        print(f"INFO [LdMessageService]: Message created with id {message.id}")
        return message

    def get_case_messages(self, db: Session, case_id: int, include_internal: bool = False) -> list[LdCaseMessage]:
        """
        Get messages for a case.

        Args:
            db: Database session
            case_id: Case identifier
            include_internal: Whether to include internal messages

        Returns:
            List of LdCaseMessage objects
        """
        print(f"INFO [LdMessageService]: Getting messages for case {case_id} (include_internal={include_internal})")
        messages = ld_message_repository.get_by_case(db, case_id, include_internal=include_internal)
        print(f"INFO [LdMessageService]: Found {len(messages)} messages for case {case_id}")
        return messages


# Singleton instance
ld_message_service = LdMessageService()
