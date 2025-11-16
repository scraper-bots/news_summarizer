"""
Test script for Banker.az scraper
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sources.banker_az import BankerAzScraper


def test_scraper():
    """Test the Banker.az scraper"""
    scraper = BankerAzScraper()

    print("Testing Banker.az scraper...")
    print("=" * 60)

    # Test scraping article list
    print("\n1. Testing article list scraping...")
    article_urls = scraper.scrape_article_list(page=1)
    print(f"Found {len(article_urls)} articles")

    if article_urls:
        # Test scraping first article
        print(f"\n2. Testing single article scraping...")
        print(f"URL: {article_urls[0]}")
        article = scraper.scrape_article(article_urls[0])

        if article:
            try:
                print(f"\nTitle: {article['title']}")
            except UnicodeEncodeError:
                print(f"\nTitle: [Contains Azerbaijani characters - {len(article['title'])} chars]")

            print(f"Date: {article['published_date']}")
            print(f"Content length: {len(article['content'])} characters")
            print(f"Source: {article['source']}")
            print(f"Language: {article['language']}")

            # Verify Azerbaijani characters are preserved
            az_chars = ['ə', 'ı', 'ğ', 'ş', 'ç', 'ö', 'ü']
            found_az_chars = [char for char in az_chars if char in article['title'].lower() or char in article['content'].lower()]
            if found_az_chars:
                print(f"[SUCCESS] Azerbaijani characters preserved correctly ({len(found_az_chars)} unique chars found)")

            print("\n" + "=" * 60)
            print("TEST PASSED")
            print("=" * 60)
        else:
            print("[ERROR] Failed to scrape article")
    else:
        print("[ERROR] No articles found")


if __name__ == "__main__":
    test_scraper()
