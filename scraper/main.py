"""
Main scraper script
Runs all news source scrapers and saves articles to database
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db import Database
from sources.banker_az import BankerAzScraper


def scrape_banker_az(db: Database, num_pages: int = 2, limit_per_page: int = 10):
    """
    Scrape articles from Banker.az

    Args:
        db: Database instance
        num_pages: Number of pages to scrape
        limit_per_page: Maximum articles per page
    """
    print("\n" + "=" * 60)
    print("SCRAPING BANKER.AZ")
    print("=" * 60)

    scraper = BankerAzScraper()
    total_scraped = 0
    total_saved = 0

    for page in range(1, num_pages + 1):
        print(f"\n[Page {page}] Fetching article list...")

        # Get article URLs from this page
        article_urls = scraper.scrape_article_list(page=page)

        if not article_urls:
            print(f"[Page {page}] No articles found")
            break

        # Limit articles per page
        article_urls = article_urls[:limit_per_page]
        print(f"[Page {page}] Found {len(article_urls)} articles")

        # Scrape each article
        for i, url in enumerate(article_urls, 1):
            print(f"\n[{i}/{len(article_urls)}] Scraping: {url}")

            # Check if article already exists
            if db.article_exists(url):
                print(f"[SKIP] Article already exists in database")
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
    print(f"Total scraped: {total_scraped}")
    print(f"Total saved to DB: {total_saved}")
    print("=" * 60)


def main():
    """Main function to run all scrapers"""
    print("\n" + "=" * 60)
    print("NEWS SCRAPER STARTED")
    print("=" * 60)

    # Initialize database connection
    db = Database()

    if not db.connect():
        print("[ERROR] Failed to connect to database. Exiting...")
        return

    try:
        # Scrape Banker.az
        scrape_banker_az(db, num_pages=2, limit_per_page=10)

        # Add more scrapers here as you build them
        # scrape_marja_az(db, num_pages=2, limit_per_page=10)
        # scrape_other_source(db, num_pages=2, limit_per_page=10)

    except KeyboardInterrupt:
        print("\n\n[INFO] Scraping interrupted by user")

    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Close database connection
        db.close()

        print("\n" + "=" * 60)
        print("NEWS SCRAPER COMPLETED")
        print("=" * 60)


if __name__ == "__main__":
    main()
