"""Restaurant service for business logic operations."""

from uuid import UUID

from sqlalchemy.orm import Session

from src.interface.restaurant_dto import RestaurantCreateDTO, RestaurantUpdateDTO
from src.models.restaurant import Restaurant
from src.repository.restaurant_repository import restaurant_repository


class RestaurantService:
    """Service for restaurant business logic."""

    def create_restaurant(
        self,
        db: Session,
        user_id: UUID,
        data: RestaurantCreateDTO,
    ) -> Restaurant:
        """
        Create a new restaurant and add the creator as owner/admin.

        Args:
            db: Database session
            user_id: ID of the user creating the restaurant
            data: Restaurant creation data

        Returns:
            Created Restaurant object
        """
        print(f"INFO [RestaurantService]: Creating restaurant '{data.name}' for user {user_id}")

        restaurant = restaurant_repository.create_restaurant(
            db=db,
            name=data.name,
            address=data.address,
            owner_id=user_id,
        )

        print(f"INFO [RestaurantService]: Restaurant '{restaurant.name}' created with user {user_id} as owner/admin")
        return restaurant

    def get_user_restaurants(self, db: Session, user_id: UUID) -> list[Restaurant]:
        """
        Get all restaurants that a user belongs to.

        Args:
            db: Database session
            user_id: User UUID

        Returns:
            List of Restaurant objects
        """
        print(f"INFO [RestaurantService]: Getting restaurants for user {user_id}")
        return restaurant_repository.get_restaurants_by_user(db, user_id)

    def get_restaurant(
        self,
        db: Session,
        restaurant_id: UUID,
        user_id: UUID,
    ) -> Restaurant:
        """
        Get a restaurant by ID if user has access.

        Args:
            db: Database session
            restaurant_id: Restaurant UUID
            user_id: User UUID requesting access

        Returns:
            Restaurant object

        Raises:
            PermissionError: If user doesn't have access to the restaurant
            ValueError: If restaurant not found
        """
        print(f"INFO [RestaurantService]: Getting restaurant {restaurant_id} for user {user_id}")

        # Check if user has access to the restaurant
        role = restaurant_repository.get_user_restaurant_role(db, user_id, restaurant_id)
        if role is None:
            print(f"ERROR [RestaurantService]: User {user_id} doesn't have access to restaurant {restaurant_id}")
            raise PermissionError("User doesn't have access to this restaurant")

        restaurant = restaurant_repository.get_restaurant_by_id(db, restaurant_id)
        if restaurant is None:
            print(f"ERROR [RestaurantService]: Restaurant {restaurant_id} not found")
            raise ValueError("Restaurant not found")

        return restaurant

    def update_restaurant(
        self,
        db: Session,
        restaurant_id: UUID,
        user_id: UUID,
        data: RestaurantUpdateDTO,
    ) -> Restaurant:
        """
        Update a restaurant if user is owner or admin.

        Args:
            db: Database session
            restaurant_id: Restaurant UUID
            user_id: User UUID
            data: Restaurant update data

        Returns:
            Updated Restaurant object

        Raises:
            PermissionError: If user doesn't have owner/admin role
            ValueError: If restaurant not found
        """
        print(f"INFO [RestaurantService]: Updating restaurant {restaurant_id} by user {user_id}")

        # Check user role
        role = restaurant_repository.get_user_restaurant_role(db, user_id, restaurant_id)
        if role not in ("admin",):
            print(f"ERROR [RestaurantService]: User {user_id} doesn't have permission to update restaurant {restaurant_id}")
            raise PermissionError("Only owner or admin can update restaurant")

        # Get restaurant
        restaurant = restaurant_repository.get_restaurant_by_id(db, restaurant_id)
        if restaurant is None:
            print(f"ERROR [RestaurantService]: Restaurant {restaurant_id} not found")
            raise ValueError("Restaurant not found")

        # Also allow owner
        if role != "admin" and restaurant.owner_id != user_id:
            print(f"ERROR [RestaurantService]: User {user_id} is not owner or admin of restaurant {restaurant_id}")
            raise PermissionError("Only owner or admin can update restaurant")

        # Update fields if provided
        if data.name is not None:
            restaurant.name = data.name
        if data.address is not None:
            restaurant.address = data.address

        updated_restaurant = restaurant_repository.update_restaurant(db, restaurant)
        print(f"INFO [RestaurantService]: Restaurant {restaurant_id} updated successfully")
        return updated_restaurant

    def delete_restaurant(
        self,
        db: Session,
        restaurant_id: UUID,
        user_id: UUID,
    ) -> bool:
        """
        Delete a restaurant if user is owner or admin.

        Args:
            db: Database session
            restaurant_id: Restaurant UUID
            user_id: User UUID

        Returns:
            True if deleted

        Raises:
            PermissionError: If user doesn't have owner/admin role
            ValueError: If restaurant not found
        """
        print(f"INFO [RestaurantService]: Deleting restaurant {restaurant_id} by user {user_id}")

        # Check user role
        role = restaurant_repository.get_user_restaurant_role(db, user_id, restaurant_id)
        if role not in ("admin",):
            print(f"ERROR [RestaurantService]: User {user_id} doesn't have permission to delete restaurant {restaurant_id}")
            raise PermissionError("Only owner or admin can delete restaurant")

        # Delete restaurant
        deleted = restaurant_repository.delete_restaurant(db, restaurant_id)
        if not deleted:
            print(f"ERROR [RestaurantService]: Restaurant {restaurant_id} not found for deletion")
            raise ValueError("Restaurant not found")

        print(f"INFO [RestaurantService]: Restaurant {restaurant_id} deleted successfully")
        return True


# Singleton instance
restaurant_service = RestaurantService()
