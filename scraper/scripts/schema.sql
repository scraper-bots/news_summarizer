-- News articles table schema
-- Supports Azerbaijani characters with UTF-8 encoding

CREATE SCHEMA IF NOT EXISTS news;

-- Scraping summaries table
-- Stores comprehensive session summaries with metadata
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

-- Create index for scraping_summaries
CREATE INDEX IF NOT EXISTS idx_scraping_summaries_date ON news.scraping_summaries(scraping_date DESC);

-- Create updated_at trigger for scraping_summaries
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

-- Articles table
-- NOTE: This table references scraping_summaries, so scraping_summaries must be created first
CREATE TABLE IF NOT EXISTS news.articles (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    source VARCHAR(100) NOT NULL,
    url TEXT NOT NULL UNIQUE,
    published_date TIMESTAMP,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    language VARCHAR(10) DEFAULT 'az',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    scraping_session_id INTEGER REFERENCES news.scraping_summaries(id) ON DELETE SET NULL
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_articles_source ON news.articles(source);
CREATE INDEX IF NOT EXISTS idx_articles_published_date ON news.articles(published_date DESC);
CREATE INDEX IF NOT EXISTS idx_articles_scraped_at ON news.articles(scraped_at DESC);
CREATE INDEX IF NOT EXISTS idx_articles_session ON news.articles(scraping_session_id);

-- Create updated_at trigger
CREATE OR REPLACE FUNCTION news.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_articles_updated_at
    BEFORE UPDATE ON news.articles
    FOR EACH ROW
    EXECUTE FUNCTION news.update_updated_at_column();
