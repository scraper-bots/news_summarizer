"""
Async base scraper class for news sources
All async source scrapers should inherit from this class
"""

import aiohttp
import asyncio
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Optional
from abc import ABC, abstractmethod


class BaseScraper(ABC):
    """Abstract base class for async news scrapers"""

    def __init__(self, source_name: str, base_url: str):
        self.source_name = source_name
        self.base_url = base_url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = None
        self.semaphore = asyncio.Semaphore(5)  # Limit concurrent requests

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    async def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """
        Fetch and parse a webpage asynchronously

        Args:
            url: URL to fetch

        Returns:
            BeautifulSoup object or None if failed
        """
        async with self.semaphore:  # Limit concurrent requests
            try:
                if not self.session:
                    self.session = aiohttp.ClientSession(headers=self.headers)

                async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    response.raise_for_status()
                    html = await response.text(encoding='utf-8')
                    return BeautifulSoup(html, 'html.parser')
            except asyncio.TimeoutError:
                print(f"[ERROR] Timeout fetching {url}")
                return None
            except aiohttp.ClientError as e:
                print(f"[ERROR] Client error fetching {url}: {e}")
                return None
            except Exception as e:
                print(f"[ERROR] Error fetching {url}: {e}")
                return None

    @abstractmethod
    async def scrape_article_list(self, page: int = 1) -> List[str]:
        """
        Scrape the list of article URLs from a page

        Args:
            page: Page number to scrape

        Returns:
            List of article URLs
        """
        pass

    @abstractmethod
    async def scrape_article(self, url: str) -> Optional[Dict]:
        """
        Scrape a single article asynchronously

        Args:
            url: Article URL

        Returns:
            Dictionary with article data: {title, content, url, published_date, source, language}
        """
        pass

    async def scrape_articles_batch(self, urls: List[str], batch_size: int = 10) -> List[Dict]:
        """
        Scrape multiple articles concurrently in batches

        Args:
            urls: List of article URLs
            batch_size: Number of articles to scrape concurrently

        Returns:
            List of article dictionaries
        """
        articles = []

        # Process in batches to avoid overwhelming the server
        for i in range(0, len(urls), batch_size):
            batch = urls[i:i + batch_size]
            print(f"[INFO] Scraping batch {i//batch_size + 1}/{(len(urls)-1)//batch_size + 1} ({len(batch)} articles)")

            # Scrape batch concurrently
            tasks = [self.scrape_article(url) for url in batch]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Filter out None and exceptions
            for result in results:
                if isinstance(result, Exception):
                    print(f"[ERROR] Exception during scraping: {result}")
                elif result is not None:
                    articles.append(result)

            # Small delay between batches
            if i + batch_size < len(urls):
                await asyncio.sleep(1)

        return articles

    async def scrape_all(self, num_pages: int = 1, limit_per_page: Optional[int] = None,
                        batch_size: int = 10) -> List[Dict]:
        """
        Scrape all articles from the source asynchronously

        Args:
            num_pages: Number of pages to scrape
            limit_per_page: Maximum number of articles per page
            batch_size: Number of articles to scrape concurrently

        Returns:
            List of article dictionaries
        """
        print(f"Starting async scraper for {self.source_name}...")

        all_article_urls = []

        # Scrape article lists from all pages concurrently
        print(f"[INFO] Fetching article lists from {num_pages} page(s)...")
        list_tasks = [self.scrape_article_list(page=p) for p in range(1, num_pages + 1)]
        list_results = await asyncio.gather(*list_tasks, return_exceptions=True)

        # Collect all URLs
        for i, result in enumerate(list_results, 1):
            if isinstance(result, Exception):
                print(f"[ERROR] Exception fetching page {i}: {result}")
            elif result:
                urls = result[:limit_per_page] if limit_per_page else result
                all_article_urls.extend(urls)
                print(f"[Page {i}] Found {len(urls)} articles")

        if not all_article_urls:
            print(f"[WARNING] No articles found")
            return []

        print(f"[INFO] Total articles to scrape: {len(all_article_urls)}")

        # Scrape all articles in batches
        articles = await self.scrape_articles_batch(all_article_urls, batch_size=batch_size)

        print(f"[SUCCESS] Successfully scraped {len(articles)} articles from {self.source_name}")
        return articles

    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text.strip()

    async def close(self):
        """Close the session"""
        if self.session:
            await self.session.close()
