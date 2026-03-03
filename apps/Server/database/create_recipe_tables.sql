-- Recipe and RecipeItem Tables
-- RestaurantOS Wave 5: ROS-016

CREATE TABLE recipe (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    restaurant_id UUID NOT NULL REFERENCES restaurant(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    sale_price DECIMAL(12,2) NOT NULL,
    current_cost DECIMAL(12,2) NOT NULL DEFAULT 0,
    margin_percent DECIMAL(5,2) NOT NULL DEFAULT 0,
    is_profitable BOOLEAN NOT NULL DEFAULT true,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE recipe_item (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recipe_id UUID NOT NULL REFERENCES recipe(id) ON DELETE CASCADE,
    resource_id UUID NOT NULL REFERENCES resource(id) ON DELETE RESTRICT,
    quantity DECIMAL(12,4) NOT NULL,
    unit VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for common queries
CREATE INDEX idx_recipe_restaurant ON recipe(restaurant_id);
CREATE INDEX idx_recipe_item_recipe ON recipe_item(recipe_id);
CREATE INDEX idx_recipe_item_resource ON recipe_item(resource_id);

-- Trigger for auto-updating updated_at on recipe
CREATE TRIGGER update_recipe_updated_at
    BEFORE UPDATE ON recipe
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
