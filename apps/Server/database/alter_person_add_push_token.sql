-- Add push_token column to person table for FCM push notification device tokens
ALTER TABLE person ADD COLUMN push_token TEXT;
