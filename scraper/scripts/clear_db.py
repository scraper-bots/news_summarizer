"""
Clear all data from database tables for testing
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'scraper'))

from scraper.db import Database

print("Clearing database...")
print("=" * 80)

db = Database()

if db.connect():
    # Delete all summaries
    db.cursor.execute("DELETE FROM news.scraping_summaries")
    db.conn.commit()
    print("[SUCCESS] Cleared scraping_summaries table")

    # Delete all articles
    db.cursor.execute("DELETE FROM news.articles")
    db.conn.commit()
    print("[SUCCESS] Cleared articles table")

    # Verify
    db.cursor.execute("SELECT COUNT(*) as count FROM news.articles")
    article_count = db.cursor.fetchone()['count']

    db.cursor.execute("SELECT COUNT(*) as count FROM news.scraping_summaries")
    summary_count = db.cursor.fetchone()['count']

    print(f"\n[INFO] Articles remaining: {article_count}")
    print(f"[INFO] Summaries remaining: {summary_count}")

    db.close()
else:
    print("[ERROR] Failed to connect to database")

print("=" * 80)
