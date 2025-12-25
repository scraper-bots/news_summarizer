import { Pool } from 'pg';
import { Article, ScrapingSummary } from '@/types';

// Create a connection pool
let pool: Pool | null = null;

function getPool(): Pool {
  if (!pool) {
    pool = new Pool({
      connectionString: process.env.DATABASE_URL,
      ssl: process.env.DATABASE_URL?.includes('localhost') ? false : {
        rejectUnauthorized: false
      },
      max: 20,
      idleTimeoutMillis: 30000,
      connectionTimeoutMillis: 2000,
    });
  }
  return pool;
}

/**
 * Get all scraping summaries ordered by date (newest first)
 */
export async function getSummaries(limit: number = 30): Promise<ScrapingSummary[]> {
  const pool = getPool();

  const query = `
    SELECT
      id,
      scraping_date,
      summary,
      articles_count,
      sources_count,
      new_articles_count,
      scraping_duration_seconds,
      created_at,
      updated_at
    FROM news.scraping_summaries
    WHERE summary IS NOT NULL
      AND summary != 'Scraping in progress...'
      AND summary NOT LIKE '%creation failed%'
      AND summary NOT LIKE 'No new articles%'
      AND summary NOT LIKE '%kifayət qədər xəbər%'
      AND new_articles_count > 0
      AND LENGTH(summary) > 100
    ORDER BY created_at DESC
    LIMIT $1
  `;

  const result = await pool.query(query, [limit]);
  return result.rows;
}

/**
 * Get a single summary by ID
 */
export async function getSummaryById(id: number): Promise<ScrapingSummary | null> {
  const pool = getPool();

  const query = `
    SELECT
      id,
      scraping_date,
      summary,
      articles_count,
      sources_count,
      new_articles_count,
      scraping_duration_seconds,
      created_at,
      updated_at
    FROM news.scraping_summaries
    WHERE id = $1
  `;

  const result = await pool.query(query, [id]);
  return result.rows[0] || null;
}

/**
 * Get articles for a specific scraping session
 */
export async function getArticlesBySessionId(sessionId: number): Promise<Article[]> {
  const pool = getPool();

  const query = `
    SELECT
      id,
      title,
      content,
      source,
      url,
      published_date,
      scraped_at,
      language,
      created_at,
      updated_at,
      scraping_session_id
    FROM news.articles
    WHERE scraping_session_id = $1
    ORDER BY published_date DESC
  `;

  const result = await pool.query(query, [sessionId]);
  return result.rows;
}

/**
 * Get recent articles (for homepage)
 */
export async function getRecentArticles(limit: number = 20): Promise<Article[]> {
  const pool = getPool();

  const query = `
    SELECT
      id,
      title,
      content,
      source,
      url,
      published_date,
      scraped_at,
      language,
      created_at,
      updated_at,
      scraping_session_id
    FROM news.articles
    ORDER BY published_date DESC
    LIMIT $1
  `;

  const result = await pool.query(query, [limit]);
  return result.rows;
}

/**
 * Get statistics
 */
export async function getStats() {
  const pool = getPool();

  const query = `
    SELECT
      COUNT(*) as total_articles,
      COUNT(DISTINCT source) as total_sources,
      MAX(published_date) as latest_article_date
    FROM news.articles
  `;

  const result = await pool.query(query);
  return result.rows[0];
}
