"""
APA.az news scraper
Scrapes news articles from apa.az economy section
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


class ApaAzScraper(BaseScraper):
    """Scraper for apa.az news website"""

    def __init__(self):
        super().__init__(
            source_name="APA.az",
            base_url="https://apa.az"
        )
        self.category_url = "https://apa.az/economy"
        # Month mapping for Azerbaijani to numbers
        self.months = {
            'yanvar': 1, 'fevral': 2, 'mart': 3, 'aprel': 4,
            'may': 5, 'iyun': 6, 'iyul': 7, 'avqust': 8,
            'sentyabr': 9, 'oktyabr': 10, 'noyabr': 11, 'dekabr': 12
        }

    def scrape_article_list(self, page: int = 1) -> List[str]:
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

        soup = self.fetch_page(url)
        if not soup:
            return []

        article_urls = []

        # Find all article links with class="item"
        article_links = soup.select('a.item[href]')

        for link in article_links:
            article_url = link.get('href')
            # Only include actual news articles
            # News articles have pattern: https://apa.az/category/title-id
            if article_url and article_url.startswith('http'):
                # Skip non-article pages
                skip_patterns = ['/rates', '/weather-forecast', '/currency', '/jobs']
                if any(pattern in article_url for pattern in skip_patterns):
                    continue

                # Only include URLs with category and article ID (format: category/slug-id)
                # Check if URL has at least one "/" after domain and ends with digits
                url_parts = article_url.replace('https://apa.az/', '').split('/')
                if len(url_parts) >= 2 and url_parts[1]:  # Has category and article slug
                    # Check if article slug ends with a number (article ID)
                    if url_parts[1].split('-')[-1].isdigit():
                        article_urls.append(article_url)

        return article_urls

    def parse_date(self, date_str: str) -> Optional[datetime]:
        """
        Parse Azerbaijani date string to datetime
        Format: "14 noyabr 2025 16:23 (UTC +04:00)" or "14 noyabr 2025"

        Args:
            date_str: Date string in Azerbaijani

        Returns:
            datetime object or None if parsing fails
        """
        try:
            # Clean the string
            date_str = date_str.strip()
            # Remove UTC timezone info if present
            date_str = re.sub(r'\(UTC [+\-]\d{2}:\d{2}\)', '', date_str).strip()

            # Split into parts
            parts = date_str.split()

            if len(parts) >= 3:
                day = int(parts[0])
                month_str = parts[1].lower()
                year = int(parts[2])

                # Get month number
                month = self.months.get(month_str)
                if not month:
                    print(f"[WARNING] Unknown month: {month_str}")
                    return None

                # Parse time if present
                hour = 0
                minute = 0
                if len(parts) >= 4:
                    time_parts = parts[3].split(':')
                    if len(time_parts) >= 2:
                        hour = int(time_parts[0])
                        minute = int(time_parts[1])

                return datetime(year, month, day, hour, minute)

        except Exception as e:
            print(f"[WARNING] Could not parse date '{date_str}': {e}")

        return None

    def scrape_article(self, url: str) -> Optional[Dict]:
        """
        Scrape a single article from apa.az

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
            title_elem = soup.select_one('h2.title_news')
            if not title_elem:
                print(f"[ERROR] Could not find title for {url}")
                return None
            title = self.clean_text(title_elem.get_text())

            # Extract date
            date_elem = soup.select_one('span.date')
            published_date = None
            if date_elem:
                date_text = self.clean_text(date_elem.get_text())
                published_date = self.parse_date(date_text)

            # Extract content
            content_elem = soup.select_one('.texts.mb-site')
            if not content_elem:
                print(f"[ERROR] Could not find content for {url}")
                return None

            # Remove unwanted elements (ads, scripts, etc.)
            for unwanted in content_elem.select('script, style, .rek_banner, .links_block, .AdviadNativeVideo'):
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
