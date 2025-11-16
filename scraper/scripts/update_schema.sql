-- Update database schema for session-based summarization
-- Run this to migrate to the new approach

-- Create scraping_summaries table for comprehensive session summaries
CREATE TABLE IF NOT EXISTS news.scraping_summaries (
    id SERIAL PRIMARY KEY,
    scraping_date DATE NOT NULL DEFAULT CURRENT_DATE,
    summary TEXT NOT NULL,
    articles_count INTEGER NOT NULL,
    sources_count INTEGER NOT NULL,
    new_articles_count INTEGER NOT NULL,
    scraping_duration_seconds NUMERIC(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for quick date lookups
CREATE INDEX IF NOT EXISTS idx_scraping_summaries_date
ON news.scraping_summaries(scraping_date DESC);

-- Trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION news.update_scraping_summaries_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_scraping_summaries_updated_at
    BEFORE UPDATE ON news.scraping_summaries
    FOR EACH ROW
    EXECUTE FUNCTION news.update_scraping_summaries_updated_at();

-- We can optionally remove the summary column from articles table
-- (keeping it for now in case you want to go back)
-- ALTER TABLE news.articles DROP COLUMN IF EXISTS summary;

COMMENT ON TABLE news.scraping_summaries IS 'Stores comprehensive AI-generated summaries for each scraping session';
COMMENT ON COLUMN news.scraping_summaries.summary IS 'Comprehensive summary of all articles from this scraping session';
COMMENT ON COLUMN news.scraping_summaries.scraping_date IS 'Date when scraping was performed';
COMMENT ON COLUMN news.scraping_summaries.articles_count IS 'Total articles found during this session';
COMMENT ON COLUMN news.scraping_summaries.new_articles_count IS 'Number of new articles saved during this session';
