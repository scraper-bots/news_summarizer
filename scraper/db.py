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
                INSERT INTO news.articles (title, content, summary, source, url, published_date, language)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (url) DO UPDATE
                SET title = EXCLUDED.title,
                    content = EXCLUDED.content,
                    summary = EXCLUDED.summary,
                    published_date = EXCLUDED.published_date,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING id
            """)

            self.cursor.execute(query, (
                article.get('title'),
                article.get('content'),
                article.get('summary'),
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
