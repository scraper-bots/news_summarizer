"""
Sonxeber.az async news scraper
Scrapes news articles from sonxeber.az using async/await
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


class SonxeberAzScraper(BaseScraper):
    """Async scraper for sonxeber.az news website"""

    def __init__(self):
        super().__init__(
            source_name="Sonxeber.az",
            base_url="https://sonxeber.az"
        )
        self.category_url = "https://sonxeber.az/iqtisadiyyat-xeberleri/"

    async def scrape_article_list(self, page: int = 1) -> List[str]:
        """
        Scrape article URLs from the category page

        Args:
            page: Page number to scrape (pagination uses start parameter)

        Returns:
            List of article URLs
        """
        # Pagination format: ?start=0, ?start=1, ?start=2, etc.
        # Page 1 = start=0, Page 2 = start=1, etc.
        if page == 1:
            url = self.category_url
        else:
            start = page - 1
            url = f"{self.category_url}?start={start}"

        soup = await self.fetch_page(url)
        if not soup:
            return []

        article_urls = []

        # Find all article containers in <div class="newslister clearfix">
        news_container = soup.select_one('div.newslister.clearfix')
        if not news_container:
            print(f"[WARNING] Could not find news container")
            return []

        # Find all articles in <div class="nart artbig">
        article_containers = news_container.select('div.nart.artbig')

        for container in article_containers:
            # Get article link (first <a> tag in container)
            link = container.find('a', class_='thumb_zoom')
            if link and link.get('href'):
                article_url = link['href']
                # Make sure it's a full URL
                if not article_url.startswith('http'):
                    article_url = self.base_url + article_url
                article_urls.append(article_url)

        return article_urls

    def parse_date(self, date_str: str) -> Optional[datetime]:
        """
        Parse date from sonxeber.az format

        Args:
            date_str: Date string (e.g., "28 oktyabr" or "28 oktyabr 2025")

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
            # Parse format: "28 oktyabr" or "28 oktyabr 2025"
            parts = date_str.strip().split()

            if len(parts) >= 2:
                day = int(parts[0])
                month_name = parts[1].lower()

                # Get year if provided, otherwise use current year
                if len(parts) >= 3:
                    year = int(parts[2])
                else:
                    year = datetime.now().year

                month = months.get(month_name)
                if not month:
                    print(f"[WARNING] Unknown month: {month_name}")
                    return None

                return datetime(year, month, day)

            return None

        except Exception as e:
            print(f"[WARNING] Could not parse date: {date_str}, error: {e}")
            return None

    async def scrape_article(self, url: str) -> Optional[Dict]:
        """
        Scrape a single article from sonxeber.az

        Args:
            url: Article URL

        Returns:
            Dictionary with article data
        """
        soup = await self.fetch_page(url)
        if not soup:
            return None

        try:
            # Extract title from <article><h1>
            article_tag = soup.find('article')
            if not article_tag:
                print(f"[ERROR] Could not find article tag for {url}")
                return None

            title_elem = article_tag.find('h1')
            if not title_elem:
                print(f"[ERROR] Could not find title for {url}")
                return None
            title = self.clean_text(title_elem.get_text())

            # Extract date from <span class="dttime">
            date_elem = soup.select_one('span.dttime')
            published_date = None
            if date_elem:
                date_text = date_elem.get_text().strip()
                published_date = self.parse_date(date_text)

            # Extract content from <article> <p> tags
            # Get all paragraphs within the article tag
            paragraphs = article_tag.find_all('p')
            content_parts = []

            for p in paragraphs:
                # Skip if paragraph contains only links or images
                text = self.clean_text(p.get_text())
                if text and len(text) > 20:  # Only add substantial paragraphs
                    # Skip promotional text
                    if 'Modern.az' in text or 'xəbər verir ki' in text:
                        # Keep the actual content after "xəbər verir ki"
                        if 'xəbər verir ki,' in text:
                            parts = text.split('xəbər verir ki,', 1)
                            if len(parts) > 1 and len(parts[1].strip()) > 20:
                                content_parts.append(parts[1].strip())
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
