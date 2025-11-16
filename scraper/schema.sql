-- News articles table schema
-- Supports Azerbaijani characters with UTF-8 encoding

CREATE SCHEMA IF NOT EXISTS news;

CREATE TABLE IF NOT EXISTS news.articles (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    summary TEXT,
    source VARCHAR(100) NOT NULL,
    url TEXT NOT NULL UNIQUE,
    published_date TIMESTAMP,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    language VARCHAR(10) DEFAULT 'az',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_articles_source ON news.articles(source);
CREATE INDEX IF NOT EXISTS idx_articles_published_date ON news.articles(published_date DESC);
CREATE INDEX IF NOT EXISTS idx_articles_scraped_at ON news.articles(scraped_at DESC);

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
