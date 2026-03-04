"""Recipe service for business logic operations."""

import os
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from src.core.services.inventory_service import inventory_service
from src.interface.inventory_movement_dto import (
    InventoryMovementCreateDTO,
    MovementReason,
    MovementType,
)
from src.interface.recipe_dto import RecipeCreateDTO, RecipeUpdateDTO
from src.models.recipe import Recipe, RecipeItem
from src.repository.event_repository import event_repository
from src.repository.person_repository import person_repository
from src.repository.recipe_repository import recipe_repository
from src.repository.resource_repository import resource_repository
from src.repository.restaurant_repository import restaurant_repository

PROFITABILITY_THRESHOLD = Decimal(os.getenv("PROFITABILITY_THRESHOLD", "60"))


class RecipeService:
    """Service for recipe business logic with restaurant-scoped authorization."""

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
            print(f"ERROR [RecipeService]: User {user_id} doesn't have access to restaurant {restaurant_id}")
            raise PermissionError("User doesn't have access to this restaurant")

    def create_recipe(
        self,
        db: Session,
        user_id: UUID,
        data: RecipeCreateDTO,
    ) -> tuple[Recipe, list[RecipeItem]]:
        """
        Create a new recipe with items in a restaurant.

        Args:
            db: Database session
            user_id: ID of the user creating the recipe
            data: Recipe creation data

        Returns:
            Tuple of (Recipe, list[RecipeItem])

        Raises:
            PermissionError: If user doesn't have access to the restaurant
        """
        print(f"INFO [RecipeService]: Creating recipe '{data.name}' in restaurant {data.restaurant_id} by user {user_id}")

        self._check_restaurant_access(db, user_id, data.restaurant_id)

        items_data = [
            {"resource_id": item.resource_id, "quantity": item.quantity, "unit": item.unit}
            for item in data.items
        ]

        recipe = recipe_repository.create(
            db=db,
            restaurant_id=data.restaurant_id,
            name=data.name,
            sale_price=data.sale_price,
            is_active=data.is_active,
            items=items_data,
        )

        self.calculate_cost(db, recipe.id)

        recipe = recipe_repository.get_by_id(db, recipe.id)
        items = recipe_repository.get_items(db, recipe.id)

        print(f"INFO [RecipeService]: Recipe '{recipe.name}' created with id {recipe.id}")
        return recipe, items

    def get_recipes(
        self,
        db: Session,
        user_id: UUID,
        restaurant_id: UUID,
    ) -> list[tuple[Recipe, list[RecipeItem]]]:
        """
        Get all recipes in a restaurant with their items.

        Args:
            db: Database session
            user_id: User UUID
            restaurant_id: Restaurant UUID

        Returns:
            List of (Recipe, list[RecipeItem]) tuples

        Raises:
            PermissionError: If user doesn't have access to the restaurant
        """
        print(f"INFO [RecipeService]: Getting recipes for restaurant {restaurant_id} by user {user_id}")

        self._check_restaurant_access(db, user_id, restaurant_id)

        recipes = recipe_repository.get_by_restaurant(db, restaurant_id)
        result = []
        for recipe in recipes:
            items = recipe_repository.get_items(db, recipe.id)
            result.append((recipe, items))
        return result

    def get_recipe(
        self,
        db: Session,
        user_id: UUID,
        recipe_id: UUID,
    ) -> tuple[Recipe, list[RecipeItem]]:
        """
        Get a recipe by ID with items if user has access.

        Args:
            db: Database session
            user_id: User UUID
            recipe_id: Recipe UUID

        Returns:
            Tuple of (Recipe, list[RecipeItem])

        Raises:
            PermissionError: If user doesn't have access to the restaurant
            ValueError: If recipe not found
        """
        print(f"INFO [RecipeService]: Getting recipe {recipe_id} for user {user_id}")

        recipe = recipe_repository.get_by_id(db, recipe_id)
        if recipe is None:
            print(f"ERROR [RecipeService]: Recipe {recipe_id} not found")
            raise ValueError("Recipe not found")

        self._check_restaurant_access(db, user_id, recipe.restaurant_id)

        items = recipe_repository.get_items(db, recipe.id)
        return recipe, items

    def update_recipe(
        self,
        db: Session,
        user_id: UUID,
        recipe_id: UUID,
        data: RecipeUpdateDTO,
    ) -> tuple[Recipe, list[RecipeItem]]:
        """
        Update a recipe if user has access.

        Args:
            db: Database session
            user_id: User UUID
            recipe_id: Recipe UUID
            data: Recipe update data

        Returns:
            Tuple of (Recipe, list[RecipeItem])

        Raises:
            PermissionError: If user doesn't have access to the restaurant
            ValueError: If recipe not found
        """
        print(f"INFO [RecipeService]: Updating recipe {recipe_id} by user {user_id}")

        recipe = recipe_repository.get_by_id(db, recipe_id)
        if recipe is None:
            print(f"ERROR [RecipeService]: Recipe {recipe_id} not found")
            raise ValueError("Recipe not found")

        self._check_restaurant_access(db, user_id, recipe.restaurant_id)

        if data.name is not None:
            recipe.name = data.name
        if data.sale_price is not None:
            recipe.sale_price = data.sale_price
        if data.is_active is not None:
            recipe.is_active = data.is_active

        recipe = recipe_repository.update(db, recipe)

        if data.items is not None:
            items_data = [
                {"resource_id": item.resource_id, "quantity": item.quantity, "unit": item.unit}
                for item in data.items
            ]
            recipe_repository.replace_items(db, recipe.id, items_data)

        self.calculate_cost(db, recipe.id)

        recipe = recipe_repository.get_by_id(db, recipe.id)
        items = recipe_repository.get_items(db, recipe.id)

        print(f"INFO [RecipeService]: Recipe {recipe_id} updated successfully")
        return recipe, items

    def delete_recipe(
        self,
        db: Session,
        user_id: UUID,
        recipe_id: UUID,
    ) -> bool:
        """
        Delete a recipe if user has access.

        Args:
            db: Database session
            user_id: User UUID
            recipe_id: Recipe UUID

        Returns:
            True if deleted

        Raises:
            PermissionError: If user doesn't have access to the restaurant
            ValueError: If recipe not found
        """
        print(f"INFO [RecipeService]: Deleting recipe {recipe_id} by user {user_id}")

        recipe = recipe_repository.get_by_id(db, recipe_id)
        if recipe is None:
            print(f"ERROR [RecipeService]: Recipe {recipe_id} not found")
            raise ValueError("Recipe not found")

        self._check_restaurant_access(db, user_id, recipe.restaurant_id)

        deleted = recipe_repository.delete(db, recipe_id)
        if not deleted:
            print(f"ERROR [RecipeService]: Recipe {recipe_id} not found for deletion")
            raise ValueError("Recipe not found")

        print(f"INFO [RecipeService]: Recipe {recipe_id} deleted successfully")
        return True

    def produce_recipe(
        self,
        db: Session,
        user_id: UUID,
        recipe_id: UUID,
        quantity: int = 1,
    ) -> dict:
        """
        Produce a recipe: pre-check all ingredient stocks, then create exit movements.

        This is an atomic all-or-nothing operation. If any ingredient has
        insufficient stock, no deductions occur.

        Args:
            db: Database session
            user_id: User UUID
            recipe_id: Recipe UUID
            quantity: Number of recipe units to produce

        Returns:
            Dict with recipe_id, recipe_name, quantity, movements_created

        Raises:
            PermissionError: If user doesn't have access to the restaurant
            ValueError: If recipe not found or insufficient stock
        """
        print(f"INFO [RecipeService]: Producing recipe {recipe_id} x{quantity} by user {user_id}")

        recipe = recipe_repository.get_by_id(db, recipe_id)
        if recipe is None:
            print(f"ERROR [RecipeService]: Recipe {recipe_id} not found")
            raise ValueError("Recipe not found")

        self._check_restaurant_access(db, user_id, recipe.restaurant_id)

        items = recipe_repository.get_items(db, recipe_id)

        # Pre-check all ingredients for sufficient stock
        for item in items:
            resource = resource_repository.get_by_id(db, item.resource_id)
            if resource is None:
                print(f"ERROR [RecipeService]: Resource {item.resource_id} not found for recipe item")
                raise ValueError(f"Resource not found for recipe item {item.resource_id}")
            required = item.quantity * quantity
            if resource.current_stock < required:
                print(f"ERROR [RecipeService]: Insufficient stock for {resource.name}: need {required}, have {resource.current_stock}")
                raise ValueError(
                    f"Stock insuficiente para {resource.name}: necesita {required} {item.unit}, disponible {resource.current_stock}"
                )

        # Create exit movements for each ingredient
        movements = []
        for item in items:
            movement = inventory_service.create_movement(
                db,
                user_id,
                InventoryMovementCreateDTO(
                    resource_id=item.resource_id,
                    type=MovementType.EXIT,
                    quantity=item.quantity * quantity,
                    reason=MovementReason.RECETA,
                    restaurant_id=recipe.restaurant_id,
                    notes=f"Producción: {recipe.name} x{quantity}",
                ),
            )
            movements.append(movement)

        print(f"INFO [RecipeService]: Recipe '{recipe.name}' produced x{quantity}, {len(movements)} movements created")
        return {
            "recipe_id": recipe.id,
            "recipe_name": recipe.name,
            "quantity": quantity,
            "movements_created": len(movements),
        }

    def calculate_cost(self, db: Session, recipe_id: UUID) -> dict:
        """
        Calculate total cost, margin, and profitability for a recipe.

        Iterates recipe items, looks up each resource's last_unit_cost,
        computes total_cost = sum(quantity * last_unit_cost).
        margin_percent = (sale_price - total_cost) / sale_price * 100
        is_profitable = margin >= 60

        Args:
            db: Database session
            recipe_id: Recipe UUID

        Returns:
            Dict with current_cost, margin_percent, is_profitable
        """
        print(f"INFO [RecipeService]: Calculating cost for recipe {recipe_id}")

        recipe = recipe_repository.get_by_id(db, recipe_id)
        if recipe is None:
            print(f"ERROR [RecipeService]: Recipe {recipe_id} not found for cost calculation")
            raise ValueError("Recipe not found")

        items = recipe_repository.get_items(db, recipe.id)
        total_cost = Decimal("0")

        for item in items:
            resource = resource_repository.get_by_id(db, item.resource_id)
            unit_cost = Decimal("0")
            if resource and resource.last_unit_cost:
                unit_cost = resource.last_unit_cost
            total_cost += item.quantity * unit_cost

        if recipe.sale_price > 0:
            margin_percent = (recipe.sale_price - total_cost) / recipe.sale_price * Decimal("100")
        else:
            margin_percent = Decimal("0")

        is_profitable = margin_percent >= PROFITABILITY_THRESHOLD

        recipe_repository.update_cost(db, recipe_id, total_cost, margin_percent, is_profitable)

        print(f"INFO [RecipeService]: Recipe {recipe_id} cost={total_cost}, margin={margin_percent}%, profitable={is_profitable}")
        return {
            "current_cost": total_cost,
            "margin_percent": margin_percent,
            "is_profitable": is_profitable,
        }

    def recalculate_cost(
        self,
        db: Session,
        user_id: UUID,
        recipe_id: UUID,
    ) -> dict:
        """
        Force cost recalculation for a recipe with access check.

        Args:
            db: Database session
            user_id: User UUID
            recipe_id: Recipe UUID

        Returns:
            Dict with current_cost, margin_percent, is_profitable

        Raises:
            PermissionError: If user doesn't have access to the restaurant
            ValueError: If recipe not found
        """
        print(f"INFO [RecipeService]: Recalculating cost for recipe {recipe_id} by user {user_id}")

        recipe = recipe_repository.get_by_id(db, recipe_id)
        if recipe is None:
            print(f"ERROR [RecipeService]: Recipe {recipe_id} not found")
            raise ValueError("Recipe not found")

        self._check_restaurant_access(db, user_id, recipe.restaurant_id)

        return self.calculate_cost(db, recipe_id)

    def recalculate_by_resource(self, db: Session, resource_id: UUID) -> list[dict]:
        """
        Recalculate cost for all recipes that use a specific resource.

        Detects profitability transitions and creates alerts when a recipe
        transitions from profitable to unprofitable.

        Args:
            db: Database session
            resource_id: Resource UUID whose cost changed

        Returns:
            List of cost result dicts for each affected recipe
        """
        recipes = recipe_repository.get_by_resource(db, resource_id)
        print(f"INFO [RecipeService]: Recalculating {len(recipes)} recipes affected by resource {resource_id}")

        results = []
        for recipe in recipes:
            was_profitable = recipe.is_profitable
            result = self.calculate_cost(db, recipe.id)
            if was_profitable and not result["is_profitable"]:
                self._create_profitability_alert(db, recipe, result)
            results.append(result)

        return results

    def _create_profitability_alert(self, db: Session, recipe: Recipe, cost_result: dict) -> None:
        """
        Create an alerta_rentabilidad event when a recipe becomes unprofitable.

        Args:
            db: Database session
            recipe: Recipe that became unprofitable
            cost_result: Dict with current_cost, margin_percent, is_profitable
        """
        owner = person_repository.find_owner(db, recipe.restaurant_id)
        event_repository.create(
            db=db,
            restaurant_id=recipe.restaurant_id,
            event_type="alerta_rentabilidad",
            description=(
                f"Alerta de rentabilidad: {recipe.name} - "
                f"Costo: ${cost_result['current_cost']}, "
                f"Precio venta: ${recipe.sale_price}, "
                f"Margen: {cost_result['margin_percent']:.1f}%"
            ),
            event_date=datetime.utcnow(),
            frequency="none",
            responsible_id=owner.id if owner else None,
            notification_channel="whatsapp",
        )
        print(f"INFO [RecipeService]: Profitability alert created for recipe '{recipe.name}'")


# Singleton instance
recipe_service = RecipeService()
