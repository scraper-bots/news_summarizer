"""
Verify database contents
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import Database

def verify_database():
    """Check what's in the database"""
    db = Database()

    if not db.connect():
        print("[ERROR] Failed to connect to database")
        return

    try:
        # Get count of all articles
        db.cursor.execute("SELECT COUNT(*) as count FROM news.articles")
        result = db.cursor.fetchone()
        total_count = result['count']

        print(f"\n[SUCCESS] Total articles in database: {total_count}")

        # Get articles by source
        db.cursor.execute("""
            SELECT source, COUNT(*) as count
            FROM news.articles
            GROUP BY source
        """)
        results = db.cursor.fetchall()

        print("\nArticles by source:")
        for row in results:
            print(f"  - {row['source']}: {row['count']} articles")

        # Get sample articles
        db.cursor.execute("""
            SELECT id, title, source, published_date, language,
                   LENGTH(content) as content_length
            FROM news.articles
            ORDER BY published_date DESC
            LIMIT 5
        """)
        articles = db.cursor.fetchall()

        print("\nLatest 5 articles:")
        for i, article in enumerate(articles, 1):
            print(f"\n{i}. Article ID: {article['id']}")
            print(f"   Source: {article['source']}")
            print(f"   Language: {article['language']}")
            print(f"   Published: {article['published_date']}")
            print(f"   Content length: {article['content_length']} chars")

            # Try to print title, fallback if encoding fails
            try:
                print(f"   Title: {article['title']}")
            except UnicodeEncodeError:
                print(f"   Title: [Contains Azerbaijani characters - {len(article['title'])} chars]")

        # Verify Azerbaijani characters
        db.cursor.execute("""
            SELECT title, content
            FROM news.articles
            LIMIT 1
        """)
        sample = db.cursor.fetchone()

        if sample:
            az_chars = ['ə', 'ı', 'ğ', 'ş', 'ç', 'ö', 'ü', 'İ', 'Ə', 'Ğ', 'Ş', 'Ç', 'Ö', 'Ü']
            found = []
            for char in az_chars:
                if char in sample['title'] or char in sample['content']:
                    found.append(char)

            if found:
                print(f"\n[SUCCESS] Azerbaijani characters verified in database")
                print(f"Found characters: {len(found)} unique Azerbaijani letters")

    finally:
        db.close()


if __name__ == "__main__":
    verify_database()
