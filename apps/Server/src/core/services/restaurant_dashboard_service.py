"""Restaurant dashboard service for aggregating operational overview data."""

from datetime import date
from uuid import UUID

from sqlalchemy.orm import Session

from src.core.services.document_service import document_service
from src.core.services.event_service import event_service
from src.core.services.inventory_service import inventory_service
from src.core.services.person_service import person_service
from src.core.services.resource_service import resource_service
from src.repository.restaurant_repository import restaurant_repository


class RestaurantDashboardService:
    """Service for aggregating dashboard overview data from multiple entity services."""

    def _check_restaurant_access(self, db: Session, user_id: UUID, restaurant_id: UUID) -> None:
        """
        Check that a user has membership in a restaurant.

        Args:
            db: Database session
            user_id: User UUID
            restaurant_id: Restaurant UUID

        Raises:
            PermissionError: If user doesn't have access to the restaurant
        """
        role = restaurant_repository.get_user_restaurant_role(db, user_id, restaurant_id)
        if role is None:
            print(f"ERROR [RestaurantDashboardService]: User {user_id} doesn't have access to restaurant {restaurant_id}")
            raise PermissionError("User doesn't have access to this restaurant")

    def get_overview(self, db: Session, user_id: UUID, restaurant_id: UUID) -> dict:
        """
        Get aggregated dashboard overview for a restaurant.

        Delegates to individual entity services and assembles a consolidated response.

        Args:
            db: Database session
            user_id: User UUID
            restaurant_id: Restaurant UUID

        Returns:
            Dictionary with today_tasks, upcoming_expirations, low_stock_items,
            recent_movements, pending_alerts, and stats

        Raises:
            PermissionError: If user doesn't have access to the restaurant
        """
        print(f"INFO [RestaurantDashboardService]: Fetching overview for restaurant {restaurant_id} by user {user_id}")

        self._check_restaurant_access(db, user_id, restaurant_id)

        today = date.today()

        # Fetch all data from entity services
        today_tasks = event_service.get_tasks_by_date(db, user_id, restaurant_id, today)
        upcoming_expirations = document_service.get_expiring_documents(db, user_id, restaurant_id, days_ahead=30)
        low_stock_items = resource_service.get_low_stock_resources(db, user_id, restaurant_id)
        recent_movements = inventory_service.get_recent_movements(db, user_id, restaurant_id, limit=10)
        pending_alerts = event_service.get_pending_alerts(db, user_id, restaurant_id)

        # Fetch stats
        total_employees = person_service.count_by_type(db, user_id, restaurant_id, "employee")
        total_resources = resource_service.count_resources(db, user_id, restaurant_id)
        active_documents = document_service.count_active(db, user_id, restaurant_id)
        tasks_completed_today = event_service.count_completed_tasks(db, user_id, restaurant_id, today)

        overview = {
            "today_tasks": today_tasks,
            "upcoming_expirations": upcoming_expirations,
            "low_stock_items": low_stock_items,
            "recent_movements": recent_movements,
            "pending_alerts": pending_alerts,
            "stats": {
                "total_employees": total_employees,
                "total_resources": total_resources,
                "active_documents": active_documents,
                "tasks_completed_today": tasks_completed_today,
            },
        }

        print(f"INFO [RestaurantDashboardService]: Overview assembled - tasks={len(today_tasks)}, expirations={len(upcoming_expirations)}, low_stock={len(low_stock_items)}, movements={len(recent_movements)}, alerts={len(pending_alerts)}")
        return overview


# Singleton instance
restaurant_dashboard_service = RestaurantDashboardService()
