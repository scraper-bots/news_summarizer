"""
Test script for Qafqazinfo.az scraper
"""

import sys
import os
import asyncio

# Fix encoding for Azerbaijani characters
if sys.platform == 'win32' and hasattr(sys.stdout, 'buffer'):
    import io
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sources.qafqazinfo_az import QafqazinfoAzScraper


async def test_qafqazinfo():
    """Test the Qafqazinfo.az scraper"""
    print("Testing Qafqazinfo.az scraper...")
    print("=" * 60)

    async with QafqazinfoAzScraper() as scraper:
        # Test scraping article list
        print("\n[TEST 1] Scraping article list from page 1...")
        article_urls = await scraper.scrape_article_list(page=1)
        print(f"Found {len(article_urls)} article URLs")

        if article_urls:
            print("\nFirst 5 article URLs:")
            for i, url in enumerate(article_urls[:5], 1):
                print(f"  {i}. {url}")
        else:
            print("[WARNING] No article URLs found!")
            return

        # Test scraping a single article
        print("\n" + "=" * 60)
        print("[TEST 2] Scraping first article in detail...")
        test_url = article_urls[0]
        print(f"URL: {test_url}")

        article = await scraper.scrape_article(test_url)

        if article:
            print("\n[SUCCESS] Article scraped successfully!")
            print(f"\nTitle: {article['title']}")
            print(f"Source: {article['source']}")
            print(f"Language: {article['language']}")
            print(f"Published: {article['published_date']}")
            print(f"URL: {article['url']}")
            print(f"\nContent preview (first 200 chars):")
            print(article['content'][:200] + "...")
            print(f"\nTotal content length: {len(article['content'])} characters")
        else:
            print("[ERROR] Failed to scrape article!")

        # Test scraping multiple articles
        print("\n" + "=" * 60)
        print("[TEST 3] Scraping first 3 articles...")
        articles = await scraper.scrape_articles_batch(article_urls[:3], batch_size=3)
        print(f"\nSuccessfully scraped {len(articles)} out of 3 articles")

        for i, article in enumerate(articles, 1):
            print(f"\n  {i}. {article['title']}")
            print(f"     Published: {article['published_date']}")
            print(f"     Content length: {len(article['content'])} chars")

    print("\n" + "=" * 60)
    print("Testing completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_qafqazinfo())
