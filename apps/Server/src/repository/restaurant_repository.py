"""Restaurant repository for database operations."""

from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from src.models.restaurant import Restaurant
from src.models.user_restaurant import UserRestaurant


class RestaurantRepository:
    """Repository for Restaurant and UserRestaurant database operations."""

    def create_restaurant(
        self,
        db: Session,
        name: str,
        address: Optional[str],
        owner_id: UUID,
    ) -> Restaurant:
        """
        Create a new restaurant and add the owner as admin member.

        Args:
            db: Database session
            name: Restaurant name
            address: Restaurant address (optional)
            owner_id: UUID of the restaurant owner

        Returns:
            Created Restaurant object
        """
        print(f"INFO [RestaurantRepository]: Creating restaurant with name '{name}' for owner {owner_id}")
        restaurant = Restaurant(
            name=name,
            address=address,
            owner_id=owner_id,
        )
        db.add(restaurant)
        db.commit()
        db.refresh(restaurant)
        print(f"INFO [RestaurantRepository]: Restaurant created with id {restaurant.id}")

        # Add owner as admin member
        user_restaurant = UserRestaurant(
            user_id=owner_id,
            restaurant_id=restaurant.id,
            role="admin",
        )
        db.add(user_restaurant)
        db.commit()
        print(f"INFO [RestaurantRepository]: Owner {owner_id} added as admin to restaurant {restaurant.id}")

        return restaurant

    def get_restaurant_by_id(self, db: Session, restaurant_id: UUID) -> Optional[Restaurant]:
        """
        Find a restaurant by ID.

        Args:
            db: Database session
            restaurant_id: Restaurant UUID

        Returns:
            Restaurant object if found, None otherwise
        """
        print(f"INFO [RestaurantRepository]: Looking up restaurant by id {restaurant_id}")
        restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
        if restaurant:
            print(f"INFO [RestaurantRepository]: Found restaurant '{restaurant.name}'")
        else:
            print(f"INFO [RestaurantRepository]: No restaurant found with id {restaurant_id}")
        return restaurant

    def get_restaurants_by_user(self, db: Session, user_id: UUID) -> list[Restaurant]:
        """
        Get all restaurants that a user belongs to.

        Args:
            db: Database session
            user_id: User UUID

        Returns:
            List of Restaurant objects
        """
        print(f"INFO [RestaurantRepository]: Getting restaurants for user {user_id}")
        restaurants = (
            db.query(Restaurant)
            .join(UserRestaurant, Restaurant.id == UserRestaurant.restaurant_id)
            .filter(UserRestaurant.user_id == user_id)
            .all()
        )
        print(f"INFO [RestaurantRepository]: Found {len(restaurants)} restaurants for user {user_id}")
        return restaurants

    def update_restaurant(self, db: Session, restaurant: Restaurant) -> Restaurant:
        """
        Update an existing restaurant.

        Args:
            db: Database session
            restaurant: Restaurant object with updated values

        Returns:
            Updated Restaurant object
        """
        print(f"INFO [RestaurantRepository]: Updating restaurant {restaurant.id}")
        db.add(restaurant)
        db.commit()
        db.refresh(restaurant)
        print(f"INFO [RestaurantRepository]: Restaurant {restaurant.id} updated successfully")
        return restaurant

    def delete_restaurant(self, db: Session, restaurant_id: UUID) -> bool:
        """
        Delete a restaurant from the database.

        Args:
            db: Database session
            restaurant_id: Restaurant UUID

        Returns:
            True if deleted, False if not found
        """
        print(f"INFO [RestaurantRepository]: Deleting restaurant {restaurant_id}")
        restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
        if restaurant:
            db.delete(restaurant)
            db.commit()
            print(f"INFO [RestaurantRepository]: Restaurant {restaurant_id} deleted successfully")
            return True
        print(f"INFO [RestaurantRepository]: Restaurant {restaurant_id} not found for deletion")
        return False

    def get_user_restaurant_role(
        self,
        db: Session,
        user_id: UUID,
        restaurant_id: UUID,
    ) -> Optional[str]:
        """
        Get a user's role in a specific restaurant.

        Args:
            db: Database session
            user_id: User UUID
            restaurant_id: Restaurant UUID

        Returns:
            Role string if found, None otherwise
        """
        print(f"INFO [RestaurantRepository]: Getting role for user {user_id} in restaurant {restaurant_id}")
        user_restaurant = (
            db.query(UserRestaurant)
            .filter(UserRestaurant.user_id == user_id, UserRestaurant.restaurant_id == restaurant_id)
            .first()
        )
        if user_restaurant:
            print(f"INFO [RestaurantRepository]: User {user_id} has role '{user_restaurant.role}' in restaurant {restaurant_id}")
            return user_restaurant.role
        print(f"INFO [RestaurantRepository]: User {user_id} not found in restaurant {restaurant_id}")
        return None

    def add_user_to_restaurant(
        self,
        db: Session,
        user_id: UUID,
        restaurant_id: UUID,
        role: str = "user",
    ) -> UserRestaurant:
        """
        Add a user to a restaurant with a specific role.

        Args:
            db: Database session
            user_id: User UUID
            restaurant_id: Restaurant UUID
            role: User role in the restaurant (default: "user")

        Returns:
            Created UserRestaurant object
        """
        print(f"INFO [RestaurantRepository]: Adding user {user_id} to restaurant {restaurant_id} with role '{role}'")
        user_restaurant = UserRestaurant(
            user_id=user_id,
            restaurant_id=restaurant_id,
            role=role,
        )
        db.add(user_restaurant)
        db.commit()
        db.refresh(user_restaurant)
        print(f"INFO [RestaurantRepository]: User {user_id} added to restaurant {restaurant_id}")
        return user_restaurant


# Singleton instance
restaurant_repository = RestaurantRepository()
