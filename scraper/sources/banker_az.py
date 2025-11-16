"""
Banker.az news scraper
Scrapes news articles from banker.az
"""

import sys
import os

# Fix encoding for Azerbaijani characters on Windows
if sys.platform == 'win32' and hasattr(sys.stdout, 'buffer'):
    import io
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base_scraper import BaseScraper
from datetime import datetime
from typing import List, Dict, Optional
import re


class BankerAzScraper(BaseScraper):
    """Scraper for banker.az news website"""

    def __init__(self):
        super().__init__(
            source_name="Banker.az",
            base_url="https://banker.az"
        )
        self.category_url = "https://banker.az/category/xYbYrlYr/"

    def scrape_article_list(self, page: int = 1) -> List[str]:
        """
        Scrape article URLs from the category page

        Args:
            page: Page number to scrape

        Returns:
            List of article URLs
        """
        if page == 1:
            url = self.category_url
        else:
            url = f"{self.category_url}page/{page}/"

        soup = self.fetch_page(url)
        if not soup:
            return []

        article_urls = []

        # Find all article containers
        article_containers = soup.select('.td_module_wrap')

        for container in article_containers:
            # Get article link from title
            title_link = container.select_one('h3.entry-title a')
            if title_link and title_link.get('href'):
                article_url = title_link['href']
                article_urls.append(article_url)

        return article_urls

    def scrape_article(self, url: str) -> Optional[Dict]:
        """
        Scrape a single article from banker.az

        Args:
            url: Article URL

        Returns:
            Dictionary with article data
        """
        soup = self.fetch_page(url)
        if not soup:
            return None

        try:
            # Extract title
            title_elem = soup.select_one('h1.tdb-title-text')
            if not title_elem:
                print(f"[ERROR] Could not find title for {url}")
                return None
            title = self.clean_text(title_elem.get_text())

            # Extract date
            date_elem = soup.select_one('time.entry-date')
            published_date = None
            if date_elem and date_elem.get('datetime'):
                date_str = date_elem['datetime']
                try:
                    # Parse datetime (format: 2025-11-12T11:34:35+04:00)
                    published_date = datetime.fromisoformat(date_str.replace('+04:00', '+04:00'))
                except Exception as e:
                    print(f"[WARNING] Could not parse date: {date_str}, error: {e}")

            # Extract content
            content_elem = soup.select_one('.tdb_single_content .tdb-block-inner')
            if not content_elem:
                print(f"[ERROR] Could not find content for {url}")
                return None

            # Remove unwanted elements (ads, scripts, etc.)
            for unwanted in content_elem.select('script, style, .td-a-ad, .adsbygoogle'):
                unwanted.decompose()

            # Get all paragraphs
            paragraphs = content_elem.find_all('p')
            content_parts = []
            for p in paragraphs:
                text = self.clean_text(p.get_text())
                if text and len(text) > 10:  # Only add substantial paragraphs
                    content_parts.append(text)

            content = '\n\n'.join(content_parts)

            if not content:
                print(f"[ERROR] Empty content for {url}")
                return None

            return {
                'title': title,
                'content': content,
                'url': url,
                'published_date': published_date,
                'source': self.source_name,
                'language': 'az'
            }

        except Exception as e:
            print(f"[ERROR] Error scraping article {url}: {e}")
            return None
