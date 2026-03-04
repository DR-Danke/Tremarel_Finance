"""Legal Desk pricing negotiation service for business logic."""

from decimal import Decimal
from typing import Optional

from sqlalchemy.orm import Session

from src.interface.legaldesk_dto import PricingAction, PricingHistoryResponseDTO
from src.models.ld_pricing_history import LdPricingHistory
from src.repository.ld_case_repository import ld_case_repository
from src.repository.ld_pricing_repository import ld_pricing_repository


class LdPricingService:
    """Service for pricing negotiation business logic."""

    def create_proposal(
        self,
        db: Session,
        case_id: int,
        specialist_cost: Decimal,
        client_price: Decimal,
        notes: Optional[str] = None,
        created_by: Optional[str] = None,
    ) -> LdPricingHistory:
        """
        Create a pricing proposal for a case.

        Args:
            db: Database session
            case_id: Case primary key
            specialist_cost: Base cost from specialist
            client_price: Proposed client-facing price
            notes: Optional notes
            created_by: Who created the proposal

        Returns:
            Created LdPricingHistory entry

        Raises:
            ValueError: If case not found or client_price is 0
        """
        case = ld_case_repository.get_by_id(db, case_id)
        if not case:
            print(f"ERROR [LdPricingService]: Case {case_id} not found")
            raise ValueError(f"Case {case_id} not found")

        if client_price <= 0:
            print(f"ERROR [LdPricingService]: client_price must be > 0, got {client_price}")
            raise ValueError("client_price must be greater than 0")

        margin_pct = ((client_price - specialist_cost) / client_price) * 100

        entry = ld_pricing_repository.create(db, {
            "case_id": case_id,
            "action": PricingAction.PROPOSAL.value,
            "previous_amount": specialist_cost,
            "new_amount": client_price,
            "currency": "EUR",
            "changed_by": created_by,
            "notes": notes,
        })

        ld_case_repository.update(db, case_id, {"estimated_cost": specialist_cost})

        print(
            f"INFO [LdPricingService]: Proposal for case {case_id}: "
            f"specialist_cost={specialist_cost}, client_price={client_price}, margin={margin_pct:.1f}%"
        )
        return entry

    def submit_counter(
        self,
        db: Session,
        case_id: int,
        specialist_cost: Decimal,
        client_price: Decimal,
        notes: Optional[str] = None,
        created_by: Optional[str] = None,
    ) -> LdPricingHistory:
        """
        Submit a counter-offer for a case.

        Args:
            db: Database session
            case_id: Case primary key
            specialist_cost: Revised specialist cost
            client_price: Revised client-facing price
            notes: Optional notes
            created_by: Who submitted the counter-offer

        Returns:
            Created LdPricingHistory entry

        Raises:
            ValueError: If case not found or client_price is 0
        """
        case = ld_case_repository.get_by_id(db, case_id)
        if not case:
            print(f"ERROR [LdPricingService]: Case {case_id} not found")
            raise ValueError(f"Case {case_id} not found")

        if client_price <= 0:
            print(f"ERROR [LdPricingService]: client_price must be > 0, got {client_price}")
            raise ValueError("client_price must be greater than 0")

        margin_pct = ((client_price - specialist_cost) / client_price) * 100

        entry = ld_pricing_repository.create(db, {
            "case_id": case_id,
            "action": PricingAction.COUNTER.value,
            "previous_amount": specialist_cost,
            "new_amount": client_price,
            "currency": "EUR",
            "changed_by": created_by,
            "notes": notes,
        })

        print(
            f"INFO [LdPricingService]: Counter-offer for case {case_id}: "
            f"specialist_cost={specialist_cost}, client_price={client_price}, margin={margin_pct:.1f}%"
        )
        return entry

    def accept_pricing(
        self,
        db: Session,
        case_id: int,
        created_by: Optional[str] = None,
    ) -> LdPricingHistory:
        """
        Accept pricing for a case, locking financial fields.

        Args:
            db: Database session
            case_id: Case primary key
            created_by: Who accepted the pricing

        Returns:
            Created LdPricingHistory entry

        Raises:
            ValueError: If case not found or no pricing history exists
        """
        case = ld_case_repository.get_by_id(db, case_id)
        if not case:
            print(f"ERROR [LdPricingService]: Case {case_id} not found")
            raise ValueError(f"Case {case_id} not found")

        latest = ld_pricing_repository.get_latest(db, case_id)
        if not latest:
            print(f"ERROR [LdPricingService]: No pricing history for case {case_id}")
            raise ValueError(f"No pricing history exists for case {case_id}")

        client_price = latest.new_amount if latest.new_amount is not None else Decimal(0)
        specialist_cost = latest.previous_amount if latest.previous_amount is not None else Decimal(0)

        if client_price > 0:
            margin_pct = ((client_price - specialist_cost) / client_price) * 100
        else:
            margin_pct = Decimal(0)

        ld_case_repository.update(db, case_id, {
            "final_quote": client_price,
            "margin_percentage": margin_pct,
        })

        entry = ld_pricing_repository.create(db, {
            "case_id": case_id,
            "action": PricingAction.ACCEPT.value,
            "previous_amount": specialist_cost,
            "new_amount": client_price,
            "currency": "EUR",
            "changed_by": created_by,
        })

        print(
            f"INFO [LdPricingService]: Pricing accepted for case {case_id}: "
            f"final_quote={client_price}, margin={margin_pct:.1f}%"
        )
        return entry

    def reject_pricing(
        self,
        db: Session,
        case_id: int,
        notes: Optional[str] = None,
        created_by: Optional[str] = None,
    ) -> LdPricingHistory:
        """
        Reject pricing for a case.

        Args:
            db: Database session
            case_id: Case primary key
            notes: Rejection reason
            created_by: Who rejected the pricing

        Returns:
            Created LdPricingHistory entry

        Raises:
            ValueError: If case not found
        """
        case = ld_case_repository.get_by_id(db, case_id)
        if not case:
            print(f"ERROR [LdPricingService]: Case {case_id} not found")
            raise ValueError(f"Case {case_id} not found")

        entry = ld_pricing_repository.create(db, {
            "case_id": case_id,
            "action": PricingAction.REJECT.value,
            "changed_by": created_by,
            "notes": notes,
        })

        print(f"INFO [LdPricingService]: Pricing rejected for case {case_id}: {notes}")
        return entry

    def get_pricing_history(
        self,
        db: Session,
        case_id: int,
    ) -> list[PricingHistoryResponseDTO]:
        """
        Get full pricing history for a case.

        Args:
            db: Database session
            case_id: Case primary key

        Returns:
            List of PricingHistoryResponseDTO ordered chronologically
        """
        entries = ld_pricing_repository.get_by_case(db, case_id)
        dtos = [PricingHistoryResponseDTO.model_validate(entry) for entry in entries]
        print(f"INFO [LdPricingService]: Retrieved {len(dtos)} pricing entries for case {case_id}")
        return dtos


# Singleton instance
ld_pricing_service = LdPricingService()
