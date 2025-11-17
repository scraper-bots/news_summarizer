"""
Fed.az async news scraper
Scrapes news articles from fed.az across multiple categories using async/await
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


class FedAzScraper(BaseScraper):
    """Async scraper for fed.az news website"""

    def __init__(self):
        super().__init__(
            source_name="Fed.az",
            base_url="https://fed.az"
        )
        # Multiple categories for comprehensive coverage
        self.categories = [
            "az/maliyye",  # Finance
            "az/iqtisadiyyat",  # Economy
            "az/xaricde-emlak"  # Foreign real estate
        ]

    async def scrape_article_list(self, page: int = 1, category: str = None) -> List[str]:
        """
        Scrape article URLs from a category page

        Args:
            page: Page number to scrape
            category: Category path (e.g., "az/maliyye"). If None, uses first category.

        Returns:
            List of article URLs
        """
        if category is None:
            category = self.categories[0]

        # Build URL with pagination
        if page == 1:
            url = f"{self.base_url}/{category}"
        else:
            url = f"{self.base_url}/{category}/{page}"

        soup = await self.fetch_page(url)
        if not soup:
            return []

        article_urls = []

        # Find all article containers in the news list
        # Articles are in <div class="news"> blocks within <div class="row news-list">
        news_containers = soup.select('div.news')

        for container in news_containers:
            # Get article link (direct <a> child)
            link = container.find('a')
            if link and link.get('href'):
                article_url = link['href']
                # Make sure it's a full URL
                if not article_url.startswith('http'):
                    article_url = self.base_url + '/' + article_url.lstrip('/')
                article_urls.append(article_url)

        return article_urls

    async def scrape_all_categories(self, num_pages: int = 1) -> List[str]:
        """
        Scrape articles from all categories

        Args:
            num_pages: Number of pages to scrape per category

        Returns:
            List of all article URLs from all categories
        """
        all_urls = []
        for category in self.categories:
            print(f"[INFO] Scraping {category}...")
            for page in range(1, num_pages + 1):
                urls = await self.scrape_article_list(page=page, category=category)
                all_urls.extend(urls)
                print(f"[INFO] Found {len(urls)} articles on page {page} of {category}")

        return all_urls

    def parse_date(self, date_str: str, time_str: str = None) -> Optional[datetime]:
        """
        Parse date and time from fed.az format

        Args:
            date_str: Date string (e.g., "15 Noy 2025")
            time_str: Time string (e.g., "12:44")

        Returns:
            datetime object or None
        """
        # Month mapping (Azerbaijani abbreviated to number)
        months_short = {
            'yan': 1, 'fev': 2, 'mar': 3, 'apr': 4,
            'may': 5, 'iyn': 6, 'iyl': 7, 'avq': 8,
            'sen': 9, 'okt': 10, 'noy': 11, 'dek': 12
        }

        # Full month names
        months_full = {
            'yanvar': 1, 'fevral': 2, 'mart': 3, 'aprel': 4,
            'may': 5, 'iyun': 6, 'iyul': 7, 'avqust': 8,
            'sentyabr': 9, 'oktyabr': 10, 'noyabr': 11, 'dekabr': 12
        }

        try:
            # Parse format: "15 Noy 2025" or "15 Noyabr 2025"
            parts = date_str.strip().split()

            if len(parts) >= 3:
                day = int(parts[0])
                month_name = parts[1].lower()
                year = int(parts[2])

                # Try short month names first, then full
                month = months_short.get(month_name)
                if not month:
                    month = months_full.get(month_name)

                if not month:
                    print(f"[WARNING] Unknown month: {month_name}")
                    return None

                # Parse time if provided
                hour = 0
                minute = 0
                if time_str:
                    time_parts = time_str.strip().split(':')
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
        Scrape a single article from fed.az

        Args:
            url: Article URL

        Returns:
            Dictionary with article data
        """
        soup = await self.fetch_page(url)
        if not soup:
            return None

        try:
            # Extract title from <h3 class="news-head">
            title_elem = soup.select_one('h3.news-head')
            if not title_elem:
                print(f"[ERROR] Could not find title for {url}")
                return None
            title = self.clean_text(title_elem.get_text())

            # Extract date and time from news-detail spans
            published_date = None
            date_container = soup.select_one('div.news-detail')

            if date_container:
                # Find date span: <span class="time date">
                date_elem = date_container.select_one('span.time.date')
                # Find time span: <span class="time"> (without date class)
                time_elem = date_container.select_one('span.time:not(.date)')

                if date_elem:
                    date_text = date_elem.get_text().strip()
                    # Remove calendar icon if present
                    date_text = re.sub(r'^\s*\S+\s+', '', date_text)  # Remove leading icon

                    time_text = None
                    if time_elem:
                        time_text = time_elem.get_text().strip()
                        # Remove clock icon if present
                        time_text = re.sub(r'^\s*\S+\s+', '', time_text)

                    published_date = self.parse_date(date_text, time_text)

            # Extract content from <div class="news-text" itemprop="articleBody">
            content_elem = soup.select_one('div.news-text[itemprop="articleBody"]')
            if not content_elem:
                # Try alternative selector
                content_elem = soup.select_one('div.news-text')

            if not content_elem:
                print(f"[ERROR] Could not find content for {url}")
                return None

            # Remove unwanted elements (ads, scripts, etc.)
            for unwanted in content_elem.select('script, style, iframe, ins, .ainsyndicationid'):
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
