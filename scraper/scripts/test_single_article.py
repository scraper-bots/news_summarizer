"""
Test scraping a single article with debugging
"""

import sys
import os
import asyncio

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sources.qafqazinfo_az import QafqazinfoAzScraper


async def test_article():
    """Test scraping a single article with debug info"""
    # Test with the article URL from user's example
    test_url = "https://qafqazinfo.az/news/detail/azergold-zefer-adli-yeni-qizil-sikke-kolleksiyasini-teqdim-etdi-foto-488407"

    async with QafqazinfoAzScraper() as scraper:
        print(f"Testing article: {test_url}")
        print("=" * 60)

        soup = await scraper.fetch_page(test_url)
        if not soup:
            print("Failed to fetch page")
            return

        # Check for date element
        date_elem = soup.select_one('time[datetime]')
        print(f"Date element found: {date_elem is not None}")
        if date_elem:
            date_text = scraper.clean_text(date_elem.get_text())
            print(f"Date text: '{date_text}'")
            published_date = scraper.parse_date(date_text)
            print(f"Parsed date: {published_date}")

        print("\n" + "=" * 60)
        print("Full article scrape:")
        article = await scraper.scrape_article(test_url)
        if article:
            print(f"Title: {article['title']}")
            print(f"Published: {article['published_date']}")
            print(f"Content length: {len(article['content'])} chars")
        else:
            print("Failed to scrape article")


if __name__ == "__main__":
    asyncio.run(test_article())
