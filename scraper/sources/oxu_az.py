"""
Oxu.az async news scraper
Scrapes news articles from oxu.az economy section using async/await
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


class OxuAzScraper(BaseScraper):
    """Async scraper for oxu.az news website"""

    def __init__(self):
        super().__init__(
            source_name="Oxu.az",
            base_url="https://oxu.az"
        )
        self.category_url = "https://oxu.az/iqtisadiyyat"
        # Update headers to avoid being blocked
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'az,en-US;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://oxu.az/',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        }
        # Month mapping for Azerbaijani to numbers (both full and short forms)
        self.months = {
            'yanvar': 1, 'yan': 1,
            'fevral': 2, 'fev': 2,
            'mart': 3, 'mar': 3,
            'aprel': 4, 'apr': 4,
            'may': 5,
            'iyun': 6, 'iyn': 6,
            'iyul': 7, 'iyl': 7,
            'avqust': 8, 'avq': 8,
            'sentyabr': 9, 'sen': 9,
            'oktyabr': 10, 'okt': 10,
            'noyabr': 11, 'noy': 11,
            'dekabr': 12, 'dek': 12
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
            url = f"{self.category_url}/page/{page}"

        soup = await self.fetch_page(url)
        if not soup:
            return []

        article_urls = []

        # Find all article items with data-url attribute
        article_items = soup.select('.post-item.rt-news-item[data-url]')

        for item in article_items:
            article_url = item.get('data-url')
            if article_url and article_url.startswith('https://oxu.az/'):
                # Only include economy category articles
                if '/iqtisadiyyat/' in article_url and article_url not in article_urls:
                    article_urls.append(article_url)

        # Also check for article links in case data-url is not present
        if not article_urls:
            article_links = soup.select('.post-item a[href*="/iqtisadiyyat/"]')
            for link in article_links:
                href = link.get('href')
                if href:
                    if href.startswith('/'):
                        article_url = self.base_url + href
                    elif href.startswith('http'):
                        article_url = href
                    else:
                        continue

                    if article_url not in article_urls and '/iqtisadiyyat/' in article_url:
                        article_urls.append(article_url)

        return article_urls

    def parse_date(self, date_str: str) -> Optional[datetime]:
        """
        Parse Azerbaijani date string to datetime
        Format: "15 noyabr, 2025 / 19:44", "15 noy, 2025 / 19:44", "Bu gün / 12:18", "Dünən / 22:30"

        Args:
            date_str: Date string in Azerbaijani

        Returns:
            datetime object or None if parsing fails
        """
        try:
            from datetime import timedelta

            # Clean the string
            date_str = date_str.strip()

            # Split by "/" to separate date and time
            parts = date_str.split('/')
            if len(parts) < 2:
                return None

            date_part = parts[0].strip().lower()
            time_part = parts[1].strip()

            # Parse time: "19:44"
            time_components = time_part.split(':')
            hour = 0
            minute = 0
            if len(time_components) >= 2:
                hour = int(time_components[0])
                minute = int(time_components[1])

            # Handle relative dates
            today = datetime.now()

            if date_part == 'bu gün' or date_part == 'bu gun':  # Today
                return datetime(today.year, today.month, today.day, hour, minute)

            elif date_part == 'dünən' or date_part == 'dunen':  # Yesterday
                yesterday = today - timedelta(days=1)
                return datetime(yesterday.year, yesterday.month, yesterday.day, hour, minute)

            # Parse absolute date: "15 noyabr, 2025" or "15 noy, 2025"
            date_components = date_part.replace(',', '').split()

            if len(date_components) >= 3:
                day = int(date_components[0])
                month_str = date_components[1]
                year = int(date_components[2])

                # Get month number
                month = self.months.get(month_str)
                if not month:
                    print(f"[WARNING] Unknown month: {month_str}")
                    return None

                return datetime(year, month, day, hour, minute)

        except Exception as e:
            print(f"[WARNING] Could not parse date '{date_str}': {e}")

        return None

    async def scrape_article(self, url: str) -> Optional[Dict]:
        """
        Scrape a single article from oxu.az asynchronously

        Args:
            url: Article URL

        Returns:
            Dictionary with article data
        """
        soup = await self.fetch_page(url)
        if not soup:
            return None

        try:
            # Extract title from h1 in .post-detail-title
            title_elem = soup.select_one('.post-detail-title h1')
            if not title_elem:
                print(f"[ERROR] Could not find title for {url}")
                return None
            title = self.clean_text(title_elem.get_text())

            # Extract date from .post-detail-meta
            date_elem = soup.select_one('.post-detail-meta span')
            published_date = None
            if date_elem:
                date_text = self.clean_text(date_elem.get_text())
                published_date = self.parse_date(date_text)

            # Extract content from .post-detail-content-inner.resize-area
            content_elem = soup.select_one('.post-detail-content-inner.resize-area')
            if not content_elem:
                # Try alternative selector
                content_elem = soup.select_one('.post-detail-content')

            if not content_elem:
                print(f"[ERROR] Could not find content for {url}")
                return None

            # Remove unwanted elements
            for unwanted in content_elem.select('script, style, .audio-block, .player-area, .tag-area, .social-block2, .subscribe-single-block, .tag-post-list, ins'):
                unwanted.decompose()

            # Get all paragraphs
            paragraphs = content_elem.find_all('p')
            content_parts = []
            for p in paragraphs:
                text = self.clean_text(p.get_text())
                # Filter out short paragraphs and common unwanted text
                if text and len(text) > 20:
                    # Skip common unwanted patterns
                    if not any(skip in text.lower() for skip in ['newmedia', 'reklam', 'advertisement']):
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
