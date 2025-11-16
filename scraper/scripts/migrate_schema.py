"""
Migrate database schema to support session-based summarization
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import Database

db = Database()
db.connect()

print("Migrating database schema...")
print("=" * 80)

# Create scraping_summaries table
print("\n1. Creating scraping_summaries table...")
db.cursor.execute("""
    CREATE TABLE IF NOT EXISTS news.scraping_summaries (
        id SERIAL PRIMARY KEY,
        scraping_date DATE NOT NULL DEFAULT CURRENT_DATE,
        summary TEXT NOT NULL,
        articles_count INTEGER NOT NULL,
        sources_count INTEGER NOT NULL,
        new_articles_count INTEGER NOT NULL,
        scraping_duration_seconds NUMERIC(10, 2),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")
db.conn.commit()
print("[SUCCESS] Table created")

# Create index
print("\n2. Creating index...")
db.cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_scraping_summaries_date
    ON news.scraping_summaries(scraping_date DESC)
""")
db.conn.commit()
print("[SUCCESS] Index created")

# Create update function
print("\n3. Creating update trigger function...")
db.cursor.execute("""
    CREATE OR REPLACE FUNCTION news.update_scraping_summaries_updated_at()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.updated_at = CURRENT_TIMESTAMP;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql
""")
db.conn.commit()
print("[SUCCESS] Function created")

# Create trigger
print("\n4. Creating trigger...")
db.cursor.execute("""
    DROP TRIGGER IF EXISTS update_scraping_summaries_updated_at
    ON news.scraping_summaries
""")
db.cursor.execute("""
    CREATE TRIGGER update_scraping_summaries_updated_at
        BEFORE UPDATE ON news.scraping_summaries
        FOR EACH ROW
        EXECUTE FUNCTION news.update_scraping_summaries_updated_at()
""")
db.conn.commit()
print("[SUCCESS] Trigger created")

# Verify
print("\n5. Verifying schema...")
db.cursor.execute("""
    SELECT column_name, data_type
    FROM information_schema.columns
    WHERE table_schema = 'news'
    AND table_name = 'scraping_summaries'
    ORDER BY ordinal_position
""")
columns = db.cursor.fetchall()
print("\nColumns in scraping_summaries:")
for col in columns:
    print(f"  - {col['column_name']}: {col['data_type']}")

print("\n" + "=" * 80)
print("Migration completed successfully!")
db.close()
