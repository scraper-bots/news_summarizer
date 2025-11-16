"""
Test script to verify summary insertion works properly
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'scraper'))

from scraper.db import Database

# Create test summary data
test_summary_data = {
    'summary': 'Test summary: Bu gun 56 meqale toplanildi. Banker.az ve Marja.az saytlarindan melumatlar elde edildi.',
    'articles_count': 56,
    'sources_count': 2,
    'new_articles_count': 56,
    'scraping_duration_seconds': 125.5
}

print("Testing summary insertion...")
print("=" * 80)

# Initialize database
db = Database()

if db.connect():
    print("\n[INFO] Attempting to insert test summary...")

    summary_id = db.insert_scraping_summary(test_summary_data)

    if summary_id:
        print(f"[SUCCESS] Test summary inserted with ID: {summary_id}")

        # Verify it was saved
        db.cursor.execute("SELECT * FROM news.scraping_summaries WHERE id = %s", (summary_id,))
        result = db.cursor.fetchone()

        if result:
            print("\n[SUCCESS] Verified summary in database:")
            print(f"  - ID: {result['id']}")
            print(f"  - Date: {result['scraping_date']}")
            print(f"  - Articles: {result['articles_count']}")
            print(f"  - Sources: {result['sources_count']}")
            print(f"  - New articles: {result['new_articles_count']}")
            print(f"  - Duration: {result['scraping_duration_seconds']}s")
            print(f"  - Summary length: {len(result['summary'])} characters")
    else:
        print("[ERROR] Failed to insert test summary")

    db.close()
else:
    print("[ERROR] Failed to connect to database")

print("\n" + "=" * 80)
print("Test completed")
