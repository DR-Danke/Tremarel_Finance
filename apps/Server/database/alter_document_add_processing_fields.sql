-- Migration: Add processing fields to document table for Invoice OCR feature
-- These columns track the OCR processing status and results for supplier invoices.

ALTER TABLE document
ADD COLUMN IF NOT EXISTS processing_status VARCHAR(20) DEFAULT NULL;

ALTER TABLE document
ADD COLUMN IF NOT EXISTS processing_result JSONB DEFAULT NULL;

-- Index for efficient filtering by processing status
CREATE INDEX IF NOT EXISTS idx_document_processing_status
ON document (processing_status)
WHERE processing_status IS NOT NULL;
