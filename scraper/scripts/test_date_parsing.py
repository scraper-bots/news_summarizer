"""
Test date parsing for Qafqazinfo.az
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sources.qafqazinfo_az import QafqazinfoAzScraper

scraper = QafqazinfoAzScraper()

# Test various date formats
test_dates = [
    "09.11.2025 | 10:59",
    "  09.11.2025 | 10:59  ",  # with whitespace
    "\n                                09.11.2025 | 10:59                            \n",  # with lots of whitespace
    "11.09.2025 | 10:59",
]

print("Testing date parsing...")
print("=" * 60)

for date_str in test_dates:
    result = scraper.parse_date(date_str)
    print(f"Input: '{date_str}'")
    print(f"Result: {result}")
    print()
