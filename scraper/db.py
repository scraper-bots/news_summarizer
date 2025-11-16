"""
Database utilities for news scraper
Handles PostgreSQL connections with proper UTF-8 encoding for Azerbaijani characters
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import sql
from datetime import datetime
from typing import Optional, Dict, List
from dotenv import load_dotenv

# Load environment variables from parent directory
import pathlib
env_path = pathlib.Path(__file__).parent.parent / '.env.local'
load_dotenv(env_path)

class Database:
    def __init__(self):
        self.connection_string = os.getenv('DATABASE_URL')
        self.conn = None
        self.cursor = None

    def connect(self):
        """Establish database connection with UTF-8 encoding"""
        try:
            self.conn = psycopg2.connect(
                self.connection_string,
                client_encoding='UTF8'
            )
            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            print("[SUCCESS] Database connected successfully")
            return True
        except Exception as e:
            print(f"[ERROR] Database connection failed: {e}")
            return False

    def close(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
            print("[SUCCESS] Database connection closed")

    def insert_article(self, article: Dict) -> Optional[int]:
        """
        Insert a news article into the database

        Args:
            article: Dictionary with keys: title, content, source, url, published_date

        Returns:
            Article ID if successful, None otherwise
        """
        try:
            query = sql.SQL("""
                INSERT INTO news.articles (title, content, source, url, published_date, language)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (url) DO UPDATE
                SET title = EXCLUDED.title,
                    content = EXCLUDED.content,
                    published_date = EXCLUDED.published_date,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING id
            """)

            self.cursor.execute(query, (
                article.get('title'),
                article.get('content'),
                article.get('source'),
                article.get('url'),
                article.get('published_date'),
                article.get('language', 'az')
            ))

            result = self.cursor.fetchone()
            self.conn.commit()

            article_id = result['id'] if result else None

            # Try to print with title, fallback if console encoding fails
            try:
                print(f"[SUCCESS] Article saved: {article.get('title')[:50]}... (ID: {article_id})")
            except (UnicodeEncodeError, UnicodeDecodeError):
                print(f"[SUCCESS] Article saved (ID: {article_id})")

            return article_id

        except Exception as e:
            try:
                print(f"[ERROR] Error inserting article: {e}")
            except UnicodeEncodeError:
                print(f"[ERROR] Error inserting article (encoding error in message)")
            self.conn.rollback()
            return None

    def bulk_insert_articles(self, articles: List[Dict]) -> int:
        """
        Insert multiple articles in a single transaction

        Args:
            articles: List of article dictionaries

        Returns:
            Number of articles successfully inserted
        """
        inserted_count = 0
        for article in articles:
            if self.insert_article(article):
                inserted_count += 1
        return inserted_count

    def article_exists(self, url: str) -> bool:
        """Check if an article with the given URL already exists"""
        try:
            query = sql.SQL("SELECT id FROM news.articles WHERE url = %s")
            self.cursor.execute(query, (url,))
            return self.cursor.fetchone() is not None
        except Exception as e:
            print(f"[ERROR] Error checking article existence: {e}")
            return False

    def insert_scraping_summary(self, summary_data: Dict) -> Optional[int]:
        """
        Insert a scraping session summary

        Args:
            summary_data: Dictionary with keys:
                - summary: str (comprehensive summary text)
                - articles_count: int (total articles found)
                - sources_count: int (number of sources)
                - new_articles_count: int (new articles saved)
                - scraping_duration_seconds: float (optional)

        Returns:
            Summary ID if successful, None otherwise
        """
        try:
            query = sql.SQL("""
                INSERT INTO news.scraping_summaries
                (summary, articles_count, sources_count, new_articles_count, scraping_duration_seconds)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """)

            self.cursor.execute(query, (
                summary_data.get('summary'),
                summary_data.get('articles_count'),
                summary_data.get('sources_count'),
                summary_data.get('new_articles_count'),
                summary_data.get('scraping_duration_seconds')
            ))

            result = self.cursor.fetchone()
            self.conn.commit()

            summary_id = result['id'] if result else None
            print(f"[SUCCESS] Scraping summary saved (ID: {summary_id})")

            return summary_id

        except Exception as e:
            print(f"[ERROR] Error inserting scraping summary: {e}")
            self.conn.rollback()
            return None

    def get_articles_by_source(self, source: str, limit: int = 10) -> List[Dict]:
        """Retrieve articles from a specific source"""
        try:
            query = sql.SQL("""
                SELECT * FROM news.articles
                WHERE source = %s
                ORDER BY published_date DESC
                LIMIT %s
            """)
            self.cursor.execute(query, (source, limit))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"[ERROR] Error retrieving articles: {e}")
            return []
