"""
Test database connection and schema
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import Database

def test_connection():
    """Test database connection"""
    db = Database()

    if db.connect():
        print("[SUCCESS] Database connection test passed")

        # Check if table exists
        db.cursor.execute("""
            SELECT table_name, column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = 'news' AND table_name = 'articles'
            ORDER BY ordinal_position
        """)

        columns = db.cursor.fetchall()
        print(f"\nFound {len(columns)} columns in news.articles table:")
        for col in columns:
            print(f"  - {col['column_name']}: {col['data_type']}")

        db.close()
    else:
        print("[ERROR] Database connection test failed")

if __name__ == "__main__":
    test_connection()
