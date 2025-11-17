"""
Analyze scraping session results from database
Shows which sources succeeded/failed and article counts
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

def analyze_scraping_session(session_id=None):
    """Analyze scraping session results"""
    db = Database()
    if not db.connect():
        return

    try:
        # Get latest session if not specified
        if session_id is None:
            db.cursor.execute("""
                SELECT id, created_at
                FROM news.scraping_summaries
                ORDER BY created_at DESC
                LIMIT 1
            """)
            result = db.cursor.fetchone()
            if result:
                session_id = result['id']
                print(f"Analyzing latest session: ID {session_id} ({result['created_at']})")
            else:
                print("No scraping sessions found")
                return

        print("\n" + "="*60)
        print(f"SCRAPING SESSION ANALYSIS - ID: {session_id}")
        print("="*60)

        # Get session summary
        db.cursor.execute("""
            SELECT * FROM news.scraping_summaries
            WHERE id = %s
        """, (session_id,))
        summary = db.cursor.fetchone()

        if summary:
            print(f"\nSession Summary:")
            print(f"  Total Articles: {summary['articles_count']}")
            print(f"  New Articles: {summary['new_articles_count']}")
            print(f"  Duration: {summary['scraping_duration_seconds']:.2f}s" if summary['scraping_duration_seconds'] else "  Duration: N/A")
            print(f"  Sources: {summary['sources_count']}")

        # Get articles per source for this session
        print("\n" + "-"*60)
        print("ARTICLES BY SOURCE (This Session)")
        print("-"*60)

        db.cursor.execute("""
            SELECT
                source,
                COUNT(*) as article_count,
                MIN(created_at) as first_saved,
                MAX(created_at) as last_saved
            FROM news.articles
            WHERE scraping_session_id = %s
            GROUP BY source
            ORDER BY article_count DESC
        """, (session_id,))

        session_results = db.cursor.fetchall()

        expected_sources = [
            "Banker.az", "Marja.az", "Report.az", "Fed.az",
            "Sonxeber.az", "Iqtisadiyyat.az", "Trend.az", "APA.az"
        ]

        found_sources = []
        total_articles = 0

        if session_results:
            for row in session_results:
                print(f"\n✅ {row['source']}")
                print(f"   Articles: {row['article_count']}")
                print(f"   First: {row['first_saved']}")
                print(f"   Last: {row['last_saved']}")
                found_sources.append(row['source'])
                total_articles += row['article_count']
        else:
            print("\n⚠️  No articles found for this session!")

        # Check for missing sources
        print("\n" + "-"*60)
        print("SOURCE STATUS CHECK")
        print("-"*60)

        missing_sources = [s for s in expected_sources if s not in found_sources]

        if missing_sources:
            print(f"\n❌ FAILED SOURCES ({len(missing_sources)}):")
            for source in missing_sources:
                print(f"   - {source} (0 articles saved)")
        else:
            print("\n✅ ALL SOURCES SUCCEEDED!")

        # Overall statistics
        print("\n" + "-"*60)
        print("OVERALL DATABASE STATISTICS")
        print("-"*60)

        db.cursor.execute("""
            SELECT
                source,
                COUNT(*) as total_articles,
                MIN(created_at) as oldest,
                MAX(created_at) as newest
            FROM news.articles
            GROUP BY source
            ORDER BY total_articles DESC
        """)

        all_results = db.cursor.fetchall()

        print(f"\nTotal Articles in Database:")
        for row in all_results:
            print(f"  {row['source']}: {row['total_articles']} articles")

        # Check for articles with no scraping session
        db.cursor.execute("""
            SELECT COUNT(*) as orphan_count
            FROM news.articles
            WHERE scraping_session_id IS NULL
        """)
        orphan_result = db.cursor.fetchone()

        if orphan_result and orphan_result['orphan_count'] > 0:
            print(f"\n⚠️  {orphan_result['orphan_count']} articles have no scraping session ID")

        print("\n" + "="*60)
        print(f"SESSION ANALYSIS COMPLETE")
        print("="*60)

    except Exception as e:
        print(f"[ERROR] Analysis failed: {e}")
        import traceback
        traceback.print_exc()

    finally:
        db.close()

if __name__ == "__main__":
    # Allow session ID as command line argument
    session_id = None
    if len(sys.argv) > 1:
        try:
            session_id = int(sys.argv[1])
        except ValueError:
            print("Usage: python analyze_scraping_session.py [session_id]")
            sys.exit(1)

    analyze_scraping_session(session_id)
