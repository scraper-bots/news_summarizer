"""
Marja.az news scraper
Scrapes news articles from marja.az
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


class MarjaAzScraper(BaseScraper):
    """Scraper for marja.az news website"""

    def __init__(self):
        super().__init__(
            source_name="Marja.az",
            base_url="https://marja.az"
        )
        self.category_url = "https://marja.az/bank-kredit/12"

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
            url = f"{self.category_url}?page={page}"

        soup = self.fetch_page(url)
        if not soup:
            return []

        article_urls = []

        # Find all article containers
        article_containers = soup.select('figure.snip1208')

        for container in article_containers:
            # Get article link (first <a> tag in figure)
            link = container.find('a')
            if link and link.get('href'):
                article_url = link['href']
                # Make sure it's a full URL
                if not article_url.startswith('http'):
                    article_url = self.base_url + article_url
                article_urls.append(article_url)

        return article_urls

    def parse_date(self, date_str: str, time_str: str) -> Optional[datetime]:
        """
        Parse date and time from marja.az format

        Args:
            date_str: Date string (e.g., "29.10.2025")
            time_str: Time string (e.g., "13:46")

        Returns:
            datetime object or None
        """
        try:
            # Combine date and time
            datetime_str = f"{date_str} {time_str}"
            # Parse format: DD.MM.YYYY HH:MM
            return datetime.strptime(datetime_str, "%d.%m.%Y %H:%M")
        except Exception as e:
            print(f"[WARNING] Could not parse date: {date_str} {time_str}, error: {e}")
            return None

    def scrape_article(self, url: str) -> Optional[Dict]:
        """
        Scrape a single article from marja.az

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
            title_elem = soup.select_one('div.news-head h2')
            if not title_elem:
                print(f"[ERROR] Could not find title for {url}")
                return None
            title = self.clean_text(title_elem.get_text())

            # Extract date and time
            date_elems = soup.select('div.news-date small')
            published_date = None

            if len(date_elems) >= 2:
                # First small has date with icon, second has time
                date_text = date_elems[0].get_text().strip()
                time_text = date_elems[1].get_text().strip()

                # Remove icon from date text
                date_text = date_text.replace('', '').strip()

                published_date = self.parse_date(date_text, time_text)

            # Extract content
            content_elem = soup.select_one('div.content-news')
            if not content_elem:
                print(f"[ERROR] Could not find content for {url}")
                return None

            # Remove unwanted elements (ads, scripts, etc.)
            for unwanted in content_elem.select('script, style, iframe, .middle-single, a.text-link-underline'):
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
