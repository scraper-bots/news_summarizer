"""
Final schema verification after cleanup
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'scraper'))

from scraper.db import Database

output_file = "final_schema.txt"

with open(output_file, 'w', encoding='utf-8') as f:
    f.write("=" * 80 + "\n")
    f.write("FINAL SCHEMA VERIFICATION\n")
    f.write("=" * 80 + "\n\n")

    db = Database()

    if db.connect():
        # Check articles table
        f.write("[TABLE 1] news.articles\n")
        f.write("-" * 80 + "\n")
        db.cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_schema = 'news' AND table_name = 'articles'
            ORDER BY ordinal_position
        """)
        articles_columns = db.cursor.fetchall()

        for col in articles_columns:
            nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
            default = f" DEFAULT {col['column_default']}" if col['column_default'] else ""
            f.write(f"  {col['column_name']:<25} {col['data_type']:<20} {nullable}{default}\n")

        db.cursor.execute("SELECT COUNT(*) as count FROM news.articles")
        count = db.cursor.fetchone()['count']
        f.write(f"\nRows: {count}\n")

        # Check scraping_summaries table
        f.write("\n" + "=" * 80 + "\n")
        f.write("[TABLE 2] news.scraping_summaries\n")
        f.write("-" * 80 + "\n")
        db.cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_schema = 'news' AND table_name = 'scraping_summaries'
            ORDER BY ordinal_position
        """)
        summaries_columns = db.cursor.fetchall()

        for col in summaries_columns:
            nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
            default = f" DEFAULT {col['column_default']}" if col['column_default'] else ""
            f.write(f"  {col['column_name']:<25} {col['data_type']:<20} {nullable}{default}\n")

        db.cursor.execute("SELECT COUNT(*) as count FROM news.scraping_summaries")
        count = db.cursor.fetchone()['count']
        f.write(f"\nRows: {count}\n")

        # Check foreign key relationship
        f.write("\n" + "=" * 80 + "\n")
        f.write("[FOREIGN KEYS]\n")
        f.write("-" * 80 + "\n")
        db.cursor.execute("""
            SELECT
                tc.constraint_name,
                tc.table_name,
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
              AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
              ON ccu.constraint_name = tc.constraint_name
              AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
              AND tc.table_schema = 'news'
        """)
        fkeys = db.cursor.fetchall()

        for fk in fkeys:
            f.write(f"  {fk['table_name']}.{fk['column_name']} -> {fk['foreign_table_name']}.{fk['foreign_column_name']}\n")

        # Check indexes
        f.write("\n" + "=" * 80 + "\n")
        f.write("[INDEXES]\n")
        f.write("-" * 80 + "\n")
        db.cursor.execute("""
            SELECT tablename, indexname
            FROM pg_indexes
            WHERE schemaname = 'news'
            ORDER BY tablename, indexname
        """)
        indexes = db.cursor.fetchall()

        current_table = None
        for idx in indexes:
            if idx['tablename'] != current_table:
                current_table = idx['tablename']
                f.write(f"\n{current_table}:\n")
            f.write(f"  - {idx['indexname']}\n")

        # Check relationship statistics
        f.write("\n" + "=" * 80 + "\n")
        f.write("[RELATIONSHIP STATISTICS]\n")
        f.write("-" * 80 + "\n")

        db.cursor.execute("""
            SELECT
                s.id as session_id,
                s.scraping_date,
                s.new_articles_count as expected_articles,
                COUNT(a.id) as actual_linked_articles
            FROM news.scraping_summaries s
            LEFT JOIN news.articles a ON a.scraping_session_id = s.id
            GROUP BY s.id, s.scraping_date, s.new_articles_count
            ORDER BY s.id DESC
        """)
        stats = db.cursor.fetchall()

        f.write(f"\n{'Session':<10} {'Date':<12} {'Expected':<10} {'Linked':<10} {'Status'}\n")
        f.write("-" * 60 + "\n")
        for stat in stats:
            status = "✓" if stat['actual_linked_articles'] > 0 or stat['expected_articles'] == 0 else "✗"
            f.write(f"{stat['session_id']:<10} {str(stat['scraping_date']):<12} {stat['expected_articles']:<10} {stat['actual_linked_articles']:<10} {status}\n")

        f.write("\n" + "=" * 80 + "\n")
        f.write("VERIFICATION COMPLETE\n")
        f.write("=" * 80 + "\n")

        db.close()
    else:
        f.write("[ERROR] Failed to connect to database\n")

print(f"[SUCCESS] Verification complete. Report saved to: {output_file}")
