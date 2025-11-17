"""
Check date format for recent oxu.az article
"""

import sys
import os
import asyncio

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sources.oxu_az import OxuAzScraper


async def check_date():
    """Check date for recent article"""
    test_url = "https://oxu.az/iqtisadiyyat/nazir-2027-2030-cu-iller-strategiyasinda-steam-azerbaycan-tehsilinin-ozeyi-olacaq"

    async with OxuAzScraper() as scraper:
        soup = await scraper.fetch_page(test_url)

        if soup:
            # Check for date in .post-detail-meta
            date_elems = soup.select('.post-detail-meta span')
            if date_elems:
                print(f"Found {len(date_elems)} span elements:")
                for i, elem in enumerate(date_elems, 1):
                    text = scraper.clean_text(elem.get_text())
                    print(f"  {i}. '{text}'")

                    # Try parsing each one
                    if '/' in text or any(month in text.lower() for month in scraper.months.keys()):
                        parsed = scraper.parse_date(text)
                        print(f"     Parsed: {parsed}")


if __name__ == "__main__":
    asyncio.run(check_date())
