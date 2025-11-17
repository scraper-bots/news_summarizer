"""
Analyze current database state - single session analysis
Shows which sources worked and which failed in the last scraping run
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

def analyze_current_state():
    """Analyze the current database state"""
    db = Database()
    if not db.connect():
        return

    try:
        # Get the only session
        db.cursor.execute("""
            SELECT * FROM news.scraping_summaries
            ORDER BY created_at DESC
            LIMIT 1
        """)

        session = db.cursor.fetchone()

        if not session:
            print("❌ No scraping sessions found in database!")
            return

        print("\n" + "="*70)
        print(f"📊 CURRENT DATABASE STATE - Session ID: {session['id']}")
        print("="*70)

        print(f"\n📅 Scraped: {session['created_at']}")
        print(f"⏱️  Duration: {session['scraping_duration_seconds']:.2f} seconds")
        print(f"📰 Total Articles Found: {session['articles_count']}")
        print(f"✨ New Articles Saved: {session['new_articles_count']}")
        print(f"🔢 Sources Scraped: {session['sources_count']}")

        # Expected sources
        expected_sources = {
            "Banker.az": 50,      # scrapes 2 pages
            "Marja.az": 30,       # scrapes 2 pages
            "Report.az": 16,      # scrapes 1 page
            "Fed.az": 100,        # scrapes 2 pages
            "Sonxeber.az": 60,    # scrapes 2 pages
            "Iqtisadiyyat.az": 40, # scrapes 2 pages
            "Trend.az": 24,       # scrapes 1 page
            "APA.az": 48          # scrapes 2 pages
        }

        # Get actual articles per source
        db.cursor.execute("""
            SELECT
                source,
                COUNT(*) as count,
                MIN(created_at) as first_scraped,
                MAX(created_at) as last_scraped,
                MIN(published_date) as oldest_article,
                MAX(published_date) as newest_article
            FROM news.articles
            WHERE scraping_session_id = %s
            GROUP BY source
            ORDER BY count DESC
        """, (session['id'],))

        results = db.cursor.fetchall()

        print("\n" + "-"*70)
        print("✅ SUCCESSFUL SOURCES")
        print("-"*70)

        found_sources = {}
        total_saved = 0

        for row in results:
            source = row['source']
            count = row['count']
            found_sources[source] = count
            total_saved += count

            expected = expected_sources.get(source, "?")
            percentage = (count / expected * 100) if isinstance(expected, int) and expected > 0 else 0

            print(f"\n✅ {source}")
            print(f"   Saved: {count} articles (Expected: {expected}, {percentage:.1f}%)")
            print(f"   Scraped: {row['first_scraped']} to {row['last_scraped']}")
            if row['oldest_article'] and row['newest_article']:
                print(f"   Article Dates: {row['oldest_article']} to {row['newest_article']}")

        # Check for missing sources
        missing_sources = [s for s in expected_sources.keys() if s not in found_sources]

        if missing_sources:
            print("\n" + "-"*70)
            print("❌ FAILED SOURCES (0 articles saved)")
            print("-"*70)

            for source in missing_sources:
                print(f"\n❌ {source}")
                print(f"   Expected: {expected_sources[source]} articles")
                print(f"   Saved: 0 articles")
                print(f"   Status: FAILED - No articles in database")

        # Summary
        print("\n" + "="*70)
        print("📈 SUMMARY")
        print("="*70)
        print(f"✅ Successful Sources: {len(found_sources)}/{len(expected_sources)}")
        print(f"❌ Failed Sources: {len(missing_sources)}/{len(expected_sources)}")
        print(f"📊 Total Articles Saved: {total_saved}")
        print(f"🎯 Success Rate: {len(found_sources)/len(expected_sources)*100:.1f}%")

        if len(found_sources) == len(expected_sources):
            print("\n🎉 ALL SOURCES WORKING PERFECTLY!")
        elif missing_sources:
            print(f"\n⚠️  WARNING: {len(missing_sources)} source(s) failed to save any articles")
            print("   Check scraper logs for errors")

        print("="*70 + "\n")

    except Exception as e:
        print(f"[ERROR] Analysis failed: {e}")
        import traceback
        traceback.print_exc()

    finally:
        db.close()

if __name__ == "__main__":
    analyze_current_state()
