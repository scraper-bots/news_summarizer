"""
Main scraper script
Runs all news source scrapers and saves articles to database
"""

import sys
import os
from datetime import datetime, timezone
from typing import Dict

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db import Database
from sources.banker_az import BankerAzScraper
from sources.marja_az import MarjaAzScraper
from sources.report_az import ReportAzScraper
from sources.fed_az import FedAzScraper
from telegram import TelegramReporter
from summarizer import GeminiSummarizer


def scrape_banker_az(db: Database, summarizer: GeminiSummarizer, scraping_session_id: int, num_pages: int = 2, limit_per_page: int = 10) -> Dict:
    """
    Scrape articles from Banker.az

    Args:
        db: Database instance
        summarizer: GeminiSummarizer instance
        scraping_session_id: ID of the current scraping session
        num_pages: Number of pages to scrape
        limit_per_page: Maximum articles per page

    Returns:
        Dictionary with scraping statistics and new articles
    """
    print("\n" + "=" * 60)
    print("SCRAPING BANKER.AZ")
    print("=" * 60)

    scraper = BankerAzScraper()
    total_found = 0
    total_scraped = 0
    total_saved = 0
    total_skipped = 0
    new_articles = []

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

                # Save to database (no individual summarization)
                article_id = db.insert_article(article, scraping_session_id)
                if article_id:
                    total_saved += 1
                    new_articles.append(article)

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
        'skipped': total_skipped,
        'new_articles': new_articles
    }


def scrape_marja_az(db: Database, summarizer: GeminiSummarizer, scraping_session_id: int, num_pages: int = 2, limit_per_page: int = 10) -> Dict:
    """
    Scrape articles from Marja.az

    Args:
        db: Database instance
        summarizer: GeminiSummarizer instance
        scraping_session_id: ID of the current scraping session
        num_pages: Number of pages to scrape
        limit_per_page: Maximum articles per page

    Returns:
        Dictionary with scraping statistics and new articles
    """
    print("\n" + "=" * 60)
    print("SCRAPING MARJA.AZ")
    print("=" * 60)

    scraper = MarjaAzScraper()
    total_found = 0
    total_scraped = 0
    total_saved = 0
    total_skipped = 0
    new_articles = []

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

                # Save to database (no individual summarization)
                article_id = db.insert_article(article, scraping_session_id)
                if article_id:
                    total_saved += 1
                    new_articles.append(article)

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
        'skipped': total_skipped,
        'new_articles': new_articles
    }


def scrape_report_az(db: Database, summarizer: GeminiSummarizer, scraping_session_id: int, num_pages: int = 1, limit_per_page: int = 10) -> Dict:
    """
    Scrape articles from Report.az

    Args:
        db: Database instance
        summarizer: GeminiSummarizer instance
        scraping_session_id: ID of the current scraping session
        num_pages: Number of pages to scrape
        limit_per_page: Maximum articles per page

    Returns:
        Dictionary with scraping statistics and new articles
    """
    print("\n" + "=" * 60)
    print("SCRAPING REPORT.AZ")
    print("=" * 60)

    scraper = ReportAzScraper()
    total_found = 0
    total_scraped = 0
    total_saved = 0
    total_skipped = 0
    new_articles = []

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

                # Save to database (no individual summarization)
                article_id = db.insert_article(article, scraping_session_id)
                if article_id:
                    total_saved += 1
                    new_articles.append(article)

    print("\n" + "=" * 60)
    print(f"REPORT.AZ SUMMARY")
    print(f"Total found: {total_found}")
    print(f"Total scraped: {total_scraped}")
    print(f"Total saved to DB: {total_saved}")
    print(f"Total skipped: {total_skipped}")
    print("=" * 60)

    return {
        'name': 'Report.az',
        'total': total_found,
        'scraped': total_scraped,
        'saved': total_saved,
        'skipped': total_skipped,
        'new_articles': new_articles
    }


def scrape_fed_az(db: Database, summarizer: GeminiSummarizer, scraping_session_id: int, num_pages: int = 2, limit_per_page: int = 10) -> Dict:
    """
    Scrape articles from Fed.az (multiple categories)

    Args:
        db: Database instance
        summarizer: GeminiSummarizer instance
        scraping_session_id: ID of the current scraping session
        num_pages: Number of pages to scrape per category
        limit_per_page: Maximum articles per page

    Returns:
        Dictionary with scraping statistics and new articles
    """
    print("\n" + "=" * 60)
    print("SCRAPING FED.AZ")
    print("=" * 60)

    scraper = FedAzScraper()
    total_found = 0
    total_scraped = 0
    total_saved = 0
    total_skipped = 0
    new_articles = []

    # Scrape all categories
    for category in scraper.categories:
        print(f"\n[INFO] Scraping category: {category}")

        for page in range(1, num_pages + 1):
            print(f"\n[Page {page}] Fetching article list from {category}...")

            # Get article URLs from this page
            article_urls = scraper.scrape_article_list(page=page, category=category)

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

                    # Save to database (no individual summarization)
                    article_id = db.insert_article(article, scraping_session_id)
                    if article_id:
                        total_saved += 1
                        new_articles.append(article)

    print("\n" + "=" * 60)
    print(f"FED.AZ SUMMARY")
    print(f"Total found: {total_found}")
    print(f"Total scraped: {total_scraped}")
    print(f"Total saved to DB: {total_saved}")
    print(f"Total skipped: {total_skipped}")
    print("=" * 60)

    return {
        'name': 'Fed.az',
        'total': total_found,
        'scraped': total_scraped,
        'saved': total_saved,
        'skipped': total_skipped,
        'new_articles': new_articles
    }


def main():
    """Main function to run all scrapers"""
    print("\n" + "=" * 60)
    print("NEWS SCRAPER STARTED")
    print("=" * 60)

    # Initialize Telegram reporter and summarizer
    telegram = TelegramReporter()
    summarizer = GeminiSummarizer()

    # Track overall statistics
    start_time = datetime.now(timezone.utc)
    sources_stats = []
    all_new_articles = []
    errors = []

    # Skip start notification for public channel (no need to announce processing)

    # Initialize database connection
    db = Database()

    if not db.connect():
        error_msg = "Failed to connect to database"
        print(f"[ERROR] {error_msg}")
        telegram.send_error_alert(error_msg)
        return

    session_summary = None
    end_time = None
    scraping_session_id = None

    try:
        # Create scraping session record FIRST (placeholder)
        print("\n[INFO] Creating scraping session...")
        placeholder_summary = {
            'summary': 'Scraping in progress...',
            'articles_count': 0,
            'sources_count': 4,
            'new_articles_count': 0,
            'scraping_duration_seconds': 0
        }
        scraping_session_id = db.insert_scraping_summary(placeholder_summary)

        if scraping_session_id:
            print(f"[SUCCESS] Created scraping session (ID: {scraping_session_id})")
        else:
            print("[ERROR] Failed to create scraping session, articles won't be linked")

        # Scrape Banker.az - 2 pages, all articles
        banker_stats = scrape_banker_az(db, summarizer, scraping_session_id, num_pages=2, limit_per_page=999)
        sources_stats.append(banker_stats)
        all_new_articles.extend(banker_stats.get('new_articles', []))

        # Scrape Marja.az - 2 pages, all articles
        marja_stats = scrape_marja_az(db, summarizer, scraping_session_id, num_pages=2, limit_per_page=999)
        sources_stats.append(marja_stats)
        all_new_articles.extend(marja_stats.get('new_articles', []))

        # Scrape Report.az - 1 page, all articles
        report_stats = scrape_report_az(db, summarizer, scraping_session_id, num_pages=1, limit_per_page=999)
        sources_stats.append(report_stats)
        all_new_articles.extend(report_stats.get('new_articles', []))

        # Scrape Fed.az - 2 pages per category, all articles
        fed_stats = scrape_fed_az(db, summarizer, scraping_session_id, num_pages=2, limit_per_page=999)
        sources_stats.append(fed_stats)
        all_new_articles.extend(fed_stats.get('new_articles', []))

        end_time = datetime.now(timezone.utc)

        print("\n" + "=" * 60)
        print("NEWS SCRAPER COMPLETED")
        print("=" * 60)

        # Calculate totals
        total_found = sum(s['total'] for s in sources_stats)
        total_scraped = sum(s['scraped'] for s in sources_stats)
        total_saved = sum(s['saved'] for s in sources_stats)
        total_skipped = sum(s['skipped'] for s in sources_stats)

        # Create comprehensive session summary if there are new articles
        if all_new_articles and scraping_session_id:
            print(f"\n[INFO] Creating comprehensive summary for {len(all_new_articles)} new articles...")
            session_summary = summarizer.create_session_summary(all_new_articles, sources_stats)

            # Update session summary in database (BEFORE closing connection)
            if session_summary:
                duration = (end_time - start_time).total_seconds()
                summary_data = {
                    'summary': session_summary,
                    'articles_count': total_found,
                    'new_articles_count': total_saved,
                    'scraping_duration_seconds': duration
                }
                db.update_scraping_summary(scraping_session_id, summary_data)
        elif scraping_session_id and not all_new_articles:
            # No new articles, update placeholder with zero counts
            print("\n[INFO] No new articles found, updating session with zero counts...")
            duration = (end_time - start_time).total_seconds()
            summary_data = {
                'summary': 'No new articles found in this scraping session.',
                'articles_count': total_found,
                'new_articles_count': 0,
                'scraping_duration_seconds': duration
            }
            db.update_scraping_summary(scraping_session_id, summary_data)

    except KeyboardInterrupt:
        print("\n\n[INFO] Scraping interrupted by user")
        errors.append("Scraping interrupted by user")
        end_time = datetime.now(timezone.utc)

    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print(f"\n[ERROR] {error_msg}")
        errors.append(error_msg)
        telegram.send_error_alert(error_msg)
        import traceback
        traceback.print_exc()
        end_time = datetime.now(timezone.utc)

    finally:
        # Close database connection
        db.close()

        # Ensure end_time is set
        if end_time is None:
            end_time = datetime.now(timezone.utc)

        # Calculate totals (even if scraping failed)
        total_found = sum(s['total'] for s in sources_stats) if sources_stats else 0
        total_scraped = sum(s['scraped'] for s in sources_stats) if sources_stats else 0
        total_saved = sum(s['saved'] for s in sources_stats) if sources_stats else 0
        total_skipped = sum(s['skipped'] for s in sources_stats) if sources_stats else 0

        # Send Telegram report
        report_stats = {
            'start_time': start_time,
            'end_time': end_time,
            'sources': sources_stats,
            'total_found': total_found,
            'total_scraped': total_scraped,
            'total_saved': total_saved,
            'total_skipped': total_skipped,
            'session_summary': session_summary,
            'errors': errors
        }

        telegram.send_scraping_report(report_stats)


if __name__ == "__main__":
    main()
