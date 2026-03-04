-- Migration: Add related_resource_id to event table for low-stock alert linking
-- Links alerta_stock events to the specific resource that triggered the alert

ALTER TABLE event ADD COLUMN related_resource_id UUID REFERENCES resource(id) ON DELETE SET NULL;
CREATE INDEX idx_event_related_resource ON event(related_resource_id);
