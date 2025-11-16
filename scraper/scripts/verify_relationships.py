"""
Verify article-to-session relationships in the database
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'scraper'))

from scraper.db import Database

print("=" * 80)
print("VERIFYING ARTICLE-TO-SESSION RELATIONSHIPS")
print("=" * 80)

db = Database()

if db.connect():
    # Get all scraping sessions
    print("\n[1] SCRAPING SESSIONS:")
    print("-" * 80)
    db.cursor.execute("""
        SELECT id, scraping_date, new_articles_count, articles_count,
               LEFT(summary, 60) as summary_preview
        FROM news.scraping_summaries
        ORDER BY created_at DESC
    """)
    sessions = db.cursor.fetchall()

    for session in sessions:
        print(f"\nSession ID: {session['id']}")
        print(f"  Date: {session['scraping_date']}")
        print(f"  New articles: {session['new_articles_count']}")
        print(f"  Total found: {session['articles_count']}")
        print(f"  Summary: {session['summary_preview']}...")

    # Check article linkage for each session
    print("\n" + "=" * 80)
    print("[2] ARTICLES LINKED TO EACH SESSION:")
    print("=" * 80)

    for session in sessions:
        session_id = session['id']
        db.cursor.execute("""
            SELECT COUNT(*) as count
            FROM news.articles
            WHERE scraping_session_id = %s
        """, (session_id,))
        result = db.cursor.fetchone()
        article_count = result['count']

        print(f"\nSession {session_id}: {article_count} articles linked")

        if article_count > 0:
            # Show some sample articles
            db.cursor.execute("""
                SELECT id, LEFT(title, 50) as title_preview, source, scraped_at
                FROM news.articles
                WHERE scraping_session_id = %s
                ORDER BY scraped_at DESC
                LIMIT 5
            """, (session_id,))
            articles = db.cursor.fetchall()

            print("  Sample articles:")
            for article in articles:
                print(f"    - [{article['id']}] {article['source']}: {article['title_preview']}...")

    # Check articles WITHOUT session link (orphaned)
    print("\n" + "=" * 80)
    print("[3] ORPHANED ARTICLES (no session link):")
    print("=" * 80)
    db.cursor.execute("""
        SELECT COUNT(*) as count
        FROM news.articles
        WHERE scraping_session_id IS NULL
    """)
    result = db.cursor.fetchone()
    orphaned_count = result['count']

    if orphaned_count > 0:
        print(f"\nWARNING: {orphaned_count} articles have no session link!")
        db.cursor.execute("""
            SELECT id, LEFT(title, 50) as title_preview, source, scraped_at
            FROM news.articles
            WHERE scraping_session_id IS NULL
            ORDER BY scraped_at DESC
            LIMIT 5
        """)
        orphaned = db.cursor.fetchall()
        print("  Sample orphaned articles:")
        for article in orphaned:
            print(f"    - [{article['id']}] {article['source']}: {article['title_preview']}...")
    else:
        print("\n[SUCCESS] All articles are linked to a scraping session!")

    # Summary statistics
    print("\n" + "=" * 80)
    print("[4] OVERALL STATISTICS:")
    print("=" * 80)

    db.cursor.execute("SELECT COUNT(*) as count FROM news.articles")
    total_articles = db.cursor.fetchone()['count']

    db.cursor.execute("SELECT COUNT(*) as count FROM news.scraping_summaries")
    total_sessions = db.cursor.fetchone()['count']

    db.cursor.execute("""
        SELECT COUNT(*) as count
        FROM news.articles
        WHERE scraping_session_id IS NOT NULL
    """)
    linked_articles = db.cursor.fetchone()['count']

    print(f"\nTotal articles: {total_articles}")
    print(f"Total sessions: {total_sessions}")
    print(f"Linked articles: {linked_articles}")
    print(f"Orphaned articles: {orphaned_count}")
    print(f"Link coverage: {(linked_articles/total_articles*100) if total_articles > 0 else 0:.1f}%")

    db.close()
else:
    print("[ERROR] Failed to connect to database")

print("\n" + "=" * 80)
print("VERIFICATION COMPLETE")
print("=" * 80)
