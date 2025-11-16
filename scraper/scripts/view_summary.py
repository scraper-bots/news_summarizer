"""
View the AI-generated summary from the database
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'scraper'))

from scraper.db import Database

print("Retrieving AI-generated summary...")
print("=" * 80)

db = Database()

if db.connect():
    db.cursor.execute("""
        SELECT * FROM news.scraping_summaries
        ORDER BY created_at DESC
        LIMIT 1
    """)

    summary = db.cursor.fetchone()

    if summary:
        print("\n[LATEST SCRAPING SESSION SUMMARY]")
        print("-" * 80)
        print(f"Date: {summary['scraping_date']}")
        print(f"Total articles found: {summary['articles_count']}")
        print(f"New articles saved: {summary['new_articles_count']}")
        print(f"Sources scraped: {summary['sources_count']}")
        print(f"Duration: {summary['scraping_duration_seconds']:.2f} seconds")
        print(f"Created at: {summary['created_at']}")
        print("\n" + "-" * 80)
        print("AI-GENERATED SUMMARY:")
        print("-" * 80)
        print(summary['summary'])
        print("-" * 80)
    else:
        print("[INFO] No summaries found")

    db.close()
else:
    print("[ERROR] Failed to connect to database")

print("\n" + "=" * 80)
