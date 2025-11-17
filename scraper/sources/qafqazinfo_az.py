"""
Qafqazinfo.az async news scraper
Scrapes news articles from qafqazinfo.az economy section using async/await
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


class QafqazinfoAzScraper(BaseScraper):
    """Async scraper for qafqazinfo.az news website"""

    def __init__(self):
        super().__init__(
            source_name="Qafqazinfo.az",
            base_url="https://qafqazinfo.az"
        )
        self.category_url = "https://qafqazinfo.az/news/category/iqtisadiyyat-4"
        # Month mapping for Azerbaijani to numbers
        self.months = {
            'yanvar': 1, 'fevral': 2, 'mart': 3, 'aprel': 4,
            'may': 5, 'iyun': 6, 'iyul': 7, 'avqust': 8,
            'sentyabr': 9, 'oktyabr': 10, 'noyabr': 11, 'dekabr': 12
        }

    async def scrape_article_list(self, page: int = 1) -> List[str]:
        """
        Scrape article URLs from the economy category page

        Args:
            page: Page number to scrape

        Returns:
            List of article URLs
        """
        if page == 1:
            url = self.category_url
        else:
            url = f"{self.category_url}?page={page}"

        soup = await self.fetch_page(url)
        if not soup:
            return []

        article_urls = []

        # Find all article links - they're in <a> tags with href containing "/news/detail/"
        article_links = soup.select('a[href*="/news/detail/"]')

        for link in article_links:
            article_url = link.get('href')
            if article_url:
                # Make absolute URL if relative
                if article_url.startswith('/'):
                    article_url = self.base_url + article_url

                # Only add if it's a valid article URL and not already in list
                if article_url.startswith('https://qafqazinfo.az/news/detail/') and article_url not in article_urls:
                    article_urls.append(article_url)

        return article_urls

    def parse_date(self, date_str: str) -> Optional[datetime]:
        """
        Parse date string to datetime
        Format: "09.11.2025 | 10:59" or similar

        Args:
            date_str: Date string

        Returns:
            datetime object or None if parsing fails
        """
        try:
            # Clean the string
            date_str = date_str.strip()

            # Format is typically: "09.11.2025 | 10:59"
            # Remove the pipe and extra spaces
            date_str = date_str.replace('|', '').strip()

            # Split into date and time parts
            parts = date_str.split()

            if len(parts) >= 1:
                # Parse date part (DD.MM.YYYY)
                date_parts = parts[0].split('.')
                if len(date_parts) == 3:
                    day = int(date_parts[0])
                    month = int(date_parts[1])
                    year = int(date_parts[2])

                    # Parse time if present
                    hour = 0
                    minute = 0
                    if len(parts) >= 2:
                        time_parts = parts[1].split(':')
                        if len(time_parts) >= 2:
                            hour = int(time_parts[0])
                            minute = int(time_parts[1])

                    return datetime(year, month, day, hour, minute)

        except Exception as e:
            print(f"[WARNING] Could not parse date '{date_str}': {e}")

        return None

    async def scrape_article(self, url: str) -> Optional[Dict]:
        """
        Scrape a single article from qafqazinfo.az asynchronously

        Args:
            url: Article URL

        Returns:
            Dictionary with article data
        """
        soup = await self.fetch_page(url)
        if not soup:
            return None

        try:
            # Extract title - it's in <h1> with style="font-size: 32px;"
            title_elem = soup.select_one('.panel-body h1[style*="font-size: 32px"]')
            if not title_elem:
                # Try alternative selector
                title_elem = soup.select_one('.panel.panel-default.news .panel-body h1')
            if not title_elem:
                print(f"[ERROR] Could not find title for {url}")
                return None

            title = self.clean_text(title_elem.get_text())
            # Remove the "- Foto", "- Fotolar", etc. suffix if present
            title = re.sub(r'\s*-\s*(Foto|Fotolar|Video)\s*$', '', title, flags=re.IGNORECASE)

            # Extract date - it's in <time> tag
            date_elem = soup.select_one('time[datetime]')
            published_date = None
            if date_elem:
                date_text = self.clean_text(date_elem.get_text())
                published_date = self.parse_date(date_text)

            # Extract content - it's in <div class="panel-body news_text">
            content_elem = soup.select_one('.panel-body.news_text')
            if not content_elem:
                print(f"[ERROR] Could not find content for {url}")
                return None

            # Remove unwanted elements (ads, scripts, etc.)
            for unwanted in content_elem.select('script, style, .rek_banner'):
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
            import traceback
            traceback.print_exc()
            return None
