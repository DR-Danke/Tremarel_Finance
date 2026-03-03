-- Document Entity Table
-- RestaurantOS Wave 2: ROS-004

CREATE TABLE document (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    restaurant_id UUID NOT NULL REFERENCES restaurant(id) ON DELETE CASCADE,
    type VARCHAR(100) NOT NULL,
    file_url TEXT,
    issue_date DATE,
    expiration_date DATE,
    person_id UUID REFERENCES person(id) ON DELETE SET NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for common queries
CREATE INDEX idx_document_restaurant ON document(restaurant_id);
CREATE INDEX idx_document_type ON document(type);
CREATE INDEX idx_document_expiration ON document(expiration_date);
CREATE INDEX idx_document_person ON document(person_id);

-- Trigger for auto-updating updated_at on document
CREATE TRIGGER update_document_updated_at
    BEFORE UPDATE ON document
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
