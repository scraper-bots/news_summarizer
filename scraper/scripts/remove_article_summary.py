"""
Migration: Remove unused summary column from articles table
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import Database

print("=" * 80)
print("MIGRATION: Removing unused summary column from articles table")
print("=" * 80)

db = Database()
if not db.connect():
    print("[ERROR] Failed to connect to database")
    sys.exit(1)

try:
    # Step 1: Check if column exists and verify it's all NULL
    print("\n[1/3] Checking current state...")
    db.cursor.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = 'news'
        AND table_name = 'articles'
        AND column_name = 'summary'
    """)
    column_exists = db.cursor.fetchone()

    if not column_exists:
        print("[INFO] Column 'summary' does not exist, nothing to remove")
        db.close()
        sys.exit(0)

    # Check if all values are NULL
    db.cursor.execute("""
        SELECT COUNT(*) as total,
               COUNT(summary) as non_null_count
        FROM news.articles
    """)
    result = db.cursor.fetchone()
    total = result['total']
    non_null = result['non_null_count']

    print(f"[INFO] Total articles: {total}")
    print(f"[INFO] Articles with summary: {non_null}")
    print(f"[INFO] NULL summaries: {total - non_null}")

    if non_null > 0:
        print(f"\n[WARNING] {non_null} articles have non-NULL summary values!")
        response = input("Do you want to continue and delete these values? (yes/no): ")
        if response.lower() != 'yes':
            print("[INFO] Migration cancelled by user")
            db.close()
            sys.exit(0)

    # Step 2: Drop the column
    print("\n[2/3] Dropping summary column...")
    db.cursor.execute("""
        ALTER TABLE news.articles
        DROP COLUMN IF EXISTS summary
    """)
    db.conn.commit()
    print("[SUCCESS] Column dropped")

    # Step 3: Verify the changes
    print("\n[3/3] Verifying schema changes...")
    db.cursor.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = 'news'
        AND table_name = 'articles'
        AND column_name = 'summary'
    """)
    still_exists = db.cursor.fetchone()

    if still_exists:
        print("[ERROR] Column still exists after migration!")
    else:
        print("[SUCCESS] Column successfully removed")

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
