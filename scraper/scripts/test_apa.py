"""
Test script for APA.az scraper
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

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sources.apa_az import ApaAzScraper


def test_scrape_list():
    """Test scraping article list"""
    print("=" * 60)
    print("TESTING ARTICLE LIST SCRAPING")
    print("=" * 60)

    scraper = ApaAzScraper()

    # Test first page
    article_urls = scraper.scrape_article_list(page=1)

    print(f"\nFound {len(article_urls)} articles on page 1")
    print("\nFirst 5 URLs:")
    for i, url in enumerate(article_urls[:5], 1):
        print(f"{i}. {url}")

    return article_urls


def test_scrape_article(url):
    """Test scraping a single article"""
    print("\n" + "=" * 60)
    print("TESTING ARTICLE SCRAPING")
    print("=" * 60)

    scraper = ApaAzScraper()
    article = scraper.scrape_article(url)

    if article:
        print(f"\nTitle: {article['title']}")
        print(f"URL: {article['url']}")
        print(f"Source: {article['source']}")
        print(f"Language: {article['language']}")
        print(f"Published: {article['published_date']}")
        print(f"\nContent preview (first 200 chars):")
        print(article['content'][:200] + "...")
        print(f"\nTotal content length: {len(article['content'])} characters")
        return True
    else:
        print("[ERROR] Failed to scrape article")
        return False


if __name__ == "__main__":
    # Test article list
    urls = test_scrape_list()

    # Test scraping first article
    if urls:
        print(f"\n\nTesting full article scraping for: {urls[0]}")
        test_scrape_article(urls[0])
    else:
        print("[ERROR] No URLs found to test")
