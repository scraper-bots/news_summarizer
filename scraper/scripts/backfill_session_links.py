"""
Backfill scraping_session_id for existing articles based on their scraped_at timestamp
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'scraper'))

from scraper.db import Database

print("=" * 80)
print("BACKFILLING SESSION LINKS FOR ORPHANED ARTICLES")
print("=" * 80)

db = Database()

if db.connect():
    # Find orphaned articles
    db.cursor.execute("""
        SELECT COUNT(*) as count
        FROM news.articles
        WHERE scraping_session_id IS NULL
    """)
    orphaned_count = db.cursor.fetchone()['count']

    print(f"\n[INFO] Found {orphaned_count} orphaned articles")

    if orphaned_count == 0:
        print("[SUCCESS] No orphaned articles to backfill!")
        db.close()
        sys.exit(0)

    # Get all scraping sessions
    db.cursor.execute("""
        SELECT id, scraping_date, created_at
        FROM news.scraping_summaries
        ORDER BY created_at ASC
    """)
    sessions = db.cursor.fetchall()

    print(f"\n[INFO] Found {len(sessions)} scraping sessions")

    # Strategy: Link articles to the session that matches their scraping date
    # Since we have scraped_at timestamp on articles and scraping_date on sessions

    backfilled = 0
    for session in sessions:
        session_id = session['id']
        session_date = session['scraping_date']

        # Link articles scraped on the same date to this session
        db.cursor.execute("""
            UPDATE news.articles
            SET scraping_session_id = %s
            WHERE scraping_session_id IS NULL
            AND DATE(scraped_at) = %s
        """, (session_id, session_date))

        rows_updated = db.cursor.rowcount
        db.conn.commit()

        if rows_updated > 0:
            print(f"\n[SUCCESS] Linked {rows_updated} articles to session {session_id} (date: {session_date})")
            backfilled += rows_updated

    # Check if there are still orphaned articles
    db.cursor.execute("""
        SELECT COUNT(*) as count
        FROM news.articles
        WHERE scraping_session_id IS NULL
    """)
    remaining_orphaned = db.cursor.fetchone()['count']

    print("\n" + "=" * 80)
    print("BACKFILL SUMMARY")
    print("=" * 80)
    print(f"Total orphaned articles: {orphaned_count}")
    print(f"Articles linked: {backfilled}")
    print(f"Remaining orphaned: {remaining_orphaned}")

    if remaining_orphaned == 0:
        print("\n[SUCCESS] All articles are now linked to sessions!")
    else:
        print(f"\n[WARNING] {remaining_orphaned} articles could not be matched to a session")
        print("This might be because they were scraped on a date with no corresponding session")

    db.close()
else:
    print("[ERROR] Failed to connect to database")

print("\n" + "=" * 80)
