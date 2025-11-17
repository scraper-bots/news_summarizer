"""
Trend.az async news scraper
Scrapes news articles from az.trend.az using async/await
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


class TrendAzScraper(BaseScraper):
    """Async scraper for az.trend.az news website"""

    def __init__(self):
        super().__init__(
            source_name="Trend.az",
            base_url="https://az.trend.az"
        )
        self.category_url = "https://az.trend.az/business/"

    async def scrape_article_list(self, page: int = 1) -> List[str]:
        """
        Scrape article URLs from the business page

        Args:
            page: Page number to scrape

        Returns:
            List of article URLs
        """
        # Trend.az uses timestamp-based pagination
        # For now, we'll scrape the main page (page 1)
        # Pagination can be added later if needed
        url = self.category_url

        soup = await self.fetch_page(url)
        if not soup:
            return []

        article_urls = []

        # Find all article containers in <ul class="news-list with-images">
        news_list = soup.select_one('ul.news-list.with-images')
        if not news_list:
            print(f"[WARNING] Could not find news list container")
            return []

        # Find all <li> items with <a> links
        list_items = news_list.find_all('li')

        for item in list_items:
            # Get article link
            link = item.find('a')
            if link and link.get('href'):
                article_url = link['href']
                # Make sure it's a full URL
                if not article_url.startswith('http'):
                    article_url = self.base_url + article_url
                article_urls.append(article_url)

        return article_urls

    def parse_date(self, date_str: str) -> Optional[datetime]:
        """
        Parse date from trend.az format

        Args:
            date_str: Date string (e.g., "15 Noyabr 10:31 (UTC+04)")

        Returns:
            datetime object or None
        """
        # Month mapping (Azerbaijani to number)
        months = {
            'yanvar': 1, 'fevral': 2, 'mart': 3, 'aprel': 4,
            'may': 5, 'iyun': 6, 'iyul': 7, 'avqust': 8,
            'sentyabr': 9, 'oktyabr': 10, 'noyabr': 11, 'dekabr': 12
        }

        try:
            # Parse format: "15 Noyabr 10:31 (UTC+04)"
            # Remove timezone info
            date_str = date_str.replace('(UTC+04)', '').strip()

            parts = date_str.split()
            if len(parts) >= 3:
                day = int(parts[0])
                month_name = parts[1].lower()
                time_str = parts[2]

                # Get current year (trend.az doesn't show year in list)
                year = datetime.now().year

                month = months.get(month_name)
                if not month:
                    print(f"[WARNING] Unknown month: {month_name}")
                    return None

                # Parse time: "10:31"
                time_parts = time_str.split(':')
                if len(time_parts) >= 2:
                    hour = int(time_parts[0])
                    minute = int(time_parts[1])

                    return datetime(year, month, day, hour, minute)

            return None

        except Exception as e:
            print(f"[WARNING] Could not parse date: {date_str}, error: {e}")
            return None

    async def scrape_article(self, url: str) -> Optional[Dict]:
        """
        Scrape a single article from trend.az

        Args:
            url: Article URL

        Returns:
            Dictionary with article data
        """
        soup = await self.fetch_page(url)
        if not soup:
            return None

        try:
            # Extract title from <h1> tag
            title_elem = soup.find('h1')
            if not title_elem:
                print(f"[ERROR] Could not find title for {url}")
                return None
            title = self.clean_text(title_elem.get_text())

            # Extract date from meta tag or date element
            published_date = None
            # Try to find date in meta tags
            date_meta = soup.find('meta', property='article:published_time')
            if date_meta and date_meta.get('content'):
                try:
                    # Parse ISO format: "2025-11-14T17:57:00+04:00"
                    date_str = date_meta['content']
                    published_date = datetime.fromisoformat(date_str.replace('+04:00', ''))
                except Exception:
                    pass

            # If meta tag not found, try to find date in article
            if not published_date:
                date_elem = soup.select_one('span.date-time')
                if date_elem:
                    date_text = date_elem.get_text().strip()
                    published_date = self.parse_date(date_text)

            # Extract content from <div class="article-content article-paddings">
            content_div = soup.select_one('div.article-content.article-paddings')
            if not content_div:
                print(f"[ERROR] Could not find content div for {url}")
                return None

            # Get all paragraphs within the content div
            paragraphs = content_div.find_all('p')
            content_parts = []

            for p in paragraphs:
                # Skip if paragraph contains only links, images, or scripts
                text = self.clean_text(p.get_text())
                if text and len(text) > 20:  # Only add substantial paragraphs
                    # Skip promotional text like "Bakı. Trend:" at the beginning
                    if text.startswith('Bakı. Trend:'):
                        continue
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
