-- Initialize URL Shortener Database
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create index for better performance
CREATE INDEX IF NOT EXISTS idx_url_mappings_short_code ON url_mappings(short_code);
CREATE INDEX IF NOT EXISTS idx_url_mappings_created_at ON url_mappings(created_at);
CREATE INDEX IF NOT EXISTS idx_url_mappings_expires_at ON url_mappings(expires_at) WHERE expires_at IS NOT NULL;