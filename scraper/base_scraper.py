"""
Base scraper class for news sources
All source scrapers should inherit from this class
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Optional
from abc import ABC, abstractmethod

class BaseScraper(ABC):
    """Abstract base class for news scrapers"""

    def __init__(self, source_name: str, base_url: str):
        self.source_name = source_name
        self.base_url = base_url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """
        Fetch and parse a webpage

        Args:
            url: URL to fetch

        Returns:
            BeautifulSoup object or None if failed
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.encoding = 'utf-8'  # Ensure UTF-8 encoding for Azerbaijani characters
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            print(f"[ERROR] Error fetching {url}: {e}")
            return None

    @abstractmethod
    def scrape_article_list(self) -> List[str]:
        """
        Scrape the list of article URLs from the main page

        Returns:
            List of article URLs
        """
        pass

    @abstractmethod
    def scrape_article(self, url: str) -> Optional[Dict]:
        """
        Scrape a single article

        Args:
            url: Article URL

        Returns:
            Dictionary with article data: {title, content, url, published_date, source, language}
        """
        pass

    def scrape_all(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Scrape all articles from the source

        Args:
            limit: Maximum number of articles to scrape

        Returns:
            List of article dictionaries
        """
        print(f"Starting scraper for {self.source_name}...")

        # Get article URLs
        article_urls = self.scrape_article_list()

        if limit:
            article_urls = article_urls[:limit]

        print(f"Found {len(article_urls)} articles to scrape")

        # Scrape each article
        articles = []
        for i, url in enumerate(article_urls, 1):
            print(f"Scraping article {i}/{len(article_urls)}: {url}")
            article = self.scrape_article(url)
            if article:
                articles.append(article)

        print(f"[SUCCESS] Successfully scraped {len(articles)} articles from {self.source_name}")
        return articles

    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text.strip()
