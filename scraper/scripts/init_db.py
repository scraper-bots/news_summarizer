"""
Initialize database schema
Run this script to create the news schema and tables
"""

import psycopg2
import os
import pathlib
from dotenv import load_dotenv

# Load environment variables from project root
env_path = pathlib.Path(__file__).parent.parent.parent / '.env.local'
load_dotenv(env_path)

def init_database():
    """Initialize database with schema"""
    try:
        # Connect to database
        conn = psycopg2.connect(
            os.getenv('DATABASE_URL'),
            client_encoding='UTF8'
        )
        cursor = conn.cursor()

        # Read and execute schema file from project root
        schema_path = pathlib.Path(__file__).parent.parent.parent / 'schema.sql'
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()

        cursor.execute(schema_sql)
        conn.commit()

        print("[SUCCESS] Database schema initialized successfully!")
        print("[SUCCESS] Table 'news.articles' created")

        # Verify table creation
        cursor.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = 'news' AND table_name = 'articles'
            ORDER BY ordinal_position
        """)

        columns = cursor.fetchall()
        print("\nTable columns:")
        for col in columns:
            print(f"  - {col[0]}: {col[1]}")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"[ERROR] Error initializing database: {e}")
        raise

if __name__ == "__main__":
    init_database()
