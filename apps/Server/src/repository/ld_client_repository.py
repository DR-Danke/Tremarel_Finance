"""Legal Desk client repository for database operations."""

from typing import Optional

from sqlalchemy.orm import Session

from src.models.ld_client import LdClient


class LdClientRepository:
    """Repository for LdClient database operations."""

    def create(self, db: Session, data: dict) -> LdClient:
        """
        Create a new client.

        Args:
            db: Database session
            data: Client field values

        Returns:
            Created LdClient object
        """
        print(f"INFO [LdClientRepository]: Creating client with data {data}")
        client = LdClient(**data)
        db.add(client)
        db.commit()
        db.refresh(client)
        print(f"INFO [LdClientRepository]: Client created with id {client.id}")
        return client

    def get_by_id(self, db: Session, client_id: int) -> Optional[LdClient]:
        """
        Find a client by ID.

        Args:
            db: Database session
            client_id: Client primary key

        Returns:
            LdClient if found, None otherwise
        """
        print(f"INFO [LdClientRepository]: Looking up client by id {client_id}")
        client = db.query(LdClient).filter(LdClient.id == client_id).first()
        if client:
            print(f"INFO [LdClientRepository]: Found client '{client.name}'")
        else:
            print(f"INFO [LdClientRepository]: No client found with id {client_id}")
        return client

    def list_all(self, db: Session) -> list[LdClient]:
        """
        Return all clients ordered by created_at descending.

        Args:
            db: Database session

        Returns:
            List of LdClient objects
        """
        print("INFO [LdClientRepository]: Listing all clients")
        clients = db.query(LdClient).order_by(LdClient.created_at.desc()).all()
        print(f"INFO [LdClientRepository]: Found {len(clients)} clients")
        return clients

    def update(self, db: Session, client_id: int, data: dict) -> Optional[LdClient]:
        """
        Update a client by ID.

        Args:
            db: Database session
            client_id: Client primary key
            data: Fields to update

        Returns:
            Updated LdClient if found, None otherwise
        """
        print(f"INFO [LdClientRepository]: Updating client {client_id} with {data}")
        client = self.get_by_id(db, client_id)
        if not client:
            return None
        for key, value in data.items():
            setattr(client, key, value)
        db.commit()
        db.refresh(client)
        print(f"INFO [LdClientRepository]: Client {client_id} updated successfully")
        return client

    def search_by_name(self, db: Session, query: str) -> list[LdClient]:
        """
        Search clients by name using case-insensitive partial match.

        Args:
            db: Database session
            query: Search string

        Returns:
            List of matching LdClient objects
        """
        print(f"INFO [LdClientRepository]: Searching clients by name '{query}'")
        clients = (
            db.query(LdClient)
            .filter(LdClient.name.ilike(f"%{query}%"))
            .order_by(LdClient.created_at.desc())
            .all()
        )
        print(f"INFO [LdClientRepository]: Found {len(clients)} clients matching '{query}'")
        return clients


# Singleton instance
ld_client_repository = LdClientRepository()
