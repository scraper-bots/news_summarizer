"""
Verify article-to-session relationships in the database - output to file
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'scraper'))

from scraper.db import Database

output_file = "relationship_verification.txt"

with open(output_file, 'w', encoding='utf-8') as f:
    f.write("=" * 80 + "\n")
    f.write("VERIFYING ARTICLE-TO-SESSION RELATIONSHIPS\n")
    f.write("=" * 80 + "\n")

    db = Database()

    if db.connect():
        # Get all scraping sessions
        f.write("\n[1] SCRAPING SESSIONS:\n")
        f.write("-" * 80 + "\n")
        db.cursor.execute("""
            SELECT id, scraping_date, new_articles_count, articles_count,
                   LEFT(summary, 60) as summary_preview
            FROM news.scraping_summaries
            ORDER BY created_at DESC
        """)
        sessions = db.cursor.fetchall()

        for session in sessions:
            f.write(f"\nSession ID: {session['id']}\n")
            f.write(f"  Date: {session['scraping_date']}\n")
            f.write(f"  New articles: {session['new_articles_count']}\n")
            f.write(f"  Total found: {session['articles_count']}\n")
            f.write(f"  Summary: {session['summary_preview']}...\n")

        # Check article linkage for each session
        f.write("\n" + "=" * 80 + "\n")
        f.write("[2] ARTICLES LINKED TO EACH SESSION:\n")
        f.write("=" * 80 + "\n")

        for session in sessions:
            session_id = session['id']
            db.cursor.execute("""
                SELECT COUNT(*) as count
                FROM news.articles
                WHERE scraping_session_id = %s
            """, (session_id,))
            result = db.cursor.fetchone()
            article_count = result['count']

            f.write(f"\nSession {session_id}: {article_count} articles linked\n")

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

                f.write("  Sample articles:\n")
                for article in articles:
                    f.write(f"    - [{article['id']}] {article['source']}: {article['title_preview']}...\n")

        # Check articles WITHOUT session link (orphaned)
        f.write("\n" + "=" * 80 + "\n")
        f.write("[3] ORPHANED ARTICLES (no session link):\n")
        f.write("=" * 80 + "\n")
        db.cursor.execute("""
            SELECT COUNT(*) as count
            FROM news.articles
            WHERE scraping_session_id IS NULL
        """)
        result = db.cursor.fetchone()
        orphaned_count = result['count']

        if orphaned_count > 0:
            f.write(f"\nWARNING: {orphaned_count} articles have no session link!\n")
            db.cursor.execute("""
                SELECT id, LEFT(title, 50) as title_preview, source, scraped_at
                FROM news.articles
                WHERE scraping_session_id IS NULL
                ORDER BY scraped_at DESC
                LIMIT 10
            """)
            orphaned = db.cursor.fetchall()
            f.write("  Sample orphaned articles:\n")
            for article in orphaned:
                f.write(f"    - [{article['id']}] {article['source']}: {article['title_preview']}...\n")
        else:
            f.write("\n[SUCCESS] All articles are linked to a scraping session!\n")

        # Summary statistics
        f.write("\n" + "=" * 80 + "\n")
        f.write("[4] OVERALL STATISTICS:\n")
        f.write("=" * 80 + "\n")

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

        f.write(f"\nTotal articles: {total_articles}\n")
        f.write(f"Total sessions: {total_sessions}\n")
        f.write(f"Linked articles: {linked_articles}\n")
        f.write(f"Orphaned articles: {orphaned_count}\n")
        f.write(f"Link coverage: {(linked_articles/total_articles*100) if total_articles > 0 else 0:.1f}%\n")

        db.close()
    else:
        f.write("[ERROR] Failed to connect to database\n")

    f.write("\n" + "=" * 80 + "\n")
    f.write("VERIFICATION COMPLETE\n")
    f.write("=" * 80 + "\n")

print(f"[SUCCESS] Verification report saved to: {output_file}")
