"""
Test encoding for Azerbaijani characters
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

# Add parent directory (scraper) to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sources.fed_az import FedAzScraper

print("=" * 60)
print("ENCODING TEST FOR AZERBAIJANI CHARACTERS")
print("=" * 60)

print(f"\nPython version: {sys.version}")
print(f"Stdout encoding: {sys.stdout.encoding}")
print(f"Default encoding: {sys.getdefaultencoding()}")

print("\n" + "=" * 60)
print("Testing Azerbaijani characters:")
print("=" * 60)

test_words = [
    "Azərbaycan",
    "Mərkəzi Bank",
    "büdcə",
    "məzənnə",
    "iqtisadiyyat",
    "maliyyə",
    "xəbərlər",
    "gəlir",
    "xərc",
    "sığorta"
]

for word in test_words:
    print(f"  ✓ {word}")

print("\n" + "=" * 60)
print("Testing Fed.az scraper:")
print("=" * 60)

scraper = FedAzScraper()
print(f"\nSource name: {scraper.source_name}")
print(f"Base URL: {scraper.base_url}")
print(f"Categories: {len(scraper.categories)}")

for category in scraper.categories:
    print(f"  - {category}")

print("\n" + "=" * 60)
print("Testing date parsing:")
print("=" * 60)

test_dates = [
    ("15 Noy 2025", "12:44"),
    ("1 Yan 2025", "09:00"),
    ("30 Dek 2024", "23:59")
]

for date_str, time_str in test_dates:
    parsed = scraper.parse_date(date_str, time_str)
    print(f"  {date_str} {time_str} → {parsed}")

print("\n" + "=" * 60)
print("ENCODING TEST SUCCESSFUL ✓")
print("=" * 60)
