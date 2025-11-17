"""
Iqtisadiyyat.az async news scraper
Scrapes news articles from iqtisadiyyat.az using async/await
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


class IqtisadiyyatAzScraper(BaseScraper):
    """Async scraper for iqtisadiyyat.az news website"""

    def __init__(self):
        super().__init__(
            source_name="Iqtisadiyyat.az",
            base_url="https://iqtisadiyyat.az"
        )
        self.categories = [
            "az/category/bank-35",      # Banking
            "az/category/biznes-9",     # Business
            "az/category/maliyye-41"    # Finance
        ]

    async def scrape_article_list(self, page: int = 1, category: str = None) -> List[str]:
        """
        Scrape article URLs from a category page

        Args:
            page: Page number to scrape
            category: Category path (e.g., "az/category/bank-35")

        Returns:
            List of article URLs
        """
        if not category:
            category = self.categories[0]

        # Pagination format: /page/2, /page/3, etc.
        if page == 1:
            url = f"{self.base_url}/{category}"
        else:
            url = f"{self.base_url}/{category}/page/{page}"

        soup = await self.fetch_page(url)
        if not soup:
            return []

        article_urls = []

        # Find all article containers in <div class="news-card-thirteen">
        article_containers = soup.select('div.news-card-thirteen')

        for container in article_containers:
            # Get article link from <a> tag containing <h1 class="smaller-header-h1">
            link = container.find('a')
            if link and link.get('href'):
                article_url = link['href']
                # Make sure it's a full URL
                if not article_url.startswith('http'):
                    article_url = self.base_url + article_url
                article_urls.append(article_url)

        return article_urls

    def parse_date(self, date_str: str) -> Optional[datetime]:
        """
        Parse date from iqtisadiyyat.az format

        Args:
            date_str: Date string (e.g., "14 Noyabr 2025, 18:20")

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
            # Parse format: "14 Noyabr 2025, 18:20"
            # Split by comma to separate date and time
            parts = date_str.strip().split(',')

            if len(parts) >= 2:
                date_part = parts[0].strip()
                time_part = parts[1].strip()

                # Parse date: "14 Noyabr 2025"
                date_components = date_part.split()
                if len(date_components) >= 3:
                    day = int(date_components[0])
                    month_name = date_components[1].lower()
                    year = int(date_components[2])

                    month = months.get(month_name)
                    if not month:
                        print(f"[WARNING] Unknown month: {month_name}")
                        return None

                    # Parse time: "18:20"
                    time_components = time_part.split(':')
                    if len(time_components) >= 2:
                        hour = int(time_components[0])
                        minute = int(time_components[1])

                        return datetime(year, month, day, hour, minute)

            return None

        except Exception as e:
            print(f"[WARNING] Could not parse date: {date_str}, error: {e}")
            return None

    async def scrape_article(self, url: str) -> Optional[Dict]:
        """
        Scrape a single article from iqtisadiyyat.az

        Args:
            url: Article URL

        Returns:
            Dictionary with article data
        """
        soup = await self.fetch_page(url)
        if not soup:
            return None

        try:
            # Extract title from <h1 class="medium-header-h1 post-title">
            title_elem = soup.select_one('h1.medium-header-h1.post-title')
            if not title_elem:
                print(f"[ERROR] Could not find title for {url}")
                return None
            title = self.clean_text(title_elem.get_text())

            # Extract date from <time class="date-badge">
            date_elem = soup.select_one('time.date-badge')
            published_date = None
            if date_elem:
                date_text = date_elem.get_text().strip()
                published_date = self.parse_date(date_text)

            # Extract content from <div class="post-content">
            content_div = soup.select_one('div.post-content')
            if not content_div:
                print(f"[ERROR] Could not find content div for {url}")
                return None

            # Get all paragraphs within the content div
            paragraphs = content_div.find_all('p')
            content_parts = []

            for p in paragraphs:
                # Skip if paragraph contains only links or images
                text = self.clean_text(p.get_text())
                if text and len(text) > 20:  # Only add substantial paragraphs
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
