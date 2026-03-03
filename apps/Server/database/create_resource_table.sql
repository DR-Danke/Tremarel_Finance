-- Resource Entity Table
-- RestaurantOS Wave 1: ROS-003

CREATE TABLE resource (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    restaurant_id UUID NOT NULL REFERENCES restaurant(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL DEFAULT 'producto',
    name VARCHAR(255) NOT NULL,
    unit VARCHAR(50) NOT NULL,
    current_stock DECIMAL(12,4) NOT NULL DEFAULT 0,
    minimum_stock DECIMAL(12,4) NOT NULL DEFAULT 0,
    last_unit_cost DECIMAL(12,4) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for common queries
CREATE INDEX idx_resource_restaurant ON resource(restaurant_id);
CREATE INDEX idx_resource_type ON resource(type);

-- Trigger for auto-updating updated_at on resource
CREATE TRIGGER update_resource_updated_at
    BEFORE UPDATE ON resource
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
