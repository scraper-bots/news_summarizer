"""
View the AI-generated summary from the database - save to file
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
        output_file = "latest_summary.txt"

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("LATEST SCRAPING SESSION SUMMARY\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Date: {summary['scraping_date']}\n")
            f.write(f"Total articles found: {summary['articles_count']}\n")
            f.write(f"New articles saved: {summary['new_articles_count']}\n")
            f.write(f"Sources scraped: {summary['sources_count']}\n")
            f.write(f"Duration: {summary['scraping_duration_seconds']:.2f} seconds\n")
            f.write(f"Created at: {summary['created_at']}\n")
            f.write("\n" + "=" * 80 + "\n")
            f.write("AI-GENERATED SUMMARY:\n")
            f.write("=" * 80 + "\n\n")
            f.write(summary['summary'])
            f.write("\n\n" + "=" * 80 + "\n")

        print(f"[SUCCESS] Summary saved to: {output_file}")
        print(f"[INFO] Date: {summary['scraping_date']}")
        print(f"[INFO] Articles: {summary['new_articles_count']} new / {summary['articles_count']} total")
        print(f"[INFO] Duration: {summary['scraping_duration_seconds']:.2f}s")
        print(f"\n[INFO] Summary length: {len(summary['summary'])} characters")
    else:
        print("[INFO] No summaries found")

    db.close()
else:
    print("[ERROR] Failed to connect to database")

print("=" * 80)
