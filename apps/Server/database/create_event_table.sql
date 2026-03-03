-- Event Entity Table
-- RestaurantOS Wave 2: Centralized event/task management

CREATE TABLE event (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    restaurant_id UUID NOT NULL REFERENCES restaurant(id) ON DELETE CASCADE,
    type VARCHAR(100) NOT NULL,
    description TEXT,
    date TIMESTAMP NOT NULL,
    frequency VARCHAR(50) DEFAULT 'none',
    responsible_id UUID REFERENCES person(id) ON DELETE SET NULL,
    notification_channel VARCHAR(50) DEFAULT 'email',
    status VARCHAR(50) DEFAULT 'pending',
    related_document_id UUID,
    parent_event_id UUID REFERENCES event(id) ON DELETE CASCADE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for common queries
CREATE INDEX idx_event_restaurant ON event(restaurant_id);
CREATE INDEX idx_event_type ON event(type);
CREATE INDEX idx_event_date ON event(date);
CREATE INDEX idx_event_status ON event(status);
CREATE INDEX idx_event_responsible ON event(responsible_id);
CREATE INDEX idx_event_parent ON event(parent_event_id);

-- Trigger for auto-updating updated_at on event
CREATE TRIGGER update_event_updated_at
    BEFORE UPDATE ON event
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
