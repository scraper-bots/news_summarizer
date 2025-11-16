"""
Main scraper script
Runs all news source scrapers and saves articles to database
"""

import sys
import os
from datetime import datetime
from typing import Dict

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db import Database
from sources.banker_az import BankerAzScraper
from sources.marja_az import MarjaAzScraper
from telegram import TelegramReporter


def scrape_banker_az(db: Database, num_pages: int = 2, limit_per_page: int = 10) -> Dict:
    """
    Scrape articles from Banker.az

    Args:
        db: Database instance
        num_pages: Number of pages to scrape
        limit_per_page: Maximum articles per page

    Returns:
        Dictionary with scraping statistics
    """
    print("\n" + "=" * 60)
    print("SCRAPING BANKER.AZ")
    print("=" * 60)

    scraper = BankerAzScraper()
    total_found = 0
    total_scraped = 0
    total_saved = 0
    total_skipped = 0

    for page in range(1, num_pages + 1):
        print(f"\n[Page {page}] Fetching article list...")

        # Get article URLs from this page
        article_urls = scraper.scrape_article_list(page=page)

        if not article_urls:
            print(f"[Page {page}] No articles found")
            break

        # Limit articles per page
        article_urls = article_urls[:limit_per_page]
        total_found += len(article_urls)
        print(f"[Page {page}] Found {len(article_urls)} articles")

        # Scrape each article
        for i, url in enumerate(article_urls, 1):
            print(f"\n[{i}/{len(article_urls)}] Scraping: {url}")

            # Check if article already exists
            if db.article_exists(url):
                print(f"[SKIP] Article already exists in database")
                total_skipped += 1
                continue

            # Scrape article
            article = scraper.scrape_article(url)

            if article:
                total_scraped += 1

                # Save to database
                article_id = db.insert_article(article)
                if article_id:
                    total_saved += 1

    print("\n" + "=" * 60)
    print(f"BANKER.AZ SUMMARY")
    print(f"Total found: {total_found}")
    print(f"Total scraped: {total_scraped}")
    print(f"Total saved to DB: {total_saved}")
    print(f"Total skipped: {total_skipped}")
    print("=" * 60)

    return {
        'name': 'Banker.az',
        'total': total_found,
        'scraped': total_scraped,
        'saved': total_saved,
        'skipped': total_skipped
    }


def scrape_marja_az(db: Database, num_pages: int = 2, limit_per_page: int = 10) -> Dict:
    """
    Scrape articles from Marja.az

    Args:
        db: Database instance
        num_pages: Number of pages to scrape
        limit_per_page: Maximum articles per page

    Returns:
        Dictionary with scraping statistics
    """
    print("\n" + "=" * 60)
    print("SCRAPING MARJA.AZ")
    print("=" * 60)

    scraper = MarjaAzScraper()
    total_found = 0
    total_scraped = 0
    total_saved = 0
    total_skipped = 0

    for page in range(1, num_pages + 1):
        print(f"\n[Page {page}] Fetching article list...")

        # Get article URLs from this page
        article_urls = scraper.scrape_article_list(page=page)

        if not article_urls:
            print(f"[Page {page}] No articles found")
            break

        # Limit articles per page
        article_urls = article_urls[:limit_per_page]
        total_found += len(article_urls)
        print(f"[Page {page}] Found {len(article_urls)} articles")

        # Scrape each article
        for i, url in enumerate(article_urls, 1):
            print(f"\n[{i}/{len(article_urls)}] Scraping: {url}")

            # Check if article already exists
            if db.article_exists(url):
                print(f"[SKIP] Article already exists in database")
                total_skipped += 1
                continue

            # Scrape article
            article = scraper.scrape_article(url)

            if article:
                total_scraped += 1

                # Save to database
                article_id = db.insert_article(article)
                if article_id:
                    total_saved += 1

    print("\n" + "=" * 60)
    print(f"MARJA.AZ SUMMARY")
    print(f"Total found: {total_found}")
    print(f"Total scraped: {total_scraped}")
    print(f"Total saved to DB: {total_saved}")
    print(f"Total skipped: {total_skipped}")
    print("=" * 60)

    return {
        'name': 'Marja.az',
        'total': total_found,
        'scraped': total_scraped,
        'saved': total_saved,
        'skipped': total_skipped
    }


def main():
    """Main function to run all scrapers"""
    print("\n" + "=" * 60)
    print("NEWS SCRAPER STARTED")
    print("=" * 60)

    # Initialize Telegram reporter
    telegram = TelegramReporter()

    # Track overall statistics
    start_time = datetime.utcnow()
    sources_stats = []
    errors = []

    # Send start notification
    telegram.send_start_notification(num_sources=2)

    # Initialize database connection
    db = Database()

    if not db.connect():
        error_msg = "Failed to connect to database"
        print(f"[ERROR] {error_msg}")
        telegram.send_error_alert(error_msg)
        return

    try:
        # Scrape Banker.az - 2 pages, all articles
        banker_stats = scrape_banker_az(db, num_pages=2, limit_per_page=999)
        sources_stats.append(banker_stats)

        # Scrape Marja.az - 2 pages, all articles
        marja_stats = scrape_marja_az(db, num_pages=2, limit_per_page=999)
        sources_stats.append(marja_stats)

        # Add more scrapers here as you build them
        # scrape_other_source(db, num_pages=2, limit_per_page=10)

    except KeyboardInterrupt:
        print("\n\n[INFO] Scraping interrupted by user")
        errors.append("Scraping interrupted by user")

    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print(f"\n[ERROR] {error_msg}")
        errors.append(error_msg)
        telegram.send_error_alert(error_msg)
        import traceback
        traceback.print_exc()

    finally:
        # Close database connection
        db.close()

        end_time = datetime.utcnow()

        print("\n" + "=" * 60)
        print("NEWS SCRAPER COMPLETED")
        print("=" * 60)

        # Calculate totals
        total_found = sum(s['total'] for s in sources_stats)
        total_scraped = sum(s['scraped'] for s in sources_stats)
        total_saved = sum(s['saved'] for s in sources_stats)
        total_skipped = sum(s['skipped'] for s in sources_stats)

        # Send Telegram report
        report_stats = {
            'start_time': start_time,
            'end_time': end_time,
            'sources': sources_stats,
            'total_found': total_found,
            'total_scraped': total_scraped,
            'total_saved': total_saved,
            'total_skipped': total_skipped,
            'errors': errors
        }

        telegram.send_scraping_report(report_stats)


if __name__ == "__main__":
    main()
