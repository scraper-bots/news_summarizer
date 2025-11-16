"""
Verify database schema - check what tables and columns actually exist
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import pathlib

# Load environment variables
env_path = pathlib.Path(__file__).parent / '.env.local'
load_dotenv(env_path)

def check_database_schema():
    """Connect to database and check actual schema"""
    connection_string = os.getenv('DATABASE_URL')

    if not connection_string:
        print("[ERROR] DATABASE_URL not found in environment variables")
        return

    try:
        # Connect to database
        conn = psycopg2.connect(connection_string, client_encoding='UTF8')
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        print("[SUCCESS] Connected to database successfully\n")

        # Check if news schema exists
        cursor.execute("""
            SELECT schema_name
            FROM information_schema.schemata
            WHERE schema_name = 'news'
        """)
        schema = cursor.fetchone()

        if schema:
            print("[SUCCESS] Schema 'news' exists\n")
        else:
            print("[ERROR] Schema 'news' does NOT exist\n")
            return

        # Get all tables in news schema
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'news'
            ORDER BY table_name
        """)
        tables = cursor.fetchall()

        print("=" * 80)
        print("TABLES IN 'news' SCHEMA:")
        print("=" * 80)

        if not tables:
            print("[ERROR] No tables found in 'news' schema\n")
            return

        for table in tables:
            table_name = table['table_name']
            print(f"\n[TABLE] news.{table_name}")
            print("-" * 80)

            # Get columns for this table
            cursor.execute("""
                SELECT
                    column_name,
                    data_type,
                    character_maximum_length,
                    is_nullable,
                    column_default
                FROM information_schema.columns
                WHERE table_schema = 'news' AND table_name = %s
                ORDER BY ordinal_position
            """, (table_name,))

            columns = cursor.fetchall()

            print(f"{'Column':<30} {'Type':<20} {'Nullable':<10} {'Default':<30}")
            print("-" * 80)

            for col in columns:
                col_name = col['column_name']
                data_type = col['data_type']
                if col['character_maximum_length']:
                    data_type += f"({col['character_maximum_length']})"
                nullable = col['is_nullable']
                default = col['column_default'] or ''
                if len(default) > 30:
                    default = default[:27] + '...'

                print(f"{col_name:<30} {data_type:<20} {nullable:<10} {default:<30}")

            # Get row count
            cursor.execute(f"SELECT COUNT(*) as count FROM news.{table_name}")
            count = cursor.fetchone()['count']
            print(f"\n[INFO] Row count: {count}")

            # Get indexes
            cursor.execute("""
                SELECT indexname, indexdef
                FROM pg_indexes
                WHERE schemaname = 'news' AND tablename = %s
            """, (table_name,))
            indexes = cursor.fetchall()

            if indexes:
                print(f"\n[INFO] Indexes:")
                for idx in indexes:
                    print(f"  - {idx['indexname']}")

        print("\n" + "=" * 80)
        print("SCHEMA CHECK COMPLETE")
        print("=" * 80)

        # Close connection
        cursor.close()
        conn.close()
        print("\n[SUCCESS] Database connection closed")

    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    check_database_schema()
