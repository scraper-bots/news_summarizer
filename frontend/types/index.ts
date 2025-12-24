// Database types
export interface Article {
  id: number;
  title: string;
  content: string;
  source: string;
  url: string;
  published_date: string;
  scraped_at: string;
  language: string;
  created_at: string;
  updated_at: string;
  scraping_session_id: number | null;
}

export interface ScrapingSummary {
  id: number;
  scraping_date: string;
  summary: string;
  articles_count: number;
  sources_count: number;
  new_articles_count: number;
  scraping_duration_seconds: number | null;
  created_at: string;
  updated_at: string;
}

export interface SummaryWithArticles extends ScrapingSummary {
  articles: Article[];
}
