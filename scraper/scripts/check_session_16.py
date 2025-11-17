"""
Check what happened to session 16
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

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import Database

def check_session_16():
    """Check session 16 status"""
    db = Database()
    if not db.connect():
        return

    try:
        # Check if session 16 exists
        db.cursor.execute("""
            SELECT * FROM news.scraping_summaries
            WHERE id >= 15
            ORDER BY id
        """)

        sessions = db.cursor.fetchall()

        print("\n" + "="*80)
        print("SESSIONS 15-17 CHECK")
        print("="*80)

        for session in sessions:
            print(f"\nSession ID: {session['id']}")
            print(f"  Created: {session['created_at']}")
            print(f"  Total: {session['articles_count']}")
            print(f"  New: {session['new_articles_count']}")
            print(f"  Sources: {session['sources_count']}")
            print(f"  Duration: {session['scraping_duration_seconds']}")

            # Count actual articles
            db.cursor.execute("""
                SELECT COUNT(*) as cnt
                FROM news.articles
                WHERE scraping_session_id = %s
            """, (session['id'],))

            result = db.cursor.fetchone()
            print(f"  Articles Linked: {result['cnt']}")

        # Check for articles from the time period when session 16 would have run
        print("\n" + "="*80)
        print("ARTICLES CREATED DURING SESSION 16 TIMEFRAME")
        print("="*80)

        db.cursor.execute("""
            SELECT
                source,
                COUNT(*) as count,
                scraping_session_id,
                MIN(created_at) as first,
                MAX(created_at) as last
            FROM news.articles
            WHERE created_at >= '2025-11-17 05:00:00'
              AND created_at <= '2025-11-17 06:15:00'
            GROUP BY source, scraping_session_id
            ORDER BY MIN(created_at)
        """)

        articles = db.cursor.fetchall()

        if articles:
            for row in articles:
                print(f"\n{row['source']}")
                print(f"  Count: {row['count']}")
                print(f"  Session ID: {row['scraping_session_id']}")
                print(f"  First: {row['first']}")
                print(f"  Last: {row['last']}")
        else:
            print("\nNo articles found in this timeframe")

        print("\n" + "="*80)

    except Exception as e:
        print(f"[ERROR] Failed: {e}")
        import traceback
        traceback.print_exc()

    finally:
        db.close()

if __name__ == "__main__":
    check_session_16()
