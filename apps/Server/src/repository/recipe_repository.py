"""Recipe repository for database operations."""

from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from src.models.recipe import Recipe, RecipeItem


class RecipeRepository:
    """Repository for Recipe and RecipeItem database operations."""

    def create(
        self,
        db: Session,
        restaurant_id: UUID,
        name: str,
        sale_price: Decimal,
        is_active: bool,
        items: list[dict],
    ) -> Recipe:
        """
        Create a new recipe with its items atomically.

        Args:
            db: Database session
            restaurant_id: Restaurant UUID
            name: Recipe name
            sale_price: Sale price of the dish
            is_active: Whether the recipe is active
            items: List of dicts with resource_id, quantity, unit

        Returns:
            Created Recipe object
        """
        print(f"INFO [RecipeRepository]: Creating recipe '{name}' for restaurant {restaurant_id}")
        recipe = Recipe(
            restaurant_id=restaurant_id,
            name=name,
            sale_price=sale_price,
            is_active=is_active,
        )
        db.add(recipe)
        db.flush()

        for item_data in items:
            recipe_item = RecipeItem(
                recipe_id=recipe.id,
                resource_id=item_data["resource_id"],
                quantity=item_data["quantity"],
                unit=item_data["unit"],
            )
            db.add(recipe_item)

        db.commit()
        db.refresh(recipe)
        print(f"INFO [RecipeRepository]: Recipe created with id {recipe.id}")
        return recipe

    def get_by_id(self, db: Session, recipe_id: UUID) -> Optional[Recipe]:
        """
        Find a recipe by ID.

        Args:
            db: Database session
            recipe_id: Recipe UUID

        Returns:
            Recipe object if found, None otherwise
        """
        print(f"INFO [RecipeRepository]: Looking up recipe by id {recipe_id}")
        recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
        if recipe:
            print(f"INFO [RecipeRepository]: Found recipe '{recipe.name}'")
        else:
            print(f"INFO [RecipeRepository]: No recipe found with id {recipe_id}")
        return recipe

    def get_items(self, db: Session, recipe_id: UUID) -> list[RecipeItem]:
        """
        Get all items for a recipe.

        Args:
            db: Database session
            recipe_id: Recipe UUID

        Returns:
            List of RecipeItem objects
        """
        print(f"INFO [RecipeRepository]: Getting items for recipe {recipe_id}")
        items = db.query(RecipeItem).filter(RecipeItem.recipe_id == recipe_id).all()
        print(f"INFO [RecipeRepository]: Found {len(items)} items for recipe {recipe_id}")
        return items

    def get_by_restaurant(self, db: Session, restaurant_id: UUID) -> list[Recipe]:
        """
        Get all recipes in a restaurant.

        Args:
            db: Database session
            restaurant_id: Restaurant UUID

        Returns:
            List of Recipe objects
        """
        print(f"INFO [RecipeRepository]: Getting recipes for restaurant {restaurant_id}")
        recipes = db.query(Recipe).filter(Recipe.restaurant_id == restaurant_id).all()
        print(f"INFO [RecipeRepository]: Found {len(recipes)} recipes for restaurant {restaurant_id}")
        return recipes

    def update(self, db: Session, recipe: Recipe) -> Recipe:
        """
        Update an existing recipe's fields.

        Args:
            db: Database session
            recipe: Recipe object with updated values

        Returns:
            Updated Recipe object
        """
        print(f"INFO [RecipeRepository]: Updating recipe {recipe.id}")
        db.add(recipe)
        db.commit()
        db.refresh(recipe)
        print(f"INFO [RecipeRepository]: Recipe {recipe.id} updated successfully")
        return recipe

    def replace_items(self, db: Session, recipe_id: UUID, items: list[dict]) -> list[RecipeItem]:
        """
        Delete existing items and insert new ones for a recipe.

        Args:
            db: Database session
            recipe_id: Recipe UUID
            items: List of dicts with resource_id, quantity, unit

        Returns:
            List of newly created RecipeItem objects
        """
        print(f"INFO [RecipeRepository]: Replacing items for recipe {recipe_id}")
        db.query(RecipeItem).filter(RecipeItem.recipe_id == recipe_id).delete()

        new_items = []
        for item_data in items:
            recipe_item = RecipeItem(
                recipe_id=recipe_id,
                resource_id=item_data["resource_id"],
                quantity=item_data["quantity"],
                unit=item_data["unit"],
            )
            db.add(recipe_item)
            new_items.append(recipe_item)

        db.commit()
        for item in new_items:
            db.refresh(item)
        print(f"INFO [RecipeRepository]: Replaced with {len(new_items)} items for recipe {recipe_id}")
        return new_items

    def update_cost(
        self,
        db: Session,
        recipe_id: UUID,
        current_cost: Decimal,
        margin_percent: Decimal,
        is_profitable: bool,
    ) -> None:
        """
        Update computed cost fields on a recipe.

        Args:
            db: Database session
            recipe_id: Recipe UUID
            current_cost: Computed total cost
            margin_percent: Computed margin percentage
            is_profitable: Whether margin >= 60%
        """
        print(f"INFO [RecipeRepository]: Updating cost for recipe {recipe_id} (cost={current_cost}, margin={margin_percent}%)")
        recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
        if recipe:
            recipe.current_cost = current_cost
            recipe.margin_percent = margin_percent
            recipe.is_profitable = is_profitable
            db.commit()
            print(f"INFO [RecipeRepository]: Cost updated for recipe {recipe_id}")

    def delete(self, db: Session, recipe_id: UUID) -> bool:
        """
        Delete a recipe from the database (cascade deletes items).

        Args:
            db: Database session
            recipe_id: Recipe UUID

        Returns:
            True if deleted, False if not found
        """
        print(f"INFO [RecipeRepository]: Deleting recipe {recipe_id}")
        recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
        if recipe:
            db.delete(recipe)
            db.commit()
            print(f"INFO [RecipeRepository]: Recipe {recipe_id} deleted successfully")
            return True
        print(f"INFO [RecipeRepository]: Recipe {recipe_id} not found for deletion")
        return False

    def get_by_resource(self, db: Session, resource_id: UUID) -> list[Recipe]:
        """
        Find recipes that use a specific resource as an ingredient.

        Args:
            db: Database session
            resource_id: Resource UUID

        Returns:
            List of Recipe objects that contain the resource
        """
        print(f"INFO [RecipeRepository]: Finding recipes using resource {resource_id}")
        recipe_ids = (
            db.query(RecipeItem.recipe_id)
            .filter(RecipeItem.resource_id == resource_id)
            .distinct()
            .all()
        )
        ids = [r[0] for r in recipe_ids]
        if not ids:
            print(f"INFO [RecipeRepository]: No recipes found using resource {resource_id}")
            return []
        recipes = db.query(Recipe).filter(Recipe.id.in_(ids)).all()
        print(f"INFO [RecipeRepository]: Found {len(recipes)} recipes using resource {resource_id}")
        return recipes


# Singleton instance
recipe_repository = RecipeRepository()
