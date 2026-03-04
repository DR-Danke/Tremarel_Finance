"""Legal Desk client service for business logic."""

from typing import Optional

from sqlalchemy.orm import Session

from src.interface.legaldesk_dto import ClientCreateDTO, ClientUpdateDTO
from src.models.ld_client import LdClient
from src.repository.ld_client_repository import ld_client_repository


class LdClientService:
    """Service for Legal Desk client business logic."""

    def create(self, db: Session, data: ClientCreateDTO) -> LdClient:
        """
        Create a new client.

        Args:
            db: Database session
            data: Client creation data

        Returns:
            Created LdClient object
        """
        print(f"INFO [LdClientService]: Creating client '{data.name}'")
        client = ld_client_repository.create(db, data.model_dump())
        print(f"INFO [LdClientService]: Client created with id {client.id}")
        return client

    def update(self, db: Session, client_id: int, data: ClientUpdateDTO) -> Optional[LdClient]:
        """
        Update an existing client.

        Args:
            db: Database session
            client_id: Client primary key
            data: Update data (partial)

        Returns:
            Updated LdClient if found, None otherwise
        """
        print(f"INFO [LdClientService]: Updating client {client_id}")
        existing = ld_client_repository.get_by_id(db, client_id)
        if not existing:
            print(f"INFO [LdClientService]: Client {client_id} not found")
            return None
        updated = ld_client_repository.update(db, client_id, data.model_dump(exclude_unset=True))
        print(f"INFO [LdClientService]: Client {client_id} updated successfully")
        return updated

    def get(self, db: Session, client_id: int) -> Optional[LdClient]:
        """
        Get a client by ID.

        Args:
            db: Database session
            client_id: Client primary key

        Returns:
            LdClient if found, None otherwise
        """
        print(f"INFO [LdClientService]: Getting client {client_id}")
        client = ld_client_repository.get_by_id(db, client_id)
        if client:
            print(f"INFO [LdClientService]: Found client '{client.name}'")
        else:
            print(f"INFO [LdClientService]: Client {client_id} not found")
        return client

    def list_all(self, db: Session) -> list[LdClient]:
        """
        List all clients.

        Args:
            db: Database session

        Returns:
            List of LdClient objects
        """
        print("INFO [LdClientService]: Listing all clients")
        clients = ld_client_repository.list_all(db)
        print(f"INFO [LdClientService]: Found {len(clients)} clients")
        return clients

    def search(self, db: Session, query: str) -> list[LdClient]:
        """
        Search clients by name.

        Args:
            db: Database session
            query: Search string

        Returns:
            List of matching LdClient objects
        """
        print(f"INFO [LdClientService]: Searching clients with query '{query}'")
        clients = ld_client_repository.search_by_name(db, query)
        print(f"INFO [LdClientService]: Found {len(clients)} clients matching '{query}'")
        return clients


# Singleton instance
ld_client_service = LdClientService()
