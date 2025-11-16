"""
Migration: Add scraping_session_id to articles table to link articles to their scraping session
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import Database

print("=" * 80)
print("MIGRATION: Adding session link to articles table")
print("=" * 80)

db = Database()
if not db.connect():
    print("[ERROR] Failed to connect to database")
    sys.exit(1)

try:
    # Step 1: Add scraping_session_id column
    print("\n[1/3] Adding scraping_session_id column...")
    db.cursor.execute("""
        ALTER TABLE news.articles
        ADD COLUMN IF NOT EXISTS scraping_session_id INTEGER
        REFERENCES news.scraping_summaries(id)
        ON DELETE SET NULL
    """)
    db.conn.commit()
    print("[SUCCESS] Column added")

    # Step 2: Create index for better query performance
    print("\n[2/3] Creating index on scraping_session_id...")
    db.cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_articles_session
        ON news.articles(scraping_session_id)
    """)
    db.conn.commit()
    print("[SUCCESS] Index created")

    # Step 3: Verify the changes
    print("\n[3/3] Verifying schema changes...")
    db.cursor.execute("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_schema = 'news'
        AND table_name = 'articles'
        AND column_name = 'scraping_session_id'
    """)
    result = db.cursor.fetchone()

    if result:
        print("[SUCCESS] Verification passed:")
        print(f"  Column: {result['column_name']}")
        print(f"  Type: {result['data_type']}")
        print(f"  Nullable: {result['is_nullable']}")
    else:
        print("[ERROR] Column not found after migration")

    # Show updated schema
    print("\n" + "=" * 80)
    print("Updated articles table schema:")
    print("=" * 80)
    db.cursor.execute("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = 'news'
        AND table_name = 'articles'
        ORDER BY ordinal_position
    """)
    columns = db.cursor.fetchall()
    for col in columns:
        print(f"  - {col['column_name']}: {col['data_type']}")

    print("\n" + "=" * 80)
    print("Migration completed successfully!")
    print("=" * 80)

except Exception as e:
    print(f"\n[ERROR] Migration failed: {e}")
    db.conn.rollback()
    import traceback
    traceback.print_exc()
finally:
    db.close()
