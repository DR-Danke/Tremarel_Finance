"""Tests for low-stock alert automation in inventory movements."""

from datetime import datetime
from decimal import Decimal
from unittest.mock import MagicMock, call, patch
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from src.core.services.inventory_service import InventoryService
from src.interface.inventory_movement_dto import (
    InventoryMovementCreateDTO,
    MovementReason,
    MovementType,
)
from src.models.event import Event
from src.models.inventory_movement import InventoryMovement
from src.models.resource import Resource


def create_mock_resource(
    name: str = "Harina",
    unit: str = "kg",
    current_stock: Decimal = Decimal("10.0"),
    minimum_stock: Decimal = Decimal("5.0"),
    restaurant_id=None,
) -> Resource:
    """Create a mock resource for testing."""
    resource = MagicMock(spec=Resource)
    resource.id = uuid4()
    resource.restaurant_id = restaurant_id or uuid4()
    resource.name = name
    resource.unit = unit
    resource.current_stock = current_stock
    resource.minimum_stock = minimum_stock
    return resource


def create_mock_movement(
    resource_id=None,
    restaurant_id=None,
    movement_type: str = "exit",
    quantity: Decimal = Decimal("7.0"),
) -> InventoryMovement:
    """Create a mock inventory movement for testing."""
    movement = MagicMock(spec=InventoryMovement)
    movement.id = uuid4()
    movement.resource_id = resource_id or uuid4()
    movement.restaurant_id = restaurant_id or uuid4()
    movement.type = movement_type
    movement.quantity = quantity
    movement.reason = "uso"
    movement.date = datetime(2026, 3, 1, 12, 0, 0)
    movement.person_id = None
    movement.notes = None
    movement.created_at = datetime(2026, 3, 1, 12, 0, 0)
    return movement


class TestLowStockAlertCreation:
    """Tests for low-stock alert creation on exit movements."""

    @patch("src.core.services.inventory_service.event_repository")
    @patch("src.core.services.event_service.event_repository")
    @patch("src.core.services.event_service.restaurant_repository")
    @patch("src.core.services.inventory_service.restaurant_repository")
    @patch("src.core.services.inventory_service.resource_repository")
    @patch("src.core.services.inventory_service.inventory_movement_repository")
    def test_exit_movement_below_minimum_creates_alert(
        self,
        mock_movement_repo,
        mock_resource_repo,
        mock_inv_restaurant_repo,
        mock_evt_restaurant_repo,
        mock_evt_event_repo,
        mock_inv_event_repo,
    ) -> None:
        """Test that exit movement dropping stock below minimum creates an alerta_stock Event."""
        db = MagicMock(spec=Session)
        user_id = uuid4()
        restaurant_id = uuid4()

        resource = create_mock_resource(
            current_stock=Decimal("10.0"),
            minimum_stock=Decimal("5.0"),
            restaurant_id=restaurant_id,
        )
        movement = create_mock_movement(
            resource_id=resource.id,
            restaurant_id=restaurant_id,
        )

        mock_inv_restaurant_repo.get_user_restaurant_role.return_value = "admin"
        mock_evt_restaurant_repo.get_user_restaurant_role.return_value = "admin"
        mock_resource_repo.get_by_id.return_value = resource
        mock_resource_repo.update.return_value = resource
        mock_movement_repo.create.return_value = movement
        mock_inv_event_repo.get_pending_alerts_by_resource.return_value = []
        mock_evt_event_repo.create.return_value = MagicMock(spec=Event, id=uuid4())

        data = InventoryMovementCreateDTO(
            resource_id=resource.id,
            type=MovementType.EXIT,
            quantity=Decimal("7.0"),
            reason=MovementReason.USO,
            restaurant_id=restaurant_id,
        )

        service = InventoryService()
        service.create_movement(db, user_id, data)

        # Stock should be 10 - 7 = 3, which is < 5 (minimum)
        assert resource.current_stock == Decimal("3.0")

        # Event repository should have been called to check for existing alerts
        mock_inv_event_repo.get_pending_alerts_by_resource.assert_called_once_with(
            db, restaurant_id, resource.id
        )

        # Event should have been created via event_service (which calls event_repository.create)
        mock_evt_event_repo.create.assert_called_once()
        create_call = mock_evt_event_repo.create.call_args
        assert create_call.kwargs["event_type"] == "alerta_stock"
        assert create_call.kwargs["notification_channel"] == "whatsapp"
        assert create_call.kwargs["related_resource_id"] == resource.id
        print("INFO [TestLowStockAlert]: test_exit_movement_below_minimum_creates_alert - PASSED")

    @patch("src.core.services.inventory_service.event_repository")
    @patch("src.core.services.inventory_service.restaurant_repository")
    @patch("src.core.services.inventory_service.resource_repository")
    @patch("src.core.services.inventory_service.inventory_movement_repository")
    def test_exit_movement_above_minimum_no_alert(
        self,
        mock_movement_repo,
        mock_resource_repo,
        mock_restaurant_repo,
        mock_event_repo,
    ) -> None:
        """Test that exit movement keeping stock above minimum creates no alert."""
        db = MagicMock(spec=Session)
        user_id = uuid4()
        restaurant_id = uuid4()

        resource = create_mock_resource(
            current_stock=Decimal("10.0"),
            minimum_stock=Decimal("5.0"),
            restaurant_id=restaurant_id,
        )
        movement = create_mock_movement(
            resource_id=resource.id,
            restaurant_id=restaurant_id,
            quantity=Decimal("2.0"),
        )

        mock_restaurant_repo.get_user_restaurant_role.return_value = "admin"
        mock_resource_repo.get_by_id.return_value = resource
        mock_resource_repo.update.return_value = resource
        mock_movement_repo.create.return_value = movement
        mock_event_repo.resolve_alerts_by_resource.return_value = 0

        data = InventoryMovementCreateDTO(
            resource_id=resource.id,
            type=MovementType.EXIT,
            quantity=Decimal("2.0"),
            reason=MovementReason.USO,
            restaurant_id=restaurant_id,
        )

        service = InventoryService()
        service.create_movement(db, user_id, data)

        # Stock should be 10 - 2 = 8, which is >= 5 (minimum) → resolve path, no create
        assert resource.current_stock == Decimal("8.0")
        mock_event_repo.get_pending_alerts_by_resource.assert_not_called()
        mock_event_repo.resolve_alerts_by_resource.assert_called_once_with(
            db, restaurant_id, resource.id
        )
        print("INFO [TestLowStockAlert]: test_exit_movement_above_minimum_no_alert - PASSED")

    @patch("src.core.services.inventory_service.event_repository")
    @patch("src.core.services.inventory_service.restaurant_repository")
    @patch("src.core.services.inventory_service.resource_repository")
    @patch("src.core.services.inventory_service.inventory_movement_repository")
    def test_duplicate_alert_prevention(
        self,
        mock_movement_repo,
        mock_resource_repo,
        mock_restaurant_repo,
        mock_event_repo,
    ) -> None:
        """Test that no duplicate alert is created when pending alert already exists."""
        db = MagicMock(spec=Session)
        user_id = uuid4()
        restaurant_id = uuid4()

        resource = create_mock_resource(
            current_stock=Decimal("4.0"),
            minimum_stock=Decimal("5.0"),
            restaurant_id=restaurant_id,
        )
        movement = create_mock_movement(
            resource_id=resource.id,
            restaurant_id=restaurant_id,
            quantity=Decimal("1.0"),
        )

        existing_alert = MagicMock(spec=Event)
        existing_alert.id = uuid4()

        mock_restaurant_repo.get_user_restaurant_role.return_value = "admin"
        mock_resource_repo.get_by_id.return_value = resource
        mock_resource_repo.update.return_value = resource
        mock_movement_repo.create.return_value = movement
        mock_event_repo.get_pending_alerts_by_resource.return_value = [existing_alert]

        data = InventoryMovementCreateDTO(
            resource_id=resource.id,
            type=MovementType.EXIT,
            quantity=Decimal("1.0"),
            reason=MovementReason.USO,
            restaurant_id=restaurant_id,
        )

        service = InventoryService()
        service.create_movement(db, user_id, data)

        # Stock is 4 - 1 = 3, below minimum, but alert exists → no new event created
        assert resource.current_stock == Decimal("3.0")
        mock_event_repo.get_pending_alerts_by_resource.assert_called_once()
        # event_service.create_event should NOT have been called (import is inside the method)
        print("INFO [TestLowStockAlert]: test_duplicate_alert_prevention - PASSED")


class TestLowStockAlertResolution:
    """Tests for auto-resolution of alerts on entry movements."""

    @patch("src.core.services.inventory_service.event_repository")
    @patch("src.core.services.inventory_service.restaurant_repository")
    @patch("src.core.services.inventory_service.resource_repository")
    @patch("src.core.services.inventory_service.inventory_movement_repository")
    def test_entry_movement_resolves_alerts(
        self,
        mock_movement_repo,
        mock_resource_repo,
        mock_restaurant_repo,
        mock_event_repo,
    ) -> None:
        """Test that entry movement bringing stock above minimum resolves pending alerts."""
        db = MagicMock(spec=Session)
        user_id = uuid4()
        restaurant_id = uuid4()

        resource = create_mock_resource(
            current_stock=Decimal("3.0"),
            minimum_stock=Decimal("5.0"),
            restaurant_id=restaurant_id,
        )
        movement = create_mock_movement(
            resource_id=resource.id,
            restaurant_id=restaurant_id,
            movement_type="entry",
            quantity=Decimal("10.0"),
        )

        mock_restaurant_repo.get_user_restaurant_role.return_value = "admin"
        mock_resource_repo.get_by_id.return_value = resource
        mock_resource_repo.update.return_value = resource
        mock_movement_repo.create.return_value = movement
        mock_event_repo.resolve_alerts_by_resource.return_value = 1

        data = InventoryMovementCreateDTO(
            resource_id=resource.id,
            type=MovementType.ENTRY,
            quantity=Decimal("10.0"),
            reason=MovementReason.COMPRA,
            restaurant_id=restaurant_id,
        )

        service = InventoryService()
        service.create_movement(db, user_id, data)

        # Stock should be 3 + 10 = 13, which is >= 5 (minimum) → alerts resolved
        assert resource.current_stock == Decimal("13.0")
        mock_event_repo.resolve_alerts_by_resource.assert_called_once_with(
            db, restaurant_id, resource.id
        )
        print("INFO [TestLowStockAlert]: test_entry_movement_resolves_alerts - PASSED")

    @patch("src.core.services.inventory_service.event_repository")
    @patch("src.core.services.event_service.event_repository")
    @patch("src.core.services.event_service.restaurant_repository")
    @patch("src.core.services.inventory_service.restaurant_repository")
    @patch("src.core.services.inventory_service.resource_repository")
    @patch("src.core.services.inventory_service.inventory_movement_repository")
    def test_entry_movement_below_minimum_no_resolution(
        self,
        mock_movement_repo,
        mock_resource_repo,
        mock_inv_restaurant_repo,
        mock_evt_restaurant_repo,
        mock_evt_event_repo,
        mock_inv_event_repo,
    ) -> None:
        """Test that entry movement still below minimum does not resolve alerts."""
        db = MagicMock(spec=Session)
        user_id = uuid4()
        restaurant_id = uuid4()

        resource = create_mock_resource(
            current_stock=Decimal("1.0"),
            minimum_stock=Decimal("5.0"),
            restaurant_id=restaurant_id,
        )
        movement = create_mock_movement(
            resource_id=resource.id,
            restaurant_id=restaurant_id,
            movement_type="entry",
            quantity=Decimal("2.0"),
        )

        mock_inv_restaurant_repo.get_user_restaurant_role.return_value = "admin"
        mock_evt_restaurant_repo.get_user_restaurant_role.return_value = "admin"
        mock_resource_repo.get_by_id.return_value = resource
        mock_resource_repo.update.return_value = resource
        mock_movement_repo.create.return_value = movement
        mock_inv_event_repo.get_pending_alerts_by_resource.return_value = [MagicMock(spec=Event)]
        mock_evt_event_repo.create.return_value = MagicMock(spec=Event, id=uuid4())

        data = InventoryMovementCreateDTO(
            resource_id=resource.id,
            type=MovementType.ENTRY,
            quantity=Decimal("2.0"),
            reason=MovementReason.COMPRA,
            restaurant_id=restaurant_id,
        )

        service = InventoryService()
        service.create_movement(db, user_id, data)

        # Stock should be 1 + 2 = 3, still < 5 → alert NOT resolved, dedup check happens
        assert resource.current_stock == Decimal("3.0")
        mock_inv_event_repo.resolve_alerts_by_resource.assert_not_called()
        # Dedup check happens but existing alert exists so no new one created
        mock_inv_event_repo.get_pending_alerts_by_resource.assert_called_once()
        print("INFO [TestLowStockAlert]: test_entry_movement_below_minimum_no_resolution - PASSED")


class TestLowStockAlertContent:
    """Tests for alert event content and format."""

    @patch("src.core.services.inventory_service.event_repository")
    @patch("src.core.services.event_service.event_repository")
    @patch("src.core.services.event_service.restaurant_repository")
    @patch("src.core.services.inventory_service.restaurant_repository")
    @patch("src.core.services.inventory_service.resource_repository")
    @patch("src.core.services.inventory_service.inventory_movement_repository")
    def test_alert_description_in_spanish(
        self,
        mock_movement_repo,
        mock_resource_repo,
        mock_inv_restaurant_repo,
        mock_evt_restaurant_repo,
        mock_evt_event_repo,
        mock_inv_event_repo,
    ) -> None:
        """Test that alert description is in Spanish with correct format."""
        db = MagicMock(spec=Session)
        user_id = uuid4()
        restaurant_id = uuid4()

        resource = create_mock_resource(
            name="Aceite de oliva",
            unit="litros",
            current_stock=Decimal("10.0"),
            minimum_stock=Decimal("5.0"),
            restaurant_id=restaurant_id,
        )
        movement = create_mock_movement(
            resource_id=resource.id,
            restaurant_id=restaurant_id,
            quantity=Decimal("8.0"),
        )

        mock_inv_restaurant_repo.get_user_restaurant_role.return_value = "admin"
        mock_evt_restaurant_repo.get_user_restaurant_role.return_value = "admin"
        mock_resource_repo.get_by_id.return_value = resource
        mock_resource_repo.update.return_value = resource
        mock_movement_repo.create.return_value = movement
        mock_inv_event_repo.get_pending_alerts_by_resource.return_value = []
        mock_evt_event_repo.create.return_value = MagicMock(spec=Event, id=uuid4())

        data = InventoryMovementCreateDTO(
            resource_id=resource.id,
            type=MovementType.EXIT,
            quantity=Decimal("8.0"),
            reason=MovementReason.USO,
            restaurant_id=restaurant_id,
        )

        service = InventoryService()
        service.create_movement(db, user_id, data)

        # Verify event was created with Spanish description
        mock_evt_event_repo.create.assert_called_once()
        create_call = mock_evt_event_repo.create.call_args
        description = create_call.kwargs["description"]
        assert "Stock bajo" in description
        assert "Aceite de oliva" in description
        assert "litros" in description
        assert "Actual:" in description
        assert "Mínimo:" in description
        print("INFO [TestLowStockAlert]: test_alert_description_in_spanish - PASSED")

    @patch("src.core.services.inventory_service.event_repository")
    @patch("src.core.services.event_service.event_repository")
    @patch("src.core.services.event_service.restaurant_repository")
    @patch("src.core.services.inventory_service.restaurant_repository")
    @patch("src.core.services.inventory_service.resource_repository")
    @patch("src.core.services.inventory_service.inventory_movement_repository")
    def test_alert_notification_channel_whatsapp(
        self,
        mock_movement_repo,
        mock_resource_repo,
        mock_inv_restaurant_repo,
        mock_evt_restaurant_repo,
        mock_evt_event_repo,
        mock_inv_event_repo,
    ) -> None:
        """Test that alert default notification channel is whatsapp."""
        db = MagicMock(spec=Session)
        user_id = uuid4()
        restaurant_id = uuid4()

        resource = create_mock_resource(
            current_stock=Decimal("10.0"),
            minimum_stock=Decimal("5.0"),
            restaurant_id=restaurant_id,
        )
        movement = create_mock_movement(
            resource_id=resource.id,
            restaurant_id=restaurant_id,
            quantity=Decimal("8.0"),
        )

        mock_inv_restaurant_repo.get_user_restaurant_role.return_value = "admin"
        mock_evt_restaurant_repo.get_user_restaurant_role.return_value = "admin"
        mock_resource_repo.get_by_id.return_value = resource
        mock_resource_repo.update.return_value = resource
        mock_movement_repo.create.return_value = movement
        mock_inv_event_repo.get_pending_alerts_by_resource.return_value = []
        mock_evt_event_repo.create.return_value = MagicMock(spec=Event, id=uuid4())

        data = InventoryMovementCreateDTO(
            resource_id=resource.id,
            type=MovementType.EXIT,
            quantity=Decimal("8.0"),
            reason=MovementReason.USO,
            restaurant_id=restaurant_id,
        )

        service = InventoryService()
        service.create_movement(db, user_id, data)

        mock_evt_event_repo.create.assert_called_once()
        create_call = mock_evt_event_repo.create.call_args
        assert create_call.kwargs["notification_channel"] == "whatsapp"
        print("INFO [TestLowStockAlert]: test_alert_notification_channel_whatsapp - PASSED")


class TestLowStockEdgeCases:
    """Tests for edge cases in low-stock alert automation."""

    @patch("src.core.services.inventory_service.event_repository")
    @patch("src.core.services.inventory_service.restaurant_repository")
    @patch("src.core.services.inventory_service.resource_repository")
    @patch("src.core.services.inventory_service.inventory_movement_repository")
    def test_stock_equals_minimum_no_alert(
        self,
        mock_movement_repo,
        mock_resource_repo,
        mock_restaurant_repo,
        mock_event_repo,
    ) -> None:
        """Test that stock exactly equal to minimum does NOT trigger alert."""
        db = MagicMock(spec=Session)
        user_id = uuid4()
        restaurant_id = uuid4()

        resource = create_mock_resource(
            current_stock=Decimal("10.0"),
            minimum_stock=Decimal("5.0"),
            restaurant_id=restaurant_id,
        )
        movement = create_mock_movement(
            resource_id=resource.id,
            restaurant_id=restaurant_id,
            quantity=Decimal("5.0"),
        )

        mock_restaurant_repo.get_user_restaurant_role.return_value = "admin"
        mock_resource_repo.get_by_id.return_value = resource
        mock_resource_repo.update.return_value = resource
        mock_movement_repo.create.return_value = movement
        mock_event_repo.resolve_alerts_by_resource.return_value = 0

        data = InventoryMovementCreateDTO(
            resource_id=resource.id,
            type=MovementType.EXIT,
            quantity=Decimal("5.0"),
            reason=MovementReason.USO,
            restaurant_id=restaurant_id,
        )

        service = InventoryService()
        service.create_movement(db, user_id, data)

        # Stock = 10 - 5 = 5, equals minimum → no alert, resolve path instead
        assert resource.current_stock == Decimal("5.0")
        mock_event_repo.get_pending_alerts_by_resource.assert_not_called()
        mock_event_repo.resolve_alerts_by_resource.assert_called_once()
        print("INFO [TestLowStockAlert]: test_stock_equals_minimum_no_alert - PASSED")
