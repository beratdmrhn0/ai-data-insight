-- AI Data Insight Database Initialization Script

-- Create database if not exists (handled by POSTGRES_DB env var)
-- CREATE DATABASE ai_data_insight;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create uploads table
CREATE TABLE IF NOT EXISTS uploads (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    path VARCHAR(500) NOT NULL,
    status VARCHAR(50) DEFAULT 'uploaded',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create analysis table
CREATE TABLE IF NOT EXISTS analysis (
    id SERIAL PRIMARY KEY,
    upload_id INTEGER REFERENCES uploads(id) ON DELETE CASCADE,
    summary JSONB,
    insights JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create pipeline_history table
CREATE TABLE IF NOT EXISTS pipeline_history (
    id SERIAL PRIMARY KEY,
    upload_id INTEGER REFERENCES uploads(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL,
    message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_uploads_status ON uploads(status);
CREATE INDEX IF NOT EXISTS idx_uploads_created_at ON uploads(created_at);
CREATE INDEX IF NOT EXISTS idx_analysis_upload_id ON analysis(upload_id);
CREATE INDEX IF NOT EXISTS idx_pipeline_history_upload_id ON pipeline_history(upload_id);
CREATE INDEX IF NOT EXISTS idx_pipeline_history_status ON pipeline_history(status);
CREATE INDEX IF NOT EXISTS idx_pipeline_history_created_at ON pipeline_history(created_at);

-- Insert sample data for development
INSERT INTO uploads (filename, path, status) VALUES 
('sample_orders.csv', '/app/sample_orders.csv', 'completed')
ON CONFLICT DO NOTHING;

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for uploads table
CREATE TRIGGER update_uploads_updated_at 
    BEFORE UPDATE ON uploads 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions (if needed for production)
-- GRANT ALL PRIVILEGES ON DATABASE ai_data_insight TO postgres;
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;
