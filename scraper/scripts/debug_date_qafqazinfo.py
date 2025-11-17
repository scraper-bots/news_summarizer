"""
Debug script to check date format on Qafqazinfo.az
"""

import sys
import os
import asyncio

# Fix encoding
if sys.platform == 'win32' and hasattr(sys.stdout, 'buffer'):
    import io
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sources.qafqazinfo_az import QafqazinfoAzScraper


async def debug_date():
    """Debug date extraction"""
    test_url = "https://qafqazinfo.az/news/detail/azergold-zefer-adli-yeni-qizil-sikke-kolleksiyasini-teqdim-etdi-foto-488407"

    async with QafqazinfoAzScraper() as scraper:
        soup = await scraper.fetch_page(test_url)

        if soup:
            print("Looking for date element...")
            print("=" * 60)

            # Check for time element
            date_elem = soup.select_one('time[datetime]')
            if date_elem:
                print("Found <time> element!")
                print(f"  datetime attribute: {date_elem.get('datetime')}")
                print(f"  text content: {date_elem.get_text()}")
            else:
                print("No <time> element found")

            # Check for other date patterns
            print("\nSearching for date in news-time class...")
            news_time = soup.select_one('.news-time')
            if news_time:
                print("Found .news-time div:")
                print(news_time.prettify())


if __name__ == "__main__":
    asyncio.run(debug_date())
