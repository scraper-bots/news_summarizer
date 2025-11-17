"""
List all scraping sessions in the database
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

def list_sessions():
    """List all scraping sessions"""
    db = Database()
    if not db.connect():
        return

    try:
        db.cursor.execute("""
            SELECT
                s.id,
                s.created_at,
                s.articles_count,
                s.new_articles_count,
                s.sources_count,
                s.scraping_duration_seconds,
                COUNT(a.id) as actual_articles
            FROM news.scraping_summaries s
            LEFT JOIN news.articles a ON a.scraping_session_id = s.id
            GROUP BY s.id, s.created_at, s.articles_count, s.new_articles_count,
                     s.sources_count, s.scraping_duration_seconds
            ORDER BY s.created_at DESC
            LIMIT 10
        """)

        sessions = db.cursor.fetchall()

        print("\n" + "="*80)
        print("SCRAPING SESSIONS HISTORY (Last 10)")
        print("="*80)

        if not sessions:
            print("\nNo sessions found")
            return

        for session in sessions:
            duration = f"{session['scraping_duration_seconds']:.2f}s" if session['scraping_duration_seconds'] else "N/A"
            actual = session['actual_articles']
            expected_new = session['new_articles_count']

            status = "✅" if actual == expected_new else "⚠️"

            print(f"\n{status} Session ID: {session['id']}")
            print(f"   Date: {session['created_at']}")
            print(f"   Total Found: {session['articles_count']}")
            print(f"   Expected New: {expected_new}")
            print(f"   Actually Saved: {actual}")
            print(f"   Sources: {session['sources_count']}")
            print(f"   Duration: {duration}")

            if actual != expected_new:
                print(f"   ⚠️  MISMATCH: Expected {expected_new} but found {actual} linked articles")

        print("\n" + "="*80)

    except Exception as e:
        print(f"[ERROR] Failed to list sessions: {e}")
        import traceback
        traceback.print_exc()

    finally:
        db.close()

if __name__ == "__main__":
    list_sessions()
