-- Inventory Movement Table
-- RestaurantOS Wave 3: Issue #83

CREATE TABLE inventory_movement (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    resource_id UUID NOT NULL REFERENCES resource(id) ON DELETE CASCADE,
    type VARCHAR(20) NOT NULL,
    quantity DECIMAL(12,4) NOT NULL,
    reason VARCHAR(100) NOT NULL,
    date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    person_id UUID REFERENCES person(id) ON DELETE SET NULL,
    restaurant_id UUID NOT NULL,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for common queries
CREATE INDEX idx_inventory_movement_resource ON inventory_movement(resource_id);
CREATE INDEX idx_inventory_movement_restaurant ON inventory_movement(restaurant_id);
CREATE INDEX idx_inventory_movement_date ON inventory_movement(date);
