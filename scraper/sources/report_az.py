"""
Report.az scraper - Economy news section
"""

from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Optional
import sys
import os

# Fix encoding for Azerbaijani characters on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base_scraper import BaseScraper


class ReportAzScraper(BaseScraper):
    """Scraper for Report.az economy news"""

    def __init__(self):
        super().__init__(
            source_name="Report.az",
            base_url="https://report.az"
        )
        self.category_url = f"{self.base_url}/iqtisadiyyat-xeberleri"

    def scrape_article_list(self, page: int = 1) -> List[str]:
        """
        Scrape list of article URLs from Report.az economy section

        Args:
            page: Page number (Report.az uses data-page attribute, but we'll scrape first page)

        Returns:
            List of article URLs
        """
        try:
            # Note: Report.az loads additional pages via AJAX, but we'll scrape the initial page
            soup = self.fetch_page(self.category_url)
            if not soup:
                return []

            # Find all article blocks
            article_blocks = soup.find_all('div', class_='index-post-block')

            urls = []
            for block in article_blocks:
                # Find the article link
                link = block.find('a', class_='news__item')
                if link and link.get('href'):
                    # Convert relative URL to absolute
                    article_url = link['href']
                    if article_url.startswith('/'):
                        article_url = self.base_url + article_url

                    urls.append(article_url)

            return urls

        except Exception as e:
            print(f"[ERROR] Failed to scrape article list from {self.source_name}: {e}")
            return []

    def scrape_article(self, url: str) -> Optional[Dict]:
        """
        Scrape individual article from Report.az

        Args:
            url: Article URL

        Returns:
            Dictionary with article data or None if failed
        """
        try:
            soup = self.fetch_page(url)
            if not soup:
                return None

            # Extract title
            title_elem = soup.find('h1', class_='section-title')
            if not title_elem:
                print(f"[WARNING] No title found for {url}")
                return None

            title = self.clean_text(title_elem.get_text())

            # Extract content from news-detail__desc
            content_elem = soup.find('div', class_='news-detail__desc')
            if not content_elem:
                print(f"[WARNING] No content found for {url}")
                return None

            # Get all paragraphs
            paragraphs = content_elem.find_all('p')
            content = ' '.join([self.clean_text(p.get_text()) for p in paragraphs])

            if not content:
                print(f"[WARNING] Empty content for {url}")
                return None

            # Extract published date
            date_elem = soup.find('ul', class_='news__date')
            published_date = None

            if date_elem:
                date_parts = date_elem.find_all('li')
                if len(date_parts) >= 2:
                    # Format: "16 noyabr, 2025" and "14:00"
                    date_str = date_parts[0].get_text().strip()
                    time_str = date_parts[1].get_text().strip()

                    try:
                        # Parse Azerbaijani date format
                        published_date = self.parse_date(f"{date_str} {time_str}")
                    except Exception as e:
                        print(f"[WARNING] Failed to parse date: {e}")

            return {
                'title': title,
                'content': content,
                'source': self.source_name,
                'url': url,
                'published_date': published_date,
                'language': 'az'
            }

        except Exception as e:
            print(f"[ERROR] Failed to scrape article {url}: {e}")
            return None

    def parse_date(self, date_string: str) -> Optional[datetime]:
        """
        Parse Azerbaijani date format from Report.az

        Args:
            date_string: Date string like "16 noyabr, 2025 14:00"

        Returns:
            datetime object or None if parsing fails
        """
        # Month mapping (Azerbaijani to number)
        months = {
            'yanvar': 1, 'fevral': 2, 'mart': 3, 'aprel': 4,
            'may': 5, 'iyun': 6, 'iyul': 7, 'avqust': 8,
            'sentyabr': 9, 'oktyabr': 10, 'noyabr': 11, 'dekabr': 12
        }

        try:
            # Parse: "16 noyabr, 2025 14:00"
            parts = date_string.strip().split()

            if len(parts) >= 3:
                day = int(parts[0])
                month_name = parts[1].replace(',', '').lower()
                year = int(parts[2].replace(',', ''))

                # Get time if available
                hour = 0
                minute = 0
                if len(parts) >= 4:
                    time_parts = parts[3].split(':')
                    hour = int(time_parts[0])
                    if len(time_parts) > 1:
                        minute = int(time_parts[1])

                month = months.get(month_name)
                if month:
                    return datetime(year, month, day, hour, minute)

            return None

        except Exception as e:
            print(f"[WARNING] Date parsing error: {e}")
            return None
