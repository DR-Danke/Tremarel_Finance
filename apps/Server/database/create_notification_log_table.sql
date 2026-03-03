-- Notification Log Table
-- WhatsApp Notification Integration: audit trail for all notification attempts

CREATE TABLE notification_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    restaurant_id UUID NOT NULL REFERENCES restaurant(id) ON DELETE CASCADE,
    channel VARCHAR(50) NOT NULL,
    recipient VARCHAR(255) NOT NULL,
    message TEXT,
    status VARCHAR(50) NOT NULL,
    error_message TEXT,
    event_id UUID REFERENCES event(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for common queries
CREATE INDEX idx_notification_log_restaurant ON notification_log(restaurant_id);
CREATE INDEX idx_notification_log_channel ON notification_log(channel);
CREATE INDEX idx_notification_log_status ON notification_log(status);
CREATE INDEX idx_notification_log_created_at ON notification_log(created_at);
