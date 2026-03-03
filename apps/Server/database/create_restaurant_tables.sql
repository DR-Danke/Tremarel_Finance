-- Restaurant Multi-Tenant Entity Tables
-- RestaurantOS Wave 1: ROS-001

CREATE TABLE restaurant (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    address TEXT,
    owner_id UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE user_restaurants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    restaurant_id UUID NOT NULL REFERENCES restaurant(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL DEFAULT 'user',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, restaurant_id)
);

-- Indexes for common queries
CREATE INDEX idx_user_restaurants_user_id ON user_restaurants(user_id);
CREATE INDEX idx_user_restaurants_restaurant_id ON user_restaurants(restaurant_id);
CREATE INDEX idx_restaurant_owner_id ON restaurant(owner_id);

-- Trigger for auto-updating updated_at on restaurant
CREATE TRIGGER update_restaurant_updated_at
    BEFORE UPDATE ON restaurant
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
